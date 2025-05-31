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
import re
import subprocess
import logging
import json
from typing import Dict, Any, Optional

from lithops.worker.energy.interfaces import IEnergyMonitor
from lithops.worker.energy.observer import EnergySubject

logger = logging.getLogger(__name__)

class PerfEnergyMonitor(IEnergyMonitor, EnergySubject):
    """
    Energy monitor implementation using perf.
    Monitors energy consumption using the perf tool's power/energy-pkg/ counter.
    """
    
    def __init__(self, process_id: int, config: Dict[str, Any]) -> None:
        """
        Initialize the perf energy monitor.
        
        Args:
            process_id: The process ID to monitor.
            config: Configuration options.
        """
        EnergySubject.__init__(self)
        self.process_id = process_id
        self.config = config
        self.perf_process = None
        self.start_time = None
        self.end_time = None
        self.energy_pkg = None
        self.energy_cores = None
        self.cpu_percent = None
        self.perf_output_file = f"/tmp/perf_energy_{process_id}.txt"
        self.function_name = None
        
        # Additional configuration options
        self.sampling_interval = config.get('energy_sampling_interval', 1.0)  # seconds
        self.perf_events = config.get('energy_perf_events', 
                                     ['power/energy-pkg/', 'power/energy-cores/'])
        
        logger.info(f"Initialized PerfEnergyMonitor for process {process_id}")
    
    def _get_available_energy_events(self):
        """Get a list of available energy-related events from perf."""
        logger.debug("Checking available energy events")
        try:
            # Try both with and without sudo
            try:
                logger.debug("Trying 'sudo perf list'...")
                result = subprocess.run(
                    ["sudo", "perf", "list"], 
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
                logger.debug(f"sudo perf list result: {result.returncode}")
            except Exception as e:
                logger.debug(f"Error with sudo perf list: {e}")
                # Fallback to non-sudo
                logger.debug("Trying 'perf list'...")
                result = subprocess.run(
                    ["perf", "list"], 
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
                logger.debug(f"perf list result: {result.returncode}")
            
            output = result.stdout + result.stderr
            logger.debug(f"Perf list output length: {len(output)} characters")
            
            # Extract energy-related events
            energy_events = []
            for line in output.splitlines():
                if "energy" in line.lower():
                    logger.debug(f"Found energy line: {line}")
                    # Extract the event name from the line
                    match = re.search(r'(\S+/\S+/)', line)
                    if match:
                        energy_events.append(match.group(1))
            
            # Prepare the events string
            if energy_events:
                logger.debug(f"Found {len(energy_events)} energy events: {', '.join(energy_events)}")
                
                # Check for both pkg and cores events
                pkg_events = [e for e in energy_events if "energy-pkg" in e]
                cores_events = [e for e in energy_events if "energy-cores" in e]
                
                events = []
                if pkg_events:
                    logger.debug(f"Found energy-pkg event: {pkg_events[0]}")
                    events.append(pkg_events[0])
                else:
                    logger.debug("No energy-pkg event found, using default")
                    events.append("power/energy-pkg/")
                    
                if cores_events:
                    logger.debug(f"Found energy-cores event: {cores_events[0]}")
                    events.append(cores_events[0])
                else:
                    logger.debug("No energy-cores event found, using default")
                    events.append("power/energy-cores/")
                
                # Join events with comma
                events_str = ",".join(events)
                logger.debug(f"Using energy events: {events_str}")
                return events_str
            else:
                logger.debug("No energy events found in perf list")
                
            # Default to both pkg and cores events
            events_str = "power/energy-pkg/,power/energy-cores/"
            logger.debug(f"Using default energy events: {events_str}")
            return events_str
        except Exception as e:
            logger.error(f"Error getting available energy events: {e}")
            # Default to both pkg and cores events
            events_str = "power/energy-pkg/,power/energy-cores/"
            logger.debug(f"Using default energy events: {events_str}")
            return events_str
        
    def start(self) -> bool:
        """
        Start monitoring energy consumption using perf.
        
        Returns:
            bool: True if monitoring started successfully, False otherwise.
        """
        logger.info("Starting PerfEnergyMonitor")
        try:
            # Get the energy events
            energy_event = self._get_available_energy_events()
            logger.debug(f"Using energy event: {energy_event}")
            
            # Create a unique output file for this run
            self.perf_output_file = f"/tmp/perf_energy_{self.process_id}_{int(time.time())}.txt"
            
            # Start perf in the background to monitor the entire function execution
            logger.debug("Starting perf stat to monitor energy consumption...")
            
            # Use a direct approach with sudo
            cmd = [
                "sudo", "perf", "stat",
                "-e", energy_event,
                "-a",  # Monitor all CPUs
                "-o", self.perf_output_file  # Output to a file
            ]
            
            logger.debug(f"Running command: {' '.join(cmd)}")
            
            # Start perf in the background
            self.perf_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.start_time = time.time()
            logger.info(f"PerfEnergyMonitor started at: {self.start_time}")
            
            # Notify observers
            self.notify('start', {
                'monitor': 'perf',
                'process_id': self.process_id,
                'start_time': self.start_time
            })
            
            return True
        except Exception as e:
            logger.error(f"Error starting PerfEnergyMonitor: {e}")
            return False
            
    def stop(self) -> None:
        """Stop monitoring energy consumption and collect results."""
        logger.info("Stopping PerfEnergyMonitor")
        
        if self.perf_process is None:
            logger.debug("No perf process to stop")
            return
            
        try:
            # Record the end time
            self.end_time = time.time()
            duration = self.end_time - self.start_time
            logger.debug(f"Energy monitoring stopped at: {self.end_time}")
            logger.debug(f"Monitoring duration: {duration:.2f} seconds")
            
            # Stop the perf process
            logger.debug(f"Stopping perf process (PID: {self.perf_process.pid})...")
            
            # Send SIGINT to perf to make it output the results
            import signal
            os.kill(self.perf_process.pid, signal.SIGINT)
            
            # Wait for the process to exit
            try:
                stdout, stderr = self.perf_process.communicate(timeout=5)
                logger.debug("Perf process exited")
                logger.debug(f"Perf stdout: {stdout}")
                logger.debug(f"Perf stderr: {stderr}")
            except subprocess.TimeoutExpired:
                logger.debug("Perf process did not exit, killing it")
                self.perf_process.kill()
                stdout, stderr = self.perf_process.communicate()
            
            # Initialize energy values
            self.energy_pkg = None
            self.energy_cores = None
            
            # Read the output file
            logger.debug(f"Reading perf output file: {self.perf_output_file}")
            try:
                if os.path.exists(self.perf_output_file):
                    with open(self.perf_output_file, 'r') as f:
                        perf_output = f.read()
                        logger.debug(f"Perf output file content: {perf_output}")
                        
                        # Process the output to extract energy values
                        for line in perf_output.splitlines():
                            logger.debug(f"Processing line: {line}")
                            if "Joules" in line:
                                # Use a more precise regex to extract the energy value
                                match = re.search(r'\s*([\d,.]+)\s+Joules\s+(\S+)', line)
                                if match:
                                    value_str = match.group(1).replace(',', '.')
                                    event_name = match.group(2)
                                    try:
                                        # Handle numbers with multiple dots (e.g. 1.043.75 -> 1043.75)
                                        if value_str.count('.') > 1:
                                            parts = value_str.split('.')
                                            value_str = ''.join(parts[:-1]) + '.' + parts[-1]
                                            logger.debug(f"Converted malformed value with multiple dots to {value_str}")
                                        
                                        energy_value = float(value_str)
                                        logger.debug(f"Found energy value: {energy_value} Joules for {event_name}")
                                        
                                        # Store the value based on the event type
                                        if "energy-pkg" in event_name:
                                            self.energy_pkg = energy_value
                                            logger.debug(f"Stored energy-pkg value: {self.energy_pkg} Joules")
                                        elif "energy-cores" in event_name:
                                            self.energy_cores = energy_value
                                            logger.debug(f"Stored energy-cores value: {self.energy_cores} Joules")
                                    except ValueError as e:
                                        logger.error(f"Could not convert '{value_str}' to float: {e}")
                else:
                    logger.warning(f"Perf output file not found: {self.perf_output_file}")
            except Exception as e:
                logger.error(f"Error reading perf output file: {e}")
            
            # If we couldn't get the energy values, try a direct command
            if self.energy_pkg is None and self.energy_cores is None:
                logger.debug("No energy values from perf output file, trying direct command...")
                
                # Get the energy events
                energy_events = self._get_available_energy_events()
                
                # Run a direct perf command for a CPU-intensive task
                # This will give us a better baseline than sleep
                cmd = f"sudo perf stat -e {energy_events} -a python3 -c 'for i in range(10000000): pass' 2>&1"
                logger.debug(f"Running command: {cmd}")
                
                result = subprocess.run(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    check=False
                )
                
                # Get the output
                output = result.stdout
                logger.debug(f"Direct command output: {output}")
                
                # Process the output to extract energy values
                for line in output.splitlines():
                    logger.debug(f"Processing line: {line}")
                    if "Joules" in line:
                        match = re.search(r'\s*([\d,.]+)\s+Joules\s+(\S+)', line)
                        if match:
                            value_str = match.group(1).replace(',', '.')
                            event_name = match.group(2)
                            try:
                                # Handle numbers with multiple dots (e.g. 1.043.75 -> 1043.75)
                                if value_str.count('.') > 1:
                                    parts = value_str.split('.')
                                    value_str = ''.join(parts[:-1]) + '.' + parts[-1]
                                    logger.debug(f"Converted malformed value with multiple dots to {value_str}")
                                
                                energy_value = float(value_str)
                                logger.debug(f"Found energy value: {energy_value} Joules for {event_name}")
                                
                                # Store the value based on the event type
                                if "energy-pkg" in event_name:
                                    self.energy_pkg = energy_value
                                    logger.debug(f"Stored energy-pkg value: {self.energy_pkg} Joules")
                                elif "energy-cores" in event_name:
                                    self.energy_cores = energy_value
                                    logger.debug(f"Stored energy-cores value: {self.energy_cores} Joules")
                            except ValueError as e:
                                logger.error(f"Could not convert '{value_str}' to float: {e}")
            
            # Get CPU percentage for the process
            try:
                import psutil
                logger.debug(f"Getting CPU percentage for process {self.process_id}")
                process = psutil.Process(self.process_id)
                # Call cpu_percent once with interval=None to get the value since the last call
                process.cpu_percent()
                # Call again with a small interval to get a more accurate reading
                self.cpu_percent = process.cpu_percent(interval=0.1) / 100.0  # Convert to fraction
                logger.debug(f"CPU percentage: {self.cpu_percent * 100:.2f}%")
            except Exception as e:
                logger.error(f"Error getting CPU percentage: {e}")
                
            # Clean up the output file
            try:
                if os.path.exists(self.perf_output_file):
                    os.remove(self.perf_output_file)
                    logger.debug(f"Removed perf output file: {self.perf_output_file}")
            except Exception as e:
                logger.error(f"Error removing perf output file: {e}")
                
            # Notify observers
            self.notify('stop', {
                'monitor': 'perf',
                'process_id': self.process_id,
                'end_time': self.end_time,
                'duration': duration
            })
                
        except Exception as e:
            logger.error(f"Error stopping energy monitoring: {e}")
            
    def get_energy_data(self) -> Dict[str, Any]:
        """
        Get the collected energy data.
        
        Returns:
            Dict[str, Any]: A dictionary containing energy metrics.
        """
        logger.debug("Getting energy data from PerfEnergyMonitor")
        duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        logger.debug(f"Duration: {duration:.2f} seconds")
        
        # Create the base result dictionary
        result = {
            'energy': {},
            'duration': duration,
            'source': 'perf'
        }
        
        # Add CPU percentage if available (for reference only, not for estimation)
        if self.cpu_percent is not None:
            logger.debug(f"Using CPU percentage: {self.cpu_percent * 100:.2f}%")
            result['cpu_percent'] = self.cpu_percent
        
        # Add energy values if available from perf
        if self.energy_pkg is not None and self.energy_pkg > 0:
            logger.debug(f"Using measured energy-pkg: {self.energy_pkg:.2f} Joules")
            result['energy']['pkg'] = self.energy_pkg
        else:
            logger.debug("No energy-pkg data from perf, setting to 0")
            result['energy']['pkg'] = 0
            
        if self.energy_cores is not None and self.energy_cores > 0:
            logger.debug(f"Using measured energy-cores: {self.energy_cores:.2f} Joules")
            result['energy']['cores'] = self.energy_cores
        else:
            logger.debug("No energy-cores data from perf, setting to 0")
            result['energy']['cores'] = 0
            
        # Calculate core percentage (energy_cores / energy_pkg)
        if result['energy']['pkg'] > 0:
            core_percentage = result['energy']['cores'] / result['energy']['pkg']
            logger.debug(f"Core percentage: {core_percentage:.4f} ({core_percentage * 100:.2f}%)")
            result['energy']['core_percentage'] = core_percentage
        else:
            logger.debug("Cannot calculate core percentage, energy_pkg is 0")
            result['energy']['core_percentage'] = 0
        
        # If we have no energy data at all, set source to 'none'
        if result['energy']['pkg'] == 0 and result['energy']['cores'] == 0:
            result['source'] = 'none'

        logger.debug(f"Final energy data: {result}")
        
        # Notify observers
        self.notify('data', {
            'monitor': 'perf',
            'process_id': self.process_id,
            'energy_data': result
        })
        
        return result
        
    def log_energy_data(self, energy_data: Dict[str, Any], task: Any, 
                       cpu_info: Dict[str, Any], function_name: Optional[str] = None) -> None:
        """
        Log energy data and store it in JSON format.
        
        Args:
            energy_data: The energy data to log.
            task: The task object.
            cpu_info: CPU information.
            function_name: Optional function name.
        """
        # Store function name if provided
        if function_name:
            self.function_name = function_name
        
        # Log energy consumption
        logger.info(f"Perf energy consumption: {energy_data['energy'].get('pkg', 'N/A')} Joules (pkg), "
                   f"{energy_data['energy'].get('cores', 'N/A')} Joules (cores)")
        logger.info(f"Core percentage: {energy_data['energy'].get('core_percentage', 0) * 100:.2f}%")
        logger.info(f"Energy efficiency: {energy_data['energy'].get('pkg', 0) / max(energy_data['duration'], 0.001):.2f} Watts")
        
        # Store energy data in JSON format
        self._store_energy_data_json(energy_data, task, cpu_info, function_name)
        
        # Notify observers
        self.notify('log', {
            'monitor': 'perf',
            'process_id': self.process_id,
            'energy_data': energy_data,
            'function_name': function_name
        })
        
    def _store_energy_data_json(self, energy_data: Dict[str, Any], task: Any, 
                              cpu_info: Dict[str, Any], function_name: Optional[str] = None) -> None:
        """
        Store energy data in JSON format.
        
        Args:
            energy_data: The energy data to store.
            task: The task object.
            cpu_info: CPU information.
            function_name: Optional function name.
        """
        # Store function name if provided
        if function_name:
            self.function_name = function_name
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
            
            # Calculate additional metrics
            duration = energy_data['duration']
            energy_efficiency = energy_data['energy'].get('pkg', 0) / max(duration, 0.001)  # Watts
            
            # Calculate average CPU usage
            avg_cpu_usage = sum(cpu_info['usage']) / len(cpu_info['usage']) if cpu_info['usage'] else 0
            
            # Calculate energy per CPU usage
            energy_per_cpu = energy_data['energy'].get('pkg', 0) / max(avg_cpu_usage, 0.01)  # Joules per % CPU
            
            # Main energy consumption data
            energy_consumption = {
                'job_key': task.job_key,
                'call_id': task.call_id,
                'timestamp': timestamp,
                'energy_pkg': energy_data['energy'].get('pkg', 0),
                'energy_cores': energy_data['energy'].get('cores', 0),
                'core_percentage': energy_data['energy'].get('core_percentage', 0),
                'duration': energy_data['duration'],
                'source': energy_data.get('source', 'unknown'),
                'function_name': function_name,
                # Additional metrics
                'energy_efficiency': energy_efficiency,  # Watts
                'avg_cpu_usage': avg_cpu_usage,  # %
                'energy_per_cpu': energy_per_cpu,  # Joules per % CPU
                'cpu_count': len(cpu_info['usage']),  # Number of CPU cores
                'active_cpus': sum(1 for cpu in cpu_info['usage'] if cpu > 5),  # Number of active CPU cores (>5%)
                'max_cpu_usage': max(cpu_info['usage']) if cpu_info['usage'] else 0,  # Maximum CPU usage
                'system_time': cpu_info.get('system', 0),  # System CPU time
                'user_time': cpu_info.get('user', 0)  # User CPU time
            }
            
            # CPU usage data
            cpu_usage = []
            
            # Get start timestamp and end timestamps from cpu_info if available
            start_timestamp = cpu_info.get('start_timestamp', timestamp)
            end_timestamps = cpu_info.get('end_timestamps', [])
            
            # If end_timestamps is not available or empty, use the current timestamp for all cores
            if not end_timestamps:
                end_timestamps = [timestamp] * len(cpu_info['usage'])
            
            # Create CPU usage entries with both start and end timestamps
            for cpu_id, cpu_percent in enumerate(cpu_info['usage']):
                # Get the end timestamp for this CPU core
                end_timestamp = end_timestamps[cpu_id] if cpu_id < len(end_timestamps) else timestamp
                
                cpu_usage.append({
                    'cpu_id': cpu_id,
                    'cpu_percent': cpu_percent,
                    'start_timestamp': start_timestamp,
                    'end_timestamp': end_timestamp
                })
            
            # Combine all data into one object
            all_data = {
                'energy_consumption': energy_consumption,
                'cpu_usage': cpu_usage
            }
            
            # Write to a single JSON file
            json_file = os.path.join(json_dir, f"{execution_id}_perf.json")
            with open(json_file, 'w') as f:
                json.dump(all_data, f, indent=2)
            
            logger.info(f"Energy data stored in JSON file: {json_file}")
            
            # Also write a summary file that contains all execution IDs
            summary_file = os.path.join(json_dir, 'perf_summary.json')
            summary = []
            
            if os.path.exists(summary_file):
                try:
                    with open(summary_file, 'r') as f:
                        summary = json.load(f)
                except Exception as e:
                    logger.error(f"Error reading summary file: {e}")
                    summary = []
            
            summary.append({
                'execution_id': execution_id,
                'function_name': function_name,
                'timestamp': timestamp,
                'energy_pkg': energy_data['energy'].get('pkg', 0),
                'energy_cores': energy_data['energy'].get('cores', 0),
                'core_percentage': energy_data['energy'].get('core_percentage', 0),
                'energy_efficiency': energy_efficiency,
                'avg_cpu_usage': avg_cpu_usage,
                'energy_per_cpu': energy_per_cpu
            })
            
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
        except Exception as e:
            logger.error(f"Error writing energy data to JSON file: {e}")
            # Fallback to simple text file in /tmp directory if JSON fails
            energy_file = os.path.join("/tmp", f'lithops_energy_consumption_{task.job_key}_{task.call_id}.txt')
            # Ensure the directory exists
            os.makedirs(os.path.dirname(energy_file), exist_ok=True)
            with open(energy_file, 'w') as f:
                f.write("Performance counter stats for 'system wide':\n\n")
                f.write(f"          {energy_data['energy'].get('pkg', 0):.2f} Joules power/energy-pkg/\n")
                f.write(f"          {energy_data['energy'].get('cores', 0):.2f} Joules power/energy-cores/\n")
                f.write(f"          {energy_data['energy'].get('core_percentage', 0) * 100:.2f}% core percentage (cores/pkg)\n")
            logger.info(f"Energy data stored in fallback file: {energy_file}")
            
    def update_function_name(self, task: Any, function_name: str) -> None:
        """
        Update the function name in the JSON files.
        
        Args:
            task: The task object.
            function_name: The function name.
        """
        # Store function name
        self.function_name = function_name
        
        try:
            # Get the current working directory
            cwd = os.getcwd()
            json_dir = os.path.join(cwd, 'energy_data')
            json_file = os.path.join(json_dir, f"{task.job_key}_{task.call_id}_perf.json")
            
            if os.path.exists(json_file):
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                # Update function name
                if 'energy_consumption' in data:
                    data['energy_consumption']['function_name'] = function_name
                
                # Write updated data back to file
                with open(json_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                logger.info(f"Updated function name in JSON file: {function_name}")
                
                # Also update the summary file
                summary_file = os.path.join(json_dir, 'perf_summary.json')
                if os.path.exists(summary_file):
                    with open(summary_file, 'r') as f:
                        summary = json.load(f)
                    
                    for entry in summary:
                        if entry.get('execution_id') == f"{task.job_key}_{task.call_id}":
                            entry['function_name'] = function_name
                    
                    with open(summary_file, 'w') as f:
                        json.dump(summary, f, indent=2)
            else:
                logger.warning(f"JSON file not found for updating function name: {json_file}")
        except Exception as e:
            logger.error(f"Error updating function name in JSON file: {e}")
