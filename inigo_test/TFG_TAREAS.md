
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# DISTRIBUCION DE LAS TAREAS TFG: 
* discord: https://discord.gg/y5Qe5dHt


## SEMANA 1 (07/02/2025): Viaje a tarragona
1. Instalar lithops y entender el funcionamiento
2. Presentacion de la idea Green computing
3. Diseno del modelo inicial

## SEMANA 2 (28/02/2025): 
1. Introducir valor aleatorio medicion de energia 
2. Dentro del handler, ver jobs alternativos

## SEMANA 3 (7/03/2025): 
1. Explorar alternativas de medicion de energia 
2. Valorar 

## SEMANA 4 (14/03/2025):

### ENERGIA:
1. Alternatively, you could use a different approach for measuring energy consumption that doesn't require sudo, such as using the RAPL interface directly through sysfs.
2. functions --> entornos que se pueda ejecutar perf o no + rapl
    - Esquema de procesadores : conocer procesador & ver si se puede ejecutar perf
    - Condicional para establecer metodo de calculo lithops directamente
        * De momento hacemos comparativa de todos los metodos: TDP / RAPL / PERF
3. Testear con algunos ejemplos de aplicaciones lithops: 
    - https://github.com/lithops-cloud/applications/blob/master/montecarlo/pi_estimation/pi_estimation.ipynb
    - https://github.com/lithops-cloud/applications/blob/master/mandelbrot/example_mandelbrot.ipynb




## SEMANA 5 (21/03/2025): 

### PARALELISMO: 
1. medir que paralelismo se ejecuta con menos energia 
    - kpi : optimizacion kpi estimator --> optimizar para energia en local 

2. Extraccion de multiples datos para ver que paralelismo da menos consumo energetico 
    - plot graph ( x niveles paralelismo y energy consumption)

3. Diseno y analisis de los datos de energia para diferentes niveles de paralelismo --> crear problema optimizable 
- x paralelismo:  map_instances 
- y energia:  ver que paralelismo menos energia da 

4. Obtener datos (evitar dependencia de entorno de ejecucion):  
    * pi estimation
    * airbnb 
    * paralel mandelbrot 
    * stock prediction


### ELEMENTOS A INTEGRAR 
- perf: media vs suma 
- detectar rapl con lithops
- Separar codigo energia del handler 
 

### DATABASE TDP: (agg energia Crear base de datos : Firebase + Scraper + N8N diario --> calculos directas ) 
* fuentes de datos de tdp maquinas de computacion mas comunes
* maquina EC2: uso cpu +  funcion --> maquinas de instancias virtuales : 
* Github: Extraer procesadores  
* Postgres: generar base de datos 
    - Generar API:
    - Valores null 
    -  


### LISTA DE IDEAS: 
1. Diferencia energia de lithops vs nativo  1 processor--> plot  
2. guardar la energia: decir en que maquina es mas eficiente ejecutar metabolomica 



## SEMANA 6 (28/03/2025):  fiesta major => Manri se complica 



## SEMANA 7: viernes 4 no reunion 



# reunion: 
virtualizaciones sobre maquinas --> caso de que tiene no tienes acceso a rapl
* no RAPL

baremetal: rapl --> nadie mas ejecutando el servidor 
* worker vs funcion: 
worker: unidad logica que te permite ejecurar una funcion dentro 

worker puede pasar que todas las funciones se estan ejecutando 
4 maquinas virtuales --> 4 worker --> 100 funciones --> cada una de las 25 funciones 
TDP --> energia de todo el host / no de la funcion completa 
* formula computo total y dividir por numero de funciones que tiene el worker 
* consumo energia funcion de pipeline --> 
* practica valores agregados --> llamada de workers paralelos --


PASO POSTERIOR:
optimizar por pipelines 
por detras: algoritmo de normalizacion de datos comparativa ejecuciones pasadas 

comparar : algoritmo de normalizacion en base de lo que ha pasado anterior 

## SEMANA 8: SALTO / vas atrasado / recuperar 
* finalizar valores para todas las ejecutiones --> prioritario --> directamente ejecucion 
* script cleaning diferentes 
* incluir varias mediciones de energia 
* extras: powerapi / detector de cpu / ver ejecucion / tdp database 
* empezar a escribir 




# MANRI : 
1. Minio: plataforma de objet storage de codigo abierto --> docker --> hacer pruebas 
    * ejecutar deployment de minio en local con docker --> chagpt en un unico comando 
    * flexecutor --> ejecutar 
2. flexecutor: plataforma jolteon --> adaptar / plataforma estructurada donde queda mas facil llevar a cabo operaciones 
    - profiling: pi_montecarlo --> directiva que permite lanzar pipeline de ejecucion con diferentes configuraciones 
    - output guarda ejecucion de tiempo de ejecucion : 
    - Trainign que permite tomar estos profiling --> entrenar modelos predictivos que nos pueden recomendar las mejora de los tiempos futuros --> predicting 
    - Accesso manri : finales de verano / algun bug --> ajustes --> preguntar 

3. Predicting: que ejecucion tiene el menor coste, introducir la menor parte de la energia 
* deployment de minio --> lanzar en local los casos de uso 
- link con todos los datos para poder lanzar los pipelines 

mini: ejemplos -- dag_execurion 
dag_profiling.py : importante --> lo mas encapsulada posible stages de computacione y ejecutan todas un mismo codigo 


con flexecutor: tener el ciclo cerrado que sea end to end 
* sintaxis de 
despues de ejecucion de profiling --> tiempo y ejecuciones 
* cuando tengamos eso vemos como optimizar --> tener ahi la energia 
* discriminador para cual optimizar cada approach ? 
flexecutor: TDP / rapl --> cuando escriba las diferentes metricas escriba tambien las metricas de energia 
flexecutor: ofrecer de manera clara smart provisioning que lithops no ofrece
lithops ofrece las capacidades , pero sin la nocion de optimizacion 
libreria
* aportar las directrivas de optimizacion
* optimizar los resultados de optimizacion 
cuando ejecutamos --> nos explica como funciona cada uno para 

iteraciones que cada una hace diferencte --> explicar jolteon 
tiempo / energia / 
def optimize(self): --> optimiza el pipeline con todos los predict que tiene y coge las opciones que mas te favorece 


punto clave esta semans 
dag_profiling : 
hito bastante guay y hacer la optimizacion real -> cloud -> cargas interesantes -> opciones reales 


# conexion para hacer el end to end 
en funcion de los resultados que existen 
* todos los papers de jolteon los optimicemos por energia --> ml / nl / video 
* listos para lanzar 

TFG 
jolteon : 
reiterar sobre algo existente 

tfm: 
pensar despues para tener un valor nuevo --> las piensas cuando ya tienes un resultado 
con iterar con un algorimo nuevo --> tfm 

32 paginas : experiencia no copypaste 
no pages 
secciones con hablar con ciertos elementos 
tfg documento --> claro
super conciso --> primer nivel 12 paginas de maximo nivel --> 
estructura tfg resultadista --> anexo lo que sea 

minimo integracion flexecutor y caso optimizacion maximo 

preguntar jolteon : 

mas facil introducirse si esta poco explotado 
estas cargando con trabajo de manri y german --> no les hagas perder el tiempo 

# 
german: muy importante ejecutar y recopilar no el que 
# plotmap

manri sufi 
varios nodos de distribucion y han cargado los nodos --> experimentos y no funcionan 
# Tareas pendientes
grafo funcionalidad --> diagrama de flujo --> chatgpt / draw.io



# Manri 07/03/2023: 
valores base y heuristica --> estimacion de energia --> links german 
TDP= procesador 65w
porcentaje de uso de cada aplicacion --> primer aproach 

version naive : consultar basicamente 

scrapping a una api -> consumo energia base 
hardcoding --> cambiar por necesario 


# STEPS to follow: 
1. Obtener la energia
    - version basica con tdp --> funcionando 
    - perf: te falta como guardar la informacion 
    - PowerApi: intentamos hasta las 9 --> sino pedimos ayuda
    - Ver como funciona Powerapi y ver alternativas

2. Predictor de carga 


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Debbugger
## solved: 
 .vscode/launch.json

 {
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python no justMyCode",
      "type": "debugpy",
      "request": "launch",
      "purpose": ["debug-test"],
      "program": "${file}",
      "console": "integratedTerminal",
      "justMyCode": false
    }
  ]
}

ctrl + , --> justMyCode --> unselect all 


# run your own model without 
/home/bigrobbin/Desktop/git/lithops_fork/venv/bin/python flexecutor-main/examples/energy_comparison.py

