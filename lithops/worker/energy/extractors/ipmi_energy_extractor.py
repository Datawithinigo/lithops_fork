import json
import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional

class IPMIEnergyExtractor:
    """Extract and analyze energy values from IPMI monitoring data."""
    
    def __init__(self, data_path: Optional[str] = None):
        """Initialize with an optional path to data files."""
        self.data_path = data_path
        self.traces = []
        
    def load_from_string(self, json_str: str) -> None:
        """Load IPMI trace data from a JSON string."""
        try:
            trace = json.loads(json_str)
            self.traces.append(trace)
            print(f"Successfully loaded trace for execution_id: {trace.get('energy_consumption', {}).get('job_key')}-{trace.get('energy_consumption', {}).get('call_id')}")
        except json.JSONDecodeError:
            print("Error: Invalid JSON format")
            
    def load_from_file(self, file_path: str) -> None:
        """Load IPMI trace data from a JSON file."""
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
            
        json_files = glob.glob(os.path.join(dir_path, "*_ipmi.json"))
        for file_path in json_files:
            self.load_from_file(file_path)
        print(f"Loaded {len(json_files)} trace files from {dir_path}")
            
    def extract_energy_metrics(self) -> pd.DataFrame:
        """Extract energy metrics from all loaded traces into a DataFrame."""
        energy_data = []
        
        for trace in self.traces:
            # Extract basic trace information from energy_consumption
            energy_consumption = trace.get('energy_consumption', {})
            trace_info = {
                'job_key': energy_consumption.get('job_key'),
                'call_id': energy_consumption.get('call_id'),
                'function_name': energy_consumption.get('function_name'),
                'timestamp': energy_consumption.get('timestamp'),
                'duration': energy_consumption.get('duration')
            }
            
            # Extract energy metrics
            energy_metrics = {
                'system_energy': energy_consumption.get('energy_system'),
                'avg_power': energy_consumption.get('avg_power'),
                'min_power': energy_consumption.get('min_power'),
                'max_power': energy_consumption.get('max_power'),
                'power_std_dev': energy_consumption.get('power_std_dev'),
                'energy_efficiency': energy_consumption.get('energy_efficiency'),
                'avg_cpu_usage': energy_consumption.get('avg_cpu_usage'),
                'energy_per_cpu': energy_consumption.get('energy_per_cpu')
            }
            
            # Add temperature data if available
            if 'avg_cpu_temp' in energy_consumption:
                energy_metrics['avg_cpu_temp'] = energy_consumption.get('avg_cpu_temp')
            if 'avg_system_temp' in energy_consumption:
                energy_metrics['avg_system_temp'] = energy_consumption.get('avg_system_temp')
            
            # Combine data
            entry = {**trace_info, **energy_metrics}
            energy_data.append(entry)
            
        return pd.DataFrame(energy_data)
    
    def extract_power_readings(self) -> pd.DataFrame:
        """Extract power readings from all loaded traces into a DataFrame."""
        power_data = []
        
        for trace in self.traces:
            # Extract basic trace information from energy_consumption
            energy_consumption = trace.get('energy_consumption', {})
            job_key = energy_consumption.get('job_key')
            call_id = energy_consumption.get('call_id')
            function_name = energy_consumption.get('function_name')
            
            # Extract power readings
            power_readings = trace.get('power_readings', [])
            
            for reading in power_readings:
                entry = {
                    'job_key': job_key,
                    'call_id': call_id,
                    'function_name': function_name,
                    'timestamp': reading.get('timestamp'),
                    'power': reading.get('power')
                }
                power_data.append(entry)
            
        return pd.DataFrame(power_data)
    
    def extract_temperature_readings(self) -> pd.DataFrame:
        """Extract temperature readings from all loaded traces into a DataFrame."""
        temp_data = []
        
        for trace in self.traces:
            # Extract basic trace information from energy_consumption
            energy_consumption = trace.get('energy_consumption', {})
            job_key = energy_consumption.get('job_key')
            call_id = energy_consumption.get('call_id')
            function_name = energy_consumption.get('function_name')
            
            # Extract temperature readings
            temp_readings = trace.get('temperature_readings', [])
            
            for reading in temp_readings:
                entry = {
                    'job_key': job_key,
                    'call_id': call_id,
                    'function_name': function_name,
                    'timestamp': reading.get('timestamp'),
                    'sensor': reading.get('sensor'),
                    'temperature': reading.get('value')
                }
                temp_data.append(entry)
            
        return pd.DataFrame(temp_data)
    
    def extract_voltage_readings(self) -> pd.DataFrame:
        """Extract voltage readings from all loaded traces into a DataFrame."""
        voltage_data = []
        
        for trace in self.traces:
            # Extract basic trace information from energy_consumption
            energy_consumption = trace.get('energy_consumption', {})
            job_key = energy_consumption.get('job_key')
            call_id = energy_consumption.get('call_id')
            function_name = energy_consumption.get('function_name')
            
            # Extract voltage readings
            voltage_readings = trace.get('voltage_readings', [])
            
            for reading in voltage_readings:
                entry = {
                    'job_key': job_key,
                    'call_id': call_id,
                    'function_name': function_name,
                    'timestamp': reading.get('timestamp'),
                    'sensor': reading.get('sensor'),
                    'voltage': reading.get('value')
                }
                voltage_data.append(entry)
            
        return pd.DataFrame(voltage_data)
    
    def extract_current_readings(self) -> pd.DataFrame:
        """Extract current readings from all loaded traces into a DataFrame."""
        current_data = []
        
        for trace in self.traces:
            # Extract basic trace information from energy_consumption
            energy_consumption = trace.get('energy_consumption', {})
            job_key = energy_consumption.get('job_key')
            call_id = energy_consumption.get('call_id')
            function_name = energy_consumption.get('function_name')
            
            # Extract current readings
            current_readings = trace.get('current_readings', [])
            
            for reading in current_readings:
                entry = {
                    'job_key': job_key,
                    'call_id': call_id,
                    'function_name': function_name,
                    'timestamp': reading.get('timestamp'),
                    'sensor': reading.get('sensor'),
                    'current': reading.get('value')
                }
                current_data.append(entry)
            
        return pd.DataFrame(current_data)
    
    def extract_fan_readings(self) -> pd.DataFrame:
        """Extract fan speed readings from all loaded traces into a DataFrame."""
        fan_data = []
        
        for trace in self.traces:
            # Extract basic trace information from energy_consumption
            energy_consumption = trace.get('energy_consumption', {})
            job_key = energy_consumption.get('job_key')
            call_id = energy_consumption.get('call_id')
            function_name = energy_consumption.get('function_name')
            
            # Extract fan readings
            fan_readings = trace.get('fan_readings', [])
            
            for reading in fan_readings:
                entry = {
                    'job_key': job_key,
                    'call_id': call_id,
                    'function_name': function_name,
                    'timestamp': reading.get('timestamp'),
                    'sensor': reading.get('sensor'),
                    'fan_speed': reading.get('value')
                }
                fan_data.append(entry)
            
        return pd.DataFrame(fan_data)
    
    def extract_all_metrics(self) -> Dict[str, pd.DataFrame]:
        """Extract all metrics into separate DataFrames."""
        return {
            'energy': self.extract_energy_metrics(),
            'power': self.extract_power_readings(),
            'temperature': self.extract_temperature_readings(),
            'voltage': self.extract_voltage_readings(),
            'current': self.extract_current_readings(),
            'fan': self.extract_fan_readings()
        }
    
    def calculate_energy_efficiency(self) -> pd.DataFrame:
        """Calculate energy efficiency metrics."""
        df = self.extract_energy_metrics()
        
        # Calculate operations per joule (higher is more efficient)
        # This requires some measure of operations, which we don't have directly
        # Instead, we can use CPU usage as a proxy for operations
        if 'avg_cpu_usage' in df.columns and 'system_energy' in df.columns:
            # Calculate CPU-seconds per joule
            df['cpu_seconds_per_joule'] = (df['avg_cpu_usage'] * df['duration']) / df['system_energy']
            
            # Calculate energy per CPU-second
            df['energy_per_cpu_second'] = df['system_energy'] / (df['avg_cpu_usage'] * df['duration'])
        
        return df
    
    def visualize_power_distribution(self) -> None:
        """Visualize the distribution of power consumption."""
        energy_df = self.extract_energy_metrics()
        power_df = self.extract_power_readings()
        
        plt.figure(figsize=(15, 10))
        
        # Plot 1: Average Power Distribution
        plt.subplot(2, 2, 1)
        energy_df['avg_power'].hist(bins=20)
        plt.xlabel('Average Power (W)')
        plt.ylabel('Frequency')
        plt.title('Distribution of Average Power')
        
        # Plot 2: Min vs Max Power
        plt.subplot(2, 2, 2)
        plt.scatter(energy_df['min_power'], energy_df['max_power'])
        plt.xlabel('Min Power (W)')
        plt.ylabel('Max Power (W)')
        plt.title('Min vs Max Power')
        
        # Plot 3: Power over Time (for a single trace if available)
        if not power_df.empty and len(power_df) > 1:
            # Get the first job_key and call_id
            first_job = power_df.iloc[0]['job_key']
            first_call = power_df.iloc[0]['call_id']
            
            # Filter for this job
            job_power = power_df[(power_df['job_key'] == first_job) & (power_df['call_id'] == first_call)]
            
            # Sort by timestamp
            job_power = job_power.sort_values('timestamp')
            
            # Calculate relative time
            if len(job_power) > 0:
                start_time = job_power['timestamp'].min()
                job_power['relative_time'] = job_power['timestamp'] - start_time
                
                plt.subplot(2, 2, 3)
                plt.plot(job_power['relative_time'], job_power['power'])
                plt.xlabel('Time (s)')
                plt.ylabel('Power (W)')
                plt.title(f'Power over Time for Job {first_job}-{first_call}')
        
        # Plot 4: Energy vs Duration
        plt.subplot(2, 2, 4)
        plt.scatter(energy_df['duration'], energy_df['system_energy'])
        plt.xlabel('Duration (s)')
        plt.ylabel('Energy (J)')
        plt.title('Energy vs Duration')
        
        plt.tight_layout()
        plt.show()
        
    def visualize_temperature_data(self) -> None:
        """Visualize temperature data."""
        temp_df = self.extract_temperature_readings()
        
        if temp_df.empty:
            print("No temperature data available")
            return
            
        plt.figure(figsize=(15, 10))
        
        # Plot 1: Temperature Distribution by Sensor
        plt.subplot(2, 1, 1)
        sensors = temp_df['sensor'].unique()
        for sensor in sensors:
            sensor_data = temp_df[temp_df['sensor'] == sensor]
            sensor_data['temperature'].hist(alpha=0.5, label=sensor)
        plt.xlabel('Temperature (°C)')
        plt.ylabel('Frequency')
        plt.title('Temperature Distribution by Sensor')
        plt.legend()
        
        # Plot 2: Temperature over Time (for a single trace if available)
        if len(temp_df) > 1:
            # Get the first job_key and call_id
            first_job = temp_df.iloc[0]['job_key']
            first_call = temp_df.iloc[0]['call_id']
            
            # Filter for this job
            job_temp = temp_df[(temp_df['job_key'] == first_job) & (temp_df['call_id'] == first_call)]
            
            # Sort by timestamp
            job_temp = job_temp.sort_values('timestamp')
            
            # Calculate relative time
            if len(job_temp) > 0:
                start_time = job_temp['timestamp'].min()
                job_temp['relative_time'] = job_temp['timestamp'] - start_time
                
                plt.subplot(2, 1, 2)
                for sensor in job_temp['sensor'].unique():
                    sensor_data = job_temp[job_temp['sensor'] == sensor]
                    plt.plot(sensor_data['relative_time'], sensor_data['temperature'], label=sensor)
                plt.xlabel('Time (s)')
                plt.ylabel('Temperature (°C)')
                plt.title(f'Temperature over Time for Job {first_job}-{first_call}')
                plt.legend()
        
        plt.tight_layout()
        plt.show()
        
    def export_to_csv(self, directory: str = '.') -> None:
        """Export the extracted metrics to CSV files."""
        metrics = self.extract_all_metrics()
        
        for name, df in metrics.items():
            if not df.empty:
                filename = os.path.join(directory, f'ipmi_{name}_metrics.csv')
                df.to_csv(filename, index=False)
                print(f"Exported {name} data to {filename}")
        
    def get_energy_summary(self) -> Dict[str, Any]:
        """Get a summary of energy metrics."""
        df = self.extract_energy_metrics()
        
        if df.empty:
            return {"error": "No data available"}
        
        summary = {
            'total_traces': len(df),
            'total_system_energy': df['system_energy'].sum(),
            'avg_system_energy': df['system_energy'].mean(),
            'max_system_energy': df['system_energy'].max(),
            'min_system_energy': df['system_energy'].min(),
            'energy_std_dev': df['system_energy'].std(),
            'avg_power': df['avg_power'].mean(),
            'max_power_recorded': df['max_power'].max(),
            'min_power_recorded': df['min_power'].min(),
            'total_duration': df['duration'].sum(),
            'avg_duration': df['duration'].mean()
        }
        
        # Add temperature data if available
        if 'avg_cpu_temp' in df.columns:
            summary['avg_cpu_temp'] = df['avg_cpu_temp'].mean()
        if 'avg_system_temp' in df.columns:
            summary['avg_system_temp'] = df['avg_system_temp'].mean()
        
        return summary
    
    def compare_with_other_sources(self, other_extractors: Dict[str, Any]) -> pd.DataFrame:
        """
        Compare IPMI energy data with other energy sources.
        
        Args:
            other_extractors: Dictionary of other extractors, e.g., {'ebpf': ebpf_extractor}
            
        Returns:
            DataFrame with comparison data
        """
        # Get IPMI energy data
        ipmi_df = self.extract_energy_metrics()
        
        # Create a list to store all dataframes
        dfs = [ipmi_df.rename(columns={'system_energy': 'ipmi_energy'})]
        
        # Extract data from other sources
        for source, extractor in other_extractors.items():
            try:
                other_df = extractor.extract_energy_metrics()
                # Rename the energy column to indicate the source
                if 'pkg_energy' in other_df.columns:
                    other_df = other_df.rename(columns={'pkg_energy': f'{source}_energy'})
                elif 'system_energy' in other_df.columns:
                    other_df = other_df.rename(columns={'system_energy': f'{source}_energy'})
                
                # Select only the columns we need for merging
                other_df = other_df[['job_key', 'call_id', f'{source}_energy', 'duration']]
                
                # Add to the list
                dfs.append(other_df)
            except Exception as e:
                print(f"Error extracting data from {source}: {e}")
        
        # Merge all dataframes on job_key and call_id
        if len(dfs) > 1:
            comparison_df = dfs[0]
            for df in dfs[1:]:
                comparison_df = pd.merge(comparison_df, df, on=['job_key', 'call_id'], suffixes=('', f'_{df.columns[2].split("_")[0]}'))
            
            return comparison_df
        else:
            return ipmi_df
    
    def visualize_energy_comparison(self, other_extractors: Dict[str, Any]) -> None:
        """
        Visualize comparison between IPMI energy data and other sources.
        
        Args:
            other_extractors: Dictionary of other extractors, e.g., {'ebpf': ebpf_extractor}
        """
        comparison_df = self.compare_with_other_sources(other_extractors)
        
        # Get the energy columns
        energy_cols = [col for col in comparison_df.columns if col.endswith('_energy')]
        
        if len(energy_cols) < 2:
            print("Not enough energy sources to compare")
            return
        
        plt.figure(figsize=(15, 10))
        
        # Plot 1: Energy by Source
        plt.subplot(2, 2, 1)
        comparison_df[energy_cols].mean().plot(kind='bar')
        plt.ylabel('Energy (J)')
        plt.title('Average Energy by Source')
        
        # Plot 2: Energy Correlation
        plt.subplot(2, 2, 2)
        for i in range(len(energy_cols)):
            for j in range(i+1, len(energy_cols)):
                plt.scatter(comparison_df[energy_cols[i]], comparison_df[energy_cols[j]], 
                           label=f'{energy_cols[i]} vs {energy_cols[j]}')
        plt.xlabel('Energy (J)')
        plt.ylabel('Energy (J)')
        plt.title('Energy Correlation Between Sources')
        plt.legend()
        
        # Plot 3: Energy by Function
        plt.subplot(2, 2, 3)
        if 'function_name' in comparison_df.columns:
            # Group by function name and calculate mean energy
            func_energy = comparison_df.groupby('function_name')[energy_cols].mean()
            func_energy.plot(kind='bar')
            plt.ylabel('Energy (J)')
            plt.title('Average Energy by Function')
            plt.xticks(rotation=45)
        
        # Plot 4: Energy vs Duration
        plt.subplot(2, 2, 4)
        for col in energy_cols:
            plt.scatter(comparison_df['duration'], comparison_df[col], label=col)
        plt.xlabel('Duration (s)')
        plt.ylabel('Energy (J)')
        plt.title('Energy vs Duration')
        plt.legend()
        
        plt.tight_layout()
        plt.show()
