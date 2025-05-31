"""
Example script demonstrating how to use the IPMI energy monitor.

This script shows how to configure and use the IPMI energy monitor to measure
energy consumption of a function execution. The IPMI monitor uses the ipmitool
to collect power consumption data from the BMC (Baseboard Management Controller)
of the server.

Requirements:
- ipmitool must be installed on the system
- For remote servers, proper IPMI credentials are required
- For local monitoring, root privileges may be required

Usage:
    python ipmi_energy_example.py

"""

import time
import os
import json
import lithops
import numpy as np
import matplotlib.pyplot as plt
from lithops.worker.energy.monitors import IPMIEnergyMonitor
from lithops.worker.energy.extractors import IPMIEnergyExtractor

# Define a compute-intensive function to monitor
def compute_intensive_function(n):
    """A compute-intensive function that performs matrix operations."""
    # Create large matrices
    matrix_size = n
    matrix_a = np.random.rand(matrix_size, matrix_size)
    matrix_b = np.random.rand(matrix_size, matrix_size)
    
    # Perform matrix operations
    start_time = time.time()
    
    # Matrix multiplication (compute-intensive)
    result = np.matmul(matrix_a, matrix_b)
    
    # More operations to increase CPU usage
    for _ in range(3):
        result = np.matmul(result, matrix_a)
    
    # Calculate eigenvalues (also compute-intensive)
    eigenvalues = np.linalg.eigvals(result)
    
    duration = time.time() - start_time
    
    return {
        'matrix_size': matrix_size,
        'duration': duration,
        'eigenvalues_mean': float(np.mean(eigenvalues)),
        'eigenvalues_std': float(np.std(eigenvalues))
    }

# Function to run with Lithops
def run_with_lithops():
    """Run the compute-intensive function with Lithops."""
    # Configure Lithops to use the IPMI energy monitor
    config = {
        'lithops': {
            'energy': True,
            'energy_strategy': 'ipmi'
        },
        # IPMI configuration options
        'ipmi_host': 'localhost',  # Change to remote server IP if needed
        'ipmi_username': None,     # Set username for remote server
        'ipmi_password': None,     # Set password for remote server
        'ipmi_interface': 'lanplus',
        'ipmi_use_sudo': True,
        'energy_sampling_interval': 0.5  # Sample every 0.5 seconds
    }
    
    # Create a FunctionExecutor with the configuration
    fexec = lithops.FunctionExecutor(config=config)
    
    # Execute the function with different matrix sizes
    matrix_sizes = [500, 1000, 1500]
    futures = fexec.map(compute_intensive_function, matrix_sizes)
    
    # Wait for results
    results = fexec.get_result()
    
    # Print results
    for i, result in enumerate(results):
        print(f"Matrix size: {result['matrix_size']}")
        print(f"Duration: {result['duration']:.2f} seconds")
        print(f"Eigenvalues mean: {result['eigenvalues_mean']:.6f}")
        print(f"Eigenvalues std: {result['eigenvalues_std']:.6f}")
        print()
    
    # Close the executor
    fexec.close()
    
    return results

# Function to run locally with direct monitoring
def run_locally():
    """Run the compute-intensive function locally with direct monitoring."""
    # Get the current process ID
    process_id = os.getpid()
    
    # Configure the IPMI energy monitor
    config = {
        'ipmi_host': 'localhost',  # Change to remote server IP if needed
        'ipmi_username': None,     # Set username for remote server
        'ipmi_password': None,     # Set password for remote server
        'ipmi_interface': 'lanplus',
        'ipmi_use_sudo': True,
        'energy_sampling_interval': 0.5  # Sample every 0.5 seconds
    }
    
    # Create a mock task object for logging
    class MockTask:
        def __init__(self):
            self.job_key = 'local'
            self.call_id = '001'
            self.stats_file = 'stats.txt'
    
    # Create a mock CPU info object
    cpu_info = {
        'usage': [50.0] * os.cpu_count(),  # Assume 50% usage on all cores
        'system': 0.5,
        'user': 0.5
    }
    
    # Create the IPMI energy monitor
    monitor = IPMIEnergyMonitor(process_id, config)
    
    # Start monitoring
    monitor.start()
    
    try:
        # Run the compute-intensive function
        result = compute_intensive_function(1000)
        
        # Print results
        print(f"Matrix size: {result['matrix_size']}")
        print(f"Duration: {result['duration']:.2f} seconds")
        print(f"Eigenvalues mean: {result['eigenvalues_mean']:.6f}")
        print(f"Eigenvalues std: {result['eigenvalues_std']:.6f}")
        print()
    finally:
        # Stop monitoring
        monitor.stop()
        
        # Get energy data
        energy_data = monitor.get_energy_data()
        
        # Print energy data
        print("Energy Data:")
        print(f"Duration: {energy_data['duration']:.2f} seconds")
        print(f"System Energy: {energy_data['energy'].get('system', 'N/A')} Joules")
        print(f"Average Power: {energy_data['energy'].get('avg_power', 'N/A')} Watts")
        if 'min_power' in energy_data['energy']:
            print(f"Min Power: {energy_data['energy']['min_power']} Watts")
        if 'max_power' in energy_data['energy']:
            print(f"Max Power: {energy_data['energy']['max_power']} Watts")
        
        # Log energy data
        task = MockTask()
        monitor.log_energy_data(energy_data, task, cpu_info, 'compute_intensive_function')
    
    return result, energy_data

