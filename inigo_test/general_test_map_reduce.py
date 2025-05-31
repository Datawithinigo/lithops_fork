"""
Simple Lithops example using the map_reduce method.

In this example the map_reduce() method will launch one
map function for each entry in 'iterdata', and then it will
wait locally for the reduce result.

RUN WITH SUDO:

sudo env "PATH=$PATH" /home/bigrobbin/Desktop/TFG/lithops/venv/bin/python3 inigo_test/map_reduce.py

sudo env "PATH=$PATH" /home/bigrobbin/Desktop/TFG/venv/bin/python3 lithops_fork/inigo_test/general_test_map_reduce.py

previous
cd inigo_test/

"""
import psutil
import pprint
import lithops
from standarized_measurement_functions import sleep_function, prime_function

# iterdata = [1, 2, 3, 4, 5]

iterdata = [2]


# def my_reduce_function(results):
#     total = 0
#     for map_result in results:
#         total = total + map_result
#     return total

def print_stats(future):

    print(f"CPU User Time: {future.stats.get('worker_func_cpu_user_time', 'N/A')}")
    print(f"CPU Usage Average: {future.stats.get('worker_func_avg_cpu_usage', 'N/A')}")  # busqueda de que libreria usa : psutils --> percentaje uso cpu 
    print(f"Energy Consumption: {future.stats.get('worker_func_energy_consumption', 'N/A')}")
    
    # Method used: 
    print(f"Energy Method used: {future.stats.get('worker_func_energy_method_used', 'N/A')}")


    # PERF: added new
    pkg = future.stats.get('worker_func_perf_energy_pkg')
    cores = future.stats.get('worker_func_perf_energy_cores')

    print(f"Perf Energy pkg: {pkg if pkg is not None else 'N/A'}")
    print(f"Perf Energy cores: {cores if cores is not None else 'N/A'}")

    # Calculate CPU “percentage” from energy metrics, if both values are present
    if isinstance(pkg, (int, float)) and isinstance(cores, (int, float)) and pkg != 0:
        cpu_percentage = cores / pkg * 100
        print(f"Perf CPU Percentage: {cpu_percentage:.2f}%")
    else:
        print("Perf CPU Percentage: N/A")

    # For actual CPU-usage percentage at runtime, you could use psutil:
    print(f"Current CPU usage (psutil): {psutil.cpu_percent(interval=1):.1f}%")

if __name__ == "__main__":
 

    # creates an instance of Lithops’ FunctionExecutor --> localhost & manage 
    fexec = lithops.FunctionExecutor() 

    #  executor distributes the my_map_function across the items in iterdata
    # The my_reduce_function is set to combine the results of the map phase.
    # fexec.map_reduce(sleep_function, iterdata, my_reduce_function)
    # print(fexec.get_result())
 

    print("Async call SLEEP function")
    fexec = lithops.FunctionExecutor()
    future = fexec.call_async(sleep_function, iterdata[0])
    result = fexec.get_result(fs=[future]) # leng --> return list of parameters 
    # pprint.pprint(future.stats)


    # Print only the three specific metrics
    print("\n\nSLEEP function metrics:")
    print_stats(future)

    print("\n\nAsync call COSTLY function")
    fexec = lithops.FunctionExecutor()
    future = fexec.call_async(prime_function, iterdata[0])
    max_prime_method1 = future.result()                     # needed to wait 
    max_prime_method2 = fexec.get_result(fs=[future])       # needed to wait 
    print(f"Method 1 - future.result(): {max_prime_method1}")
    print(f"Method 2 - fexec.get_result(): {max_prime_method2}")
    print(f"Both methods return the same max prime number: {max_prime_method1 == max_prime_method2}")

    # Print only the three specific metrics
    print("\n\nCOSTLY function metrics:")
    print_stats(future)

