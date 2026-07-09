---
titulo: ETCD en la arquitectura de Kubernetes
tipo: documento
---

# ETCD en la arquitectura de Kubernetes

## Visión General
ETCD es un **distributed, reliable key value store** que se caracteriza por ser simple, seguro y rápido. En este tema se explica qué es un **key value store**, cómo se diferencia de las bases de datos tradicionales y cuál es el papel de **ETCD** dentro de Kubernetes.

---

## Qué es ETCD
ETCD es un **key value store** distribuido y confiable. En esta introducción se presenta su propósito, su funcionamiento básico y una visión general de cómo empezar a usarlo con su cliente de línea de comandos.

- **ETCD** → almacén distribuido y confiable de tipo clave-valor
- **distributed** → su funcionamiento distribuido se profundiza más adelante en el curso
- **reliable** → su confiabilidad también se explica después con más detalle
- **simple, secure and fast** → características principales con las que se describe ETCD

---

## Modelos de almacenamiento de datos

### Bases de datos relacionales
Las bases de datos tradicionales almacenan información en formato tabular, con **rows** y **columns**. Cada fila representa una entidad, como una persona, y cada columna representa un tipo de dato. Si se añade nueva información, como **salary** o **grade**, hay que modificar la tabla completa, lo que puede generar muchas celdas vacías cuando esos datos no aplican a todos.

- **relational databases** → almacenan datos en tablas con filas y columnas
- **SQL** → permite consultas complejas con buen rendimiento
- **strict schema** → estructura rígida, adecuada para datos estructurados
- **empty cells** → aparecen cuando se agregan columnas que no aplican a todos los registros

### Document store
Un **document store** guarda la información en documentos individuales. Cada persona puede tener su propio documento con una estructura distinta. Por ejemplo, una persona que trabaja puede tener **salary**, mientras que un estudiante puede tener **grades**, sin afectar a los demás documentos.

- **document store** → almacena información en documentos independientes
- **JSON** → formato típico de almacenamiento en este modelo
- **schema** → normalmente no necesita un esquema definido
- **semi structured data** → es el tipo de datos para el que mejor se adapta

### Key value store
El modelo **key value store** es muy simple: guarda un valor asociado a una clave. Por ejemplo, **name → John**, **location → New York**, **age → 45** o **salary → 5000**. También permite almacenar valores más complejos, como un conjunto de propiedades o incluso un documento **JSON** completo.

- **key** → identificador con el que se almacena o recupera un valor
- **value** → dato asociado a una clave
- **user:John Doe** → ejemplo de clave más compleja
- **JSON document** → puede usarse como valor completo

---

## Comparación del key value store con otros modelos
El **key value store** no requiere necesariamente un **schema**, no está orientado a consultas complejas, pero ofrece un rendimiento muy alto. Además, es muy flexible porque permite almacenar prácticamente cualquier cosa sin afectar a otras entradas ni depender de una estructura rígida.

- **no schema** → no exige una estructura fija
- **no complex queries** → no está pensado para consultas complejas
- **super fast** → destaca por su gran rendimiento
- **flexible** → permite almacenar distintos tipos de datos sin romper otras estructuras
- **simple fast look up** → es ideal para búsquedas simples y rápidas

---

## Instalación y uso básico de ETCD
Para empezar con ETCD, se descarga el binario correspondiente al sistema operativo desde la página de releases de GitHub, se extrae y se ejecuta. Al iniciar **ETCD**, el servicio escucha por defecto en el puerto **2379**.

Este es el modo más simple de ejecutar un servidor ETCD. De forma ideal, debería ejecutarse como **system service** o como un **pod** en un cluster de Kubernetes. Después, los clientes pueden conectarse al servicio para almacenar y recuperar información.

- **binary** → archivo que se descarga para ejecutar ETCD
- **port 2379** → puerto por defecto en el que escucha ETCD
- **system service** → forma recomendada de ejecución fuera del modo básico
- **pod** → otra forma recomendada de ejecutarlo en Kubernetes