# elementos de la reunion 
comando minio --> contenedor docker object storage != file storage --> almacenamiento object storage 
minio --> subir informacion ahi ( importante para replicar en el futuro --> object storage / no lithops storage --> S3 )
lithops --> bucket localhost / almacenamiento minio --> credenciales docker --> Map a storage ahi 


 

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# minio
docker run -d --name minio-server -p 9000:9000 -p 9001:9001 -v /home/bigrobbin/Desktop/git/lithops_fork/test-bucket:/data/test-bucket -e "MINIO_ROOT_USER=minioadmin" -e "MINIO_ROOT_PASSWORD=minioadmin" quay.io/minio/minio server /data --console-address ":9001"


sudo docker run -d --name minio-server -p 9000:9000 -p 9001:9001 -v /home/bigrobbin/Desktop/git/lithops_fork/test-bucket:/data/test-bucket -e "MINIO_ROOT_USER=minioadmin" -e "MINIO_ROOT_PASSWORD=minioadmin" quay.io/minio/minio server /data --console-address ":9001"

sudo docker run -d -p 9000:9000 -p 9001:9001 --name minio quay.io/minio/minio server /data --console-address ":9001"


sudo docker run -d --name minio-server -p 9000:9000 -p 9001:9001 -e "MINIO_ROOT_USER=minioadmin" -e "MINIO_ROOT_PASSWORD=minioadmin" quay.io/minio/minio server /data --console-address ":9001"

# servidor web --> 9001 / api rest 9000 : forwarding de dos puertos --> puerto sw vs api rest  

curl -O https://dl.min.io/client/mc/release/linux-amd64/mc

(venv) bigrobbin@bigrobbin:~/Desktop/git/lithops_fork$ chmod +x mc
(venv) bigrobbin@bigrobbin:~/Desktop/git/lithops_fork$ ./mc alias set myminio http://localhost:9000 minioadmin minioadmin
mc: Configuration written to `/home/bigrobbin/.mc/config.json`. Please update your access credentials.
mc: Successfully created `/home/bigrobbin/.mc/share`.
mc: Initialized share uploads `/home/bigrobbin/.mc/share/uploads.json` file.
mc: Initialized share downloads `/home/bigrobbin/.mc/share/downloads.json` file.
Added `myminio` successfully.
(venv) bigrobbin@bigrobbin:~/Desktop/git/lithops_fork$ ./mc mb myminio/test-bucket

 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# paralelismo

Now I understand how the profiling data is stored. The get_my_exec_path() function returns the path where the flexorchestrator script is located, which is set by the @flexorchestrator() decorator. This path is used as the base path for storing the profiling data.

In the main.py file, the @flexorchestrator(bucket="test-bucket") decorator is used, which sets the base path to the directory where main.py is located, which is flexecutor-main/examples/video.

So the profiling data should be stored in:
flexecutor-main/examples/video/profiling/video/stage0.json
flexecutor-main/examples/video/profiling/video/stage1.json
flexecutor-main/examples/video/profiling/video/stage2.json
flexecutor-main/examples/video/profiling/video/stage3.json



# elements to solve the error 
        //     "(cpu 1, mem, worker 2)": { 
        //     "(cpu 4, mem, worker 4)": {
        //     "(cpu 8, mem, worker 8)": {
        //     "(cpu 8, mem, worker 16)": { --> principalmete workers



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Structure of the project 

1. **Lithops** – my serverless compute framework.  
2. **MinIO** – S3-compatible object storage used as the communication bus between functions.  
3. **Flexecutor** – a Python wrapper around Lithops that aggregates execution metadata (logs, perf stats, outputs) into a single report.

 


 





# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LITHOPS 
# install lithops backend: 

docker pull lithopscloud/ibmcf-python-v312


net stop LxssManager
net start LxssManager
wsl --update

## Entorno virtual

### configuracion entorno virtual
python -m venv venv
python3 -m venv venv

### Activate: 
venv\Scripts\activate // for mac
venv\Scripts\Activate.ps1 // for windows
source venv/bin/activate 
source .venv/bin/activate 
source lithops-venv/bin/activate 

### deactivate / finalize sesion: 
deactivate

### comprobacion elementos de entorno virtual
python --version
pip list
pip install -r requirements.txt // not allways necessary
pip install setup.py

### install lithops: 
<!-- pip install lithops -->

### Install the Package in Editable Mode
venv/bin/python -m pip install -e . 
pip install -e .

### una vez instalado el v env 
pip install -e ".[all]" --break-system-packages
pip install -e ".[all]" 


# lithops config file 
# lithops yaml
https://github.com/lithops-cloud/lithops/blob/master/config/config_template.yaml

# where configuration lithops is : 
export LITHOPS_CONFIG_FILE=/home/bigrobbin/Desktop/TFG/lithops_fork/lithops_config   #/path/to/your/config

# LITHOPS_CONFIG_FILE system environment variable:
export LITHOPS_CONFIG_FILE='/home/bigrobbin/Desktop/TFG/lithops_fork/lithops_config'
unset LITHOPS_CONFIG_FILE

echo $LITHOPS_CONFIG_FILE
ls ~/.lithops/config ./.lithops_config /etc/lithops/config


nano ~/.lithops/config

# command:  
python -c "import lithops; print(lithops.__file__)"


# inside the venv 
pip install --force-reinstall lithops



# see where lithops is 
C:\Users\Usuario\Desktop\lithops\lithops\__init__.py
pip uninstall lithops -y
rmdir /s /q C:\Users\Usuario\Desktop\lithops\lithops

# all unified: 
source lithops-venv/bin/activate 
export LITHOPS_CONFIG_FILE='/home/bigrobbin/Desktop/TFG/lithops_fork/lithops_config'
docker start minio
 

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FLEXECUTOR
### sources in flexecutor: 
python3 -m venv venv-flexecutor

### Activate: 
source venv-flexecutor/bin/activate 

### install lithops in flexecutor: 
pip install --upgrade pip
pip install -e ../lithops_fork/
pip install -e . --break-system-packages

pip install -e /home/bigrobbin/Desktop/TFG/lithops_fork 

### LITHOPS_CONFIG: inside venv-flexecutor
python -c "import lithops; print(lithops.__file__)"

### where configuration lithops is : 

# LITHOPS_CONFIG_FILE system environment variable FLEXECUTOR:
* /path/to/your/config
export LITHOPS_CONFIG_FILE=/home/bigrobbin/Desktop/TFG/flexecutor-main/config_template.yaml   

* to usset 
unset LITHOPS_CONFIG_FILE

echo $LITHOPS_CONFIG_FILE
ls ~/.lithops/config ./.lithops_config /etc/lithops/config


nano ~/.lithops/config

# command:  
python -c "import lithops; print(lithops.__file__)"

### MinIO:
docker start minio


# all unified: 
source venv-flexecutor/bin/activate 
export LITHOPS_CONFIG_FILE=/home/bigrobbin/Desktop/TFG/flexecutor-main/config_template.yaml  
docker start minio
 


 
# REPASO GENERAL: 
1. variables de entorno
2. Activar
3. instalar dependencias flexecutor
4. desinstalar lithops 
5. instalar lithops especifico con -e 
6. mostrar la ruta de configuracion al fichero lithops
7. configurar minio
8. subir datos a minio -> mismo bucket 
9. evitar dependencias minio: 
10. (MANRI): errores de elementos 
- comentar valores json 
- error 9
- diferencias energia 
- Error: parametro de un map iterdata , array maximo : idealmente 

# pasar directamente storage bucket : word counter directamente un fichero en object storage directamente ahi 
https://lithops-cloud.github.io/docs/source/data_processing.html
https://lithops-cloud.github.io/docs/source/data_partitioning.html
Processing data from the Cloud — Lithops  documentation
 



# manri error 9 : error 1= cuando finalizan bien 
lithops logs poll


comentar con manri: 
==== ENERGY MONITOR INITIALIZED FOR PROCESS 9 ====
2025-05-13 18:08:43,341 [INFO] handler.py:224 -- Reading stats file before execution: /tmp/lithops-bigrobbin/storage/lithops.jobs/aaf05f-0-M000/00000/job_stats.txt
 



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# minio 
# poner los datos en minio: 
test-bucket/
└── training-data/          (empty “folder”)
    └── training-data/
        └── train_pca_transform.txt

1) nuke the entire training-data prefix in one go:
mc rm --recursive --force myminio/test-bucket/training-data

2) Re‐upload only the contents of your local training-data folder 
mc cp -r /home/bigrobbin/Desktop/TFG/flexecutor-main/test-bucket/training-data myminio/test-bucket/training-data