# Function to analyze energy data
def analyze_energy_data():
    """Analyze the energy data collected by the IPMI monitor."""
    # Create an energy extractor
    extractor = IPMIEnergyExtractor('energy_data')
    
    # Load energy data from the directory
    extractor.load_from_directory()
    
    # Extract energy metrics
    energy_df = extractor.extract_energy_metrics()
    
    # Print summary
    summary = extractor.get_energy_summary()
    print("\nEnergy Summary:")
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # Extract power readings
    power_df = extractor.extract_power_readings()
    
    # Plot power over time if data is available
    if not power_df.empty:
        plt.figure(figsize=(10, 6))
        
        # Group by job_key and call_id
        for (job_key, call_id), group in power_df.groupby(['job_key', 'call_id']):
            # Sort by timestamp
            group = group.sort_values('timestamp')
            
            # Calculate relative time
            if len(group) > 0:
                start_time = group['timestamp'].min()
                group['relative_time'] = group['timestamp'] - start_time
                
                # Plot power over time
                plt.plot(group['relative_time'], group['power'], 
                         label=f'Job {job_key}-{call_id}')
        
        plt.xlabel('Time (s)')
        plt.ylabel('Power (W)')
        plt.title('Power Consumption Over Time')
        plt.legend()
        plt.grid(True)
        plt.savefig('ipmi_power_over_time.png')
        plt.show()
    
    # Extract temperature readings if available
    temp_df = extractor.extract_temperature_readings()
    
    # Plot temperature over time if data is available
    if not temp_df.empty:
        plt.figure(figsize=(10, 6))
        
        # Get the first job_key and call_id
        first_job = temp_df.iloc[0]['job_key']
        first_call = temp_df.iloc[0]['call_id']
        
        # Filter for this job
        job_temp = temp_df[(temp_df['job_key'] == first_job) & 
                           (temp_df['call_id'] == first_call)]
        
        # Sort by timestamp
        job_temp = job_temp.sort_values('timestamp')
        
        # Calculate relative time
        if len(job_temp) > 0:
            start_time = job_temp['timestamp'].min()
            job_temp['relative_time'] = job_temp['timestamp'] - start_time
            
            # Plot temperature over time for each sensor
            for sensor in job_temp['sensor'].unique():
                sensor_data = job_temp[job_temp['sensor'] == sensor]
                plt.plot(sensor_data['relative_time'], 
                         sensor_data['temperature'], 
                         label=sensor)
        
        plt.xlabel('Time (s)')
        plt.ylabel('Temperature (°C)')
        plt.title(f'Temperature Over Time for Job {first_job}-{first_call}')
        plt.legend()
        plt.grid(True)
        plt.savefig('ipmi_temperature_over_time.png')
        plt.show()
    
    return energy_df, power_df, temp_df

if __name__ == "__main__":
    print("IPMI Energy Monitoring Example")
    print("==============================")
    
    # Ask the user which mode to run
    print("\nSelect a mode to run:")
    print("1. Run with Lithops (distributed)")
    print("2. Run locally (direct monitoring)")
    print("3. Analyze existing energy data")
    
    choice = input("Enter your choice (1-3): ")
    
    if choice == '1':
        print("\nRunning with Lithops...")
        results = run_with_lithops()
        print("\nAnalyzing energy data...")
        analyze_energy_data()
    elif choice == '2':
        print("\nRunning locally...")
        result, energy_data = run_locally()
        print("\nAnalyzing energy data...")
        analyze_energy_data()
    elif choice == '3':
        print("\nAnalyzing existing energy data...")
        analyze_energy_data()
    else:
        print("Invalid choice. Exiting.")
