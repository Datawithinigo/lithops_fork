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

class IEnergyMonitor(ABC):
    """Interface for all energy monitoring strategies."""
    
    @abstractmethod
    def start(self) -> bool:
        """Start monitoring energy consumption.
        
        Returns:
            bool: True if monitoring started successfully, False otherwise.
        """
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Stop monitoring energy consumption."""
        pass
    
    @abstractmethod
    def get_energy_data(self) -> Dict[str, Any]:
        """Get the collected energy data.
        
        Returns:
            Dict[str, Any]: A dictionary containing energy metrics.
        """
        pass
    
    @abstractmethod
    def log_energy_data(self, energy_data: Dict[str, Any], task: Any, 
                        cpu_info: Dict[str, Any], function_name: Optional[str] = None) -> None:
        """Log energy data and store it in JSON format.
        
        Args:
            energy_data: The energy data to log.
            task: The task object.
            cpu_info: CPU information.
            function_name: Optional function name.
        """
        pass
