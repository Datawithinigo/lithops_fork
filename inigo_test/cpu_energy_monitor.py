#!/usr/bin/env python3
"""
CPU Energy Monitor using PowerAPI

This script monitors and calculates CPU energy consumption in real-time using PowerAPI.
It collects energy data over a defined period and saves results to a CSV file.
"""

import os
import time
import csv
import logging
import argparse
import signal
import threading
from datetime import datetime
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('cpu_energy_monitor')

# PowerAPI might need to be installed from its GitHub repository
# as it may not be available via pip directly
try:
    import powerapi
    from powerapi.sensor import PowerSensor
    from powerapi.report import PowerReport
    POWERAPI_AVAILABLE = True
except ImportError:
    logger.error("""
    PowerAPI library not found. To install PowerAPI:
    
    1. Clone the repository:
       git clone https://github.com/powerapi-ng/powerapi.git
       
    2. Install from the cloned repository:
       cd powerapi
       pip install -e .
       
    Alternatively, you can use a simulated version by setting SIMULATE_POWERAPI=True below.
    """)
    POWERAPI_AVAILABLE = False

# Set to True to use simulated PowerAPI when the actual library is not available
SIMULATE_POWERAPI = False

class SimulatedPowerSensor:
    """A simulated power sensor for testing when PowerAPI is not available."""
    
    def __init__(self):
        self.base_power = 15.0  # Base power in watts
        
    def get_power_report(self):
        """Return a simulated power report."""
        # Simulate some variation in power readings
        power = self.base_power + (random.random() * 5.0)
        
        # Create a simple object with a power attribute
        class SimulatedReport:
            def __init__(self, power_value):
                self.power = power_value
                
        return SimulatedReport(power)

class CPUEnergyMonitor:
    """
    A class to monitor CPU energy consumption using PowerAPI.
    """
    
    def __init__(self, duration=60, output_file=None, sampling_rate=1.0):
        """
        Initialize the CPU energy monitor.
        
        Args:
            duration (int): Monitoring duration in seconds
            output_file (str): Path to save CSV results
            sampling_rate (float): Sampling rate in seconds
        """
        self.duration = duration
        self.sampling_rate = sampling_rate
        self.running = False
        self.energy_data = []
        self.total_energy = 0.0
        self.start_time = None
        
        # Set default output file if not provided
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_file = Path(os.path.dirname(os.path.abspath(__file__))) / f"energy_results_{timestamp}.csv"
        else:
            self.output_file = Path(output_file)
        
        # Initialize sensor (PowerAPI or simulated)
        try:
            if POWERAPI_AVAILABLE and not SIMULATE_POWERAPI:
                self.sensor = PowerSensor()
                logger.info("PowerAPI sensor initialized successfully")
            else:
                import random  # Import here to avoid unused import if not using simulation
                self.sensor = SimulatedPowerSensor()
                logger.info("Using simulated power sensor (PowerAPI not available)")
        except Exception as e:
            logger.error(f"Failed to initialize power sensor: {e}")
            raise
    
    def start_monitoring(self):
        """Start the energy monitoring process."""
        if self.running:
            logger.warning("Monitoring is already running")
            return
        
        self.running = True
        self.energy_data = []
        self.total_energy = 0.0
        self.start_time = time.time()
        
        # Start monitoring in a non-blocking way
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logger.info(f"Started CPU energy monitoring for {self.duration} seconds")
        
        # Set a timer to stop monitoring after the specified duration
        if self.duration > 0:
            stop_timer = threading.Timer(self.duration, self.stop_monitoring)
            stop_timer.daemon = True
            stop_timer.start()
    
    def _monitor_loop(self):
        """Internal monitoring loop that collects energy data."""
        try:
            while self.running:
                # Get current power reading
                report = self.sensor.get_power_report()
                timestamp = time.time() - self.start_time
                
                # Extract CPU power data
                cpu_power = report.cpu_power if hasattr(report, 'cpu_power') else report.power
                
                # Calculate energy for this interval (power * time)
                interval_energy = cpu_power * self.sampling_rate
                self.total_energy += interval_energy
                
                # Store the data point
                data_point = {
                    'timestamp': timestamp,
                    'power_watts': cpu_power,
                    'energy_joules': interval_energy,
                    'total_energy_joules': self.total_energy
                }
                self.energy_data.append(data_point)
                
                # Log data point
                if len(self.energy_data) % 10 == 0:  # Log every 10th reading to avoid excessive output
                    logger.info(f"Current power: {cpu_power:.2f}W, Total energy: {self.total_energy:.2f}J")
                
                # Sleep for the sampling interval
                time.sleep(self.sampling_rate)
                
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            self.running = False
    
    def stop_monitoring(self):
        """Stop the energy monitoring process."""
        if not self.running:
            logger.warning("Monitoring is not running")
            return
        
        self.running = False
        if hasattr(self, 'monitor_thread') and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
        
        elapsed_time = time.time() - self.start_time
        logger.info(f"Stopped CPU energy monitoring after {elapsed_time:.2f} seconds")
        logger.info(f"Total energy consumed: {self.total_energy:.2f} Joules")
        logger.info(f"Average power: {self.total_energy / elapsed_time:.2f} Watts")
        
        # Save results to CSV
        self.save_results()
    
    def save_results(self):
        """Save the collected energy data to a CSV file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            
            with open(self.output_file, 'w', newline='') as csvfile:
                fieldnames = ['timestamp', 'power_watts', 'energy_joules', 'total_energy_joules']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for data_point in self.energy_data:
                    writer.writerow(data_point)
            
            logger.info(f"Results saved to {self.output_file}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")

def handle_signal(signum, frame):
    """Signal handler for graceful shutdown."""
    logger.info(f"Received signal {signum}, shutting down...")
    if monitor and monitor.running:
        monitor.stop_monitoring()
    sys.exit(0)

def main():
    """Main function to parse arguments and run the monitor."""
    parser = argparse.ArgumentParser(description='Monitor CPU energy consumption using PowerAPI')
    parser.add_argument('-d', '--duration', type=int, default=60,
                        help='Monitoring duration in seconds (default: 60)')
    parser.add_argument('-o', '--output', type=str, default=None,
                        help='Output CSV file path (default: inigo_test/energy_results_TIMESTAMP.csv)')
    parser.add_argument('-r', '--rate', type=float, default=1.0,
                        help='Sampling rate in seconds (default: 1.0)')
    parser.add_argument('-s', '--simulate', action='store_true',
                        help='Use simulated power data instead of PowerAPI')
    
    args = parser.parse_args()
    
    # Set simulation flag if requested
    global SIMULATE_POWERAPI
    if args.simulate:
        SIMULATE_POWERAPI = True
        logger.info("Using simulated power data as requested")
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    try:
        global monitor
        monitor = CPUEnergyMonitor(
            duration=args.duration,
            output_file=args.output,
            sampling_rate=args.rate
        )
        
        # Start monitoring
        monitor.start_monitoring()
        
        # Wait for the monitoring to complete if duration is specified
        if args.duration > 0:
            # Use a non-blocking approach to wait
            end_time = time.time() + args.duration + 5  # Add a small buffer
            while monitor.running and time.time() < end_time:
                time.sleep(0.1)
        
        # If no duration specified, run until interrupted
        else:
            logger.info("Running until interrupted (Ctrl+C to stop)")
            while monitor.running:
                time.sleep(1)
                
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        if 'monitor' in globals() and monitor.running:
            monitor.stop_monitoring()
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