2.1)
mc cp -r /home/bigrobbin/Desktop/TFG/flexecutor-main/test-bucket/training-data myminio/test-bucket/


3) Verify
mc ls myminio/test-bucket/training-data
4) Rerun your pipeline


ver si servidor minio esta accesible: 
telnet 192.168.1.168 9000

# minio 
6. put all elements:
mc cp -r /home/bigrobbin/Desktop/REPASO/flexecutor/test-bucket/ myminio/test-bucket/
7. recordar configuracion en vez de localhost la propia de minio 
8. export LITHOPS_CONFIG_FILE=/home/bigrobbin/Desktop/REPASO/flexecutor/config.yaml  --> mejor que config normal 
- comandos 
 
source venv-flexecutor/bin/activate 
export LITHOPS_CONFIG_FILE=/home/bigrobbin/Desktop/REPASO/flexecutor/config.yaml
docker start minio

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


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

 


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Problemas: 
## no module pika installed as well as all requierements and libraries
* only when i intall lithops in local and execute the examples in the virtual machine it works 
* seems that the file should be installed in the venv python but also in the system
* in the folder: C:\Users\Usuario\AppData\Local\Temp\lithops-root there where errors bc the both enviroments are using the same folder 


```bash
$env:LITHOPS_DEBUG = "True"
lithops hello
```
 

## to run the examples:

* have complete and funtional commits in your local git repository
* create a new branch
* push the branch to the remote repository
* create a new cloud function
* push the cloud function to the remote repository
* create a new job
* push the job to the remote repository
* run the job
* validate before update 


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# elements to execution enviroments 
lithops logs poll

# test in local: 
https://github.com/lithops-cloud/lithops/blob/master/docs/source/compute_config/localhost.md 
lithops hello -b localhost -s localhost

# see the logs : 
lithops logs poll



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
GERMAN REVISIONES: 
(venv) bigrobbin@bigrobbin:~/Desktop/TFG$ sudo groupadd docker
groupadd: group 'docker' already exists
(venv) bigrobbin@bigrobbin:~/Desktop/TFG$ sudo usermod -aG docker $USER
(venv) bigrobbin@bigrobbin:~/Desktop/TFG$ newgrp docker
bigrobbin@bigrobbin:~/Desktop/TFG$ docker run  hello-world

german: 
usuario no permisos sobre docker --> bigrrobin 

diferentes entornos con configuraciones 
imagen --> definir el container con una imagen especifica


runtime: docker.io/lithopscloud/ibmcf-python-v312 # imagen publica en docker: 
* permisos especiales por default --> usuario normal no tiene permisos 
* anadir usuario al grupo de docker 
(venv) bigrobbin@bigrobbin:~/Desktop/TFG$ docker ps
permission denied while trying to connect to the Docker daemon socket at 


unix:///var/run/docker.sock: Get "http://%2Fvar%2Frun%2Fdocker.sock/v1.45/containers/json": dial unix /var/run/docker.sock: connect: permission denied

framework programacion 
por debajo container 
no podias correr containers de locker 

hello world de docker --> 
primero a gestionar c group de docker 
https://stackoverflow.com/questions/48957195/how-to-fix-docker-permission-denied



 docker ps -a

 
(venv) bigrobbin@bigrobbin:~/Desktop/TFG$ docker rm minio
Error response from daemon: No such container: minio
(venv) bigrobbin@bigrobbin:~/Desktop/TFG$ docker rm /minio-server


 
    
time sleep_pro 
forzar cpu loggaritmo --> replantear funcion 
chunck --> dividir en 2 
que la funcion que haga 
1000 ciclos
2 500 ciclos 
4 250 ciclos 

weak scaling 
automatizar sobre ese codigo --> cambiar para que sea 
consumo de energia segun paralelismo 
minio y runtimes 
automatizas + plot 



# GERMAN eror docker tipico : 
error docker --> clasico permisos
lithops logs poll

docker ps -a
* no puedes usar sudo pq en las maquinas virtuales y funciones no permite
* eliminar imagenes no necesarios: docker rm /minio-server

# POC
* word count: 
    - 1 lee 
    - 2 archivo la mitad 

# web interface / rest api 

 


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~





prompt : I want a detailed guide and process of how to run this file: main_german.py
 
i am having some problems for the execution of a simple example using lithops with minio. The file is 

1) venv and installed lithops from my fork folder using: 
source venv-flexecutor/bin/activate 
pip install -e ../lithops_fork/


2) set the configuration to this file: 
export LITHOPS_CONFIG_FILE=/home/bigrobbin/Desktop/TFG/flexecutor-main/config_template.yaml   
export LITHOPS_CONFIG_FILE=/home/users/iarriazu/flexecutor-main/lithops_config

3) minio storage / runtime selected and iniciated
docker start minio

To check the logs is useful the command :  lithops logs poll




## after meeting: 

Flexecutor acts as a wrapper of lithops: 
i want to store the energy measures imported by lithops in this folder
examples/ml/profiling/machine_learning 
1) if i delete the json inside the folder i obtain errors, why is that? is correct? whould not be useful if the json are generated in each execution.

2) after run examples/ml/main.py  is always needed to run  minio_cleanup.py to do not have elements inside minio to dificult the execution. 

3) how i can store the measures of energy in examples/ml/profiling/machine_learning  after running examples/ml/main.py ?  



# 
# Flexecutor
A flexible and DAG-optimized executor over Lithops

*Documentation pending to be written*


# ERRORES: 
1. circular imports 
2. dependencias flexecutor / diferentes carpetas
3. flexecutor : cd /home/bigrobbin/Desktop/REPASO/flexecutor && /home/bigrobbin/Desktop/REPASO/flexecutor/venv-flexecutor/bin/python -m pip install -e .
4. dataplug & cloud objets: /home/bigrobbin/Desktop/REPASO/flexecutor/venv-flexecutor/bin/python -m pip install dataplug

5. PYTHONPATH=. python3 examples/mini/dag_profiling.py



# prompt inicial : 

Explícame detalladamente los siguientes pasos para ejecutar flexecutor un entorno de pruebas:

1. He instalado MinIO en un entorno local y va a actuar como object storage
2. Tiene un bucket llamado "test-bucket" donde almacenaré archivos de prueba.

3. quiero que experimentes con ejecuciones varios ejemplos ubicados en examples/{ml|video}.

4. En los scripts de los casos de uso (examples/ml/main.py y examples/video/main.py), específicamente en la variable FlexData.prefix, encontraré las rutas donde debo subir los archivos de entrada para las diferentes aplicaciones.

5. El objetivo final es ejecutar diferentes configuraciones utilizando la operación DAGExecutor.profile y recopilar métricas de cada configuración.

Por favor, proporciona instrucciones paso a paso sobre:
 
- Cómo ejecutar DAGExecutor.profile con diferentes configuraciones (examples/ml/main.py y examples/video/main.py)
- Cómo recopilar y analizar los datos de consumo energético


IMPORTANTE: 
- centrate en la estructura existente y en entender como funciona, no crees archivos nuevos si no es absolutamente necesario 

Incluye ejemplos de comandos específicos que debería ejecutar en cada paso.


# error retorno 
código de retorno -9, lo que generalmente indica que el proceso fue terminado por una señal SIGKILL


lithops:
    backend: localhost 
    storage: minio  

 


minio:
    # storage_bucket: lithops-test
    storage_bucket: test-bucket
    endpoint: http://192.168.1.168:9000 # dentro de docker s3 / minio: self deployed accesible desde ambos entornos : 172.17.0.1 --> r
    access_key_id: minioadmin
    secret_access_key: minioadmin
<!-- # 
# (venv-flexecutor) bigrobbin@bigrobbin:~/Desktop/TFG/flexecutor-main$ telnet 172.17.0.1 9000
# Trying 172.17.0.1...
# Connected to 172.17.0.1.
# Escape character is '^]'.

# sudo entorno de docker --> $  -->




docker start minio
source venv-flexecutor/bin/activate
export LITHOPS_CONFIG_FILE=/home/bigrobbin/Desktop/REPASO/flexecutor/config.yaml


Vale entiendo lo que me propones pero hay areas de mejora: 
1. tras la ejecucion de examples/ml/main_profile.py se ha quedado estancado. 
- 2025-05-16 00:08:02,254 [INFO] invokers.py:225 -- ExecutorID 6d6aec-0 | JobID M004 - View execution logs at /tmp/lithops-bigrobbin/logs/6d6aec-0-M004.log
2025-05-16 00:08:02,254 [INFO] wait.py:101 -- ExecutorID 6d6aec-0 - Waiting for 1 function activations to complete

