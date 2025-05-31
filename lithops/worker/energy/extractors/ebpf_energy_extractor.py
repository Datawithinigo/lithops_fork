import json
import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional

class EBPFEnergyExtractor:
    """Extract and analyze energy values from eBPF trace data."""
    
    def __init__(self, data_path: Optional[str] = None):
        """Initialize with an optional path to data files."""
        self.data_path = data_path
        self.traces = []
        
    def load_from_string(self, json_str: str) -> None:
        """Load eBPF trace data from a JSON string."""
        try:
            trace = json.loads(json_str)
            self.traces.append(trace)
            print(f"Successfully loaded trace for execution_id: {trace.get('execution_id')}")
        except json.JSONDecodeError:
            print("Error: Invalid JSON format")
            
    def load_from_file(self, file_path: str) -> None:
        """Load eBPF trace data from a JSON file."""
        try:
            with open(file_path, 'r') as f:
                trace = json.load(f)
                self.traces.append(trace)
                print(f"Successfully loaded trace from {file_path}")
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading file {file_path}: {str(e)}")
            
    def load_from_directory(self, directory: Optional[str] = None) -> None:
        """Load all JSON files from a directory."""
        dir_path = directory or self.data_path
        if not dir_path:
            print("Error: No directory specified")
            return
            
        json_files = glob.glob(os.path.join(dir_path, "*.json"))
        for file_path in json_files:
            self.load_from_file(file_path)
        print(f"Loaded {len(json_files)} trace files from {dir_path}")
            
    def extract_energy_metrics(self) -> pd.DataFrame:
        """Extract energy metrics from all loaded traces into a DataFrame."""
        energy_data = []
        
        for trace in self.traces:
            # Extract basic trace information
            trace_info = {
                'execution_id': trace.get('execution_id'),
                'job_key': trace.get('job_key'),
                'function_name': trace.get('function_name'),
                'timestamp': trace.get('timestamp'),
                'duration': trace.get('duration')
            }
            
            # Extract energy metrics
            energy = trace.get('energy', {})
            energy_metrics = {
                'pkg_energy': energy.get('pkg'),
                'cores_energy': energy.get('cores'),
                'core_percentage': energy.get('core_percentage'),
                'cpu_cycles': energy.get('cpu_cycles'),
                'energy_from_cycles': energy.get('energy_from_cycles')
            }
            
            # Combine data
            entry = {**trace_info, **energy_metrics}
            energy_data.append(entry)
            
        return pd.DataFrame(energy_data)
    
    def extract_all_metrics(self) -> pd.DataFrame:
        """Extract all metrics including CPU, BPF, syscall, and memory metrics."""
        all_data = []
        
        for trace in self.traces:
            # Extract basic trace information
            trace_info = {
                'execution_id': trace.get('execution_id'),
                'job_key': trace.get('job_key'),
                'function_name': trace.get('function_name'),
                'timestamp': trace.get('timestamp'),
                'duration': trace.get('duration')
            }
            
            # Extract energy metrics
            energy = trace.get('energy', {})
            energy_metrics = {
                'pkg_energy': energy.get('pkg'),
                'cores_energy': energy.get('cores'),
                'core_percentage': energy.get('core_percentage'),
                'cpu_cycles': energy.get('cpu_cycles'),
                'energy_from_cycles': energy.get('energy_from_cycles')
            }
            
            # Extract CPU performance metrics
            cpu_perf = trace.get('cpu_perf_metrics', {})
            cpu_metrics = {
                'instructions': cpu_perf.get('instructions'),
                'cycles': cpu_perf.get('cycles'),
                'cache_references': cpu_perf.get('cache_references'),
                'cache_misses': cpu_perf.get('cache_misses'),
                'task_clock': cpu_perf.get('task_clock'),
                'instructions_per_cycle': cpu_perf.get('instructions_per_cycle'),
                'cache_miss_rate': cpu_perf.get('cache_miss_rate'),
                'cpu_cycles_per_second': cpu_perf.get('cpu_cycles_per_second')
            }
            
            # Extract BPF program metrics
            bpf = trace.get('bpf_program_metrics', {})
            bpf_metrics = {
                'run_count': bpf.get('run_count'),
                'run_time_ns': bpf.get('run_time_ns'),
                'run_time_us': bpf.get('run_time_us')
            }
            
            # Combine all data
            entry = {**trace_info, **energy_metrics, **cpu_metrics, **bpf_metrics}
            all_data.append(entry)
            
        return pd.DataFrame(all_data)
    
    def calculate_energy_efficiency(self) -> pd.DataFrame:
        """Calculate energy efficiency metrics."""
        df = self.extract_all_metrics()
        
        # Calculate operations per joule (higher is more efficient)
        df['instructions_per_joule'] = df['instructions'] / df['pkg_energy']
        
        # Calculate energy per instruction (lower is more efficient)
        df['energy_per_instruction'] = df['pkg_energy'] / df['instructions']
        
        # Calculate energy per operation (another efficiency metric)
        df['energy_per_operation'] = df['pkg_energy'] / df['run_count']
        
        return df
    
    def visualize_energy_distribution(self) -> None:
        """Visualize the distribution of energy consumption."""
        energy_df = self.extract_energy_metrics()
        
        plt.figure(figsize=(12, 6))
        
        # Plot 1: Package vs Core Energy
        plt.subplot(1, 2, 1)
        plt.scatter(energy_df['pkg_energy'], energy_df['cores_energy'])
        plt.xlabel('Package Energy (J)')
        plt.ylabel('Core Energy (J)')
        plt.title('Package vs Core Energy')
        
        # Plot 2: Energy distribution
        plt.subplot(1, 2, 2)
        energy_df['pkg_energy'].hist(bins=20)
        plt.xlabel('Package Energy (J)')
        plt.ylabel('Frequency')
        plt.title('Distribution of Package Energy')
        
        plt.tight_layout()
        plt.show()
        
    def export_to_csv(self, filename: str = 'ebpf_energy_metrics.csv') -> None:
        """Export the extracted energy metrics to a CSV file."""
        df = self.extract_all_metrics()
        df.to_csv(filename, index=False)
        print(f"Exported data to {filename}")
        
    def get_energy_summary(self) -> Dict[str, Any]:
        """Get a summary of energy metrics."""
        df = self.extract_energy_metrics()
        
        summary = {
            'total_traces': len(df),
            'total_pkg_energy': df['pkg_energy'].sum(),
            'avg_pkg_energy': df['pkg_energy'].mean(),
            'max_pkg_energy': df['pkg_energy'].max(),
            'min_pkg_energy': df['pkg_energy'].min(),
            'energy_std_dev': df['pkg_energy'].std(),
            'total_duration': df['duration'].sum(),
            'avg_core_percentage': df['core_percentage'].mean()
        }
        
        return summary
