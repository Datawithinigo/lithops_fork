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

import logging
from typing import Optional, List, Type, Dict, Any
from .energymonitor_interface import EnergyMonitorInterface, EnergyMonitorCapabilities

logger = logging.getLogger(__name__)


class EnergyMonitorFactory:
    """
    Factory for creating appropriate energy monitors based on system capabilities.
    
    This factory automatically detects available energy monitoring methods and
    instantiates the best available monitor based on a priority hierarchy.
    """
    
    # Monitor priority order (highest to lowest accuracy/preference)
    MONITOR_PRIORITY = [
        'ebpf',      # eBPF-based monitoring (highest accuracy)
        'rapl',      # Direct RAPL access
        'perf',      # Perf-based monitoring
        'enhanced',  # Enhanced monitor with fallbacks
        'base'       # Base monitor with estimation
    ]
    
    # Lazy-loaded monitor classes to avoid import errors
    _monitor_classes: Dict[str, Type[EnergyMonitorInterface]] = {}
    
    @classmethod
    def create_monitor(cls, process_id: int, 
                      preferred_methods: Optional[List[str]] = None,
                      fallback_enabled: bool = True) -> EnergyMonitorInterface:
        """
        Create the best available energy monitor for the current system.
        
        Args:
            process_id: Process ID to monitor
            preferred_methods: List of preferred monitoring methods in order
            fallback_enabled: Whether to fall back to less accurate methods
            
        Returns:
            EnergyMonitorInterface: The best available energy monitor instance
        """
        methods_to_try = preferred_methods or cls.MONITOR_PRIORITY
        
        logger.info(f"Creating energy monitor for process {process_id}")
        logger.info(f"Available methods: {EnergyMonitorCapabilities.get_available_methods()}")
        
        for method in methods_to_try:
            logger.debug(f"Trying energy monitoring method: {method}")
            
            if cls._is_method_available(method):
                monitor_class = cls._get_monitor_class(method)
                if monitor_class:
                    try:
                        monitor = monitor_class(process_id)
                        logger.info(f"Successfully created {method} energy monitor")
                        return monitor
                    except Exception as e:
                        logger.warning(f"Failed to create {method} monitor: {e}")
                        if not fallback_enabled:
                            raise
                        continue
            else:
                logger.debug(f"Method {method} not available on this system")
        
        # Last resort fallback
        logger.warning("No preferred energy monitoring methods available, using base monitor")
        base_monitor_class = cls._get_monitor_class('base')
        return base_monitor_class(process_id)
    
    @classmethod
    def create_multiple_monitors(cls, process_id: int, 
                               methods: List[str]) -> List[EnergyMonitorInterface]:
        """
        Create multiple energy monitors for comparison purposes.
        
        Args:
            process_id: Process ID to monitor
            methods: List of monitoring methods to create
            
        Returns:
            List of energy monitor instances
        """
        monitors = []
        
        for method in methods:
            if cls._is_method_available(method):
                monitor_class = cls._get_monitor_class(method)
                if monitor_class:
                    try:
                        monitor = monitor_class(process_id)
                        monitors.append(monitor)
                        logger.info(f"Created {method} monitor for comparison")
                    except Exception as e:
                        logger.warning(f"Failed to create {method} monitor: {e}")
        
        return monitors
    
    @classmethod
    def get_available_methods(cls) -> List[str]:
        """
        Get list of energy monitoring methods available on current system.
        
        Returns:
            List of available method names
        """
        available = []
        
        for method in cls.MONITOR_PRIORITY:
            if cls._is_method_available(method):
                available.append(method)
        
        return available
    
    @classmethod
    def get_method_info(cls, method: str) -> Dict[str, Any]:
        """
        Get information about a specific monitoring method.
        
        Args:
            method: Method name to get info for
            
        Returns:
            Dictionary with method information
        """
        info = {
            'name': method,
            'available': cls._is_method_available(method),
            'description': cls._get_method_description(method),
            'requirements': cls._get_method_requirements(method),
            'accuracy': cls._get_method_accuracy(method)
        }
        
        return info
    
    @classmethod
    def _get_monitor_class(cls, method: str) -> Optional[Type[EnergyMonitorInterface]]:
        """
        Get monitor class for given method (with lazy loading).
        
        Args:
            method: Method name
            
        Returns:
            Monitor class or None if not available
        """
        if method not in cls._monitor_classes:
            cls._monitor_classes[method] = cls._load_monitor_class(method)
        
        return cls._monitor_classes[method]
    
    @classmethod
    def _load_monitor_class(cls, method: str) -> Optional[Type[EnergyMonitorInterface]]:
        """
        Dynamically load monitor class to avoid import errors.
        
        Args:
            method: Method name
            
        Returns:
            Monitor class or None if import fails
        """
        try:
            if method == 'ebpf':
                from .energymonitor_ebpf import EBPFEnergyMonitor
                return EBPFEnergyMonitor
            elif method == 'rapl':
                from .energymonitor_rapl import EnergyMonitor as RAPLEnergyMonitor
                return RAPLEnergyMonitor
            elif method == 'perf':
                from .energymonitor_perf import EnergyMonitor as PerfEnergyMonitor
                return PerfEnergyMonitor
            elif method == 'enhanced':
                from .energymonitor_fixed import EnergyMonitor as EnhancedEnergyMonitor
                return EnhancedEnergyMonitor
            elif method == 'base':
                from .energymonitor_base import EnergyMonitor as BaseEnergyMonitor
                return BaseEnergyMonitor
            else:
                logger.warning(f"Unknown energy monitoring method: {method}")
                return None
        except ImportError as e:
            logger.debug(f"Could not import {method} monitor: {e}")
            return None
        except Exception as e:
            logger.warning(f"Error loading {method} monitor class: {e}")
            return None
    
    @classmethod
    def _is_method_available(cls, method: str) -> bool:
        """
        Check if monitoring method is available on current system.
        
        Args:
            method: Method name to check
            
        Returns:
            True if method is available, False otherwise
        """
        if method == 'ebpf':
            return EnergyMonitorCapabilities.check_ebpf_support()
        elif method == 'rapl':
            return EnergyMonitorCapabilities.check_rapl_support()
        elif method == 'perf':
            return EnergyMonitorCapabilities.check_perf_support()
        elif method in ['enhanced', 'base']:
            # These methods are always available as they have fallbacks
            return True
        else:
            return False
    
    @classmethod
    def _get_method_description(cls, method: str) -> str:
        """Get description for monitoring method."""
        descriptions = {
            'ebpf': 'eBPF-based kernel-level energy monitoring with CPU cycle counting',
            'rapl': 'Direct RAPL energy counter access via sysfs',
            'perf': 'Perf-based energy monitoring using hardware counters',
            'enhanced': 'Enhanced monitor with multiple fallback mechanisms',
            'base': 'Base monitor with CPU-based energy estimation'
        }
        return descriptions.get(method, 'Unknown monitoring method')
    
    @classmethod
    def _get_method_requirements(cls, method: str) -> List[str]:
        """Get requirements for monitoring method."""
        requirements = {
            'ebpf': ['BCC (BPF Compiler Collection)', 'Kernel BPF support', 'MSR access'],
            'rapl': ['RAPL sysfs access (/sys/class/powercap/)', 'Read permissions'],
            'perf': ['perf tool', 'Energy event support', 'Appropriate privileges'],
            'enhanced': ['psutil (optional)', 'perf tool (optional)', 'RAPL access (optional)'],
            'base': ['psutil', 'perf tool']
        }
        return requirements.get(method, [])
    
    @classmethod
    def _get_method_accuracy(cls, method: str) -> str:
        """Get accuracy level for monitoring method."""
        accuracy = {
            'ebpf': 'Highest (kernel-level, real-time)',
            'rapl': 'High (direct hardware counters)',
            'perf': 'High (hardware counters via perf)',
            'enhanced': 'Medium (adaptive with fallbacks)',
            'base': 'Medium (estimation-based)'
        }
        return accuracy.get(method, 'Unknown')