2. Me puedes explicar paso a paso como y por que se generan los  archivos json generados examples/ml/profiling/machine_learning , 
3. Ademas explicame el comportamiento de las diferentes fases y el orden entre ellas: 
- executor.train() 
- executor.predict(config)
- executor.optimize()

asi como generan : 
- examples/*/images/
- examples/*/profiling/
- examples/*/profiling/mocks
- examples/*/models/	
# conect to the server:
ssh -L 21000:192.168.2.2:6443 iarriazu@cloudfunctions.urv.cat -N

# PROMPT 2: 

Act as a Architectural software engieneer and analyze the architecture of my Lithops-based project. Please provide:

1. A sequential summary of all files involved in the execution flow, starting from general_test_map_reduce.py through to the energy monitoring components. For each file, provide a brief description of its purpose and role in the execution pipeline.
 

2. An architectural analysis that identifies each file for:
   - its main purpose
   - The key design patterns being used in the project
   - How these patterns affect the performance of thread workers and all flow
   - Critical performance considerations in the execution flow
   - The relationship between the core execution components and the energy management system
   - Add important information to present to the project 


# con ese promt --> disenas flujo de trabajo lithops + tfg 

pregunta como diseno de patrones como integrar energia de forma escalable sin alterar handler.py  
como crear una pequena interfaz o elemento que incluya diversos elementos de electricidad 



Act as a Architectural software engieneer you are in charge to  introduced the energy elements into an existing framework call lithops  but: 
- I want to have  nice patterns included 
- An option to don't use the energy module with energy = False
- I need to be able to implement new energy measurements tools, now are only 2 but in the future could be 10, so maintain an easy inclusion of each energy element
so keep that in mind to suggest how to design the project 



PROMPT ARCHITECTURE: 


Aswer deep searh: 
Act as an Architectural Software Engineer tasked with integrating energy monitoring capabilities into the Lithops framework. Design a modular energy monitoring system with the following requirements:

1. Recommend appropriate design patterns for seamlessly integrating energy monitoring into Lithops without disrupting its core functionality. Consider patterns like:
   - Factory Method or Abstract Factory for creating energy measurement tools
   - Strategy Pattern for different energy measurement implementations
   - Observer Pattern for monitoring energy events
   - Decorator Pattern for optionally adding energy monitoring
   - Any other patterns you believe would create a clean, maintainable architecture

2. Include a mechanism to completely disable energy monitoring with a simple "energy=False" parameter, ensuring:
   - Zero performance impact when disabled
   - No code changes required to toggle this feature
   - Clean handling of all related components when disabled

3. Design for extensibility to accommodate future energy measurement tools:
   - Currently supporting perf and eBPF as the two measurement tools
   - Must scale to support 10+ tools in the future
   - Allow for easy registration of new measurement tools without modifying core code
   - Maintain consistent interfaces across all measurement implementations

4. Ensure equal compatibility across all Lithops backend types:
   - Serverless backends
   - Standalone backends
   - Localhost backends

Please provide:
- A high-level architectural diagram represented both:
  * Visually (generated diagram)
  * As detailed text with hierarchies and relationships clearly indicated
- Interface definitions for the key components
- Explanation of how the selected design patterns fulfill the requirements
- Implementation considerations for ensuring performance is not significantly impacted
- Code examples for critical integration points

Consider how your design will interact with Lithops' existing components, particularly the execution flow from executors.py through handler.py.

# EBPF
cpu-cycles or CPU_CYCLES:PACKAGE0: Number of CPU cycles executed. This is highly correlated with energy consumption.
instructions or CPU_INSTRUCTIONS:PACKAGE0: Number of instructions retired. Provides a measure of work done.
cache-misses (e.g., LLC_MISSES:PACKAGE0): Last-Level Cache misses often lead to more energy-intensive main memory accesses.



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# conexion remota: 
sudo apt update
sudo apt install -y openssh-client
ssh-keygen -t rsa -b 4096 -C "inigo.arriazu@dataoverkill.com"


/home/bigrobbin/.ssh/id_rsa


The key fingerprint is:
SHA256:gaHMVBV4W9hoAFXVsxjtHfhlcMINSc7S82LujPTn8S8 inigo.arriazu@dataoverkill.com


The key's randomart image is:
+---[RSA 4096]----+
|    o+==+*.o +==.|
|   + ..o= + =++o+|
|    + .o.o +.==+ |
|        ... o.oo |
|        S     o .|
|             o . |
|            . .. |
|           . =E +|
|            . ++=|
+----[SHA256]-----+
 



 

conexion al rack 


ssh <username>@cloudfunctions.urv.cat

MI CASO : 

Buenas. Acceso completado. Te dejo aquí la información necesaria:

- username: iarriazu
- password: password (cambiala con `passwd` ASAP) -> password44
- manual de bienvenida al rack: (adjunto)

Saludos,



ssh iarriazu@cloudfunctions.urv.cat



iarriazu@proxy1:~$ ./init_ssh.sh
Bienvenido, , introduce tu contraseña de SSH: Generating public/private rsa key pair.
Enter file in which to save the key (/home/users/iarriazu/.ssh/id_rsa): 
/home/users/iarriazu/.ssh/id_rsa already exists.
Overwrite (y/n)? y
Enter passphrase (empty for no passphrase): 
Enter same passphrase again: 
Your identification has been saved in /home/users/iarriazu/.ssh/id_rsa
Your public key has been saved in /home/users/iarriazu/.ssh/id_rsa.pub
The key fingerprint is:
SHA256:iJf355qOEnZPwIKNnbFMZLy0aRbYwCUEcyjPmrFNyco iarriazu@proxy1
The key's randomart image is:
+---[RSA 3072]----+
|  o==B+          |
|. .oooB          |
| = . O X         |
|. * o.&oo        |
|.O  .o+.S.       |
|=E.  .o....      |
|     . o o. .    |
|      .  ..+     |
|       ...+..    |
+----[SHA256]-----+
 

*** System restart required ***

The programs included with the Ubuntu system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Ubuntu comes with ABSOLUTELY NO WARRANTY, to the extent permitted by
applicable law.

ssh <usuario>@cloudfunctions.urv.cat



Test si funciona:
# kubernetes  
kubectl get nodes

# docker 
docker run hello-world

ssh -N -L 44444:storage4-10Gbit:9001 <usuario>@cloudfunctions.urv.cat 


ssh -N -L 44444:storage4-10Gbit:9001 iarriazu@cloudfunctions.urv.cat






ssh -A \
    -J iarriazu@cloudfunctions.urv.cat \
    -N -L 44444:storage4-10Gbit:9001 \
    iarriazu@proxy1





in ssH : 
cd flexecutor-main && source venv-flexecutor/bin/activate && cd ../lithops_fork && pip install -e 

cd flexecutor-main && source venv-flexecutor/bin/activate && python examples/general_usage/main_german.py

cd flexecutor-main && source venv-flexecutor/bin/activate && python examples/ml/main.py



# elements: 
- __Complete the SSH Setup__:

  - Answer "y" to copy your SSH key to the cluster (this will make future connections easier)
  - The script will test the SSH connection and provide instructions for connecting with VSCode

- __Connect to proxy1 with VSCode__:

  - Open VSCode
  - Press F1 or Ctrl+Shift+P to open the Command Palette
  - Type "Remote-SSH: Connect to Host..." and select it
  - Select "cloudfunctions.urv.cat" from the list
  - VSCode will connect to proxy1 and open a new window



cd flexecutor-main && source venv-flexecutor/bin/activate && cd ../lithops_fork && pip install -e .



pip install flexecutor + pip install lithops 















Buenas Íñigo,

Vamos a comenzar como te comenté a lanzar en un entorno distribuido, ver que todo el sistema de monitorización de energía funcione ok y ya obtener resultados, pero sin todavía meternos en nada de modelos ni optimización. 

Para ello, te voy a dar acceso a nuestro k8s cluster + minio object storage. Con minor modifications podrán lanzar tu código en este entorno del mismo modo que en local.

Lista de tareas entonces a realizar:
       0. Mándame una public key para acceder via ssh a nuestro cluster. Cuando lo hagas, te mando instrucciones de como acceder y un doc con explicaciones del entorno.
