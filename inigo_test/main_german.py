import lithops
from lithops.storage import Storage ## abstraccion de lithops para interactuar con el subyacente : interfaz comun independiente al storage

 

def funcion_german ( x ): 
    storage = Storage()
    print(storage.list_keys("lithops-test")) #
    return x + 1

executor= lithops.FunctionExecutor(log_level='debug' )

ft = executor.map(funcion_german, [1,2,3])

#  mv venv .venv # no flag activado 
# code /home/bigrobbin/.lithops/config
# path de config 
# anadir usuario al c group de docker 

print(executor.get_result(ft))

 