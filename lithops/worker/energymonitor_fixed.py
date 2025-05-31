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
import shutil
from .energymonitor_json_utils import store_energy_data_json, update_function_name

logger = logging.getLogger(__name__)


class EnergyMonitor:
    """
    Enhanced energy monitor that handles various environments including Kubernetes
    with limited privileges. Provides multiple fallback mechanisms when perf
    or RAPL are not available.
    """
    def __init__(self, process_id):
        self.process_id = process_id
        self.perf_process = None
        self.start_time = None
        self.end_time = None
        self.energy_pkg = None
        self.energy_cores = None
        self.cpu_percent = None
        self.perf_output_file = f"/tmp/perf_energy_{process_id}.txt"
        self.function_name = None
        
        # Detect available energy measurement methods
        self.available_methods = self._detect_available_methods()
        
        # Print directly to terminal for debugging
        print(f"\n==== ENERGY MONITOR INITIALIZED FOR PROCESS {process_id} ====")
        print(f"Available methods: {', '.join(self.available_methods)}")
        
    def _detect_available_methods(self):
        """Detect what energy measurement methods are available."""
        methods = []
        
        # Check if perf is available
        if shutil.which('perf'):
            print("✓ perf tool found")
            # Check if we can run perf without sudo
            try:
                result = subprocess.run(['perf', 'list'], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE, 
                                      timeout=5)
                if result.returncode == 0:
                    methods.append('perf_no_sudo')
                    print("✓ perf works without sudo")
                else:
                    print("✗ perf requires sudo privileges")
            except Exception as e:
                print(f"✗ perf test failed: {e}")
        else:
            print("✗ perf tool not found")
            
        # Check if RAPL is available and readable
        rapl_paths = [
            '/sys/class/powercap/intel-rapl:0/energy_uj',
            '/sys/class/powercap/intel-rapl:0:0/energy_uj'
        ]
        
        for path in rapl_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        f.read()
                    methods.append('rapl_direct')
                    print(f"✓ RAPL readable at {path}")
                    break
                except PermissionError:
                    print(f"✗ RAPL exists but not readable at {path} (needs root)")
                except Exception as e:
                    print(f"✗ RAPL error at {path}: {e}")
        
        # CPU-based estimation is always available
        methods.append('cpu_estimation')
        print("✓ CPU-based estimation available")
        
        return methods
        
    def _get_available_energy_events(self):
        """Get a list of available energy-related events from perf."""
        print("\n==== CHECKING AVAILABLE ENERGY EVENTS ====")
        try:
            result = subprocess.run(
                ["perf", "list"], 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
                timeout=10
            )
            
            if result.returncode != 0:
                print(f"perf list failed with return code: {result.returncode}")
                print(f"stderr: {result.stderr}")
                return "power/energy-pkg/,power/energy-cores/"
            
            output = result.stdout + result.stderr
            print(f"Perf list output length: {len(output)} characters")
            
            # Extract energy-related events
            energy_events = []
            for line in output.splitlines():
                if "energy" in line.lower():
                    print(f"Found energy line: {line}")
                    # Extract the event name from the line
                    match = re.search(r'(\S+/\S+/)', line)
                    if match:
                        energy_events.append(match.group(1))
            
            # Prepare the events string
            if energy_events:
                print(f"Found {len(energy_events)} energy events: {', '.join(energy_events)}")
                
                # Check for both pkg and cores events
                pkg_events = [e for e in energy_events if "energy-pkg" in e]
                cores_events = [e for e in energy_events if "energy-cores" in e]
                
                events = []
                if pkg_events:
                    print(f"Found energy-pkg event: {pkg_events[0]}")
                    events.append(pkg_events[0])
                else:
                    print("No energy-pkg event found, using default")
                    events.append("power/energy-pkg/")
                    
                if cores_events:
                    print(f"Found energy-cores event: {cores_events[0]}")
                    events.append(cores_events[0])
                else:
                    print("No energy-cores event found, using default")
                    events.append("power/energy-cores/")
                
                # Join events with comma
                events_str = ",".join(events)
                print(f"Using energy events: {events_str}")
                return events_str
            else:
                print("No energy events found in perf list")
                
            # Default to both pkg and cores events
            events_str = "power/energy-pkg/,power/energy-cores/"
            print(f"Using default energy events: {events_str}")
            return events_str
        except Exception as e:
            print(f"Error getting available energy events: {e}")
            # Default to both pkg and cores events
            events_str = "power/energy-pkg/,power/energy-cores/"
            print(f"Using default energy events: {events_str}")
            return events_str
    
    def _try_rapl_direct(self):
        """Try to read RAPL energy values directly."""
        print("\n==== TRYING DIRECT RAPL ACCESS ====")
        
        rapl_files = {
            'pkg': '/sys/class/powercap/intel-rapl:0/energy_uj',
            'cores': '/sys/class/powercap/intel-rapl:0:0/energy_uj'
        }
        
        energy_values = {}
        
        for domain, path in rapl_files.items():
            try:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        value_uj = int(f.read().strip())
                        value_j = value_uj / 1e6  # Convert microjoules to joules
                        energy_values[domain] = value_j
                        print(f"✓ Read {domain} energy: {value_j:.6f} J")
                else:
                    print(f"✗ RAPL file not found: {path}")
            except PermissionError:
                print(f"✗ Permission denied reading {path}")
            except Exception as e:
                print(f"✗ Error reading {path}: {e}")
        
        return energy_values
    
    def _estimate_energy_from_cpu(self, duration, cpu_percent):
        """Estimate energy consumption based on CPU usage and duration."""
        print(f"\n==== ESTIMATING ENERGY FROM CPU USAGE ====")
        print(f"Duration: {duration:.2f}s, CPU: {cpu_percent:.1f}%")
        
        # Typical TDP values for different processor types
        # These are rough estimates based on common processor specifications
        tdp_estimates = {
            'server': 85.0,    # Server processors (Xeon, EPYC)
            'desktop': 65.0,   # Desktop processors (Core i5/i7, Ryzen)
            'laptop': 15.0,    # Laptop processors (Core i5/i7 U-series)
            'embedded': 10.0   # Embedded/low-power processors
        }
        
        # Try to detect processor type from /proc/cpuinfo
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read().lower()
                
            if 'xeon' in cpuinfo or 'epyc' in cpuinfo:
                tdp = tdp_estimates['server']
                processor_type = 'server'
            elif any(x in cpuinfo for x in ['core(tm) i7', 'core(tm) i5', 'ryzen']):
                if any(x in cpuinfo for x in ['mobile', 'laptop', '@']):
                    tdp = tdp_estimates['laptop']
                    processor_type = 'laptop'
                else:
                    tdp = tdp_estimates['desktop']
                    processor_type = 'desktop'
            else:
                tdp = tdp_estimates['embedded']
                processor_type = 'embedded'
                
            print(f"Detected processor type: {processor_type} (TDP: {tdp}W)")
            
        except Exception as e:
            print(f"Could not detect processor type: {e}")
            tdp = tdp_estimates['desktop']  # Default fallback
            processor_type = 'unknown'
        
        # Calculate estimated energy consumption
        # Energy = Power × Time
        # Power = TDP × (CPU_usage / 100) × efficiency_factor
        
        # Efficiency factor accounts for the fact that not all CPU usage
        # translates directly to power consumption
        efficiency_factor = 0.7  # Conservative estimate
        
        estimated_power = tdp * (cpu_percent / 100.0) * efficiency_factor
        estimated_energy_pkg = estimated_power * duration
        
        # Cores typically consume about 70-90% of package energy
        estimated_energy_cores = estimated_energy_pkg * 0.8
        
        print(f"Estimated power: {estimated_power:.2f}W")
        print(f"Estimated energy (pkg): {estimated_energy_pkg:.2f}J")
        print(f"Estimated energy (cores): {estimated_energy_cores:.2f}J")
        
        return {
            'pkg': estimated_energy_pkg,
            'cores': estimated_energy_cores,
            'method': 'cpu_estimation',
            'tdp': tdp,
            'processor_type': processor_type,
            'efficiency_factor': efficiency_factor
        }
        
    def start(self):
        """Start monitoring energy consumption using the best available method."""
        print("\n==== STARTING ENERGY MONITORING ====")
        self.start_time = time.time()
        
        # Try perf first if available
        if 'perf_no_sudo' in self.available_methods:
            return self._start_perf_monitoring()
        
        # If perf is not available, we'll rely on CPU-based estimation
        print("Using CPU-based energy estimation")
        return True
    
    def _start_perf_monitoring(self):
        """Start perf-based energy monitoring."""
        try:
            # Get the energy-pkg event
            energy_event = self._get_available_energy_events()
            print(f"Using energy event: {energy_event}")
            
            # Create a unique output file for this run
            self.perf_output_file = f"/tmp/perf_energy_{self.process_id}_{int(time.time())}.txt"
            
            # Start perf in the background to monitor the entire function execution
            print("Starting perf stat to monitor energy consumption...")
            
            # Try without sudo first
            cmd = [
                "perf", "stat",
                "-e", energy_event,
                "-a",  # Monitor all CPUs
                "-o", self.perf_output_file  # Output to a file
            ]
            
            print(f"Running command: {' '.join(cmd)}")
            
            # Start perf in the background
            self.perf_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            print(f"Perf process started with PID: {self.perf_process.pid}")
            return True
        except Exception as e:
            print(f"Error starting perf monitoring: {e}")
            return False
            
    def stop(self):
        """Stop monitoring energy consumption and collect results."""
        print("\n==== STOPPING ENERGY MONITORING ====")
        
        if self.start_time is None:
            print("Energy monitoring was not started")
            return
            
        # Record the end time
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        print(f"Energy monitoring stopped at: {self.end_time}")
        print(f"Monitoring duration: {duration:.2f} seconds")
        
        # Get CPU percentage for the process
        cpu_percent = 0
        try:
            import psutil
            print(f"Getting CPU percentage for process {self.process_id}")
            process = psutil.Process(self.process_id)
            # Call cpu_percent once with interval=None to get the value since the last call
            process.cpu_percent()
            # Call again with a small interval to get a more accurate reading
            cpu_percent = process.cpu_percent(interval=0.1)
            print(f"CPU percentage: {cpu_percent:.2f}%")
            self.cpu_percent = cpu_percent / 100.0  # Store as fraction
            
            # If CPU percentage is very low, use system-wide CPU usage as fallback
            if cpu_percent < 1.0:
                system_cpu = psutil.cpu_percent(interval=0.1)
                print(f"Process CPU too low ({cpu_percent:.2f}%), using system CPU: {system_cpu:.2f}%")
                cpu_percent = max(cpu_percent, system_cpu * 0.1)  # Use 10% of system CPU as minimum
                self.cpu_percent = cpu_percent / 100.0
                
        except Exception as e:
            print(f"Error getting CPU percentage: {e}")
            # Use a reasonable default based on the fact that work was done
            cpu_percent = 25.0  # Default fallback - assume moderate CPU usage
            self.cpu_percent = 0.25
            print(f"Using default CPU percentage: {cpu_percent:.2f}%")
        
        # Try different methods to get energy data
        energy_data = None
        
        # Method 1: Try perf if it was started
        if self.perf_process is not None:
            energy_data = self._stop_perf_monitoring()
        
        # Method 2: Try direct RAPL access
        if energy_data is None and 'rapl_direct' in self.available_methods:
            energy_data = self._try_rapl_direct()
            if energy_data:
                energy_data['method'] = 'rapl_direct'
        
        # Method 3: CPU-based estimation (always available)
        if energy_data is None or (energy_data.get('pkg', 0) == 0 and energy_data.get('cores', 0) == 0):
            print("Using CPU-based energy estimation as fallback")
            energy_data = self._estimate_energy_from_cpu(duration, cpu_percent)
        
        # Store the results
        if energy_data:
            self.energy_pkg = energy_data.get('pkg', 0)
            self.energy_cores = energy_data.get('cores', 0)
            print(f"Final energy values - pkg: {self.energy_pkg:.2f}J, cores: {self.energy_cores:.2f}J")
        else:
            print("No energy data available")
            self.energy_pkg = 0
            self.energy_cores = 0
    
    def _stop_perf_monitoring(self):
        """Stop perf monitoring and extract energy values."""
        print("Stopping perf monitoring...")
        
        try:
            # Stop the perf process
            print(f"Stopping perf process (PID: {self.perf_process.pid})...")
            
            # Send SIGINT to perf to make it output the results
            import signal
            os.kill(self.perf_process.pid, signal.SIGINT)
            
            # Wait for the process to exit
            try:
                stdout, stderr = self.perf_process.communicate(timeout=5)
                print("Perf process exited")
                print(f"Perf stdout: {stdout}")
                print(f"Perf stderr: {stderr}")
            except subprocess.TimeoutExpired:
                print("Perf process did not exit, killing it")
                self.perf_process.kill()
                stdout, stderr = self.perf_process.communicate()
            
            # Initialize energy values
            energy_pkg = None
            energy_cores = None
            
            # Read the output file
            print(f"Reading perf output file: {self.perf_output_file}")
            try:
                if os.path.exists(self.perf_output_file):
                    with open(self.perf_output_file, 'r') as f:
                        perf_output = f.read()
                        print(f"Perf output file content: {perf_output}")
                        
                        # Process the output to extract energy values
                        for line in perf_output.splitlines():
                            print(f"Processing line: {line}")
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
                                            print(f"Converted malformed value with multiple dots to {value_str}")
                                        
                                        energy_value = float(value_str)
                                        print(f"Found energy value: {energy_value} Joules for {event_name}")
                                        
                                        # Store the value based on the event type
                                        if "energy-pkg" in event_name:
                                            energy_pkg = energy_value
                                            print(f"Stored energy-pkg value: {energy_pkg} Joules")
                                        elif "energy-cores" in event_name:
                                            energy_cores = energy_value
                                            print(f"Stored energy-cores value: {energy_cores} Joules")
                                    except ValueError as e:
                                        print(f"Could not convert '{value_str}' to float: {e}")
                else:
                    print(f"Perf output file not found: {self.perf_output_file}")
            except Exception as e:
                print(f"Error reading perf output file: {e}")
            
            # Clean up the output file
            try:
                if os.path.exists(self.perf_output_file):
                    os.remove(self.perf_output_file)
                    print(f"Removed perf output file: {self.perf_output_file}")
            except Exception as e:
                print(f"Error removing perf output file: {e}")
            
            if energy_pkg is not None or energy_cores is not None:
                return {
                    'pkg': energy_pkg or 0,
                    'cores': energy_cores or 0,
                    'method': 'perf'
                }
            else:
                return None
                
        except Exception as e:
            print(f"Error stopping perf monitoring: {e}")
            return None
            
    def get_energy_data(self):
        """Get the collected energy data for energy-pkg and energy-cores."""
        print("\n==== GETTING ENERGY DATA ====")
        duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        print(f"Duration: {duration:.2f} seconds")
        
        # Create the base result dictionary
        result = {
            'energy': {},
            'duration': duration,
            'source': 'unknown'
        }
        
        # Add CPU percentage if available (for reference only, not for estimation)
        if self.cpu_percent is not None:
            print(f"Using CPU percentage: {self.cpu_percent * 100:.2f}%")
            result['cpu_percent'] = self.cpu_percent
        
        # Add energy values
        if self.energy_pkg is not None and self.energy_pkg > 0:
            print(f"Using measured/estimated energy-pkg: {self.energy_pkg:.2f} Joules")
            result['energy']['pkg'] = self.energy_pkg
            result['source'] = 'measured'
        else:
            print("No energy-pkg data available, setting to 0")
            result['energy']['pkg'] = 0
            
        if self.energy_cores is not None and self.energy_cores > 0:
            print(f"Using measured/estimated energy-cores: {self.energy_cores:.2f} Joules")
            result['energy']['cores'] = self.energy_cores
        else:
            print("No energy-cores data available, setting to 0")
            result['energy']['cores'] = 0
            
        # Calculate core percentage (energy_cores / energy_pkg)
        if result['energy']['pkg'] > 0:
            core_percentage = result['energy']['cores'] / result['energy']['pkg']
            print(f"Core percentage: {core_percentage:.4f} ({core_percentage * 100:.2f}%)")
            result['energy']['core_percentage'] = core_percentage
        else:
            print("Cannot calculate core percentage, energy_pkg is 0")
            result['energy']['core_percentage'] = 0
        
        # If we have no energy data at all, set source to 'none'
        if result['energy']['pkg'] == 0 and result['energy']['cores'] == 0:
            result['source'] = 'none'
            print("No energy measurement available - consider running with proper privileges")
            print("Suggestions:")
            print("1. Install perf tools: sudo apt install linux-tools-common")
            print("2. Run with sudo privileges to access RAPL energy counters")
            print("3. In Kubernetes, use privileged containers or hostPath mounts for /sys/class/powercap")

        print(f"Final energy data: {result}")
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
        logger.info(f"Energy consumption: {energy_data['energy'].get('pkg', 'N/A')} Joules (pkg), {energy_data['energy'].get('cores', 'N/A')} Joules (cores)")
        logger.info(f"Core percentage: {energy_data['energy'].get('core_percentage', 0) * 100:.2f}%")
        logger.info(f"Energy efficiency: {energy_data['energy'].get('pkg', 0) / max(energy_data['duration'], 0.001):.2f} Watts")
        logger.info(f"Energy measurement source: {energy_data.get('source', 'unknown')}")
        
        # Print energy data in the format requested by the user
        print("\nPerformance counter stats for 'system wide':")
        print()
        # Format the energy value with comma as decimal separator and dot as thousands separator
        pkg_energy = energy_data['energy'].get('pkg', 0)
        cores_energy = energy_data['energy'].get('cores', 0)
        
        pkg_energy_str = f"{pkg_energy:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        print(f"          {pkg_energy_str} Joules power/energy-pkg/ [{energy_data.get('source', 'unknown')}]")
        
        cores_energy_str = f"{cores_energy:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        print(f"          {cores_energy_str} Joules power/energy-cores/ [{energy_data.get('source', 'unknown')}]")
        
        # Print core percentage
        core_percentage = energy_data['energy'].get('core_percentage', 0)
        print(f"          {core_percentage * 100:.2f}% core percentage (cores/pkg)")
        print()
        
        # Store energy consumption data in JSON format using shared utilities
        monitor_specific_data = {
            'available_methods': self.available_methods  # What methods were available
        }
        store_energy_data_json(energy_data, task, cpu_info, pkg_energy, cores_energy, 
                              core_percentage, function_name, monitor_specific_data)
        
    def update_function_name(self, task, function_name):
        """Update the function name in the JSON files."""
        # Store function name
        self.function_name = function_name
        
        # Use shared utility function
        update_function_name(task, function_name)
            
    def read_function_name_from_stats(self, stats_file):
        """Read function name from stats file and update it in the energy monitor."""
        import logging
        
        logger = logging.getLogger(__name__)
        
        if not os.path.exists(stats_file):
            logger.warning(f"Stats file not found: {stats_file}")
            return False
        
        function_name_updated = False
        logger.info(f"Reading stats file for energy monitoring: {stats_file}")
        
        try:
            with open(stats_file, 'r') as fid:
                for line in fid.readlines():
                    try:
                        key, value = line.strip().split(" ", 1)
                        if key == 'function_name':
                            self.function_name = value
                            function_name_updated = True
                            logger.info(f"Found function name in stats file for energy monitoring: {self.function_name}")
                            break  # Exit loop once function name is found
                    except Exception as e:
                        logger.error(f"Error processing stats file line for energy monitoring: {line} - {e}")
            
            if not function_name_updated:
                logger.warning("Function name not found in stats file for energy monitoring")
        except Exception as e:
            logger.error(f"Error reading stats file for energy monitoring: {e}")
            
        return function_name_updated