Preparar el setup de ejecución:
El cluster completo de k8s está formado por compute{2-7}: esto es un problema porque cada una tiene hardware diferente. Entonces, las máquinas que usaremos serán compute6 y compute7. Cada uno de los servers tienen 2 x https://ibertronica.es/amd-epyc-7502-335ghz-socket-sp3-bulk. TDP = 180W.
Para ello, tendrás que modificar la lógica de control de lithops con k8s. No es muy chungo (te dejo pistas):
Definir nodeSelector en la config de los pods: https://github.com/lithops-cloud/lithops/blob/883618c60e8297e9feba346ef55e9dff0ae510a1/lithops/serverless/backends/k8s/config.py#L119.
Etiquetar los nodos para que nodeSelector solo use compute{6,7}.
Conectar lithops/flexecutor al cluster.
Build de runtimes docker para k8s (lithops runtime build ...)
Apuntar la config de lithops al cluster
Lanzar los pipelines sobre el cluster. Puedes cambiar la escala, crear algún pipeline propio que sea algo intensivo, para ver las diff. de energía según configuraciones. DagExecutor.profile()
Comprobar los resultados de energía (en k8s solamente podrás usar el método del TDP): ver que tengan sentido.
***Quizá sea necesario iterar los puntos 3 y 4 varias veces, hasta obtener resultados esperados. 

El output de esto serán unos profilings de calidad, que nos darán:
Métricas para plotear en el TFG.
Input para el futuro training/optimizing. 

Saludos, (recuerda mandarme la PK) y buen finde,








conexion SSH : 
VScode 
conection to host 


Adapta lithops fork para: Lista de tareas entonces a realizar quiero : ejecutar 

/home/users/iarriazu/lithops/main_german.py

en el cluster y para ello hay que Preparar el setup de ejecución:

1) El cluster completo de k8s está formado por compute{2-7}: esto es un problema porque cada una tiene hardware diferente. Entonces, las máquinas que usaremos serán compute6 y compute7. Cada uno de los servers tienen 2 x https://ibertronica.es/amd-epyc-7502-335ghz-socket-sp3-bulk. TDP = 180W.
Para ello, tendrás que modificar la lógica de control de lithops con k8s. No es muy chungo (te dejo pistas):
- Definir nodeSelector en la config de los pods: https://github.com/lithops-cloud/lithops/blob/883618c60e8297e9feba346ef55e9dff0ae510a1/lithops/serverless/backends/k8s/config.py#L119.
- Etiquetar los nodos para que nodeSelector solo use compute{6,7}.

2) Conectar lithops/flexecutor al cluster.
Build de runtimes docker para k8s (lithops runtime build ...)
Apuntar la config de lithops al cluster




y si hacemos la version mas basica? 
lithops logs poll

1) lithops base 
2) lithosp handler
3) lithosp energia 
4) flexecutor ... 




# Lithops with Kubernetes in the Cluster: Setup Complete

I've created a comprehensive set of scripts and documentation to help you run Lithops in the Kubernetes cluster using VSCode's SSH integration. Here's a summary of what we've done and the next steps:

## What We've Done

1. __Created Configuration Files__:

   - Updated the Lithops configuration to work with Kubernetes and MinIO
   - Set up SSH configuration for connecting to the cluster

2. __Created Setup Scripts__:

   - `setup_vscode_ssh.sh`: Sets up VSCode SSH configuration for connecting to the cluster
   - `setup_lithops_config_on_proxy1.py`: Sets up Lithops on proxy1 after connecting with VSCode SSH
   - Additional scripts for alternative approaches

3. __Created Documentation__:

   - `VSCODE_SSH_CLUSTER_GUIDE.md`: Comprehensive guide for using VSCode with SSH to develop and run Lithops in the cluster

## Next Steps

You've already started the setup process by running `./setup_vscode_ssh.sh iarriazu`. Here's how to complete the setup:

1. __Complete the SSH Setup__:

   - Answer "y" to copy your SSH key to the cluster (this will make future connections easier)
   - The script will test the SSH connection and provide instructions for connecting with VSCode

2. __Connect to proxy1 with VSCode__:

   - Open VSCode
   - Press F1 or Ctrl+Shift+P to open the Command Palette
   - Type "Remote-SSH: Connect to Host..." and select it
   - Select "cloudfunctions.urv.cat" from the list
   - VSCode will connect to proxy1 and open a new window

3. __Set up Lithops on proxy1__:

   - Once connected to proxy1 with VSCode, open a terminal
   - Copy the `setup_lithops_config_on_proxy1.py` script to proxy1 or create it directly in VSCode
   - Run the script: `python3 setup_lithops_config_on_proxy1.py`

4. __Run the Test Script__:

   - After the setup script completes, run the test script: `python3 ~/test_lithops.py`
   - This will verify that Lithops is working correctly with Kubernetes and MinIO

5. __Develop Your Lithops Applications__:

   - Create a new project directory: `mkdir -p ~/lithops_project`
   - Open this directory in VSCode
   - Create and edit your Lithops applications directly on proxy1
   - Run your applications with the integrated terminal

## Key Benefits of This Approach

1. __Direct Access to Kubernetes__: The proxy1 node already has kubeconfig configured, so you don't need to set up Kubernetes access
2. __Integrated Development__: Use VSCode's full features (syntax highlighting, code completion, debugging) while working directly on the cluster
3. __No Code Copying__: Edit and run code directly on the cluster without copying files back and forth
4. __Seamless Experience__: Develop, test, and debug in the same environment











# LITHOPS 
# install lithops backend: 

docker pull lithopscloud/ibmcf-python-v312


 

## Entorno virtual
 
python3 -m venv lithops-venv
source lithops-venv/bin/activate 
pip install -e ".[all]" 

export LITHOPS_CONFIG_FILE=/home/users/iarriazu/lithops/lithops_config


















2. cp esto en ~/.kube/config
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURCVENDQWUyZ0F3SUJBZ0lJVE0xQ0dTZzlPM0F3RFFZSktvWklodmNOQVFFTEJRQXdGVEVUTUJFR0ExVUUKQXhNS2EzVmlaWEp1WlhSbGN6QWVGdzB5TXpFd01qZ3hNVEU0TVRsYUZ3MHpNekV3TWpVeE1USXpNVGxhTUJVeApFekFSQmdOVkJBTVRDbXQxWW1WeWJtVjBaWE13Z2dFaU1BMEdDU3FHU0liM0RRRUJBUVVBQTRJQkR3QXdnZ0VLCkFvSUJBUUNoVnFZd0haamVGcVlydVFiN2l4bFF2Mi9lQitjZVcvZjVxdjQ3b1R3YU1jUmI4NkJlMzh6SHJLTHAKWmprSXk3TFZUVkhuN2JYanFTcUpTSmtuTVQvaEZBRjhjWnhLeEpQa21pWDdKenZmc0hDV2wrcUQ5cC9UbDM4MApTeURlUmFZUTFYMFNWb0x2dUVzUERtbGFMWTFvdkxDUGlQcmE4Q0pYOVFuc0pVSUgwTFhaZkZOYmJpaytyMzllCkh4QWN0aXJESk9HcnhmVkFFd3UxV0hEVTdmb3ZRNlFZQnQ0aUlmZ0ZzWFRLU2xPRzRSN0N0eFhhRzBGWU5DUFgKNEtWR1hjb01UYTkwWTRCLzFxZndSZU1kM3lpWG9leEFiNHo4UHlzaDlaSGRTN09mSTNmSnd4M2ZxY3k0ZTJPbApZNnpiSy9JUnVKK3VrejZlWlkxMGViZjBqbm43QWdNQkFBR2pXVEJYTUE0R0ExVWREd0VCL3dRRUF3SUNwREFQCkJnTlZIUk1CQWY4RUJUQURBUUgvTUIwR0ExVWREZ1FXQkJRNTJFWE5hQ1JNdkd4V1h0L0FERmV6am1zYWZ6QVYKQmdOVkhSRUVEakFNZ2dwcmRXSmxjbTVsZEdWek1BMEdDU3FHU0liM0RRRUJDd1VBQTRJQkFRQnZFbUZQYzZJVQpOTnR6bmcwVG5pbVNmbllLY0psS2cxL3JJZWg0UWErWXB0aWpJNEZueUpESGhSSDJCN0VzblQzNTdEckdNdkFJCkNZcm4zTEFZZHlBOVNPNG5HNjArT09taytXbDFwVmozVFRpZDcrSTRvcUVncGFkU2d5Rk5ZU25IcUFnbGVVQmYKN0dkQjlJNUFXQXVENzV4eGlxcjFRQ2VYYUpIT2x5MFc5OVhTUWJKdm9tMjdrdXBBVE40MnVHdzRqZjIvOWc0egpzM0RxdWkvZHpSVUxLN2d5b21IWlRFSmVGdFB1VmJVQWF5K0VEUHJTQ1dVZHRlcDIzNlBIdWNtcDlGT09BcUN4ClNCUWpuSTdraDNoQ3JSeXFQRnhabEVKbll6QjNiV3F0eDY1bWFQRHVKSGFKZFpWdVRtdEN0TEpxWWVyaVhQQzIKekdZQWpYUnl4US9oCi0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K
    server: https://proxy1:21000
  name: kubernetes
