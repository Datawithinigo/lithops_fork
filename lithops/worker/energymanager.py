#
# (C) Copyright IBM Corp. 2020
# (C) Copyright Cloudlab URV 2020
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import logging
from lithops.worker.energymonitor_rapl import EnergyMonitor
from lithops.worker.energymonitor_ebpf import EBPFEnergyMonitor

logger = logging.getLogger(__name__)

class EnergyManager:
    """
    Manager class for energy monitoring.
    Handles both eBPF and regular energy monitors.
    """
    
    def __init__(self, process_id, run_both_monitors=False):
        """
        Initialize the energy manager.
        
        Args:
            process_id: The process ID to monitor
            run_both_monitors: Whether to run both eBPF and regular energy monitors
        """
        self.process_id = process_id
        self.run_both_monitors = run_both_monitors
        self.energy_monitor = EnergyMonitor(process_id)
        self.ebpf_energy_monitor = EBPFEnergyMonitor(process_id)
        self.energy_monitor_started = False
        self.ebpf_energy_monitor_started = False
        self.function_name = None
    
    def start(self):
        """Start energy monitoring."""
        # Try to start eBPF energy monitor first
        self.ebpf_energy_monitor_started = self.ebpf_energy_monitor.start()
        
        # Determine if we should also start the regular energy monitor
        if self.run_both_monitors:
            # Start both monitors regardless of eBPF success
            self.energy_monitor_started = self.energy_monitor.start()
            if self.ebpf_energy_monitor_started:
                logger.info("Running both eBPF and regular energy monitors")
            else:
                logger.info("eBPF energy monitor failed to start, running only regular energy monitor")
        else:
            # Fall back to regular monitor only if eBPF fails
            if not self.ebpf_energy_monitor_started:
                logger.info("eBPF energy monitor failed to start, falling back to regular energy monitor")
                self.energy_monitor_started = self.energy_monitor.start()
            else:
                logger.info("eBPF energy monitor started successfully")
                self.energy_monitor_started = False
        
        return self.energy_monitor_started or self.ebpf_energy_monitor_started
    
    def stop(self):
        """Stop energy monitoring."""
        if self.ebpf_energy_monitor_started:
            self.ebpf_energy_monitor.stop()
        if self.energy_monitor_started:
            self.energy_monitor.stop()
    
    def read_function_name_from_stats(self, stats_file):
        """Read function name from stats file."""
        if not os.path.exists(stats_file):
            return None
            
        logger.info(f"Reading stats file for function name: {stats_file}")
        try:
            with open(stats_file, 'r') as fid:
                for line in fid.readlines():
                    try:
                        key, value = line.strip().split(" ", 1)
                        if key == 'function_name':
                            self.function_name = value
                            logger.info(f"Found function name in stats file: {self.function_name}")
                            return self.function_name
                    except Exception as e:
                        logger.error(f"Error processing stats file line: {line} - {e}")
        except Exception as e:
            logger.error(f"Error reading stats file: {e}")
        
        return None
    
    def process_energy_data(self, task, call_status, cpu_info):
        """Process energy data and add it to call status."""
        # Add energy monitoring data
        if self.ebpf_energy_monitor_started:
            # Get eBPF energy data
            ebpf_energy_data = self.ebpf_energy_monitor.get_energy_data()
            
            # Add duration and source
            call_status.add('worker_func_energy_duration', ebpf_energy_data['duration'])
            call_status.add('worker_func_energy_source', ebpf_energy_data.get('source', 'ebpf'))
            call_status.add('worker_func_energy_method_used', 'ebpf')
            
            # Add energy metrics
            if ebpf_energy_data['energy']:
                # Add individual energy metrics
                for metric, value in ebpf_energy_data['energy'].items():
                    call_status.add(f'worker_func_energy_{metric}', value)
                
                # Add energy metrics for pkg and cores
                call_status.add('worker_func_perf_energy_pkg', ebpf_energy_data['energy']['pkg'])
                call_status.add('worker_func_perf_energy_cores', ebpf_energy_data['energy']['cores'])
                
                # Add eBPF-specific metrics
                call_status.add('worker_func_ebpf_cpu_cycles', ebpf_energy_data['energy']['cpu_cycles'])
                call_status.add('worker_func_ebpf_energy_from_cycles', ebpf_energy_data['energy']['energy_from_cycles'])
            
            # Log energy data and store it in JSON format
            self.ebpf_energy_monitor.log_energy_data(ebpf_energy_data, task, cpu_info, self.function_name)
        
        if self.energy_monitor_started:
            # Get RAPL energy data
            energy_data = self.energy_monitor.get_energy_data()
            
            # Add duration and source
            call_status.add('worker_func_energy_duration', energy_data['duration'])
            call_status.add('worker_func_energy_source', energy_data.get('source', 'unknown'))
            
            # Add method used based on the source
            source = energy_data.get('source', 'unknown')
            if source == 'perf':
                call_status.add('worker_func_energy_method_used', 'perf')
            elif source == 'rapl_direct':
                call_status.add('worker_func_energy_method_used', 'rapl')
            elif source == 'cpu_estimate':
                call_status.add('worker_func_energy_method_used', 'cpu_estimation')
            elif source == 'duration_estimate':
                call_status.add('worker_func_energy_method_used', 'duration_estimation')
            else:
                call_status.add('worker_func_energy_method_used', 'unknown')
            
            # Add energy metrics
            if energy_data['energy']:
                # Add individual energy metrics
                for metric, value in energy_data['energy'].items():
                    call_status.add(f'worker_func_energy_{metric}', value)
                
                # Add energy metrics for pkg and cores
                call_status.add('worker_func_perf_energy_pkg', energy_data['energy']['pkg'])
                call_status.add('worker_func_perf_energy_cores', energy_data['energy']['cores'])
            
            # Log energy data and store it in JSON format
            self.energy_monitor.log_energy_data(energy_data, task, cpu_info, self.function_name)
    
    def update_function_name(self, task, cpu_info, stats_file):
        """Update function name in energy data if available."""
        if not (self.ebpf_energy_monitor_started or self.energy_monitor_started):
            return
            
        if not os.path.exists(stats_file):
            logger.warning("Stats file not found for updating function name")
            return
            
        function_name = self.read_function_name_from_stats(stats_file)
        if not function_name:
            logger.warning("Function name not found in stats file for energy monitoring")
            return
            
        logger.info(f"Updating function name in energy data: {function_name}")
        
        # Update function name in energy monitors
        if self.ebpf_energy_monitor_started:
            self.ebpf_energy_monitor._store_energy_data_json(
                self.ebpf_energy_monitor.get_energy_data(), 
                task, 
                cpu_info, 
                function_name
            )
        
        if self.energy_monitor_started:
            self.energy_monitor.update_function_name(task, function_name)
