"""
Simple Lithops example using the map_reduce method.

In this example the map_reduce() method will launch one
map function for each entry in 'iterdata', and then it will
wait locally for the reduce result.
"""
import pprint
import lithops
import time

iterdata = [1, 2, 3, 4, 5]


def my_map_function(x):
    print(f"Processing input: {x}")
    print(f"MAP FUNCITOPM ")
    # time.sleep(x * 2)
    return x + 7


def my_reduce_function(results):
    total = 0
    for map_result in results:
        total = total + map_result
    return total


if __name__ == "__main__":
 

    # creates an instance of Lithops’ FunctionExecutor --> localhost & manage 
    fexec = lithops.FunctionExecutor() 

    #  executor distributes the my_map_function across the items in iterdata
    # The my_reduce_function is set to combine the results of the map phase.
    fexec.map_reduce(my_map_function, iterdata, my_reduce_function)
    print(fexec.get_result())

    #  chunk 1 = 2
    #  chunk 2 = 3 
 
    fexec = lithops.FunctionExecutor()
    future = fexec.call_async(my_map_function, 3)
    result = fexec.get_result(fs=[future]) # leng --> return list of parameters 
    pprint.pprint(future.stats)
