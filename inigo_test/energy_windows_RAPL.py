import ctypes
import time
import subprocess
import os

# Path to the Intel Power Gadget DLL.
# Adjust this path according to your installation.
dll_path = r"C:\Program Files\Intel\Power Gadget 3.0\PowerGadgetLib.dll"

# Load the DLL using ctypes
try:
    pg = ctypes.WinDLL(dll_path)
except Exception as e:
    print("Error loading Power Gadget DLL:", e)
    exit(1)

# Set up function prototypes
# Initialize the library
pg.PowerGadgetLibInitialize.restype = ctypes.c_int

# Read a sample (updates internal energy counters)
pg.PowerGadgetLibReadSample.restype = ctypes.c_int

# Get the number of sockets/nodes on the system
pg.PowerGadgetLibGetNumNodes.argtypes = [ctypes.POINTER(ctypes.c_int)]
pg.PowerGadgetLibGetNumNodes.restype = ctypes.c_int

# Get power data for a given node and signal.
# The API expects: (int iNode, const char* sSignalName, double* pData, int* pLength)
pg.PowerGadgetLibGetPowerData.argtypes = [
    ctypes.c_int,
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_int)
]
pg.PowerGadgetLibGetPowerData.restype = ctypes.c_int

# Uninitialize the library when finished.
pg.PowerGadgetLibUnInitialize.restype = ctypes.c_int

# Initialize Power Gadget
if pg.PowerGadgetLibInitialize() == 0:
    print("Failed to initialize Intel Power Gadget library.")
    exit(1)

def get_energy():
    """
    Reads the energy consumption (in Joules) for each socket.
    Returns a dictionary mapping socket identifiers to energy values.
    """
    # Get number of nodes/sockets
    num_nodes = ctypes.c_int(0)
    pg.PowerGadgetLibGetNumNodes(ctypes.byref(num_nodes))
    
    energy_dict = {}
    # We allocate an array to hold the returned data; 12 is a common size for the returned vector.
    num_values = ctypes.c_int(12)
    data = (ctypes.c_double * 12)()
    # The signal name for processor energy consumption. (Exact string must match what the API expects.)
    signal = b"Processor Energy_Consumed"

    for i in range(num_nodes.value):
        # For each node, get the energy data.
        pg.PowerGadgetLibGetPowerData(i, signal, data, ctypes.byref(num_values))
        # Typically, the first element (data[0]) holds the energy (in Joules)
        energy_dict[f"Socket {i}"] = data[0]
    return energy_dict

def measure_energy(program, args):
    """
    Measures the energy consumption difference before and after running a program.
    'program' is the executable name (or full path) and 'args' is a list of arguments.
    Returns a dictionary with energy consumed per socket (in Joules).
    """
    # Take an initial sample
    pg.PowerGadgetLibReadSample()
    start_energy = get_energy()

    # Run the target program and wait for it to finish.
    proc = subprocess.Popen([program] + args)
    proc.wait()

    # Read sample again after execution
    pg.PowerGadgetLibReadSample()
    end_energy = get_energy()

    # Calculate the difference per socket
    energy_diff = {}
    for key in start_energy:
        energy_diff[key] = end_energy[key] - start_energy[key]
    return energy_diff

if __name__ == "__main__":
    # Example: measure energy consumption of the "ping" command (which runs for a few seconds)
    # You can replace "ping" and its arguments with any other program or script.
    energy_used = measure_energy("ping", ["127.0.0.1", "-n", "5"])
    print("Energy consumption (Joules):")
    for socket, energy in energy_used.items():
        print(f"{socket}: {energy:.3f} J")

    # Clean up and uninitialize the Power Gadget library
    pg.PowerGadgetLibUnInitialize()
