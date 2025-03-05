install lithops backend: 

docker pull lithopscloud/ibmcf-python-v312


net stop LxssManager
net start LxssManager
wsl --update

# Entorno virtual

## configuracion entorno virtual
python -m venv venv

venv\Scripts\activate // for linux
venv\Scripts\Activate.ps1 // for windows
source venv/bin/activate 

## comprobacion elementos de entorno virtual
python --version
pip list
pip install -r requirements.txt // not allways necessary

## install lithops: 
pip install lithops


# DOCKER
## Install wsl
https://docs.microsoft.com/es-es/windows/wsl/install-win10

## install docker
https://docs.docker.com/docker-for-windows/install/

* verify docker is installed
* verify the path to docker is in the environment variables


## instalar docker imagen de lithops
docker pull lithopscloud/ibmcf-python-v312

docker images

docker run -it lithopscloud/ibmcf-python-v312 python --version



pip install .
  pip install joblib 



# Comprobar lithops 




# Problemas: 
## no module pika installed as well as all requierements and libraries
* only when i intall lithops in local and execute the examples in the virtual machine it works 
* seems that the file should be installed in the venv python but also in the system
* in the folder: C:\Users\Usuario\AppData\Local\Temp\lithops-root there where errors bc the both enviroments are using the same folder 


```bash
$env:LITHOPS_DEBUG = "True"
lithops hello
```
 

# to run the examples:

* have complete and funtional commits in your local git repository
* create a new branch
* push the branch to the remote repository
* create a new cloud function
* push the cloud function to the remote repository
* create a new job
* push the job to the remote repository
* run the job
* validate before update 



# elements to execution enviroments 
lithops logs poll


# test in local: 
https://github.com/lithops-cloud/lithops/blob/master/docs/source/compute_config/localhost.md 
lithops hello -b localhost -s localhost

# see the logs : 
lithops logs poll



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# New approack 
* Install the Package in Editable Mode
pip install -e .

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~











!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# to finish the sesion: 
deactivate


# Tareas pendientes
grafo funcionalidad --> diagrama de flujo --> chatgpt / draw.io



# command:  
python -c "import lithops; print(lithops.__file__)"


# inside the venv 
pip install --force-reinstall lithops



# see where lithops is 
C:\Users\Usuario\Desktop\lithops\lithops\__init__.py
pip uninstall lithops -y
rmdir /s /q C:\Users\Usuario\Desktop\lithops\lithops


# install all libraries : 
pip install lithops[all]
 


