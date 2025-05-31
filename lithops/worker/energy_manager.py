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
import json
import logging
from typing import Dict, Any, Optional, Union, List

from lithops.worker.energy import IEnergyMonitor
from lithops.worker.energy.factory import EnergyMonitorFactory
from lithops.worker.energy.monitors import NoOpEnergyMonitor, PerfEnergyMonitor, EBPFEnergyMonitor, IPMIEnergyMonitor

logger = logging.getLogger(__name__)

class EnergyManager:
    """
    Manager class for energy monitoring.
    Handles energy monitoring strategies based on configuration.
    """
    
    def __init__(self, process_id: int, config: Dict[str, Any] = None):
        """
        Initialize the energy manager.
        
        Args:
            process_id: The process ID to monitor.
            config: Configuration options.
        """
        self.process_id = process_id
        self.config = config or {}
        self.function_name = None
        
        # Register available energy monitoring strategies
        EnergyMonitorFactory.register_strategy('perf', PerfEnergyMonitor)
        EnergyMonitorFactory.register_strategy('ebpf', EBPFEnergyMonitor)
        EnergyMonitorFactory.register_strategy('ipmi', IPMIEnergyMonitor)
        EnergyMonitorFactory.register_strategy('noop', NoOpEnergyMonitor)
        
        # Get energy monitoring configuration
        energy_enabled = self.config.get('energy', True)
        energy_strategy = self.config.get('energy_strategy', 'auto')
        
        # Create energy monitor
        self.energy_monitor = EnergyMonitorFactory.create_monitor(
            energy_strategy,
            process_id,
            self.config
        )
        
        logger.info(f"Energy manager initialized for process {process_id} with strategy {energy_strategy}")
    
    def start(self) -> bool:
        """
        Start energy monitoring.
        
        Returns:
            bool: True if monitoring started successfully, False otherwise.
        """
        return self.energy_monitor.start()
    
    def stop(self) -> None:
        """Stop energy monitoring."""
        self.energy_monitor.stop()
    
    def get_energy_data(self) -> Dict[str, Any]:
        """
        Get the collected energy data.
        
        Returns:
            Dict[str, Any]: A dictionary containing energy metrics.
        """
        return self.energy_monitor.get_energy_data()
    
    def process_energy_data(self, task: Any, call_status: Any, cpu_info: Dict[str, Any]) -> None:
        """
        Process energy data and add it to call status.
        
        Args:
            task: The task object.
            call_status: The call status object.
            cpu_info: CPU information.
        """
        # Read function name from stats file if not already set
        if not self.function_name:
            self.read_function_name_from_stats(task.stats_file)
            
        # Get energy data
        energy_data = self.get_energy_data()
        
        # Add function name to energy data if available
        if self.function_name:
            if 'metadata' not in energy_data:
                energy_data['metadata'] = {}
            energy_data['metadata']['function_name'] = self.function_name
        
        # Add energy metrics to call status
        call_status.add('worker_func_energy_duration', energy_data['duration'])
        call_status.add('worker_func_energy_source', energy_data.get('source', 'unknown'))
        
        # Add energy metrics
        if 'energy' in energy_data:
            for metric, value in energy_data['energy'].items():
                # Handle both simple values and dictionaries with statistics
                if isinstance(value, dict) and 'avg' in value:
                    call_status.add(f'worker_func_energy_{metric}', value['avg'])
                    call_status.add(f'worker_func_energy_{metric}_min', value['min'])
                    call_status.add(f'worker_func_energy_{metric}_max', value['max'])
                else:
                    call_status.add(f'worker_func_energy_{metric}', value)
            
            # Add specific energy metrics for backward compatibility
            if 'pkg' in energy_data['energy']:
                pkg_value = energy_data['energy']['pkg']
                if isinstance(pkg_value, dict) and 'avg' in pkg_value:
                    call_status.add('worker_func_perf_energy_pkg', pkg_value['avg'])
                else:
                    call_status.add('worker_func_perf_energy_pkg', pkg_value)
            
            if 'cores' in energy_data['energy']:
                cores_value = energy_data['energy']['cores']
                if isinstance(cores_value, dict) and 'avg' in cores_value:
                    call_status.add('worker_func_perf_energy_cores', cores_value['avg'])
                else:
                    call_status.add('worker_func_perf_energy_cores', cores_value)
        
        # Add monitor-specific data
        if 'monitors' in energy_data:
            for monitor_name, monitor_data in energy_data['monitors'].items():
                call_status.add(f'worker_func_energy_monitor_{monitor_name}', monitor_data)
        
        # Log energy data
        self.energy_monitor.log_energy_data(energy_data, task, cpu_info, self.function_name)
    
    def read_function_name_from_stats(self, stats_file: str) -> Optional[str]:
        """
        Read function name from stats file.
        
        Args:
            stats_file: Path to the stats file.
            
        Returns:
            Optional[str]: The function name if found, None otherwise.
        """
        if not os.path.exists(stats_file):
            logger.warning(f"Stats file not found: {stats_file}")
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
    
    def update_function_name(self, task: Any, cpu_info: Dict[str, Any], stats_file: str) -> None:
        """
        Update the function name in the energy monitor.
        
        Args:
            task: The task object.
            cpu_info: CPU information.
            stats_file: Path to the stats file.
        """
        # Try to read function name from stats file
        function_name = None
        if os.path.exists(stats_file):
            try:
                with open(stats_file, 'r') as fid:
                    for line in fid.readlines():
                        try:
                            key, value = line.strip().split(" ", 1)
                            if key == 'function_name':
                                function_name = value
                                self.function_name = value
                                logger.info(f"Found function name in stats file: {function_name}")
                                break
                        except Exception as e:
                            logger.error(f"Error processing stats file line: {e}")
            except Exception as e:
                logger.error(f"Error reading stats file: {e}")
        
        if not function_name:
            logger.warning("Function name not found in stats file for energy monitoring")
            return
            
        logger.info(f"Updating function name in energy data: {function_name}")
        
        # If the energy monitor has an update_function_name method, call it
        if hasattr(self.energy_monitor, 'update_function_name'):
            self.energy_monitor.update_function_name(task, function_name)
            
        # Also update the JSON files directly
        try:
            # Get the current working directory
            cwd = os.getcwd()
            json_dir = os.path.join(cwd, 'energy_data')
            
            # Update perf JSON file
            perf_file = os.path.join(json_dir, f"{task.job_key}_{task.call_id}_perf.json")
            if os.path.exists(perf_file):
                with open(perf_file, 'r') as f:
                    data = json.load(f)
                
                if 'energy_consumption' in data:
                    data['energy_consumption']['function_name'] = function_name
                
                with open(perf_file, 'w') as f:
                    json.dump(data, f, indent=2)
                logger.info(f"Updated function name in perf JSON file: {function_name}")
            
            # Update ebpf JSON file
            ebpf_file = os.path.join(json_dir, f"{task.job_key}_{task.call_id}_ebpf.json")
            if os.path.exists(ebpf_file):
                with open(ebpf_file, 'r') as f:
                    data = json.load(f)
                
                if 'energy_consumption' in data:
                    data['energy_consumption']['function_name'] = function_name
                
                with open(ebpf_file, 'w') as f:
                    json.dump(data, f, indent=2)
                logger.info(f"Updated function name in ebpf JSON file: {function_name}")
            
            # Update composite JSON file
            composite_file = os.path.join(json_dir, f"{task.job_key}_{task.call_id}_composite.json")
            if os.path.exists(composite_file):
                with open(composite_file, 'r') as f:
                    data = json.load(f)
                
                data['function_name'] = function_name
                
                with open(composite_file, 'w') as f:
                    json.dump(data, f, indent=2)
                logger.info(f"Updated function name in composite JSON file: {function_name}")
                
            # Update ipmi JSON file
            ipmi_file = os.path.join(json_dir, f"{task.job_key}_{task.call_id}_ipmi.json")
            if os.path.exists(ipmi_file):
                with open(ipmi_file, 'r') as f:
                    data = json.load(f)
                
                if 'energy_consumption' in data:
                    data['energy_consumption']['function_name'] = function_name
                
                with open(ipmi_file, 'w') as f:
                    json.dump(data, f, indent=2)
                logger.info(f"Updated function name in ipmi JSON file: {function_name}")
            
            # Update summary files
            for summary_file in ['perf_summary.json', 'ebpf_summary.json', 'ipmi_summary.json', 'composite_summary.json']:
                summary_path = os.path.join(json_dir, summary_file)
                if os.path.exists(summary_path):
                    with open(summary_path, 'r') as f:
                        summary = json.load(f)
                    
                    for entry in summary:
                        if entry.get('execution_id') == f"{task.job_key}_{task.call_id}":
                            entry['function_name'] = function_name
                    
                    with open(summary_path, 'w') as f:
                        json.dump(summary, f, indent=2)
                    logger.info(f"Updated function name in {summary_file}")
        except Exception as e:
            logger.error(f"Error updating function name in JSON files: {e}")
