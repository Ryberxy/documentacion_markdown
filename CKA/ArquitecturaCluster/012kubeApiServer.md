---
titulo: Kube API server en Kubernetes
tipo: documento
---

# Kube API server en Kubernetes

## Visión General
El **Kube API server** es el componente principal de gestión dentro de Kubernetes y está en el centro de las operaciones del cluster. Se encarga de autenticar y validar solicitudes, interactuar con **etcd** y coordinar la comunicación entre los distintos componentes.

---

## Rol del Kube API server
El **Kube API server** es el componente principal de administración en Kubernetes. Cuando se ejecuta un comando con **kubectl**, en realidad la herramienta se comunica con el **Kube API server**.

- **kubectl** → cliente que envía solicitudes al **Kube API server**
- **Kube API server** → componente central de gestión del cluster
- **API directa** → también se puede invocar sin **kubectl**, enviando una solicitud **POST**

---

## Flujo de una solicitud al API server
Cuando llega una solicitud al **Kube API server**, este primero la autentica y la valida. Después consulta la información en el cluster de **etcd** y responde con los datos solicitados.

- <span class="truncated-code-wrapper" data-full-text="**authenticate**" title="**authenticate**"><code class="truncated-code">**authenticate*…</code><span class="copy-code-inline-btn" data-copy="**authenticate**"></span></span> → verifica la identidad de la solicitud
- **validate** → comprueba que la solicitud sea válida
- **retrieve data from etcd** → obtiene la información desde **etcd**
- **respond back** → devuelve la respuesta al usuario o cliente

---

## Ejemplo: creación de un pod
Cuando se crea un **pod**, el proceso sigue un patrón concreto coordinado por el **Kube API server**. Primero, la solicitud se autentica y valida. Después, el API server crea el objeto **pod** sin asignarlo todavía a ningún **node**, actualiza la información en **etcd** e informa al usuario de que el pod ha sido creado.

A continuación, el **scheduler** detecta que existe un nuevo pod sin nodo asignado, identifica el **node** adecuado y comunica esa decisión al **Kube API server**. El API server actualiza de nuevo la información en **etcd** y transmite la instrucción al **kubelet** del **worker node** <span class="truncated-code-wrapper" data-full-text="correspondiente." title="correspondiente."><code class="truncated-code">correspondiente…</code><span class="copy-code-inline-btn" data-copy="correspondiente."></span></span> El **kubelet** crea el pod en el nodo e indica al **container runtime engine** que despliegue la imagen de la aplicación. Una vez completado, el kubelet actualiza el estado en el API server y este vuelve a registrar el cambio en **etcd**.

- **pod object** → se crea inicialmente sin nodo asignado
- **scheduler** → detecta pods sin asignación y elige el nodo adecuado
- **kubelet** → crea el pod en el **worker node**
- **container runtime engine** → despliega la imagen de la aplicación
- **status update** → el **kubelet** informa del estado al **Kube API server**
- **etcd update** → el API server registra cada cambio en **etcd**

### Patrón general de cambios en el cluster
Este mismo patrón se sigue cada vez que se solicita un cambio en el cluster. El **Kube API server** está en el centro de todas las tareas necesarias para ejecutar cualquier modificación.

- **center of all tasks** → coordina los cambios dentro del cluster
- **change requested** → cualquier cambio pasa por el API server

---

## <span class="truncated-code-wrapper" data-full-text="Responsabilidades" title="Responsabilidades"><code class="truncated-code">Responsabilidad…</code><span class="copy-code-inline-btn" data-copy="Responsabilidades"></span></span> principales
El **Kube API server** tiene varias <span class="truncated-code-wrapper" data-full-text="responsabilidades" title="responsabilidades"><code class="truncated-code">responsabilidad…</code><span class="copy-code-inline-btn" data-copy="responsabilidades"></span></span> esenciales en Kubernetes. Se encarga de autenticar y validar solicitudes, así como de recuperar y actualizar datos en el almacén **etcd**.

Además, es el único componente que interactúa directamente con el almacén de datos **etcd**. Otros componentes como el **scheduler**, **kube controller manager** y **kubelet** utilizan el API server para realizar cambios en sus respectivas áreas.

- **authenticate requests** → autentica las solicitudes
- **validate requests** → valida las solicitudes
- **retrieve data** → recupera datos desde **etcd**
- **update data** → actualiza datos en **etcd**
- **only direct component to etcd** → es el único componente que accede directamente a **etcd**
- **scheduler / kube controller manager / kubelet** → usan el API server para actualizar el cluster

---

## Instalación del Kube API server
Si el cluster se ha desplegado usando **kubeadm**, no es necesario profundizar en la instalación manual. Pero si el cluster se configura **the hard way**, el **Kube API server** se obtiene como un binario desde la página de releases de Kubernetes, se descarga y se configura para ejecutarse como un servicio en el **master node**.

- **kubeadm** → simplifica el despliegue del **Kube API server**
- **binary** → forma en que se distribuye para instalación manual
- **service** → se configura como servicio en el **master node**
- **the hard way** → instalación y configuración manual del componente

---