contexts:
- context:
    cluster: kubernetes
    user: kubernetes-admin
  name: kubernetes-admin@kubernetes
current-context: ""
kind: Config
preferences: {}
users:
- name: kubernetes-admin
  user:
    client-certificate-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURJVENDQWdtZ0F3SUJBZ0lJZXRGMzRWa01lNWd3RFFZSktvWklodmNOQVFFTEJRQXdGVEVUTUJFR0ExVUUKQXhNS2EzVmlaWEp1WlhSbGN6QWVGdzB5TXpFd01qZ3hNVEU0TVRsYUZ3MHlOVEV3TWpneE1EQTVNVGhhTURReApGekFWQmdOVkJBb1REbk41YzNSbGJUcHRZWE4wWlhKek1Sa3dGd1lEVlFRREV4QnJkV0psY201bGRHVnpMV0ZrCmJXbHVNSUlCSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DQVE4QU1JSUJDZ0tDQVFFQXljT0tXYUZOS0F0M0VrcGYKZlFSQ1dsNFlQN2hmWjFIYXRaZ3lrRU8vNUgvbVZucHpweUhuOFp0M0hUeXZiZDJMcDhnK1VoMEN3SSsxWUtobQpNeVVHNjJrWWhWNStsb1NqODNHOCtWQ3BRZ3pSRUkwaDhqY1NzRC9laDg1ckV6bnpURDU5WTk3QjhDSDYxRFlCCmhTdjdaMDV1UGJSWmptOTVaeDdtTDhjVmRZMUpqM0NuVE84UUU5cXhtbmdWTFl5U2FjMGtyUlNxYWRNQWUvaE4KdlVWR05PWmdXeDJYVjJ0S252MmdmUk5PYWNCd09VTEEyUWtkbnB0NmxZT1NaVWE2ekt4RFV2VTE2T3lnT3dQYgo1dldpcGpxWkRIaUVud05abUxTYktkVXg3RW50Y20vWFVSUDB4N0VrdWpWR1RSZjZTM3ZzRW5JakNDUVhTN0M5CnlNRDAzd0lEQVFBQm8xWXdWREFPQmdOVkhROEJBZjhFQkFNQ0JhQXdFd1lEVlIwbEJBd3dDZ1lJS3dZQkJRVUgKQXdJd0RBWURWUjBUQVFIL0JBSXdBREFmQmdOVkhTTUVHREFXZ0JRNTJFWE5hQ1JNdkd4V1h0L0FERmV6am1zYQpmekFOQmdrcWhraUc5dzBCQVFzRkFBT0NBUUVBa2VpN1c3bVdyYXN3MmhHNlRSU2JNMU1SaHR0WHVwWlF4QzV0CjdQc3JRRDJ2N0Z0OVR1RW9MZ2F4UGlNanhBT0FhUWFHdGxvaXZoRUxVWGhlc0x2eTJJaWE1Y2pRa2E4NmxjY3YKVVBqQXNQOVhOQ2sxcHhjeitCaHJFbWN4d1JMT0tGNVZ6WWlVcXRWdUZCbEFiemxDRmNWZ0U0N2Eya3FrbUd2cwpkQlZORm9ZaFRPam9yK29Vb3dKRjZhbkIxY3pSTVpRY1ZpKy9GclBJUktYVTJLdXVYYjd5cnI5ZmpYcjhQVjcvClRKWHVRNWx1K1ljWXFmODduSG93SnZaNnZZTkV5aWRPMHhjanNMQ3NFc2FoaHhoSFRmRGJ1aTVtUUNTclpQUUEKZXF4YWxrQVYwQmlkT2xOUHNzN1VzUGVvOGdmNEdyNTJsR1kzQ2VvQnJoY3U4T2R0RUE9PQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==
    client-key-data: LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlFcEFJQkFBS0NBUUVBeWNPS1dhRk5LQXQzRWtwZmZRUkNXbDRZUDdoZloxSGF0Wmd5a0VPLzVIL21WbnB6CnB5SG44WnQzSFR5dmJkMkxwOGcrVWgwQ3dJKzFZS2htTXlVRzYya1loVjUrbG9TajgzRzgrVkNwUWd6UkVJMGgKOGpjU3NEL2VoODVyRXpuelRENTlZOTdCOENINjFEWUJoU3Y3WjA1dVBiUlpqbTk1Wng3bUw4Y1ZkWTFKajNDbgpUTzhRRTlxeG1uZ1ZMWXlTYWMwa3JSU3FhZE1BZS9oTnZVVkdOT1pnV3gyWFYydEtudjJnZlJOT2FjQndPVUxBCjJRa2RucHQ2bFlPU1pVYTZ6S3hEVXZVMTZPeWdPd1BiNXZXaXBqcVpESGlFbndOWm1MU2JLZFV4N0VudGNtL1gKVVJQMHg3RWt1alZHVFJmNlMzdnNFbklqQ0NRWFM3Qzl5TUQwM3dJREFRQUJBb0lCQUdHYXp0cjlSUzRTSGRBagpXbjVJQ1RGZVE2elBySmQyNmE3ZnFkWlFjQXhDTTFPeWVUQnBIcU9xNmJ5akZ0cTNTbEFvZHIyU2V6cGNTd292CmJRRmc4REFCNzNMVmU3ZWxBd3RLQW5rNXBDZm51MXVlYXNXYUR0aGtqV3AxV1NjNzZZOEF5L2Y4VXlXdnluL08KZ0gzRUFTTEF0bVB6VXorc2ZiWjlKQzRJeVVETDlLN2ZwYko4ejk3QmtoTW1UWEYzRFFtWjFDTUtGcUN1WTZ3Zwo0RnV6WlVNaUYyRlFDZ2JSOWxTT2lqYnB2ZmNrZmNpRXVTMng2d0FCZ2U2a0hwQjB1c2RMSWIzWVpnclBkaE5KCjFvRXVIZlV1UWdaVnY5ek93K1JicUUzYys5bjJrNUFkNDRDbzd4eUVDTG9WNVhlVUJHVDFsdWorb0p5L1l2S3kKNFJYbU9vRUNnWUVBMmlUZTE4bVRBUHlKZFZvS21RMncyM3piYVl0N2hFRDl3ZmpkM2tkOUttaDdsald2WEtITgp4V2tTQWpnL0p6bmg0amdweHRPNjdwaXViLzhsVE9SOG9zTjdrUFlJcEpOQVdEMXZydDgzWjZFMnJhOFdsV2c0CjFwNFNFaGRLcXoyNWZZZUhHcW55djVDcVFFejNpZmVwVGJFLzZNRmViNko2bFZQNzdXVWcwc2NDZ1lFQTdNYjUKUWtrakVKelVLdmRNMjdzTXdaUXlTRHpPNFhoUDRUYUV1Z2lFVm9lUHVCaVVrc1BiOGMrZmlFTDg4SGM2MHlYVgpWRTc4ZGxMQ3R0NG0zby94ZU9aVERlUEpWS2JUMzFJQ0s4ZE5VaTc0TzlEekNQZkJSTDhVWWh1YlRyKzZRSEx3CmxxNWt0dEYwUnpZbWpIekNubktld0ZjclJCRjkxNXRwK3NKRU5Ta0NnWUExd01JY29ESVdHeVJ3QTFqN0wvRjEKbEVXb3MxTWpXclJzMkxzcks2aC9DN0h3YUpnbWxrUlRNYm5iVENyYnFwcXJtTFZLcGgrNDdXeUdjbk9waDkvaQpaNU1LUEdZU3o2b2FWRUV4OFJVQTl5dTNEcDdkQUFxSmIvZjU5ejFTQnVxdk1QY3NyZFlBT0ZDTGVhdkJsb0prCmY1bkU2K2t1VHZZdjE3c0xXMUVFUHdLQmdRRGVLckMxRHBUMVFJSWZzcDJPUzB0ajA1NytndmdIUFhHT095NTgKdEFNZ2dlQkxkOXpvZlJoQ0kzTm9VcHF0TXVLaVBveVZwK3RoUnJSbkM3bGkrYU0wc3NEWmRwTnhkM3V6dm1wRgpFNk9zYW1BSEdEOENlaDRCV0YxUzFONThISkF4YXVmdUtzSmJlOXJqK3A1ZkVhMDNLUXRtSkNSM29RWDRLVjVlCnFLdUJTUUtCZ1FEU1BqQlFqQjdFTVcxamVQMU9TWjdmYlVmKzhlamp6YkJqQ1ZhVDEyOXB1NjVNK0pUMkdkL0UKSHVLUmVsclViU1J0aUtkTm9IYWxZNnZSVUFTeXBXSzFpMkUxWFJtVlg1Q21iK2xjbTd0VGROSGdKOGFGcWFUZQpWNmRzN3Y2U0xsVGN0eFNaS2JuRUxvQ0wvUVh1ditqT0pZTVN1NzBybUdabFNOZ20xQVhkZFE9PQotLS0tLUVORCBSU0EgUFJJVkFURSBLRVktLS0tLQo=

