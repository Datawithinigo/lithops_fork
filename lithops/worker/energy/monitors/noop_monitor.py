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

from typing import Dict, Any, Optional
import logging

from lithops.worker.energy.interfaces import IEnergyMonitor

logger = logging.getLogger(__name__)

class NoOpEnergyMonitor(IEnergyMonitor):
    """
    No-operation energy monitor for when monitoring is disabled.
    Implements the Null Object pattern to provide a do-nothing implementation.
    """
    
    def __init__(self, process_id: int, config: Dict[str, Any]) -> None:
        """
        Initialize the no-op energy monitor.
        
        Args:
            process_id: The process ID to monitor (ignored).
            config: Configuration options (ignored).
        """
        self.process_id = process_id
        logger.info(f"Initialized NoOpEnergyMonitor for process {process_id}")
    
    def start(self) -> bool:
        """
        Do nothing when monitoring is disabled.
        
        Returns:
            bool: Always returns True.
        """
        logger.debug("NoOpEnergyMonitor.start() - No operation performed")
        return True
    
    def stop(self) -> None:
        """Do nothing when monitoring is disabled."""
        logger.debug("NoOpEnergyMonitor.stop() - No operation performed")
    
    def get_energy_data(self) -> Dict[str, Any]:
        """
        Return empty energy data.
        
        Returns:
            Dict[str, Any]: An empty energy data dictionary.
        """
        logger.debug("NoOpEnergyMonitor.get_energy_data() - Returning empty data")
        return {
            'energy': {},
            'duration': 0,
            'source': 'disabled'
        }
    
    def log_energy_data(self, energy_data: Dict[str, Any], task: Any, 
                       cpu_info: Dict[str, Any], function_name: Optional[str] = None) -> None:
        """
        Do nothing when monitoring is disabled.
        
        Args:
            energy_data: The energy data to log (ignored).
            task: The task object (ignored).
            cpu_info: CPU information (ignored).
            function_name: Optional function name (ignored).
        """
        logger.debug("NoOpEnergyMonitor.log_energy_data() - No operation performed")