## Parámetros y configuración
El **Kube API server** se ejecuta con muchos parámetros. Esto se debe a que la arquitectura de Kubernetes tiene muchos componentes que deben comunicarse entre sí y todos necesitan saber dónde están los demás.

También existen diferentes modos de <span class="truncated-code-wrapper" data-full-text="**authentication**," title="**authentication**,"><code class="truncated-code">**authenticatio…</code><span class="copy-code-inline-btn" data-copy="**authentication**,"></span></span> <span class="truncated-code-wrapper" data-full-text="**authorization**," title="**authorization**,"><code class="truncated-code">**authorization…</code><span class="copy-code-inline-btn" data-copy="**authorization**,"></span></span> **encryption** y seguridad, lo que explica la gran cantidad de opciones disponibles. Muchas de estas opciones están relacionadas con <span class="truncated-code-wrapper" data-full-text="**certificates**," title="**certificates**,"><code class="truncated-code">**certificates*…</code><span class="copy-code-inline-btn" data-copy="**certificates**,"></span></span> utilizados para asegurar la conectividad entre componentes.

- **many parameters** → el API server requiere numerosas opciones de configuración
- <span class="truncated-code-wrapper" data-full-text="**authentication**" title="**authentication**"><code class="truncated-code">**authenticatio…</code><span class="copy-code-inline-btn" data-copy="**authentication**"></span></span> → mecanismo para verificar identidades
- <span class="truncated-code-wrapper" data-full-text="**authorization**" title="**authorization**"><code class="truncated-code">**authorization…</code><span class="copy-code-inline-btn" data-copy="**authorization**"></span></span> → mecanismo para controlar permisos
- **encryption** → protege la comunicación
- **security** → conjunto de opciones relacionadas con protección del sistema
- <span class="truncated-code-wrapper" data-full-text="**certificates**" title="**certificates**"><code class="truncated-code">**certificates*…</code><span class="copy-code-inline-btn" data-copy="**certificates**"></span></span> → usados para asegurar la conectividad entre componentes

### Opción importante: etcd servers
Entre los parámetros, uno de los más importantes es **etcd servers**, que indica la ubicación de los servidores **etcd**. Gracias a esta opción, el **Kube API server** puede conectarse al almacén **etcd**.

- **etcd servers** → especifica dónde están los servidores **etcd**
- **connection to etcd** → permite al API server interactuar con el datastore del cluster

---

## Cómo ver las opciones del Kube API server en un cluster existente

### En un cluster creado con kubeadm
Si el cluster se creó con **kubeadm**, este despliega el **Kube API server** como un **pod** en el namespace **kube-system** sobre el **master node**. Las opciones se pueden consultar dentro del archivo de definición del pod, ubicado en el directorio **/etc**.

- **kubeadm** → despliega el API server como **pod**
- **kube-system** → namespace donde se ejecuta
- **pod definition file** → contiene las opciones del componente
- **/etc** → ubicación mencionada para consultar la definición

### En un cluster no creado con kubeadm
En una instalación que no usa **kubeadm**, las opciones pueden revisarse viendo el servicio del **kubeapi server** ubicado en **/etc**. También es posible inspeccionar el proceso en ejecución dentro del **master node** y buscar **kube API server** para ver las opciones efectivas.

- **service located at /etc** → permite inspeccionar la configuración
- **running process** → muestra las opciones efectivas en uso
- **master node** → nodo donde se inspecciona el proceso del API server

---

## Resumen Visual
```text
Kube API server
├── Rol principal
│   ├── componente principal de gestión
│   ├── punto central de cambios en el cluster
│   └── receptor de solicitudes de kubectl o API directa
├── Flujo de solicitud
│   ├── authenticate
│   ├── validate
│   ├── <span class="truncated-code-wrapper" data-full-text="consultar/actualizar" title="consultar/actualizar"><code class="truncated-code">consultar/actua…</code><span class="copy-code-inline-btn" data-copy="consultar/actualizar"></span></span> etcd
│   └── responder al cliente
├── Ejemplo de creación de pod
│   ├── API server crea pod object sin node
│   ├── actualiza etcd
│   ├── scheduler detecta pod sin asignación
│   ├── scheduler elige node
│   ├── API server actualiza etcd
│   ├── API server informa al kubelet
│   ├── kubelet crea el pod
│   ├── container runtime engine despliega la imagen
│   ├── kubelet actualiza estado al API server
│   └── API server actualiza etcd
├── <span class="truncated-code-wrapper" data-full-text="Responsabilidades" title="Responsabilidades"><code class="truncated-code">Responsabilidad…</code><span class="copy-code-inline-btn" data-copy="Responsabilidades"></span></span>
│   ├── authenticate requests
│   ├── validate requests
│   ├── retrieve data from etcd
│   ├── update data in etcd
│   └── único acceso directo a etcd
├── Otros componentes que dependen de él
│   ├── scheduler
│   ├── kube controller manager
│   └── kubelet
├── Instalación
│   ├── con kubeadm
│   │   └── despliegue automático
│   └── the hard way
│       ├── descargar binary
│       └── configurar como service en master node
└── Configuración
    ├── many parameters
    ├── authentication
    ├── authorization
    ├── encryption
    ├── security
    ├── certificates
    └── etcd servers
        └── ubicación de los servidores etcd
```text