3. Añade esta linea a /etc/hosts: 127.0.0.1       proxy1

4. Creat tunel SSH:  ssh -L 21000:192.168.2.2:6443 iarriazu@cloudfunctions.urv.cat -N

























export LITHOPS_CONFIG_FILE=/home/users/iarriazu/lithops_fork/lithops_config
	
# conect to the server:
ssh -L 21000:192.168.2.2:6443 iarriazu@cloudfunctions.urv.cat -N



1. Etiquetar los nodos compute6 y compute7:

# Etiquetar los nodos para identificarlos
kubectl label nodes compute6 node-type=compute-high-performance
kubectl label nodes compute7 node-type=compute-high-performance

# Verificar las etiquetas
kubectl get nodes --show-labels | grep compute


# Ver las etiquetas de los nodos compute
kubectl get nodes --show-labels | grep compute

# Ver específicamente compute6 y compute7
kubectl describe node compute6 | grep Labels
kubectl describe node compute7 | grep Labels

3. 
# Crear namespace para lithops
kubectl create namespace lithops

# Verificar que el namespace se creó
kubectl get namespaces | grep lithops


5. 

# Construir el runtime para k8s
lithops runtime build -b k8s

# Listar los runtimes disponibles
lithops runtime list -b k8s



# crear dockerfile: 
lithops/Dockerfile

# Crear un Dockerfile básico para lithops
cat > Dockerfile << 'EOF'
FROM python:3.10-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar lithops
RUN pip install lithops

# Configurar el directorio de trabajo
WORKDIR /lithops

# Copiar el handler de lithops
COPY lithops_k8s.zip /opt/lithops/

# Comando por defecto
CMD ["python"]
EOF

# Ahora construir el runtime
lithops runtime build -b k8s lithops-k8s-runtime

# ¡Perfecto! La imagen se construyó correctamente, pero el error es que está intentando hacer push a Docker Hub sin autenticación. Para usar lithops con k8s en un cluster local, no necesitas hacer push a un registry externo. Necesitas actualizar tu configuración para usar un registry local o evitar el push.

docker images | grep lithops-k8s-runtime


pip install pytest
lithops test -b k8s



Tengo estas instrucciones para correr lithops en el cluster, mi pregunta es, cual debe de ser el archivo de configuracion en base a el build runtime de docker (https://github.com/lithops-cloud/lithops/blob/master/config/config_template.yaml ) INSTRUCCIONES: Preparar el setup de ejecución: El cluster completo de k8s está formado por compute{2-7}: esto es un problema porque cada una tiene hardware diferente. Entonces, las máquinas que usaremos serán compute6 y compute7. Cada uno de los servers tienen 2 x https://ibertronica.es/amd-epyc-7502-335ghz-socket-sp3-bulk. TDP = 180W. Para ello, tendrás que modificar la lógica de control de lithops con k8s. No es muy chungo (te dejo pistas): 1. Definir nodeSelector en la config de los pods: https://github.com/lithops-cloud/lithops/blob/883618c60e8297e9feba346ef55e9dff0ae510a1/lithops/serverless/backends/k8s/config.py#L119. 2. Etiquetar los nodos para que nodeSelector solo use compute{6,7}. 1. Conectar lithops/flexecutor al cluster. 1. Build de runtimes docker para k8s (lithops runtime build ...) 2. Apuntar la config de lithops al cluster tengo actualmente una configuracion similar a esta lithops:     backend: k8s     storage: minio  k8s:     kubecfg_path: /home/users/iarriazu/.kube/config     worker_processes: 4     docker_user: iarriazu     runtime: macarronesc0lithops/lithops-kubernetes-default-v38:3.6.0     docker_server: docker.io     runtime_cpu: 1     runtime_memory: 2048     runtime_timeout: 600     standalone: true     node_selector:         compute-node: high-performance  minio:     storage_bucket: test-bucket     endpoint: http://storage4-10Gbit:9000     access_key_id: lab144     secret_access_key: astl1a4b4







# DOCKER cluster: 

# subir al docker la imagen correcta:  --> FUNCIONA
lithops runtime build -b k8s iarriazu/inigo_runtime



# Si tu Dockerfile se llama Dockerfile.lithops (o similar):
lithops runtime build -f Dockerfile.lithops -b k8s iarriazu/inigo_runtime

# Si tu Dockerfile se llama simplemente Dockerfile:
lithops runtime build -b k8s iarriazu/inigo_runtime

# namespace (si aún no lo has creado):
kubectl create namespace lithops-jobs








 
 
# extraer los logs 

## Tras error pull image ver el pod: 
kubectl describe pod <nombre-del-NUEVO-pod-meta> -n lithops-jobs

## cuando no da tiempo: 
kubectl get events -n lithops-jobs --sort-by='.metadata.creationTimestamp'

# ver la ejecucion: 
kubectl get pods -n lithops-jobs -w
kubectl describe pod lithops-worker-361dev0-77d9c221a5-meta-5zft4 -n lithops-jobs









kubectl get jobs -n lithops-jobs

 
kubectl logs -f job/<nombre-del-nuevo-job> -n lithops-jobs --all-containers


kubectl logs -f job/lithops-worker-361dev0-c5d206f475-meta -n lithops-jobs --all-containers


lithops runtime build -f Dockerfile -b k8s iarriazu/inigo_runtime


# PODS de kubernetes data inbound --> direccion de ip 


funcion de metadata para conectar datos con clientes 
https://k8slens.dev/


# eliminar todos los eventos a la vez 
kubectl delete events --all --namespace lithops-jobs


# coger algun ultimo log: 
POD_NAME=$(kubectl get pods --namespace lithops-jobs --sort-by='.metadata.creationTimestamp' -o jsonpath='{.items[-1:].metadata.name}') && echo "Intentando obtener logs para el pod más reciente: $POD_NAME" && kubectl logs --namespace lithops-jobs $POD_NAME


# congigure other execution space
 
# Check which namespace actually has pods
kubectl get pods --all-namespaces | grep lithops

# Use your configured namespace
POD_NAME=$(kubectl get pods --namespace inigo-jobs-energy --sort-by='.metadata.creationTimestamp' -o jsonpath='{.items[-1:].metadata.name}') && echo "Getting logs for most recent pod: $POD_NAME" && kubectl logs --namespace inigo-jobs-energy $POD_NAME


## elemenst
mc alias set myminio http://192.168.5.24:9000 lab144 astl1a4b4
mc ls myminio




 
 

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TRABAJO CLUSTER: 

# Activate: 
source lithops-venv/bin/activate 
source .venv/bin/activate

# Verificar: 
lithops logs poll


# conect to the server: 
ssh -L 21000:192.168.2.2:6443 iarriazu@cloudfunctions.urv.cat -N
  
# general  # Export values  --> ERROR futuro runtime 
export LITHOPS_CONFIG_FILE=/home/users/iarriazu/lithops/lithops_config

export LITHOPS_CONFIG_FILE=/home/users/iarriazu/lithops_fork/lithops_config
export LITHOPS_CONFIG_FILE=/home/users/iarriazu/lithops/lithops_config
export LITHOPS_CONFIG_FILE=/home/users/iarriazu/flexecutor-main/lithops_config


cd ~/lithops
python3 -m venv .venv
source .venv/bin/activate


pip install --upgrade pip
pip install -e .
pip install kubernetes pyyaml


docker start minio



 


# ANTES DE EJECUTAR: 
1) crear namespace: 
kubectl create namespace inigo-jobs-energy
kubectl create namespace inigo-jobs-flexecutor

2) docker login


3) construir la runtimebuild: 

lithops runtime build -b k8s iarriazu/inigo_runtime

