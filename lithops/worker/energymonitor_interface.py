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

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class EnergyMonitorInterface(ABC):
    """
    Abstract base class for all energy monitors.
    
    This interface ensures all energy monitoring implementations provide
    consistent methods and behavior across different monitoring techniques
    (eBPF, RAPL, perf, CPU estimation, etc.).
    """
    
    @abstractmethod
    def __init__(self, process_id: int):
        """
        Initialize the energy monitor.
        
        Args:
            process_id: The process ID to monitor for energy consumption
        """
        self.process_id = process_id
        self.start_time = None
        self.end_time = None
        self.function_name = None
    
    @abstractmethod
    def start(self) -> bool:
        """
        Start energy monitoring.
        
        Returns:
            bool: True if monitoring started successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """
        Stop energy monitoring and collect final measurements.
        """
        pass
    
    @abstractmethod
    def get_energy_data(self) -> Dict[str, Any]:
        """
        Get the collected energy data.
        
        Returns:
            Dict containing energy measurements with the following structure:
            {
                'energy': {
                    'pkg': float,           # Package energy in Joules
                    'cores': float,         # Core energy in Joules
                    'core_percentage': float # cores/pkg ratio
                },
                'duration': float,          # Measurement duration in seconds
                'source': str              # Monitoring method used
            }
        """
        pass
    
    @abstractmethod
    def log_energy_data(self, energy_data: Dict[str, Any], task: Any, 
                       cpu_info: Dict[str, Any], function_name: Optional[str] = None) -> None:
        """
        Log energy data and store it in JSON format.
        
        Args:
            energy_data: Energy measurement data from get_energy_data()
            task: Task object containing job_key and call_id
            cpu_info: CPU usage information
            function_name: Optional function name for the measurement
        """
        pass
    
    @abstractmethod
    def update_function_name(self, task: Any, function_name: str) -> None:
        """
        Update the function name in stored energy data.
        
        Args:
            task: Task object containing job_key and call_id
            function_name: Function name to update in the data
        """
        pass
    
    def read_function_name_from_stats(self, stats_file: str) -> Optional[str]:
        """
        Read function name from stats file (common implementation).
        
        Args:
            stats_file: Path to the stats file
            
        Returns:
            Function name if found, None otherwise
        """
        import os
        import logging
        
        logger = logging.getLogger(__name__)
        
        if not os.path.exists(stats_file):
            logger.warning(f"Stats file not found: {stats_file}")
            return None
        
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


class EnergyMonitorCapabilities:
    """
    Utility class to check system capabilities for different energy monitoring methods.
    """
    
    @staticmethod
    def check_ebpf_support() -> bool:
        """Check if eBPF monitoring is supported."""
        try:
            import bcc
            # Try to create a simple BPF program to test functionality
            bcc.BPF(text='int kprobe__sys_clone(void *ctx) { return 0; }')
            return True
        except Exception:
            return False
    
    @staticmethod
    def check_rapl_support() -> bool:
        """Check if RAPL direct access is supported."""
        import os
        rapl_paths = [
            '/sys/class/powercap/intel-rapl:0/energy_uj',
            '/sys/class/powercap/intel-rapl:0:0/energy_uj'
        ]
        
        for path in rapl_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        f.read()
                    return True
                except PermissionError:
                    continue
                except Exception:
                    continue
        return False
    
    @staticmethod
    def check_perf_support() -> bool:
        """Check if perf energy monitoring is supported."""
        import shutil
        import subprocess
        
        if not shutil.which('perf'):
            return False
        
        try:
            result = subprocess.run(['perf', 'list'], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE, 
                                  timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def get_available_methods() -> list:
        """Get list of available energy monitoring methods."""
        methods = []
        
        if EnergyMonitorCapabilities.check_ebpf_support():
            methods.append('ebpf')
        
        if EnergyMonitorCapabilities.check_rapl_support():
            methods.append('rapl')
        
        if EnergyMonitorCapabilities.check_perf_support():
            methods.append('perf')
        
        # CPU estimation is always available
        methods.append('cpu_estimation')
        
        return methods