### etcdctl
El cliente por defecto que acompaña a ETCD es **etcdctl**, una herramienta de línea de comandos para interactuar con el almacén.

- **etcdctl** → cliente de línea de comandos de ETCD
- **put** → comando para guardar una pareja clave-valor
- **get** → comando para recuperar el valor de una clave
- **etcdctl sin argumentos** → muestra más opciones disponibles

Ejemplo de uso básico:
- **put key1 value1** → crea una entrada en la base de datos
- **get key1** → recupera el valor almacenado en esa clave

---

## Versiones y cambios de API en ETCD
Es importante entender que existen diferencias entre versiones de ETCD, especialmente entre la **API v2** y la **API v3**. Esto explica por qué en documentación antigua pueden aparecer comandos distintos.

La primera versión, **0.1**, se lanzó en agosto de 2013. La versión estable **2.0** se publicó en febrero de 2015. En enero de 2017 llegó la versión **3**, con muchas optimizaciones y mejoras de rendimiento. Más adelante, en noviembre de 2018, ETCD pasó a ser un proyecto **CNCF incubated**, y en noviembre de 2020 se convirtió en **CNCF graduated project**. En junio de 2021 se lanzó la versión **3.5**.

### Diferencias entre v2 y v3
En la versión 3 cambió la API, y con ello también los comandos de **etcdctl**.

- **v2 set / get** → comandos antiguos usados por la API v2
- **v3 put / get** → comandos usados en la API v3
- **v2 rm** → comando antiguo para borrar valores
- **v3 delete** → comando actual para eliminar valores
- <span class="truncated-code-wrapper" data-full-text="**transactions**" title="**transactions**"><code class="truncated-code">**transactions*…</code><span class="copy-code-inline-btn" data-copy="**transactions**"></span></span> → no estaban soportadas en v2, pero sí en v3

Para comprobar la versión, se usa el comando:
- **etcdctl version** → permite ver la versión y confirmar si se usa la API v2 o v3

La idea principal es no alarmarse si se encuentran blogs o documentos con comandos antiguos como **set**, **get** y **rm**, porque pertenecen a versiones anteriores.

---

## Rol de ETCD en Kubernetes
En Kubernetes, ETCD actúa como el **datastore** del cluster. Almacena información sobre **nodes**, **pods**, **configs**, **secrets**, **accounts**, **roles**, **role bindings** y otros objetos del cluster.

Toda la información que aparece al ejecutar **kubectl get** proviene del servidor ETCD. Además, cualquier cambio realizado en el cluster, como añadir **nodes**, desplegar **pods** o **replica sets**, se actualiza en ETCD. Solo cuando ese cambio queda registrado en ETCD se considera completado.

- **datastore** → almacenamiento principal del estado del cluster
- **kubectl get** → obtiene información almacenada en ETCD
- **nodes, pods, configs, secrets** → ejemplos de datos guardados en ETCD
- **change considered complete** → un cambio solo se considera completo cuando se actualiza en ETCD

---

## Despliegue de ETCD en Kubernetes

### Cluster configurado desde cero
Si el cluster se configura desde cero, ETCD se despliega descargando sus binarios, instalándolos y configurándolo como un servicio en el **master node**. En esta configuración intervienen varias opciones, muchas de ellas relacionadas con <span class="truncated-code-wrapper" data-full-text="**certificates**." title="**certificates**."><code class="truncated-code">**certificates*…</code><span class="copy-code-inline-btn" data-copy="**certificates**."></span></span>

- <span class="truncated-code-wrapper" data-full-text="**certificates**" title="**certificates**"><code class="truncated-code">**certificates*…</code><span class="copy-code-inline-btn" data-copy="**certificates**"></span></span> → parte de la configuración del servicio ETCD
- **TLS certificates** → se tratarán más adelante en otra sección del curso
- **cluster configuration** → otras opciones sirven para configurar ETCD como cluster

La opción más importante en este punto es:

- **advertised client URL** → dirección en la que ETCD escucha peticiones de clientes