class EnergyMonitorRegistry:
    """
    Registry for tracking active energy monitors and their performance.
    """
    
    def __init__(self):
        self.active_monitors: Dict[int, EnergyMonitorInterface] = {}
        self.monitor_stats: Dict[str, Dict[str, Any]] = {}
    
    def register_monitor(self, process_id: int, monitor: EnergyMonitorInterface):
        """Register an active monitor."""
        self.active_monitors[process_id] = monitor
        
        monitor_type = type(monitor).__name__
        if monitor_type not in self.monitor_stats:
            self.monitor_stats[monitor_type] = {
                'created_count': 0,
                'success_count': 0,
                'failure_count': 0
            }
        
        self.monitor_stats[monitor_type]['created_count'] += 1
    
    def unregister_monitor(self, process_id: int, success: bool = True):
        """Unregister a monitor and update stats."""
        if process_id in self.active_monitors:
            monitor = self.active_monitors.pop(process_id)
            monitor_type = type(monitor).__name__
            
            if monitor_type in self.monitor_stats:
                if success:
                    self.monitor_stats[monitor_type]['success_count'] += 1
                else:
                    self.monitor_stats[monitor_type]['failure_count'] += 1
    
    def get_active_monitors(self) -> Dict[int, EnergyMonitorInterface]:
        """Get all active monitors."""
        return self.active_monitors.copy()
    
    def get_monitor_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get monitor usage statistics."""
        return self.monitor_stats.copy()


# Global registry instance
monitor_registry = EnergyMonitorRegistry()
