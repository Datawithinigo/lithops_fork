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
import time
import logging
from typing import Dict, List, Any, Optional

from lithops.worker.energy.interfaces import IEnergyMonitor

logger = logging.getLogger(__name__)

class CompositeEnergyMonitor(IEnergyMonitor):
    """
    Composite energy monitor that manages multiple monitoring strategies.
    Implements the Composite pattern to treat individual monitors and 
    groups of monitors uniformly.
    """
    
    def __init__(self, monitors: List[IEnergyMonitor]) -> None:
        """
        Initialize the composite energy monitor with a list of monitors.
        
        Args:
            monitors: List of energy monitoring strategies to use.
        """
        self.monitors = monitors
        self.active_monitors = []
        self.results = {}
        logger.info(f"Initialized CompositeEnergyMonitor with {len(monitors)} strategies")
    
    def start(self) -> bool:
        """
        Start all monitoring strategies.
        
        Returns:
            bool: True if at least one monitor started successfully.
        """
        success = False
        self.active_monitors = []
        
        for i, monitor in enumerate(self.monitors):
            try:
                if monitor.start():
                    self.active_monitors.append(monitor)
                    logger.info(f"Started monitor {i+1}/{len(self.monitors)}: {type(monitor).__name__}")
                    success = True
                else:
                    logger.warning(f"Failed to start monitor {i+1}/{len(self.monitors)}: {type(monitor).__name__}")
            except Exception as e:
                logger.error(f"Error starting monitor {i+1}/{len(self.monitors)}: {type(monitor).__name__} - {e}")
        
        logger.info(f"Started {len(self.active_monitors)}/{len(self.monitors)} energy monitors")
        return success
    
    def stop(self) -> None:
        """Stop all active monitoring strategies."""
        for i, monitor in enumerate(self.active_monitors):
            try:
                monitor.stop()
                logger.info(f"Stopped monitor {i+1}/{len(self.active_monitors)}: {type(monitor).__name__}")
            except Exception as e:
                logger.error(f"Error stopping monitor {i+1}/{len(self.active_monitors)}: {type(monitor).__name__} - {e}")
    
    def get_energy_data(self) -> Dict[str, Any]:
        """
        Get energy data from all active monitors.
        
        Returns:
            Dict[str, Any]: Aggregated energy data from all monitors.
        """
        # Initialize result dictionary
        result = {
            'energy': {},
            'duration': 0,
            'source': 'composite',
            'monitors': {}
        }
        
        # Collect data from all active monitors
        for i, monitor in enumerate(self.active_monitors):
            try:
                monitor_data = monitor.get_energy_data()
                monitor_name = type(monitor).__name__
                
                # Store individual monitor results
                result['monitors'][monitor_name] = monitor_data
                
                # Update duration with the maximum duration from all monitors
                if monitor_data.get('duration', 0) > result['duration']:
                    result['duration'] = monitor_data.get('duration', 0)
                
                # Store the monitor's data for later use
                self.results[monitor_name] = monitor_data
                
                logger.info(f"Collected energy data from {monitor_name}")
            except Exception as e:
                logger.error(f"Error getting energy data from monitor {i+1}: {e}")
        
        # Aggregate energy data from all monitors
        # For each energy metric, calculate average, min, max
        energy_metrics = set()
        for monitor_name, monitor_data in self.results.items():
            if 'energy' in monitor_data:
                for metric in monitor_data['energy']:
                    energy_metrics.add(metric)
        
        # Initialize aggregated metrics
        for metric in energy_metrics:
            result['energy'][metric] = {
                'values': [],
                'avg': 0,
                'min': 0,
                'max': 0
            }
        
        # Collect values for each metric
        for monitor_name, monitor_data in self.results.items():
            if 'energy' in monitor_data:
                for metric, value in monitor_data['energy'].items():
                    if isinstance(value, (int, float)):
                        result['energy'][metric]['values'].append(value)
        
        # Calculate statistics
        for metric in energy_metrics:
            values = result['energy'][metric]['values']
            if values:
                result['energy'][metric]['avg'] = sum(values) / len(values)
                result['energy'][metric]['min'] = min(values)
                result['energy'][metric]['max'] = max(values)
                # Also store the raw value for backward compatibility
                result['energy'][metric] = result['energy'][metric]['avg']
        
        return result
    
    def log_energy_data(self, energy_data: Dict[str, Any], task: Any, 
                       cpu_info: Dict[str, Any], function_name: Optional[str] = None) -> None:
        """
        Log energy data from all active monitors.
        
        Args:
            energy_data: The energy data to log.
            task: The task object.
            cpu_info: CPU information.
            function_name: Optional function name.
        """
        # Log composite energy data
        logger.info(f"Logging composite energy data from {len(self.active_monitors)} monitors")
        
        # Log aggregated energy metrics
        if 'energy' in energy_data:
            for metric, value in energy_data['energy'].items():
                if isinstance(value, dict) and 'avg' in value:
                    logger.info(f"Composite {metric}: avg={value['avg']:.2f}, min={value['min']:.2f}, max={value['max']:.2f}")
        
        # Log individual monitor data
        for i, monitor in enumerate(self.active_monitors):
            try:
                monitor_name = type(monitor).__name__
                if monitor_name in self.results:
                    monitor_data = self.results[monitor_name]
                    # Pass the function name to each individual monitor
                    monitor.log_energy_data(monitor_data, task, cpu_info, function_name)
                    logger.info(f"Logged energy data from {monitor_name}")
            except Exception as e:
                logger.error(f"Error logging energy data from monitor {i+1}: {e}")
        
        # Store composite energy data in JSON format
        self._store_composite_energy_data(energy_data, task, cpu_info, function_name)
    
    def _store_composite_energy_data(self, energy_data: Dict[str, Any], task: Any, 
                                   cpu_info: Dict[str, Any], function_name: Optional[str] = None) -> None:
        """
        Store composite energy data in JSON format.
        
        Args:
            energy_data: The energy data to store.
            task: The task object.
            cpu_info: CPU information.
            function_name: Optional function name.
        """
        # Base directory for JSON files
        try:
            # Get the current working directory
            cwd = os.getcwd()
            json_dir = os.path.join(cwd, 'energy_data')
            # Create directory with proper permissions
            os.makedirs(json_dir, exist_ok=True)
            # Ensure the directory has the right permissions
            os.chmod(json_dir, 0o777)  # rwx for all users
            logger.info(f"Created energy data directory: {json_dir}")
        except Exception as e:
            logger.error(f"Error creating energy data directory: {e}")
            # Fallback to /tmp directory which should be writable
            json_dir = os.path.join("/tmp", 'lithops_energy_data')
            os.makedirs(json_dir, exist_ok=True)
            logger.info(f"Using fallback energy data directory: {json_dir}")
        
        timestamp = time.time()
        
        try:
            # Create a unique ID for this execution
            execution_id = f"{task.job_key}_{task.call_id}"
            
            # Create the composite energy data object
            composite_data = {
                'execution_id': execution_id,
                'job_key': task.job_key,
                'call_id': task.call_id,
                'timestamp': timestamp,
                'function_name': function_name,  # Explicitly include function name at top level
                'duration': energy_data.get('duration', 0),
                'energy': energy_data.get('energy', {}),
                'monitors': energy_data.get('monitors', {})
            }
            
            # Write to a single JSON file
            json_file = os.path.join(json_dir, f"{execution_id}_composite.json")
            with open(json_file, 'w') as f:
                json.dump(composite_data, f, indent=2)
            
            logger.info(f"Stored composite energy data in {json_file}")
            
            # Also write a summary file that contains all execution IDs
            summary_file = os.path.join(json_dir, 'composite_summary.json')
            summary = []
            
            if os.path.exists(summary_file):
                try:
                    with open(summary_file, 'r') as f:
                        summary = json.load(f)
                except Exception as e:
                    logger.error(f"Error reading summary file: {e}")
                    summary = []
            
            # Add this execution to the summary with function name
            summary_entry = {
                'execution_id': execution_id,
                'function_name': function_name,  # Include function name in summary
                'timestamp': timestamp
            }
            
            # Add energy metrics to summary
            for metric, value in energy_data.get('energy', {}).items():
                if isinstance(value, dict) and 'avg' in value:
                    summary_entry[f'energy_{metric}_avg'] = value['avg']
                    summary_entry[f'energy_{metric}_min'] = value['min']
                    summary_entry[f'energy_{metric}_max'] = value['max']
                else:
                    summary_entry[f'energy_{metric}'] = value
            
            summary.append(summary_entry)
            
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
        except Exception as e:
            logger.error(f"Error writing composite energy data to JSON file: {e}")