docker push iarriazu/inigo_runtime
  ### Build mean 
  cd /home/users/iarriazu/
  docker build -f flexecutor-main/Dockerfile -t flexecutor-app .

kubectl get nodes

4) kubectl get nodes --show-labels
5) kubectl auth can-i create pods --namespace=default 

rename the nodes: 
kubectl label nodes compute6 node-type=highcpu --overwrite
kubectl label nodes compute7 node-type=highcpu --overwrite


kubectl get nodes --show-labels

lithops runtime build k8s --name inigo_runtime --dockerfile Dockerfile




# Verificar acceso a los nodos correctos:
kubectl get nodes -l node-type=highcpu,lithops-node=true

# Gemini 
kubectl label nodes compute6 lithops-target-node=true --overwrite
kubectl label nodes compute7 lithops-target-node=true --overwrite


kubectl get nodes --show-labels
# O para un nodo específico:
kubectl get node compute6 --show-labels
kubectl get node compute7 --show-labels



# Si tienes un requirements.txt en el directorio actual:
lithops runtime build -b k8s mi-runtime-lithops-k8s

# Si necesitas un Dockerfile específico (p.ej., Dockerfile.lithops):
# lithops runtime build -b k8s -f Dockerfile.lithops mi-runtime-lithops-k8s
lithops runtime build -b k8s inigo_runtime



crear una cuenta de docker donde subir tus imagenes 


iarriazu
password44

# Desde el directorio donde está tu Dockerfile
lithops runtime build -b k8s iarriazu/inigo_runtime:latest

docker push iarriazu/inigo_runtime:latest

# eliminar todos los eventos a la vez 
kubectl delete events --all --namespace lithops-jobs




# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


TESTEAMos
# Primero, lista los pods en tu namespace 'lithops-jobs' para encontrar los relevantes
kubectl get pods -n lithops-jobs

# Luego, obtén los logs de un pod específico (reemplaza <nombre-del-pod> con el nombre real)
kubectl logs <nombre-del-pod> -n lithops-jobs

# Si el pod tiene múltiples contenedores (aunque para Lithops suele ser uno principal), puedes especificar el contenedor:
# kubectl logs <nombre-del-pod> -c <nombre-del-contenedor> -n lithops-jobs




# prompt : 
Adapta lithops fork para: Lista de tareas entonces a realizar quiero : ejecutar 

/home/users/iarriazu/lithops/main_german.py

en el cluster y para ello hay que Preparar el setup de ejecución:


1) El cluster completo de k8s está formado por compute{2-7}: esto es un problema porque cada una tiene hardware diferente. Entonces, las máquinas que usaremos serán compute6 y compute7. Cada uno de los servers tienen 2 x https://ibertronica.es/amd-epyc-7502-335ghz-socket-sp3-bulk. TDP = 180W.

Para ello, tendrás que modificar la lógica de control de lithops con k8s. No es muy chungo (te dejo pistas):

- Definir nodeSelector en la config de los pods: https://github.com/lithops-cloud/lithops/blob/883618c60e8297e9feba346ef55e9dff0ae510a1/lithops/serverless/backends/k8s/config.py#L119.

- Etiquetar los nodos para que nodeSelector solo use compute{6,7}.



2) Conectar lithops/flexecutor al cluster.

Build de runtimes docker para k8s (lithops runtime build ...)

Apuntar la config de lithops al cluster



kubectl get events -n inigo-jobs-energy --sort-by='.metadata.creationTimestamp'







# List all pods in your namespace
kubectl get pods -n inigo-jobs-energy

# Get detailed pod information
kubectl describe pods -n inigo-jobs-energy

# Get pod logs
kubectl logs <pod-name> -n inigo-jobs-energy

# Get pod status in YAML format
kubectl get pods -n inigo-jobs-energy -o yaml

# Watch pods in real-time
kubectl get pods -n inigo-jobs-energy -w


# Tras la ejecucion: 

tras la ejecucion de /home/users/iarriazu/lithops_fork/inigo_test/main_german.py deberia haber una carpeta de energia generada por lithops, si la ejecucion es en k8s no aparece, cual es la razon ? que puedo hacer para solucionarlo?
Ahora entiendo el problema. Basándome en el análisis del código y los logs, puedo explicarte qué está pasando y cómo solucionarlo:


## **Razón del problema:**

La carpeta de energía no se genera en Kubernetes porque:

1. **Falta de herramientas necesarias en el contenedor**: Los logs muestran que tanto `sudo` como `perf` no están disponibles en el runtime de Kubernetes:
   ```
   Error with sudo perf list: [Errno 2] No such file or directory: 'sudo'
   Error getting available energy events: [Errno 2] No such file or directory: 'perf'
   Error starting energy monitoring: [Errno 2] No such file or directory: 'sudo'
   ```

2. **Falta de BCC (BPF Compiler Collection)**: El monitor eBPF tampoco puede funcionar:
   ```
   BCC (BPF Compiler Collection) is not installed.
   Please install it with: sudo apt-get install bpfcc-tools python3-bpfcc
   ```

3. **Permisos insuficientes**: Incluso si las herramientas estuvieran disponibles, los contenedores de Kubernetes normalmente no tienen permisos para acceder a contadores de hardware de bajo nivel.

## **Soluciones:**

### **Solución 1: Modificar el runtime de Docker**

Necesitas actualizar tu imagen Docker `iarriazu/inigo_runtime` para incluir las herramientas necesarias:







# cluster solucion claude: 
https://claude.ai/share/fada8ad6-dd06-48ea-a1d8-42c63a920d31




glujo de la tabla 









Estoy en un entorno compartido, donde uso docker y no tengo permisos de super usuario

por un error de espacio tuve que eliminar algunos volumenes y ahora no puede jeecutar nada correctamente, no funciona bien el build.

comando que ejectute hace itempo y alguno extra 
pip cache purge

Comandos que no funcionan
sudo pkill -9 -f docker
docker system prune -f && docker builder prune -f
pkill -f "docker build"

cuando ejecuto un build nunca termina: 

(.venv) iarriazu@proxy1:~/lithops_fork$ lithops runtime build -b k8s iarriazu/inigo_runtime
2025-05-31 17:04:19,857 [INFO] config.py:139 -- Lithops v3.6.1.dev0 - Python3.10
2025-05-31 17:04:19,858 [DEBUG] config.py:101 -- Loading configuration from /home/users/iarriazu/.lithops/config
2025-05-31 17:04:19,885 [DEBUG] config.py:179 -- Loading Serverless backend module: k8s
2025-05-31 17:04:20,273 [DEBUG] k8s.py:51 -- Creating Kubernetes client
2025-05-31 17:04:20,273 [DEBUG] k8s.py:67 -- Loading kubeconfig file: /home/users/iarriazu/.kube/config
2025-05-31 17:04:20,303 [DEBUG] k8s.py:78 -- Using kubeconfig conetxt: kubernetes-admin@kubernetes - cluster: kubernetes
2025-05-31 17:04:20,304 [INFO] k8s.py:112 -- Kubernetes client created - Namespace: lithops-jobs
2025-05-31 17:04:20,305 [INFO] k8s.py:132 -- Building runtime docker.io/iarriazu/inigo_runtime from Dockerfile
2025-05-31 17:04:20,305 [DEBUG] utils.py:234 -- Creating function handler zip in /home/users/iarriazu/lithops_fork/lithops_k8s.zip
[+] Building 21.5s (0/2)                                                         docker:default
 => [internal] load .dockerignore                                                         21.5s
 => [internal] load build definition from Dockerfile                                      21.5s

 

ME gustaria saber como hacer qeu este elemento complile y funcione correctamente  

lithops runtime build -b k8s iarriazu/


# ERROR
ERROR: Could not install packages due to an OSError: [Errno 28] No space left on device
(venv) iarriazu@proxy1:~/flexecutor-main$ pip cache purge



ver cuanto necesitas: 
(venv) iarriazu@proxy1:~$ du -sh .
18G     .

(venv) iarriazu@proxy1:~$ du -sh * .[^.]* | sort -rh | head -n 20
13G     flexecutor-main
1.6G    .cache
1.3G    lithops_fork
1.2G    lithops
875M    .vscode-server
225M    .local
11M     .kube
744K    move
556K    manual-de-primera-conexion-rack-v1.1 (1).pdf
412K    .docker
208K    .dotnet
112K    .ssh
104K    energy_data
100K    .lithops
36K     .mc
36K     .bash_history
12K     Cline
8.0K    lithops-custom-runtime
8.0K    .config
4.0K    label_nodes.sh














