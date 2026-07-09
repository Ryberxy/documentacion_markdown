---
titulo: Arquitectura de Kubernetes
tipo: documento
---

# 01 Arquitectura de Kubernetes

## Visión General

En este tema se presenta una visión general de la arquitectura de un clúster de Kubernetes y de los componentes principales que trabajan juntos para gestionar aplicaciones en forma de contenedores. Se revisan sus responsabilidades, cómo se relacionan entre ellos y cómo permiten desplegar, gestionar y comunicar servicios dentro del clúster.

Para entender la arquitectura se utiliza una analogía con barcos: los **worker nodes** representan barcos de carga que ejecutan el trabajo, mientras que el **Control Plane** representa los barcos de control encargados de gestionar y supervisar todo el sistema.

---

## Arquitectura general del clúster Kubernetes

El propósito de Kubernetes es alojar aplicaciones en forma de **containers** de manera automatizada.

Kubernetes permite:

- Desplegar aplicaciones con el número de instancias necesario.
- Gestionar la comunicación entre diferentes servicios.
- Administrar automáticamente los componentes que forman parte del clúster.

Un clúster de Kubernetes está formado por un conjunto de **nodes**, que pueden ser:

- **Physical nodes**.
- **Virtual nodes**.
- Nodos en infraestructura **on-premise**.
- Nodos en infraestructura cloud.

Estos nodos alojan aplicaciones en forma de **containers**.

---

## Analogía de los barcos

Para entender la arquitectura de Kubernetes se utiliza una analogía con dos tipos de barcos:

### Barcos de carga

Los **cargo ships** son los barcos que realizan el trabajo real de transportar contenedores.

En Kubernetes representan a los **worker nodes**.

- **worker node** → nodo donde se ejecutan los containers.
- **container** → aplicación que se despliega dentro del nodo.

---

### Barcos de control

Los **control ships** son responsables de:

- Supervisar los barcos de carga.
- Gestionar la carga.
- Planificar dónde colocar los contenedores.
- Mantener información sobre los barcos.
- Controlar todo el proceso.

En Kubernetes representan el **master node** o **Control Plane**.

---

## Control Plane (Master Node)

El **Control Plane** es el encargado de gestionar el clúster Kubernetes.

Sus responsabilidades principales son:

- **Gestionar el clúster** → controla las operaciones generales.
- **Almacenar información de los nodes** → mantiene datos sobre los diferentes componentes.
- **Planificar dónde colocar containers** → decide dónde deben ejecutarse.
- **Monitorizar nodes y containers** → comprueba el estado del sistema.

El Control Plane realiza estas tareas mediante un conjunto de componentes conocidos como **Control Plane Components**.

---

## etcd

**etcd** es el sistema donde Kubernetes almacena la información del clúster.

En la analogía de los barcos representa el sistema donde se guarda información como:

- Qué contenedor está en cada barco.
- Cuándo fue cargado.
- Información sobre los barcos.

Características principales:

- **Base de datos key-value** → almacena información en formato clave-valor.
- **Highly available store** → almacén de alta disponibilidad.

Ejemplo:


Key:
container/application

Value:
running on worker-node-1


---

## kube-scheduler

El **kube-scheduler** es el componente encargado de decidir en qué node se debe colocar un container.

En la analogía representa las grúas que deciden:

- Qué contenedor cargar.
- En qué barco colocarlo.

Para tomar la decisión analiza:

- **Container resource requirements** → requisitos de recursos del container.
- **Worker node capacity** → capacidad disponible del node.
- **Policies and constraints** → políticas y restricciones.

Ejemplos de restricciones:

- **Taints and tolerations**.
- **Node affinity rules**.

El scheduler identifica el node más adecuado para ejecutar una aplicación.

---

## Controllers

Los **controllers** son componentes que gestionan diferentes áreas del clúster.

En la analogía representan los diferentes departamentos del puerto:

- Departamento de operaciones.
- Departamento de carga.
- Departamento de servicios.

Cada controller tiene una responsabilidad específica.

---

### Node Controller

El **Node Controller** se encarga de gestionar los nodes.

Responsabilidades:

