#!/usr/bin/env python3

import lithops

def test_alternative_energy_methods():
    """Test alternative methods to get energy data without perf"""
    import subprocess
    import os
    import glob
    
    # Display available methods table
    print("============================================================")
    print("AVAILABLE METHODS")
    print("============================================================")
    print("✓ direct_rapl_access")
    print("✓ amd_energy_access")
    print("✓ perf_without_sudo")
    print("✓ alternative_perf_events")
    print("✓ msr_access")
    print("============================================================")
    print()
    
    print("=== TESTING ALTERNATIVE ENERGY METHODS ===")
    
    # Dictionary to store test results
    results = {
        'direct_rapl_access': False,
        'amd_energy_access': False,
        'perf_without_sudo': False,
        'alternative_perf_events': False,
        'msr_access': False
    }
    
    # Method 1: Direct RAPL access
    print("\n1. Testing direct RAPL access...")
    rapl_paths = [
        '/sys/class/powercap/intel-rapl:0/energy_uj',
        '/sys/class/powercap/intel-rapl:0/package-0/energy_uj',
        '/sys/devices/virtual/powercap/intel-rapl/intel-rapl:0/energy_uj',
        '/sys/devices/virtual/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:0/energy_uj'
    ]
    
    for path in rapl_paths:
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    value = f.read().strip()
                print(f"✅ Found RAPL at {path}: {value} microjoules")
                results['direct_rapl_access'] = True
                break
        except Exception as e:
            print(f"❌ Cannot read {path}: {e}")
    
    # Method 2: Check for AMD energy files
    print("\n2. Testing AMD energy access...")
    amd_paths = [
        '/sys/class/hwmon/hwmon*/energy*',
        '/sys/class/hwmon/hwmon*/power*',
        '/sys/devices/pci*/*/hwmon/hwmon*/energy*'
    ]
    
    for pattern in amd_paths:
        try:
            files = glob.glob(pattern)
            for file in files:
                try:
                    with open(file, 'r') as f:
                        value = f.read().strip()
                    print(f"✅ Found AMD energy at {file}: {value}")
                    results['amd_energy_access'] = True
                    break
                except Exception as e:
                    print(f"❌ Cannot read {file}: {e}")
            if results['amd_energy_access']:
                break
        except Exception as e:
            print(f"❌ Error with pattern {pattern}: {e}")
    
    # Method 3: Try perf without sudo
    print("\n3. Testing perf without sudo...")
    try:
        result = subprocess.run([
            'perf', 'stat', '-e', 'power/energy-pkg/', '-a', 'sleep', '0.1'
        ], capture_output=True, text=True, timeout=5)
        
        print(f"Perf without sudo return code: {result.returncode}")
        if result.returncode == 0 and "Joules" in result.stderr:
            print("✅ SUCCESS: Perf works without sudo!")
            results['perf_without_sudo'] = True
        else:
            print(f"❌ Perf without sudo failed: {result.stderr[:200]}")
    except Exception as e:
        print(f"❌ Error with perf without sudo: {e}")
    
    # Method 4: Try alternative perf events
    print("\n4. Testing alternative perf events...")
    alt_events = [
        'cpu-cycles',
        'instructions', 
        'cache-references',
        'cache-misses',
        'branches',
        'branch-misses'
    ]
    
    for event in alt_events:
        try:
            result = subprocess.run([
                'perf', 'stat', '-e', event, '-a', 'sleep', '0.1'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                print(f"✅ Event {event} works without sudo")
                results['alternative_perf_events'] = True
                break
        except Exception as e:
            print(f"❌ Event {event} failed: {e}")
    
    # Method 5: Check MSR access
    print("\n5. Testing MSR access...")
    msr_files = [
        '/dev/cpu/0/msr',
        '/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq'
    ]
    
    for msr_file in msr_files:
        try:
            if os.path.exists(msr_file):
                with open(msr_file, 'r') as f:
                    value = f.read().strip()
                print(f"✅ MSR access works: {msr_file}")
                results['msr_access'] = True
                break
        except Exception as e:
            print(f"❌ Cannot access {msr_file}: {e}")
    
    # Display final results table
    print("\n" + "="*60)
    print("FINAL RESULTS - AVAILABLE METHODS IN THIS BACKEND")
    print("="*60)
    for method, available in results.items():
        status = "✓" if available else "✗"
        print(f"{status} {method}")
    print("="*60)
    
    # Return summary for lithops
    available_methods = [method for method, available in results.items() if available]
    if available_methods:
        return f"SUCCESS: Available methods: {', '.join(available_methods)}"
    else:
        return "NO_ALTERNATIVES"

def display_results_table(result_string):
    """Parse the result string and display a formatted table"""
    print("\n" + "="*60)
    print("AVAILABLE METHODS IN THIS BACKEND")
    print("="*60)
    
    # All possible methods
    all_methods = [
        'direct_rapl_access',
        'amd_energy_access', 
        'perf_without_sudo',
        'alternative_perf_events',
        'msr_access'
    ]
    
    # Parse available methods from result
    available_methods = []
    if result_string.startswith("SUCCESS: Available methods:"):
        methods_part = result_string.split("SUCCESS: Available methods: ")[1]
        available_methods = [method.strip() for method in methods_part.split(",")]
    
    # Display table
    for method in all_methods:
        status = "✓" if method in available_methods else "✗"
        print(f"{status} {method}")
    
    print("="*60)

if __name__ == "__main__":
    fexec = lithops.FunctionExecutor()
    future = fexec.call_async(test_alternative_energy_methods, {})
    result = future.result()
    print(f"\nFinal result: {result}")
    
    # Display the results table
    display_results_table(result)
