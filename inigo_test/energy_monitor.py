from inigo_test.enery_windows_pywin32 import get_process_energy_metrics

# python -m inigo_test.energy_monitor
"""
Cannot access process with PID 1234                                                               
Energy consumption estimate: N/A Joules 

"""


if __name__ == "__main__":
    # Replace 1234 with the actual PID of the process you want to monitor
    pid = 1234  # Get this from Task Manager
    metrics = get_process_energy_metrics(pid, duration_seconds=30)
    print(f"Energy consumption estimate: {metrics.get('energy_joules', 'N/A')} Joules")