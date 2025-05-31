# IPMI Energy Monitor for Lithops

This document describes the IPMI (Intelligent Platform Management Interface) energy monitor for Lithops, which allows measuring server power consumption and energy usage through the BMC (Baseboard Management Controller).

## Overview

The IPMI Energy Monitor provides a system-level view of power consumption by communicating with the server's BMC through the IPMI protocol. This monitor is particularly useful for:

- Measuring total server power consumption during function execution
- Monitoring server temperatures, voltages, and fan speeds
- Collecting energy metrics from servers where RAPL (Running Average Power Limit) is not available
- Getting a more comprehensive view of system energy usage beyond just CPU energy

Unlike the eBPF and perf monitors that focus on CPU energy consumption, the IPMI monitor provides a holistic view of the entire server's power consumption, which can be valuable for understanding the total energy footprint of your workloads.

## Requirements

To use the IPMI Energy Monitor, you need:

1. **ipmitool**: The monitor uses the `ipmitool` command-line utility to communicate with the BMC.
   - Install on Ubuntu/Debian: `sudo apt-get install ipmitool`
   - Install on CentOS/RHEL: `sudo yum install ipmitool`

2. **Server with BMC**: The server must have a BMC that supports IPMI.

3. **Permissions**:
   - For local monitoring: Root privileges are typically required
   - For remote monitoring: IPMI credentials (username/password) for the remote server

## Configuration

The IPMI Energy Monitor can be configured with the following options:

```python
config = {
    'lithops': {
        'energy': True,
        'energy_strategy': 'ipmi'  # Use IPMI monitor
    },
    # IPMI-specific configuration
    'ipmi_host': 'localhost',      # Change to remote server IP if needed
    'ipmi_username': 'admin',      # IPMI username for remote server
    'ipmi_password': 'password',   # IPMI password for remote server
    'ipmi_interface': 'lanplus',   # IPMI interface type
    'ipmi_use_sudo': True,         # Whether to use sudo with ipmitool
    'energy_sampling_interval': 1.0 # Sampling interval in seconds
}
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `ipmi_host` | Hostname or IP address of the server with BMC | `localhost` |
| `ipmi_username` | Username for IPMI authentication | `None` |
| `ipmi_password` | Password for IPMI authentication | `None` |
| `ipmi_interface` | IPMI interface type | `lanplus` |
| `ipmi_use_sudo` | Whether to use sudo with ipmitool | `True` |
| `energy_sampling_interval` | Sampling interval in seconds | `1.0` |

## Usage

### Basic Usage with Lithops

```python
import lithops

# Configure Lithops to use the IPMI energy monitor
config = {
    'lithops': {
        'energy': True,
        'energy_strategy': 'ipmi'
    },
    'ipmi_host': 'localhost'
}

# Create a FunctionExecutor with the configuration
fexec = lithops.FunctionExecutor(config=config)

# Execute your function
def my_function(x):
    return x * 2

futures = fexec.map(my_function, range(10))
results = fexec.get_result()

# Close the executor
fexec.close()
```

### Direct Usage

You can also use the IPMI Energy Monitor directly:

```python
import os
from lithops.worker.energy.monitors import IPMIEnergyMonitor

# Get the current process ID
process_id = os.getpid()

# Configure the IPMI energy monitor
config = {
    'ipmi_host': 'localhost',
    'ipmi_username': None,
    'ipmi_password': None,
    'energy_sampling_interval': 0.5
}

# Create the IPMI energy monitor
monitor = IPMIEnergyMonitor(process_id, config)

# Start monitoring
monitor.start()

try:
    # Run your code here
    result = compute_intensive_function()
finally:
    # Stop monitoring
    monitor.stop()
    
    # Get energy data
    energy_data = monitor.get_energy_data()
    
    # Print energy data
    print(f"System Energy: {energy_data['energy'].get('system')} Joules")
    print(f"Average Power: {energy_data['energy'].get('avg_power')} Watts")
```

### Analyzing Energy Data

The IPMI Energy Monitor stores energy data in JSON files in the `energy_data` directory. You can analyze this data using the `IPMIEnergyExtractor`:

```python
from lithops.worker.energy.extractors import IPMIEnergyExtractor
import matplotlib.pyplot as plt

# Create an energy extractor
extractor = IPMIEnergyExtractor('energy_data')

# Load energy data from the directory
extractor.load_from_directory()

# Extract energy metrics
energy_df = extractor.extract_energy_metrics()

# Print summary
summary = extractor.get_energy_summary()
print("Energy Summary:")
for key, value in summary.items():
    print(f"{key}: {value}")

# Extract power readings
power_df = extractor.extract_power_readings()

# Plot power over time
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
    plt.show()
```

## Example

See the `ipmi_energy_example.py` script for a complete example of using the IPMI Energy Monitor.

## Collected Metrics

The IPMI Energy Monitor collects the following metrics:

- **Power Consumption**: Instantaneous power readings in Watts
- **Energy Consumption**: Total energy consumption in Joules
- **Voltage Readings**: Voltage readings from various sensors
- **Current Readings**: Current readings from various sensors
- **Temperature Readings**: Temperature readings from various sensors
- **Fan Speeds**: Fan speed readings in RPM

## Limitations

- **Accuracy**: IPMI power readings may not be as accurate or fine-grained as RAPL readings
- **Sampling Rate**: The sampling rate is typically lower than with eBPF or perf monitors
- **Permissions**: Root privileges are typically required for local monitoring
- **Availability**: Not all servers have BMCs that support power monitoring through IPMI

## Troubleshooting

### Common Issues

1. **ipmitool not found**:
   - Make sure ipmitool is installed: `sudo apt-get install ipmitool`

2. **Permission denied**:
   - Run with sudo or as root
   - Check that the user has permission to use ipmitool

3. **No power readings**:
   - Verify that the server's BMC supports power monitoring
   - Try running `sudo ipmitool dcmi power reading` manually to check

4. **Connection failed for remote server**:
   - Check the IP address, username, and password
   - Verify that the remote server's BMC is accessible from your network
   - Try running `ipmitool -I lanplus -H <ip> -U <username> -P <password> dcmi power reading`

### Placeholder Data

If the IPMI monitor cannot connect to the BMC or retrieve power readings, it will generate placeholder data to ensure that JSON files are still created. This allows your code to continue running without errors, but the energy data will not be accurate.

To check if placeholder data was used, look for the `placeholder: true` field in the energy data or check the logs for warnings about generating placeholder data.

## Combining with Other Monitors

The IPMI Energy Monitor can be used in combination with other monitors like eBPF and perf to get a more comprehensive view of energy consumption:

```python
config = {
    'lithops': {
        'energy': True,
        'energy_strategy': ['ipmi', 'ebpf', 'perf']  # Use multiple monitors
    }
}
```

This will create a composite monitor that collects data from all three sources, allowing you to compare CPU-specific energy consumption with system-level power consumption.

## Further Reading

- [IPMI Specification](https://www.intel.com/content/www/us/en/products/docs/servers/ipmi/ipmi-second-gen-interface-spec-v2-rev1-1.html)
- [ipmitool Documentation](https://github.com/ipmitool/ipmitool)
- [Lithops Energy Monitoring Documentation](https://lithops-cloud.github.io/docs/source/energy_monitoring.html)
