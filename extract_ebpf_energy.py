#!/usr/bin/env python3
"""
Script to extract and analyze energy values from eBPF trace data.
"""

import os
import sys
import argparse
from lithops.worker.energy.extractors import EBPFEnergyExtractor

def main():
    """Main function to extract and analyze eBPF energy data."""
    parser = argparse.ArgumentParser(description='Extract and analyze eBPF energy data')
    parser.add_argument('--data-dir', type=str, default='energy_data',
                        help='Directory containing eBPF JSON files (default: energy_data)')
    parser.add_argument('--output', type=str, default='ebpf_energy_metrics.csv',
                        help='Output CSV file (default: ebpf_energy_metrics.csv)')
    parser.add_argument('--visualize', action='store_true',
                        help='Visualize energy distribution')
    parser.add_argument('--file', type=str, help='Process a single eBPF JSON file')
    args = parser.parse_args()
    
    # Initialize the extractor
    extractor = EBPFEnergyExtractor(args.data_dir)
    
    # Load data
    if args.file:
        if os.path.exists(args.file):
            extractor.load_from_file(args.file)
        else:
            print(f"Error: File {args.file} not found")
            return 1
    else:
        if os.path.exists(args.data_dir):
            # Find all eBPF JSON files
            ebpf_files = [os.path.join(args.data_dir, f) for f in os.listdir(args.data_dir) 
                         if f.endswith('_ebpf.json')]
            
            if not ebpf_files:
                print(f"No eBPF JSON files found in {args.data_dir}")
                return 1
                
            print(f"Found {len(ebpf_files)} eBPF JSON files")
            
            # Load each file
            for file_path in ebpf_files:
                extractor.load_from_file(file_path)
        else:
            print(f"Error: Directory {args.data_dir} not found")
            return 1
    
    # Extract energy metrics
    energy_df = extractor.extract_energy_metrics()
    print("\nExtracted Energy Metrics:")
    print(energy_df)
    
    # Extract all metrics
    all_metrics_df = extractor.extract_all_metrics()
    print("\nExtracted All Metrics (first few rows):")
    print(all_metrics_df.head())
    
    # Calculate energy efficiency
    efficiency_df = extractor.calculate_energy_efficiency()
    print("\nEnergy Efficiency Metrics (first few rows):")
    print(efficiency_df[['execution_id', 'pkg_energy', 'instructions', 
                         'instructions_per_joule', 'energy_per_instruction']].head())
    
    # Get energy summary
    summary = extractor.get_energy_summary()
    print("\nEnergy Summary:")
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # Export to CSV
    extractor.export_to_csv(args.output)
    
    # Visualize energy distribution
    if args.visualize:
        extractor.visualize_energy_distribution()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
