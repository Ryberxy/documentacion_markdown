---
titulo: Kube Controller Manager en Kubernetes
tipo: documento
---

# Kube Controller Manager en Kubernetes

## Visión General
El **Kube Controller Manager** agrupa y ejecuta varios **controllers** de Kubernetes. Estos procesos monitorizan continuamente el estado del cluster y realizan acciones para llevar el sistema al **desired state**.

---

## Qué es un controller
Un **controller** puede entenderse como una oficina o departamento dentro del barco maestro de la analogía de Kubernetes. Cada uno tiene <span class="truncated-code-wrapper" data-full-text="responsabilidades" title="responsabilidades"><code class="truncated-code">responsabilidad…</code><span class="copy-code-inline-btn" data-copy="responsabilidades"></span></span> concretas, como vigilar el estado de ciertos componentes y actuar cuando ocurre algún cambio o problema.

En Kubernetes, un **controller** es un proceso que observa continuamente el estado de varios componentes del sistema y trabaja para que todo vuelva o permanezca en el estado deseado.

- **controller** → proceso que monitoriza componentes y corrige desviaciones
- **desired state** → estado de funcionamiento esperado del sistema
- **monitoring** → observación continua del estado del cluster
- **remediation** → acciones necesarias para corregir una situación

---

## Funcionamiento general de los controllers
Los controllers realizan dos funciones principales: vigilar el estado de los componentes y ejecutar acciones cuando detectan una situación que requiere corrección. Por eso se consideran una parte esencial de la lógica de Kubernetes.

- **continuous monitoring** → supervisión constante del estado de los recursos
- **necessary actions** → acciones para mantener el sistema funcionando correctamente
- **brain behind Kubernetes** → idea usada para destacar su importancia en el comportamiento del sistema

---

## Node Controller
El **Node Controller** es responsable de monitorizar el estado de los **nodes** y tomar las acciones necesarias para mantener las aplicaciones en funcionamiento. Para ello se apoya en el **Kube API server**.

El **Node Controller** comprueba el estado de los nodos cada **5 segundos**. Si deja de recibir el **heartbeat** de un nodo, lo marca como <span class="truncated-code-wrapper" data-full-text="**unreachable**," title="**unreachable**,"><code class="truncated-code">**unreachable**…</code><span class="copy-code-inline-btn" data-copy="**unreachable**,"></span></span> pero espera **40 segundos** antes de hacerlo. Después de marcarlo como inalcanzable, le concede **5 minutos** para volver a estar disponible. Si no regresa en ese tiempo, elimina los **pods** asignados a ese nodo y los aprovisiona en nodos sanos, siempre que esos pods formen parte de un **replica set**.

- **Node Controller** → monitoriza nodos y actúa ante fallos
- **Kube API server** → canal a través del cual actúa el controller
- **every 5 seconds** → frecuencia con la que revisa el estado de los nodos
- **heartbeat** → señal usada para comprobar la salud del nodo
- **unreachable** → estado asignado a un nodo cuando no responde
- **40 seconds** → tiempo de espera antes de marcar un nodo como inalcanzable
- **5 minutes** → tiempo concedido para que el nodo vuelva
- **remove pods** → acción que realiza si el nodo no se recupera
- **replica set** → condición bajo la que los pods se vuelven a aprovisionar en nodos saludables

---

## Replication Controller
El **Replication Controller** se encarga de monitorizar el estado de los **replica sets** y garantizar que el número deseado de **pods** esté disponible en todo momento dentro del conjunto. Si un pod deja de funcionar o muere, crea otro para reemplazarlo.

- **Replication Controller** → mantiene el número deseado de pods
- **replica sets** → conjunto cuyo estado supervisa
- **desired number of pods** → cantidad de pods que debe estar disponible
- **if a pod dies, it creates another one** → comportamiento básico de recuperación

---

## Otros controllers en Kubernetes
Los controllers no se limitan solo al **Node Controller** y al **Replication Controller**. Kubernetes dispone de muchos más controllers. La lógica e inteligencia de conceptos como <span class="truncated-code-wrapper" data-full-text="**deployments**," title="**deployments**,"><code class="truncated-code">**deployments**…</code><span class="copy-code-inline-btn" data-copy="**deployments**,"></span></span> **services**, **namespaces** o **persistent volumes** se implementa a través de estos controllers.

- **deployments** → su comportamiento se implementa mediante controllers
- **services** → también dependen de controllers
- **namespaces** → forman parte de los conceptos gestionados por controllers
- **persistent volumes** → su lógica también se implementa con controllers
- **many more controllers** → existen numerosos controllers adicionales en Kubernetes

