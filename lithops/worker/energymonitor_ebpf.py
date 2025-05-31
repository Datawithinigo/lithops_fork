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
import time
import logging
import subprocess
import threading
from collections import defaultdict
from .energymonitor_json_utils import store_energy_data_json, update_function_name

logger = logging.getLogger(__name__)

# BPF program to monitor CPU cycles and RAPL counters
BPF_PROGRAM = """
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>
#include <linux/perf_event.h>

// Define a structure to store energy data
struct energy_data_t {
    u32 pid;
    u64 cpu_cycles;
    u64 rapl_energy_pkg;
    u64 rapl_energy_cores;
    u64 timestamp;
};

// Create BPF maps to store energy data
BPF_HASH(energy_data, u32, struct energy_data_t);
BPF_PERF_OUTPUT(energy_events);

// Function to be called on context switch
int on_context_switch(struct pt_regs *ctx, struct task_struct *prev, struct task_struct *next)
{
    u32 pid = prev->pid;
    
    // Skip kernel threads
    if (pid == 0)
        return 0;
    
    // Get current timestamp
    u64 ts = bpf_ktime_get_ns();
    
    // Read CPU cycles
    u64 cpu_cycles = 0;
    bpf_perf_event_read(ctx, &cpu_cycles);
    
    // Read RAPL counters
    u64 rapl_energy_pkg = 0;
    u64 rapl_energy_cores = 0;
    
    // Try to read RAPL counters from MSR
    int cpu = bpf_get_smp_processor_id();
    u32 msr_pkg = 0x611;  // MSR_PKG_ENERGY_STATUS
    u32 msr_cores = 0x639;  // MSR_PP0_ENERGY_STATUS
    
    // Read MSR_PKG_ENERGY_STATUS
    bpf_probe_read(&rapl_energy_pkg, sizeof(rapl_energy_pkg), (void *)msr_pkg);
    
    // Read MSR_PP0_ENERGY_STATUS
    bpf_probe_read(&rapl_energy_cores, sizeof(rapl_energy_cores), (void *)msr_cores);
    
    // Create energy data structure
    struct energy_data_t data = {};
    data.pid = pid;
    data.cpu_cycles = cpu_cycles;
    data.rapl_energy_pkg = rapl_energy_pkg;
    data.rapl_energy_cores = rapl_energy_cores;
    data.timestamp = ts;
    
    // Store energy data in map
    energy_data.update(&pid, &data);
    
    // Send energy data to user space
    energy_events.perf_submit(ctx, &data, sizeof(data));
    
    return 0;
}
"""