Esta dirección suele corresponder a la IP del servidor y al puerto **2379**, que es el puerto por defecto de ETCD. Esta es la URL que debe configurar el **KubeAPI server** para conectarse a ETCD.

### Cluster configurado con KubeADM
Si el cluster se crea con **KubeADM**, entonces KubeADM despliega el servidor ETCD automáticamente como un **pod** dentro del namespace <span class="truncated-code-wrapper" data-full-text="**kube-system**." title="**kube-system**."><code class="truncated-code">**kube-system**…</code><span class="copy-code-inline-btn" data-copy="**kube-system**."></span></span> En este caso, se puede explorar la base de datos usando **etcdctl** dentro de ese pod.

- **KubeADM** → despliega ETCD automáticamente
- **kube-system** → namespace donde se ejecuta el pod de ETCD
- **etcdctl dentro del pod** → permite explorar la base de datos de Kubernetes

Para listar todas las claves almacenadas por Kubernetes, se usa el comando **get** con **etcdctl**.

---

## Estructura de datos de Kubernetes en ETCD
Kubernetes guarda la información en una estructura específica de directorios dentro de ETCD. El directorio raíz es **registry**, y debajo de él se organizan los distintos objetos de Kubernetes.

- **registry** → directorio raíz donde Kubernetes almacena sus datos
- **minions o nodes** → una de las categorías almacenadas
- **pods** → objetos guardados bajo la estructura de registry
- **replica sets** → también forman parte de la estructura almacenada
- **deployments** → otro de los recursos presentes en ETCD

---

## ETCD en alta disponibilidad
En un entorno de **high availability**, habrá múltiples **master nodes** en el cluster, y por tanto varias instancias de ETCD distribuidas entre ellos. En ese escenario, es necesario asegurarse de que las instancias de ETCD se conozcan entre sí mediante la configuración adecuada del servicio.

- **multiple master nodes** → base de un entorno de alta disponibilidad
- **multiple ETCD instances** → instancias distribuidas entre los master nodes
- **initial cluster** → parámetro donde se especifican las diferentes instancias de ETCD

El detalle completo sobre **high availability**, el funcionamiento en modo cluster, el protocolo **Raft** y las mejores prácticas sobre el número de nodos se aborda más adelante en el curso.

---

## Resumen Visual
```text
ETCD
├── Naturaleza
│   ├── distributed
│   ├── reliable
│   └── key value store
├── Modelos de almacenamiento
│   ├── relational databases
│   │   ├── rows and columns
│   │   ├── SQL
│   │   └── rigid schema
│   ├── document store
│   │   ├── documentos independientes
│   │   ├── JSON
│   │   └── semi structured data
│   └── key value store
│       ├── key -> value
│       ├── no schema
│       ├── no complex queries
│       └── super fast
├── Uso básico
│   ├── descargar binary
│   ├── extraer y ejecutar
│   ├── escucha en port 2379
│   └── cliente etcdctl
│       ├── put
│       ├── get
│       └── delete
├── Versiones
│   ├── v2
│   │   ├── set
│   │   ├── get
│   │   └── rm
│   └── v3
│       ├── put
│       ├── get
│       ├── delete
│       └── transactions
└── Rol en Kubernetes
    ├── almacena estado del cluster
    │   ├── nodes
    │   ├── pods
    │   ├── configs
    │   ├── secrets
    │   ├── accounts
    │   ├── roles
    │   └── role bindings
    ├── fuente de kubectl get
    ├── despliegue
    │   ├── desde cero
    │   │   ├── binarios
    │   │   ├── service en master node
    │   │   └── advertised client URL
    │   └── con KubeADM
    │       ├── pod en kube-system
    │       └── uso de etcdctl dentro del pod
    ├── estructura de datos
    │   └── registry
    │       ├── nodes
    │       ├── pods
    │       ├── replica sets
    │       └── deployments
    └── high availability
        ├── multiple master nodes
        ├── multiple ETCD instances
        └── initial cluster
```text