---

## Qué es el Kube Controller Manager
Todos estos controllers están empaquetados dentro de un único proceso llamado **Kubernetes Controller Manager**. Cuando se instala el **Kube Controller Manager**, también se instalan los distintos controllers que forman parte de él.

- **Kubernetes Controller Manager** → proceso único que agrupa los controllers
- **single process** → forma en que se empaquetan los controllers
- **install the Controller Manager** → al instalarlo, se incluyen los controllers

---

## Instalación del Kube Controller Manager
Para instalar el **Kube Controller Manager**, se descarga desde la página de releases de Kubernetes, se extrae y se ejecuta como un servicio. Al arrancarlo, se le pueden pasar diferentes opciones para personalizar su comportamiento.

- **download from Kubernetes release page** → origen del binario
- **extract** → paso previo a su ejecución
- **run it as a service** → forma de despliegue indicada
- **options** → parámetros para personalizar el comportamiento de los controllers

---

## Opciones de configuración
Entre las opciones configurables se encuentran algunos valores por defecto del **Node Controller** mencionados anteriormente, como el **node monitor period**, el **grace period** y el **eviction timeout**. También existe una opción llamada <span class="truncated-code-wrapper" data-full-text="**controllers**," title="**controllers**,"><code class="truncated-code">**controllers**…</code><span class="copy-code-inline-btn" data-copy="**controllers**,"></span></span> que permite especificar qué controllers se quieren habilitar.

Por defecto, todos los controllers están habilitados, pero se puede elegir activar solo algunos. Si algún controller no parece funcionar o no está disponible, este es un buen punto inicial para revisar la configuración.

- **node monitor period** → intervalo de supervisión del nodo
- **grace period** → tiempo de espera antes de considerar un problema
- **eviction timeout** → tiempo relacionado con la expulsión o reubicación
- **controllers** → opción para indicar qué controllers habilitar
- **all enabled by default** → comportamiento predeterminado
- **good starting point to look at** → lugar recomendado para revisar si algo falla

---

## Cómo ver las opciones del Kube Controller Manager

### En un cluster creado con kubeadm
Si el cluster se ha creado con **kubeadm**, este despliega el **Kube Controller Manager** como un **pod** en el namespace **kube-system** sobre el **master node**. Las opciones se pueden consultar en el directorio de manifiestos de Kubernetes.

- **kubeadm** → despliega el componente automáticamente
- **pod** → formato en que se ejecuta en este tipo de instalación
- **kube-system** → namespace donde se encuentra
- **master node** → nodo donde se ejecuta
- **kubernetes manifest folder** → ubicación donde revisar las opciones

### En un cluster no creado con kubeadm
En una instalación no basada en **kubeadm**, se pueden inspeccionar las opciones revisando el servicio del **Kube Controller Manager** ubicado en el directorio de servicios. También se puede listar el proceso en ejecución en el **master node** y buscar **Kube controller manager** para ver las opciones efectivas.

- **service located at the services directory** → ubicación de revisión en instalaciones no kubeadm
- **running process** → muestra la configuración efectiva
- **master node** → lugar donde inspeccionar el proceso

---

## Resumen Visual
```text
Kube Controller Manager
├── Función principal
│   ├── agrupa múltiples controllers
│   ├── monitoriza el estado del cluster
│   └── lleva el sistema al desired state
├── Qué es un controller
│   ├── monitoriza componentes
│   ├── detecta problemas o cambios
│   └── ejecuta acciones correctivas
├── Controllers destacados
│   ├── Node Controller
│   │   ├── revisa nodes cada 5 seconds
│   │   ├── detecta falta de heartbeat
│   │   ├── marca unreachable tras 40 seconds
│   │   ├── espera 5 minutes
│   │   └── elimina y reprovisiona pods si pertenecen a replica set
│   └── Replication Controller
│       ├── monitoriza replica sets
│       ├── asegura desired number of pods
│       └── crea otro pod si uno muere
├── Otros recursos gestionados mediante controllers
│   ├── deployments
│   ├── services
│   ├── namespaces
│   └── persistent volumes
├── Instalación
│   ├── descargar desde Kubernetes release page
│   ├── extraer
│   └── ejecutar como service
├── Configuración
│   ├── node monitor period
│   ├── grace period
│   ├── eviction timeout
│   └── controllers
│       ├── todos habilitados por defecto
│       └── permite habilitar solo algunos
└── Dónde ver opciones
    ├── con kubeadm
    │   ├── pod en kube-system
    │   └── kubernetes manifest folder
    └── sin kubeadm
        ├── service en services directory
        └── proceso en master node
```text