class EBPFEnergyMonitor:
    """
    eBPF-based energy monitor that hooks into the scheduler to count CPU cycles
    and reads RAPL counters in-kernel on every context switch.
    """
    def __init__(self, process_id):
        self.process_id = process_id
        self.bpf = None
        self.thread = None
        self.running = False
        self.energy_data = defaultdict(lambda: {
            'cpu_cycles': 0,
            'rapl_energy_pkg': 0,
            'rapl_energy_cores': 0,
            'timestamps': []
        })
        self.start_time = None
        self.end_time = None
        self.function_name = None
        
        # Print directly to terminal for debugging
        print(f"\n==== EBPF ENERGY MONITOR INITIALIZED FOR PROCESS {process_id} ====")
        
    def _check_bpf_dependencies(self):
        """Check if BPF dependencies are installed."""
        try:
            # Check if BCC is installed
            import bcc
            return True
        except ImportError:
            print("BCC (BPF Compiler Collection) is not installed.")
            print("Please install it with: sudo apt-get install bpfcc-tools python3-bpfcc")
            return False
            
    def _check_kernel_config(self):
        """Check if the kernel is configured for BPF."""
        try:
            # Check if BPF is enabled in the kernel
            with open('/proc/config.gz', 'rb') as f:
                config = subprocess.check_output(['zcat'], stdin=f).decode()
                if 'CONFIG_BPF=y' not in config:
                    print("BPF is not enabled in the kernel.")
                    return False
                if 'CONFIG_BPF_SYSCALL=y' not in config:
                    print("BPF syscall is not enabled in the kernel.")
                    return False
                return True
        except Exception as e:
            print(f"Error checking kernel config: {e}")
            # Try to check if BPF is available by running a simple BPF program
            try:
                import bcc
                bcc.BPF(text='int kprobe__sys_clone(void *ctx) { return 0; }')
                return True
            except Exception as e:
                print(f"Error running BPF program: {e}")
                return False
                
    def _process_energy_event(self, cpu, data, size):
        """Process energy events from BPF."""
        event = self.bpf["energy_events"].event(data)
        pid = event.pid
        
        # Store energy data for the process
        self.energy_data[pid]['cpu_cycles'] += event.cpu_cycles
        self.energy_data[pid]['rapl_energy_pkg'] = event.rapl_energy_pkg
        self.energy_data[pid]['rapl_energy_cores'] = event.rapl_energy_cores
        self.energy_data[pid]['timestamps'].append(event.timestamp)
        
    def _run_bpf_monitor(self):
        """Run the BPF monitor in a separate thread."""
        try:
            # Import BCC
            from bcc import BPF
            
            # Load BPF program
            self.bpf = BPF(text=BPF_PROGRAM)
            
            # Attach to context switch events
            self.bpf.attach_kprobe(event="finish_task_switch", fn_name="on_context_switch")
            
            # Open perf buffer for energy events
            self.bpf["energy_events"].open_perf_buffer(self._process_energy_event)
            
            # Process events
            while self.running:
                try:
                    self.bpf.perf_buffer_poll(timeout=100)
                except KeyboardInterrupt:
                    break
                    
        except Exception as e:
            print(f"Error running BPF monitor: {e}")
            
    def start(self):
        """Start monitoring energy consumption using eBPF."""
        print("\n==== STARTING EBPF ENERGY MONITORING ====")
        
        # Check if BPF dependencies are installed
        if not self._check_bpf_dependencies():
            print("BPF dependencies are not installed. Falling back to perf.")
            return False
            
        # Check if the kernel is configured for BPF
        if not self._check_kernel_config():
            print("Kernel is not configured for BPF. Falling back to perf.")
            return False
            
        try:
            # Set running flag
            self.running = True
            
            # Start BPF monitor in a separate thread
            self.thread = threading.Thread(target=self._run_bpf_monitor)
            self.thread.daemon = True
            self.thread.start()
            
            # Record start time
            self.start_time = time.time()
            
            print(f"eBPF energy monitoring started at: {self.start_time}")
            return True
        except Exception as e:
            print(f"Error starting eBPF energy monitoring: {e}")
            return False
            
    def stop(self):
        """Stop monitoring energy consumption."""
        print("\n==== STOPPING EBPF ENERGY MONITORING ====")
        
        if not self.running:
            print("eBPF energy monitoring is not running.")
            return
            
        try:
            # Set running flag to False
            self.running = False
            
            # Wait for thread to finish
            if self.thread:
                self.thread.join(timeout=5)
                
            # Record end time
            self.end_time = time.time()
            
            # Calculate duration
            duration = self.end_time - self.start_time
            print(f"eBPF energy monitoring stopped at: {self.end_time}")
            print(f"Monitoring duration: {duration:.2f} seconds")
            
            # Detach BPF program
            if self.bpf:
                self.bpf.detach_kprobe(event="finish_task_switch")
                
        except Exception as e:
            print(f"Error stopping eBPF energy monitoring: {e}")
            
    def get_energy_data(self):
        """Get the collected energy data."""
        print("\n==== GETTING EBPF ENERGY DATA ====")
        
        # Calculate duration
        duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        print(f"Duration: {duration:.2f} seconds")
        
        # Get energy data for the process
        process_data = self.energy_data.get(self.process_id, {
            'cpu_cycles': 0,
            'rapl_energy_pkg': 0,
            'rapl_energy_cores': 0,
            'timestamps': []
        })
        
        # Convert CPU cycles to energy (joules)
        # This is a rough estimate based on Intel RAPL
        # 1 CPU cycle = ~20 pJ (picojoules) = 2e-11 J
        cpu_cycles = process_data['cpu_cycles']
        energy_from_cycles = cpu_cycles * 2e-11
        
        # Get RAPL energy values
        rapl_energy_pkg = process_data['rapl_energy_pkg'] * 1e-6  # Convert from microjoules to joules
        rapl_energy_cores = process_data['rapl_energy_cores'] * 1e-6  # Convert from microjoules to joules
        
        # Calculate core percentage
        core_percentage = rapl_energy_cores / rapl_energy_pkg if rapl_energy_pkg > 0 else 0
        
        # Create result dictionary
        result = {
            'energy': {
                'pkg': rapl_energy_pkg,
                'cores': rapl_energy_cores,
                'core_percentage': core_percentage,
                'cpu_cycles': cpu_cycles,
                'energy_from_cycles': energy_from_cycles
            },
            'duration': duration,
            'source': 'ebpf'
        }
        
        # Add timestamps
        if process_data['timestamps']:
            result['start_timestamp'] = min(process_data['timestamps']) * 1e-9  # Convert from ns to s
            result['end_timestamp'] = max(process_data['timestamps']) * 1e-9  # Convert from ns to s
            
        print(f"Final eBPF energy data: {result}")
        return result
        
    def log_energy_data(self, energy_data, task, cpu_info, function_name=None):
        """Log energy data and store it in JSON format."""
        import json
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Store function name if provided
        if function_name:
            self.function_name = function_name
        
        # Log energy consumption
        logger.info(f"eBPF Energy consumption: {energy_data['energy'].get('pkg', 'N/A')} Joules (pkg), {energy_data['energy'].get('cores', 'N/A')} Joules (cores)")
        logger.info(f"eBPF Core percentage: {energy_data['energy'].get('core_percentage', 0) * 100:.2f}%")
        logger.info(f"eBPF CPU cycles: {energy_data['energy'].get('cpu_cycles', 0)}")
        logger.info(f"eBPF Energy from CPU cycles: {energy_data['energy'].get('energy_from_cycles', 0):.6f} Joules")
        
        # Print energy data
        print("\neBPF Performance counter stats:")
        print(f"CPU Cycles: {energy_data['energy'].get('cpu_cycles', 0)}")
        print(f"Energy (pkg): {energy_data['energy'].get('pkg', 0):.6f} Joules")
        print(f"Energy (cores): {energy_data['energy'].get('cores', 0):.6f} Joules")
        print(f"Core percentage: {energy_data['energy'].get('core_percentage', 0) * 100:.2f}%")
        print(f"Energy from CPU cycles: {energy_data['energy'].get('energy_from_cycles', 0):.6f} Joules")
        print()
        
        # Store energy data in JSON format using shared utilities
        pkg_energy = energy_data['energy'].get('pkg', 0)
        cores_energy = energy_data['energy'].get('cores', 0)
        core_percentage = energy_data['energy'].get('core_percentage', 0)
        
        monitor_specific_data = {
            'cpu_cycles': energy_data['energy'].get('cpu_cycles', 0),
            'energy_from_cycles': energy_data['energy'].get('energy_from_cycles', 0),
        }
        store_energy_data_json(energy_data, task, cpu_info, pkg_energy, cores_energy, 
                              core_percentage, function_name, monitor_specific_data)
