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
from typing import Dict, Type, Optional, Any, Union, List

from lithops.worker.energy.interfaces import IEnergyMonitor
from lithops.worker.energy.composite import CompositeEnergyMonitor

logger = logging.getLogger(__name__)

class EnergyMonitorFactory:
    """Factory for creating energy monitors."""
    
    # Registry of available monitor strategies
    _strategies: Dict[str, Type[IEnergyMonitor]] = {}
    
    @classmethod
    def register_strategy(cls, name: str, strategy_class: Type[IEnergyMonitor]) -> None:
        """Register a new energy monitoring strategy."""
        cls._strategies[name] = strategy_class
        logger.info(f"Registered energy monitoring strategy: {name}")
    
    @classmethod
    def create_monitor(cls, strategy_names: Union[str, List[str]], process_id: int, 
                      config: Dict[str, Any]) -> Optional[IEnergyMonitor]:
        """
        Create energy monitors based on strategy names.
        
        Args:
            strategy_names: Name(s) of the strategy to use. Can be a single string or a list.
                           Special values:
                           - 'all': Use all available strategies
                           - 'auto': Auto-select the best available strategies
            process_id: The process ID to monitor.
            config: Configuration options.
            
        Returns:
            An energy monitor instance or None if energy monitoring is disabled.
        """
        # Check if energy monitoring is disabled
        if not config.get('energy', True):
            logger.info("Energy monitoring is disabled")
            from lithops.worker.energy.monitors.noop_monitor import NoOpEnergyMonitor
            return NoOpEnergyMonitor(process_id, config)
        
        # Convert single strategy name to list
        if isinstance(strategy_names, str):
            if strategy_names == 'all':
                # Use all available strategies except NoOp
                strategy_names = [name for name in cls._strategies.keys() 
                                 if name != 'noop']
            elif strategy_names == 'auto':
                # Auto-select the best available strategies
                strategy_names = ['ebpf', 'ipmi', 'perf']  # Prefer eBPF, then IPMI, fall back to perf
            else:
                strategy_names = [strategy_names]
        
        # Create monitors for each strategy
        monitors = []
        for strategy_name in strategy_names:
            if strategy_name in cls._strategies:
                try:
                    strategy_class = cls._strategies[strategy_name]
                    monitor = strategy_class(process_id, config)
                    
                    # For eBPF, we'll add it even if it fails to start when not running as root
                    # This ensures we still generate the appropriate JSON files
                    if strategy_name == 'ebpf' and os.geteuid() != 0:
                        logger.warning(f"eBPF monitor requires root privileges, but will be added anyway for JSON generation")
                        monitors.append(monitor)
                    # For other monitors, test if they can start successfully
                    elif monitor.start():
                        logger.info(f"Successfully started energy monitor: {strategy_name}")
                        # Stop the monitor after testing
                        monitor.stop()
                        # Create a fresh instance for actual use
                        monitor = strategy_class(process_id, config)
                        monitors.append(monitor)
                    else:
                        logger.warning(f"Energy monitor {strategy_name} failed to start, skipping")
                except Exception as e:
                    logger.error(f"Error creating energy monitor {strategy_name}: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
        
        # If no monitors were created, return NoOp monitor
        if not monitors:
            logger.warning("No energy monitors created, using NoOp monitor")
            from lithops.worker.energy.monitors.noop_monitor import NoOpEnergyMonitor
            return NoOpEnergyMonitor(process_id, config)
        
        # If only one monitor was created, return it directly
        if len(monitors) == 1:
            return monitors[0]
        
        # Otherwise, return a composite monitor
        return CompositeEnergyMonitor(monitors)
    
    @classmethod
    def available_strategies(cls) -> List[str]:
        """Get a list of available strategy names."""
        return list(cls._strategies.keys())
