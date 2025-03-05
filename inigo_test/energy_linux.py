import time
import subprocess

def read_energy():
    """
    Reads the current energy consumption value in microjoules
    from the RAPL interface.
    """
    with open('/sys/class/powercap/intel-rapl:0/energy_uj', 'r') as f:
        return int(f.read().strip())

def get_max_energy_range():
    """
    Reads the maximum energy range before the counter wraps.
    """
    with open('/sys/class/powercap/intel-rapl:0/max_energy_range_uj', 'r') as f:
        return int(f.read().strip())

def measure_process_energy(command):
    """
    Measures the energy consumed while running the specified command.
    
    Args:
        command (str): The shell command to execute.
    
    Returns:
        tuple: (energy_consumed in Joules, elapsed time in seconds, average power in Watts)
    """
    # Read starting energy value
    start_energy = read_energy()
    start_time = time.time()
    
    # Run the target process (blocking call)
    subprocess.run(command, shell=True)
    
    # Read ending energy value
    end_time = time.time()
    end_energy = read_energy()
    
    # Calculate the energy difference
    delta_energy = end_energy - start_energy
    # Handle counter wrap-around if the counter resets
    if delta_energy < 0:
        max_energy = get_max_energy_range()
        delta_energy += max_energy
    
    elapsed_time = end_time - start_time
    
    # Convert microjoules to joules
    energy_joules = delta_energy / 1e6
    # Calculate average power (Joules per second = Watts)
    average_power = energy_joules / elapsed_time if elapsed_time > 0 else 0
    
    return energy_joules, elapsed_time, average_power

if __name__ == '__main__':
    # Replace 'ls -l' with the command you want to measure.
    command = "ls -l"
    
    energy, elapsed, power = measure_process_energy(command)
    print(f"Energy Consumed: {energy:.6f} Joules")
    print(f"Elapsed Time  : {elapsed:.6f} seconds")
    print(f"Average Power : {power:.6f} Watts")
