import win32pdh # pip install pywin32
import win32process
import win32api
import time
import os
import psutil

def get_process_energy_metrics(process_id, duration_seconds=10, sample_interval=1):
    """
    Monitor energy consumption of a specific process using Windows Performance Counters.
    
    Args:
        process_id (int): The PID of the process to monitor
        duration_seconds (int): How long to monitor in seconds
        sample_interval (int): Interval between samples in seconds
        
    Returns:
        dict: Energy metrics for the process
    """
    # Get process name for better counter path specification
    try:
        process = psutil.Process(process_id)
        process_name = process.name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        print(f"Cannot access process with PID {process_id}")
        return {}
    
    # Set up performance counters
    counters = {
        'processor_time': f'\\Process({process_name})\\% Processor Time',
        'power_usage': f'\\Processor Information(_Total)\\% Processor Utility'
    }
    
    # Try to add power consumption counter (not available on all systems)
    try:
        # This counter path might vary depending on Windows version
        counters['energy'] = f'\\Processor Information(_Total)\\Processor Power'
    except:
        print("Power consumption counter not available")
    
    # Initialize counters
    query = win32pdh.OpenQuery()
    counter_handles = {}
    
    for counter_name, counter_path in counters.items():
        try:
            counter_handles[counter_name] = win32pdh.AddCounter(query, counter_path)
        except Exception as e:
            print(f"Failed to add counter {counter_path}: {e}")
    
    # Collect data
    samples = []
    print(f"Monitoring process {process_name} (PID: {process_id}) for {duration_seconds} seconds...")
    
    # First collection to establish baseline
    win32pdh.CollectQueryData(query)
    
    for _ in range(duration_seconds // sample_interval):
        time.sleep(sample_interval)
        win32pdh.CollectQueryData(query)
        
        sample = {}
        for counter_name, handle in counter_handles.items():
            try:
                type, val = win32pdh.GetFormattedCounterValue(handle, win32pdh.PDH_FMT_DOUBLE)
                sample[counter_name] = val
            except Exception as e:
                sample[counter_name] = None
                print(f"Error reading {counter_name}: {e}")
        
        # Get memory info using psutil
        try:
            mem_info = process.memory_info()
            sample['memory_rss'] = mem_info.rss / (1024 * 1024)  # Convert to MB
        except:
            sample['memory_rss'] = None
        
        samples.append(sample)
        print(f"Sample {len(samples)}: CPU: {sample.get('processor_time', 'N/A')}%, "
              f"Power: {sample.get('energy', 'N/A')} W, "
              f"Memory: {sample.get('memory_rss', 'N/A')} MB")
    
    # Close query
    win32pdh.CloseQuery(query)
    
    # Calculate energy consumption estimate
    # Note: This is an approximation based on CPU usage and system power metrics
    energy_samples = [s.get('energy') for s in samples if s.get('energy') is not None]
    cpu_samples = [s.get('processor_time') for s in samples if s.get('processor_time') is not None]
    
    if energy_samples and cpu_samples:
        # Calculate average power usage
        avg_power = sum(energy_samples) / len(energy_samples)
        # Calculate process contribution based on CPU utilization percentage
        avg_cpu_percent = sum(cpu_samples) / len(cpu_samples)
        # Estimate process energy consumption (W)
        estimated_process_power = avg_power * (avg_cpu_percent / 100.0)
        
        # Calculate total energy (Watt-seconds or Joules)
        energy_joules = estimated_process_power * duration_seconds
    else:
        estimated_process_power = None
        energy_joules = None
    
    return {
        'samples': samples,
        'avg_cpu_percent': sum(cpu_samples) / len(cpu_samples) if cpu_samples else None,
        'avg_power_watts': avg_power if energy_samples else None,
        'estimated_process_power_watts': estimated_process_power,
        'energy_joules': energy_joules,
        'monitoring_duration_seconds': duration_seconds
    }

def monitor_energy_for_command(command, duration_seconds=30):
    """
    Run a command and monitor its energy consumption.
    
    Args:
        command (str): Command to execute
        duration_seconds (int): How long to monitor
    
    Returns:
        dict: Energy metrics
    """
    # Start the process
    print(f"Starting process: {command}")
    process = psutil.Popen(command, shell=True)
    pid = process.pid
    
    # Monitor energy consumption
    metrics = get_process_energy_metrics(pid, duration_seconds)
    
    # Terminate the process if it's still running
    if process.poll() is None:
        process.terminate()
    
    return metrics

# Example usage
if __name__ == "__main__":
    # Option 1: Monitor an existing process by PID
    pid = 1234  # Replace with actual PID
    metrics = get_process_energy_metrics(pid, duration_seconds=60)
    print(f"Energy consumption estimate: {metrics.get('energy_joules', 'N/A')} Joules")
    
    # Option 2: Run and monitor a command
    command_metrics = monitor_energy_for_command("python -c 'import time; [print(i) for i in range(10000)]'", 20)
    print(f"Command energy consumption: {command_metrics.get('energy_joules', 'N/A')} Joules")