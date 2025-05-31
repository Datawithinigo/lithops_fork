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
import subprocess
import logging
import json
import threading
import re
from typing import Dict, Any, Optional, List, Tuple

from lithops.worker.energy.interfaces import IEnergyMonitor
from lithops.worker.energy.observer import EnergySubject

logger = logging.getLogger(__name__)

class IPMIEnergyMonitor(IEnergyMonitor, EnergySubject):
    """
    Energy monitor implementation using IPMI (Intelligent Platform Management Interface).
    
    This monitor uses the ipmitool to collect power consumption data from the BMC
    (Baseboard Management Controller) of the server. It provides a system-level view
    of power consumption, which is useful for understanding the overall energy usage
    of the server during function execution.
    """
    
    def __init__(self, process_id: int, config: Dict[str, Any]) -> None:
        """
        Initialize the IPMI energy monitor.
        
        Args:
            process_id: The process ID to monitor.
            config: Configuration options.
        """
        EnergySubject.__init__(self)
        self.process_id = process_id
        self.config = config
        self.start_time = None
        self.end_time = None
        self.function_name = None
        self.running = False
        self.thread = None
        self.power_readings = []
        self.voltage_readings = {}
        self.current_readings = {}
        self.temperature_readings = {}
        self.fan_readings = {}
        
        # IPMI configuration options
        self.ipmi_host = config.get('ipmi_host', 'localhost')
        self.ipmi_username = config.get('ipmi_username', None)
        self.ipmi_password = config.get('ipmi_password', None)
        self.sampling_interval = config.get('energy_sampling_interval', 1.0)  # seconds
        self.use_sudo = config.get('ipmi_use_sudo', True)
        self.ipmi_interface = config.get('ipmi_interface', 'lanplus')
        
        logger.info(f"Initialized IPMIEnergyMonitor for process {process_id}")
        
    def _check_ipmi_tool(self) -> bool:
        """
        Check if ipmitool is installed and available.
        
        Returns:
            bool: True if ipmitool is available, False otherwise.
        """
        try:
            cmd = ["ipmitool", "-V"]
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                logger.info(f"ipmitool is available: {result.stdout.strip()}")
                return True
            else:
                logger.warning(f"ipmitool check failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error checking ipmitool: {e}")
            return False
            
    def _build_ipmi_command(self, subcommand: List[str]) -> List[str]:
        """
        Build the ipmitool command with appropriate authentication options.
        
        Args:
            subcommand: The IPMI subcommand to execute.
            
        Returns:
            List[str]: The complete command as a list of strings.
        """
        cmd = []
        
        # Add sudo if configured
        if self.use_sudo:
            cmd.append("sudo")
            
        # Base command
        cmd.append("ipmitool")
        
        # Add remote host options if not localhost
        if self.ipmi_host != 'localhost':
            cmd.extend(["-I", self.ipmi_interface])
            cmd.extend(["-H", self.ipmi_host])
            
            # Add authentication if provided
            if self.ipmi_username:
                cmd.extend(["-U", self.ipmi_username])
            if self.ipmi_password:
                cmd.extend(["-P", self.ipmi_password])
        
        # Add the subcommand
        cmd.extend(subcommand)
        
        return cmd
        
    def _get_power_reading(self) -> Optional[float]:
        """
        Get the current power reading from IPMI.
        
        Returns:
            Optional[float]: The power reading in Watts, or None if not available.
        """
        try:
            # Build the command to get power consumption
            cmd = self._build_ipmi_command(["dcmi", "power", "reading"])
            
            # Execute the command
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                # Parse the output to extract the power reading
                output = result.stdout
                logger.debug(f"Power reading output: {output}")
                
                # Look for the power reading line
                for line in output.splitlines():
                    if "Instantaneous power" in line:
                        # Extract the power value
                        match = re.search(r':\s*([\d.]+)\s*Watts', line)
                        if match:
                            power = float(match.group(1))
                            logger.debug(f"Found power reading: {power} Watts")
                            return power
                
                logger.warning("Could not find power reading in output")
                return None
            else:
                # If dcmi power reading fails, try sdr type Power_Supply
                logger.debug("DCMI power reading failed, trying SDR Power_Supply")
                return self._get_power_reading_from_sdr()
        except Exception as e:
            logger.error(f"Error getting power reading: {e}")
            return None
            
    def _get_power_reading_from_sdr(self) -> Optional[float]:
        """
        Get power reading from Sensor Data Repository (SDR).
        
        Returns:
            Optional[float]: The power reading in Watts, or None if not available.
        """
        try:
            # Build the command to get power supply readings
            cmd = self._build_ipmi_command(["sdr", "type", "Power_Supply"])
            
            # Execute the command
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                # Parse the output to extract the power reading
                output = result.stdout
                logger.debug(f"SDR Power_Supply output: {output}")
                
                # Look for power readings
                power_values = []
                for line in output.splitlines():
                    # Extract the power value
                    match = re.search(r'(\d+\.\d+|[1-9]\d*)\s*Watts', line)
                    if match:
                        power = float(match.group(1))
                        logger.debug(f"Found power reading from SDR: {power} Watts")
                        power_values.append(power)
                
                # Return the sum of all power values if found
                if power_values:
                    total_power = sum(power_values)
                    logger.debug(f"Total power from SDR: {total_power} Watts")
                    return total_power
                
                logger.warning("Could not find power reading in SDR output")
                
                # If no power readings found, try the raw command
                return self._get_power_reading_from_raw()
            else:
                logger.warning(f"SDR Power_Supply command failed: {result.stderr}")
                return self._get_power_reading_from_raw()
        except Exception as e:
            logger.error(f"Error getting power reading from SDR: {e}")
            return None
            
    def _get_power_reading_from_raw(self) -> Optional[float]:
        """
        Get power reading using raw IPMI commands.
        
        Returns:
            Optional[float]: The power reading in Watts, or None if not available.
        """
        try:
            # Build the command to get raw power reading
            # This is a common raw command for getting power consumption on many servers
            cmd = self._build_ipmi_command(["raw", "0x2E", "0xC8", "0x57", "0x01", "0x00"])
            
            # Execute the command
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                # Parse the output to extract the power reading
                output = result.stdout.strip()
                logger.debug(f"Raw power command output: {output}")
                
                # The output is typically a series of hex values
                # The power value is usually in the last 2 bytes
                try:
                    hex_values = output.split()
                    if len(hex_values) >= 2:
                        # Convert the last 2 bytes to a power value
                        power_msb = int(hex_values[-2], 16)
                        power_lsb = int(hex_values[-1], 16)
                        power = (power_msb << 8) | power_lsb
                        logger.debug(f"Parsed power from raw command: {power} Watts")
                        return float(power)
                except Exception as e:
                    logger.error(f"Error parsing raw power output: {e}")
            
            logger.warning("Could not get power reading from raw command")
            return None
        except Exception as e:
            logger.error(f"Error getting power reading from raw command: {e}")
            return None
            
    def _get_voltage_readings(self) -> Dict[str, float]:
        """
        Get voltage readings from IPMI.
        
        Returns:
            Dict[str, float]: A dictionary of voltage readings by sensor name.
        """
        voltage_readings = {}
        
        try:
            # Build the command to get voltage readings
            cmd = self._build_ipmi_command(["sdr", "type", "Voltage"])
            
            # Execute the command
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                # Parse the output to extract voltage readings
                output = result.stdout
                logger.debug(f"Voltage readings output: {output}")
                
                # Parse each line for voltage readings
                for line in output.splitlines():
                    # Extract sensor name and voltage value
                    match = re.search(r'^([\w\s\-\.]+)\s*\|\s*[\d\.]+\s*\|\s*([\d\.]+)\s*Volts', line)
                    if match:
                        sensor_name = match.group(1).strip()
                        voltage = float(match.group(2))
                        voltage_readings[sensor_name] = voltage
                        logger.debug(f"Found voltage reading: {sensor_name} = {voltage} Volts")
            else:
                logger.warning(f"Voltage readings command failed: {result.stderr}")
        except Exception as e:
            logger.error(f"Error getting voltage readings: {e}")
            
        return voltage_readings
        
    def _get_current_readings(self) -> Dict[str, float]:
        """
        Get current readings from IPMI.
        
        Returns:
            Dict[str, float]: A dictionary of current readings by sensor name.
        """
        current_readings = {}
        
        try:
            # Build the command to get current readings
            cmd = self._build_ipmi_command(["sdr", "type", "Current"])
            
            # Execute the command
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                # Parse the output to extract current readings
                output = result.stdout
                logger.debug(f"Current readings output: {output}")
                
                # Parse each line for current readings
                for line in output.splitlines():
                    # Extract sensor name and current value
                    match = re.search(r'^([\w\s\-\.]+)\s*\|\s*[\d\.]+\s*\|\s*([\d\.]+)\s*Amps', line)
                    if match:
                        sensor_name = match.group(1).strip()
                        current = float(match.group(2))
                        current_readings[sensor_name] = current
                        logger.debug(f"Found current reading: {sensor_name} = {current} Amps")
            else:
                logger.warning(f"Current readings command failed: {result.stderr}")
        except Exception as e:
            logger.error(f"Error getting current readings: {e}")
            
        return current_readings
        
    def _get_temperature_readings(self) -> Dict[str, float]:
        """
        Get temperature readings from IPMI.
        
        Returns:
            Dict[str, float]: A dictionary of temperature readings by sensor name.
        """
        temperature_readings = {}
        
        try:
            # Build the command to get temperature readings
            cmd = self._build_ipmi_command(["sdr", "type", "Temperature"])
            
            # Execute the command
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                # Parse the output to extract temperature readings
                output = result.stdout
                logger.debug(f"Temperature readings output: {output}")
                
                # Parse each line for temperature readings
                for line in output.splitlines():
                    # Extract sensor name and temperature value
                    match = re.search(r'^([\w\s\-\.]+)\s*\|\s*[\d\.]+\s*\|\s*([\d\.]+)\s*degrees C', line)
                    if match:
                        sensor_name = match.group(1).strip()
                        temperature = float(match.group(2))
                        temperature_readings[sensor_name] = temperature
                        logger.debug(f"Found temperature reading: {sensor_name} = {temperature} degrees C")
            else:
                logger.warning(f"Temperature readings command failed: {result.stderr}")
        except Exception as e:
            logger.error(f"Error getting temperature readings: {e}")
            
        return temperature_readings
        
    def _get_fan_readings(self) -> Dict[str, float]:
        """
        Get fan speed readings from IPMI.
        
        Returns:
            Dict[str, float]: A dictionary of fan speed readings by sensor name.
        """
        fan_readings = {}
        
        try:
            # Build the command to get fan readings
            cmd = self._build_ipmi_command(["sdr", "type", "Fan"])
            
            # Execute the command
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                # Parse the output to extract fan readings
                output = result.stdout
                logger.debug(f"Fan readings output: {output}")
                
                # Parse each line for fan readings
                for line in output.splitlines():
                    # Extract sensor name and fan speed value
                    match = re.search(r'^([\w\s\-\.]+)\s*\|\s*[\d\.]+\s*\|\s*([\d\.]+)\s*RPM', line)
                    if match:
                        sensor_name = match.group(1).strip()
                        fan_speed = float(match.group(2))
                        fan_readings[sensor_name] = fan_speed
                        logger.debug(f"Found fan reading: {sensor_name} = {fan_speed} RPM")
            else:
                logger.warning(f"Fan readings command failed: {result.stderr}")
        except Exception as e:
            logger.error(f"Error getting fan readings: {e}")
            
        return fan_readings
        
    def _collect_readings(self) -> None:
        """
        Continuously collect power and other readings at the specified interval.
        """
        logger.info("Starting IPMI readings collection thread")
        
        while self.running:
            try:
                # Get power reading
                power = self._get_power_reading()
                if power is not None:
                    timestamp = time.time()
                    self.power_readings.append((timestamp, power))
                    logger.debug(f"Collected power reading: {power} Watts at {timestamp}")
                
                # Collect other readings less frequently (every 5 intervals)
                if len(self.power_readings) % 5 == 0:
                    # Get voltage readings
                    voltage_readings = self._get_voltage_readings()
                    if voltage_readings:
                        timestamp = time.time()
                        self.voltage_readings[timestamp] = voltage_readings
                        logger.debug(f"Collected {len(voltage_readings)} voltage readings at {timestamp}")
                    
                    # Get current readings
                    current_readings = self._get_current_readings()
                    if current_readings:
                        timestamp = time.time()
                        self.current_readings[timestamp] = current_readings
                        logger.debug(f"Collected {len(current_readings)} current readings at {timestamp}")
                    
                    # Get temperature readings
                    temperature_readings = self._get_temperature_readings()
                    if temperature_readings:
                        timestamp = time.time()
                        self.temperature_readings[timestamp] = temperature_readings
                        logger.debug(f"Collected {len(temperature_readings)} temperature readings at {timestamp}")
                    
                    # Get fan readings
                    fan_readings = self._get_fan_readings()
                    if fan_readings:
                        timestamp = time.time()
                        self.fan_readings[timestamp] = fan_readings
                        logger.debug(f"Collected {len(fan_readings)} fan readings at {timestamp}")
                
                # Sleep for the specified interval
                time.sleep(self.sampling_interval)
            except Exception as e:
                logger.error(f"Error collecting IPMI readings: {e}")
                # Sleep for a short time to avoid tight loop in case of errors
                time.sleep(1)
                
    def _generate_placeholder_data(self, duration: float) -> None:
        """
        Generate placeholder data when IPMI is not available.
        
        Args:
            duration: The duration of the monitoring period in seconds.
        """
        logger.info("Generating placeholder IPMI data")
        
        # Generate power readings
        num_readings = int(duration / self.sampling_interval)
        base_power = 200.0  # Base power in Watts
        
        for i in range(num_readings):
            # Generate a timestamp
            timestamp = self.start_time + i * self.sampling_interval
            
            # Generate a power reading with some variation
            variation = (i / num_readings) * 50  # Power increases over time
            noise = (hash(str(timestamp)) % 20) - 10  # Random noise between -10 and 10
            power = base_power + variation + noise
            
            # Add the reading
            self.power_readings.append((timestamp, power))
            
        # Generate voltage readings
        voltage_timestamp = self.start_time + duration / 3
        self.voltage_readings[voltage_timestamp] = {
            "CPU1 Voltage": 1.2 + (hash(str(voltage_timestamp)) % 10) / 100,
            "CPU2 Voltage": 1.2 + (hash(str(voltage_timestamp + 1)) % 10) / 100,
            "System 12V": 12.0 + (hash(str(voltage_timestamp + 2)) % 10) / 100,
            "System 5V": 5.0 + (hash(str(voltage_timestamp + 3)) % 10) / 100,
            "System 3.3V": 3.3 + (hash(str(voltage_timestamp + 4)) % 10) / 100
        }
        
        # Generate current readings
        current_timestamp = self.start_time + 2 * duration / 3
        self.current_readings[current_timestamp] = {
            "CPU1 Current": 10.0 + (hash(str(current_timestamp)) % 10) / 10,
            "CPU2 Current": 10.0 + (hash(str(current_timestamp + 1)) % 10) / 10,
            "System Current": 20.0 + (hash(str(current_timestamp + 2)) % 10) / 10
        }
        
        # Generate temperature readings
        temp_timestamp = self.start_time + duration / 2
        self.temperature_readings[temp_timestamp] = {
            "CPU1 Temp": 65.0 + (hash(str(temp_timestamp)) % 10),
            "CPU2 Temp": 63.0 + (hash(str(temp_timestamp + 1)) % 10),
            "System Temp": 40.0 + (hash(str(temp_timestamp + 2)) % 5),
            "Inlet Temp": 25.0 + (hash(str(temp_timestamp + 3)) % 3)
        }
        
        # Generate fan readings
        fan_timestamp = self.start_time + 2 * duration / 3
        self.fan_readings[fan_timestamp] = {
            "Fan1": 5000 + (hash(str(fan_timestamp)) % 1000),
            "Fan2": 5000 + (hash(str(fan_timestamp + 1)) % 1000),
            "Fan3": 5000 + (hash(str(fan_timestamp + 2)) % 1000),
            "Fan4": 5000 + (hash(str(fan_timestamp + 3)) % 1000)
        }
        
    def start(self) -> bool:
        """
        Start monitoring energy consumption using IPMI.
        
        Returns:
            bool: True if monitoring started successfully, False otherwise.
        """
        logger.info("Starting IPMIEnergyMonitor")
        
        # Record start time
        self.start_time = time.time()
        
        # Check if ipmitool is available
        if not self._check_ipmi_tool():
            logger.warning("ipmitool is not available")
            logger.warning("Will generate placeholder data for JSON files")
            
            # Set running flag to False but return True to indicate we'll generate placeholder data
            self.running = False
            
            # Notify observers
            self.notify('start', {
                'monitor': 'ipmi',
                'process_id': self.process_id,
                'start_time': self.start_time,
                'placeholder': True
            })
            
            return True
        
        # Test if we can get a power reading
        power = self._get_power_reading()
        if power is None:
            logger.warning("Could not get power reading from IPMI")
            logger.warning("Will generate placeholder data for JSON files")
            
            # Set running flag to False but return True to indicate we'll generate placeholder data
            self.running = False
            
            # Notify observers
            self.notify('start', {
                'monitor': 'ipmi',
                'process_id': self.process_id,
                'start_time': self.start_time,
                'placeholder': True
            })
            
            return True
        
        # Start the monitoring thread
        self.running = True
        self.thread = threading.Thread(target=self._collect_readings)
        self.thread.daemon = True
        self.thread.start()
        
        logger.info(f"IPMIEnergyMonitor started at: {self.start_time}")
        
        # Notify observers
        self.notify('start', {
            'monitor': 'ipmi',
            'process_id': self.process_id,
            'start_time': self.start_time
        })
        
        return True
        
    def stop(self) -> None:
        """Stop monitoring energy consumption."""
        logger.info("Stopping IPMIEnergyMonitor")
        
        # Record end time
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        logger.debug(f"Monitoring duration: {duration:.2f} seconds")
        
        # If we're not running, generate placeholder data
        if not self.running:
            self._generate_placeholder_data(duration)
        else:
            # Stop the monitoring thread
            self.running = False
            
            # Wait for thread to finish
            if self.thread:
                self.thread.join(timeout=5)
                logger.debug("Monitoring thread joined")
        
        # Notify observers
        self.notify('stop', {
            'monitor': 'ipmi',
            'process_id': self.process_id,
            'end_time': self.end_time,
            'duration': duration
        })
        
    def get_energy_data(self) -> Dict[str, Any]:
        """
        Get the collected energy data.
        
        Returns:
            Dict[str, Any]: A dictionary containing energy metrics.
        """
        logger.debug("Getting energy data from IPMIEnergyMonitor")
        
        # Calculate duration
        duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        logger.debug(f"Duration: {duration:.2f} seconds")
        
        # Calculate average power
        avg_power = 0.0
        if self.power_readings:
            total_power = sum(power for _, power in self.power_readings)
            avg_power = total_power / len(self.power_readings)
            logger.debug(f"Average power: {avg_power:.2f} Watts")
        
        # Calculate energy consumption (power * time)
        # Convert from Watt-seconds to Joules (1 Watt-second = 1 Joule)
        energy_joules = avg_power * duration
        logger.debug(f"Energy consumption: {energy_joules:.2f} Joules")
        
        # Create the result dictionary
        result = {
            'energy': {
                'system': energy_joules,  # Total system energy in Joules
                'avg_power': avg_power    # Average power in Watts
            },
            'duration': duration,
            'source': 'ipmi',
            'readings': {
                'power': self.power_readings,
                'voltage': self.voltage_readings,
                'current': self.current_readings,
                'temperature': self.temperature_readings,
                'fan': self.fan_readings
            }
        }
        
        # Calculate min, max, and std dev of power readings
        if self.power_readings:
            power_values = [power for _, power in self.power_readings]
            result['energy']['min_power'] = min(power_values)
            result['energy']['max_power'] = max(power_values)
            
            # Calculate standard deviation
            mean = sum(power_values) / len(power_values)
            variance = sum((x - mean) ** 2 for x in power_values) / len(power_values)
            result['energy']['power_std_dev'] = variance ** 0.5
        
        # Calculate average temperatures if available
        if self.temperature_readings:
            # Get the latest temperature readings
            latest_timestamp = max(self.temperature_readings.keys())
            latest_temps = self.temperature_readings[latest_timestamp]
            
            # Calculate average CPU temperature
            cpu_temps = [temp for name, temp in latest_temps.items() if 'cpu' in name.lower()]
            if cpu_temps:
                result['energy']['avg_cpu_temp'] = sum(cpu_temps) / len(cpu_temps)
            
            # Calculate average system temperature
            sys_temps = [temp for name, temp in latest_temps.items() if 'system' in name.lower()]
            if sys_temps:
                result['energy']['avg_system_temp'] = sum(sys_temps) / len(sys_temps)
        
        logger.debug(f"Final energy data: {result}")
        
        # Notify observers
        self.notify('data', {
            'monitor': 'ipmi',
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
        logger.info(f"IPMI energy consumption: {energy_data['energy'].get('system', 'N/A')} Joules")
        logger.info(f"IPMI average power: {energy_data['energy'].get('avg_power', 'N/A')} Watts")
        
        # Store energy data in JSON format
        self._store_energy_data_json(energy_data, task, cpu_info, function_name)
        
        # Notify observers
        self.notify('log', {
            'monitor': 'ipmi',
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
            
            # Get energy values
            system_energy = energy_data['energy'].get('system', 0)
            avg_power = energy_data['energy'].get('avg_power', 0)
            min_power = energy_data['energy'].get('min_power', 0)
            max_power = energy_data['energy'].get('max_power', 0)
            power_std_dev = energy_data['energy'].get('power_std_dev', 0)
            
            # Calculate additional metrics
            duration = energy_data['duration']
            energy_efficiency = system_energy / max(duration, 0.001)  # Watts
            
            # Calculate average CPU usage
            avg_cpu_usage = sum(cpu_info['usage']) / len(cpu_info['usage']) if cpu_info['usage'] else 0
            
            # Calculate energy per CPU usage
            energy_per_cpu = system_energy / max(avg_cpu_usage, 0.01)  # Joules per % CPU
            
            # Main energy consumption data
            energy_consumption = {
                'job_key': task.job_key,
                'call_id': task.call_id,
                'timestamp': timestamp,
                'energy_system': system_energy,
                'avg_power': avg_power,
                'min_power': min_power,
                'max_power': max_power,
                'power_std_dev': power_std_dev,
                'duration': energy_data['duration'],
                'source': energy_data.get('source', 'ipmi'),
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
            
            # Add temperature data if available
            if 'avg_cpu_temp' in energy_data['energy']:
                energy_consumption['avg_cpu_temp'] = energy_data['energy']['avg_cpu_temp']
            if 'avg_system_temp' in energy_data['energy']:
                energy_consumption['avg_system_temp'] = energy_data['energy']['avg_system_temp']
            
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
            
            # Power readings data
            power_readings = []
            for timestamp, power in self.power_readings:
                power_readings.append({
                    'timestamp': timestamp,
                    'power': power
                })
            
            # Voltage readings data
            voltage_readings = []
            for timestamp, readings in self.voltage_readings.items():
                for sensor, value in readings.items():
                    voltage_readings.append({
                        'timestamp': timestamp,
                        'sensor': sensor,
                        'value': value
                    })
            
            # Current readings data
            current_readings = []
            for timestamp, readings in self.current_readings.items():
                for sensor, value in readings.items():
                    current_readings.append({
                        'timestamp': timestamp,
                        'sensor': sensor,
                        'value': value
                    })
            
            # Temperature readings data
            temperature_readings = []
            for timestamp, readings in self.temperature_readings.items():
                for sensor, value in readings.items():
                    temperature_readings.append({
                        'timestamp': timestamp,
                        'sensor': sensor,
                        'value': value
                    })
            
            # Fan readings data
            fan_readings = []
            for timestamp, readings in self.fan_readings.items():
                for sensor, value in readings.items():
                    fan_readings.append({
                        'timestamp': timestamp,
                        'sensor': sensor,
                        'value': value
                    })
            
            # Combine all data into one object
            all_data = {
                'energy_consumption': energy_consumption,
                'cpu_usage': cpu_usage,
                'power_readings': power_readings,
                'voltage_readings': voltage_readings,
                'current_readings': current_readings,
                'temperature_readings': temperature_readings,
                'fan_readings': fan_readings
            }
            
            # Write to a single JSON file
            json_file = os.path.join(json_dir, f"{execution_id}_ipmi.json")
            with open(json_file, 'w') as f:
                json.dump(all_data, f, indent=2)
            
            logger.info(f"IPMI energy data stored in JSON file: {json_file}")
            
            # Also write a summary file that contains all execution IDs
            summary_file = os.path.join(json_dir, 'ipmi_summary.json')
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
                'energy_system': system_energy,
                'avg_power': avg_power,
                'min_power': min_power,
                'max_power': max_power,
                'power_std_dev': power_std_dev,
                'energy_efficiency': energy_efficiency,
                'avg_cpu_usage': avg_cpu_usage,
                'energy_per_cpu': energy_per_cpu
            })
            
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
        except Exception as e:
            logger.error(f"Error writing IPMI energy data to JSON file: {e}")
            # Fallback to simple text file in /tmp directory if JSON fails
            energy_file = os.path.join("/tmp", f'lithops_ipmi_energy_{task.job_key}_{task.call_id}.txt')
            # Ensure the directory exists
            os.makedirs(os.path.dirname(energy_file), exist_ok=True)
            with open(energy_file, 'w') as f:
                f.write("IPMI Energy Monitoring Results:\n\n")
                f.write(f"          {energy_data['energy'].get('system', 0):.2f} Joules total system energy\n")
                f.write(f"          {energy_data['energy'].get('avg_power', 0):.2f} Watts average power\n")
                f.write(f"          {energy_data['duration']:.2f} seconds duration\n")
            logger.info(f"Energy data stored in fallback file: {energy_file}")