- **Añadir nuevos nodes al clúster**.
- **Gestionar nodes no disponibles**.
- Gestionar situaciones donde un node desaparece o es destruido.

---

### Replication Controller

El **Replication Controller** garantiza que exista siempre el número deseado de containers ejecutándose dentro de un grupo de replicación.

Ejemplo:

Configuración deseada:


3 containers running


Si uno falla:


2 containers running


El controller crea uno nuevo para volver al estado esperado.

---

## kube-apiserver

El **kube-apiserver** es el componente principal de gestión de Kubernetes.

Es responsable de coordinar las operaciones dentro del clúster.

Funciones principales:

- **Exponer la Kubernetes API**.
- Permitir que usuarios externos realicen operaciones de administración.
- Permitir que los controllers consulten el estado del clúster.
- Permitir que los worker nodes se comuniquen con el servidor.

El kube-apiserver es el punto central de comunicación entre los componentes.

---

## Container Runtime

Kubernetes trabaja completamente con containers, por lo que necesita un software capaz de ejecutarlos.

Este software se conoce como **container runtime engine**.

Ejemplos:

- **Docker**.
- **containerd**.
- **rkt**.

El container runtime debe estar instalado en los nodes del clúster.

Puede instalarse también en los master nodes si los componentes del Control Plane se ejecutan como containers.

---

## Worker Nodes

Los **worker nodes** son los nodos donde se ejecutan las aplicaciones.

Cada worker node contiene componentes encargados de ejecutar y gestionar containers.

Los principales componentes son:

- **kubelet**.
- **kube-proxy**.
- Container runtime.

---

## kubelet

El **kubelet** es un agente que se ejecuta en cada node del clúster.

En la analogía representa al capitán del barco.

Responsabilidades:

- Comunicarse con el **kube-apiserver**.
- Recibir instrucciones del Control Plane.
- Crear containers.
- Destruir containers cuando sea necesario.
- Enviar información del estado del node y de los containers.

El kube-apiserver consulta periódicamente al kubelet para conocer:

- Estado del node.
- Estado de los containers.

---

## kube-proxy

El **kube-proxy** permite la comunicación entre aplicaciones que se ejecutan en diferentes worker nodes.

Ejemplo:


Web Server Container

    |

    |

Database Container


Aunque estén en diferentes nodes, kube-proxy permite que puedan comunicarse.

Responsabilidades:

- Mantener las reglas necesarias de red.
- Permitir que los containers puedan comunicarse entre ellos.
- Facilitar la comunicación entre servicios dentro del clúster.

---

## Resumen de componentes principales

| Componente | Ubicación | Responsabilidad |
|---|---|---|
| **kube-apiserver** | Control Plane | Coordina las operaciones del clúster y expone la API |
| **etcd** | Control Plane | Guarda información del clúster en formato key-value |
| **kube-scheduler** | Control Plane | Decide dónde ejecutar containers |
| **Controllers** | Control Plane | Gestionan diferentes áreas del clúster |
| **Node Controller** | Control Plane | Gestiona el estado de los nodes |
| **Replication Controller** | Control Plane | Mantiene el número deseado de containers |
| **kubelet** | Worker Node | Ejecuta instrucciones y gestiona containers |
| **kube-proxy** | Worker Node | Permite comunicación entre servicios |
| **Container Runtime** | Worker Node | Ejecuta los containers |

---

## Resumen Visual

```text
Kubernetes Cluster

|
|
+------------------------------------------------+
|
|
+---------------------+
|    Control Plane     |
+---------------------+
|
|-- kube-apiserver
|       |
|       +-- Kubernetes API
|
|-- etcd
|       |
|       +-- Cluster information
|
|-- kube-scheduler
|       |
|       +-- Selects worker node
|
|-- Controllers
        |
        +-- Node Controller
        |
        +-- Replication Controller


|
|
+---------------------+
|    Worker Nodes      |
+---------------------+
|
|-- kubelet
|       |
|       +-- Manages containers
|
|-- kube-proxy
|       |
|       +-- Enables communication
|
|-- Container Runtime
        |
        +-- Runs containers
