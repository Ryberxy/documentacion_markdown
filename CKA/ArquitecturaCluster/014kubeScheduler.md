---
titulo: Kube Scheduler en Kubernetes
tipo: documento
---

# Kube Scheduler en Kubernetes

## Visión General
El **Kube Scheduler** es el componente encargado de decidir en qué **node** debe ejecutarse cada **pod**. Su función no es crear el pod en el nodo, sino seleccionar el mejor destino según ciertos criterios como recursos disponibles y reglas de ubicación.

---

## Qué hace el Kube Scheduler
El **Kubernetes scheduler** es responsable de decidir qué **pod** va en qué **node**. Es importante no confundir su función con la del **kubelet**: el scheduler no coloca realmente el pod en el nodo, solo toma la decisión de ubicación.

- **Kube Scheduler** → decide en qué nodo debe ejecutarse un pod
- **kubelet** → es quien crea realmente el pod en el nodo
- **scheduling** → proceso de decisión sobre la ubicación de los pods

---

## Por qué se necesita un scheduler
Cuando hay muchos nodos y muchos pods, es necesario asegurar que cada pod termine en el nodo adecuado. En la analogía de los barcos, no todos los barcos tienen el mismo tamaño ni todos los contenedores tienen las mismas necesidades, por lo que hay que elegir correctamente dónde ubicar cada uno.

También puede ocurrir que distintos nodos estén orientados a diferentes propósitos o aplicaciones. Por eso, en Kubernetes el scheduler evalúa distintos criterios antes de decidir dónde se colocará un pod.

- **right pod on the right node** → objetivo principal del scheduling
- **capacity** → el nodo debe tener capacidad suficiente
- **different destinations** → analogía usada para explicar que no todos los nodos son equivalentes
- **resource requirements** → los pods pueden tener requisitos distintos
- **dedicated nodes** → algunos nodos pueden estar dedicados a ciertas aplicaciones

---

## Cómo decide el scheduler
El scheduler analiza cada **pod** e intenta encontrar el mejor **node** para él. Para ello sigue un proceso de dos fases.

### Fase 1: filtrado
En la primera fase, el scheduler descarta los nodos que no cumplen con el perfil necesario para el pod. Por ejemplo, elimina aquellos que no tienen suficiente **CPU** o **memory** para satisfacer los recursos solicitados por ese pod.

- **filtering** → fase en la que se descartan nodos no válidos
- **CPU requirements** → criterio de recursos evaluado
- **memory requirements** → otro criterio de recursos evaluado
- **nodes that do not fit** → nodos eliminados por no cumplir el perfil

### Fase 2: ranking
Después del filtrado, el scheduler compara los nodos restantes para elegir el mejor ajuste. Para ello utiliza una **priority function** que asigna una puntuación a cada nodo en una escala de **0 a 10**.

Un ejemplo mostrado es calcular cuántos recursos quedarían libres en cada nodo después de colocar el pod. Si un nodo deja más **CPU** libre que otro tras la asignación, puede recibir una puntuación mayor y resultar elegido.

- **ranking** → comparación de nodos válidos para elegir el mejor
- **priority function** → función usada para puntuar los nodos
- **0 to 10** → escala de puntuación utilizada
- **best fit** → nodo que mejor encaja para el pod
- **free resources after placement** → criterio usado en el ejemplo para decidir

---

## Personalización del scheduling
El funcionamiento del scheduler puede personalizarse y también es posible escribir un **custom scheduler**. Además, el tema del scheduling incluye muchos otros conceptos que se estudiarán más adelante con mayor detalle.

- **custom scheduler** → se puede crear un scheduler propio
- **resource requirements** → forman parte de los criterios de planificación
- **limits** → se tratarán en la sección dedicada a scheduling
- **taints and tolerations** → reglas relacionadas con la asignación de pods
- **node selectors** → mecanismo para influir en la selección de nodos
- **affinity rules** → reglas adicionales de ubicación

---

## Instalación del Kube Scheduler
Para instalar el **Kube Scheduler**, se descarga el binario desde la página de releases de Kubernetes, se extrae y se ejecuta como un servicio. Al ejecutarlo como servicio, se debe especificar el archivo de configuración del scheduler.

- **binary** → archivo descargado para instalar el scheduler
- **Kubernetes release page** → lugar desde donde se obtiene
- **run it as a service** → forma de ejecución indicada
- **scheduler configuration file** → archivo que se especifica al arrancar el servicio

---

## Cómo ver las opciones del Kube Scheduler

### En un cluster creado con KubeADM
Si el cluster se ha creado con **KubeADM**, esta herramienta despliega el **Kube Scheduler** como un **pod** en el namespace **kube-system** sobre el **master node**. Las opciones pueden verse dentro del archivo de definición del pod ubicado en <span class="truncated-code-wrapper" data-full-text="**/etc/kubernetes/manifests**." title="**/etc/kubernetes/manifests**."><code class="truncated-code">**/etc/kubernet…</code><span class="copy-code-inline-btn" data-copy="**/etc/kubernetes/manifests**."></span></span>

- **KubeADM** → despliega automáticamente el scheduler
- **pod** → formato en que se ejecuta en este tipo de instalación
- **kube-system** → namespace donde se encuentra
- **master node** → nodo donde corre el componente
- <span class="truncated-code-wrapper" data-full-text="**/etc/kubernetes/manifests**" title="**/etc/kubernetes/manifests**"><code class="truncated-code">**/etc/kubernet…</code><span class="copy-code-inline-btn" data-copy="**/etc/kubernetes/manifests**"></span></span> → ruta donde se revisa la definición del pod

### Ver proceso y opciones efectivas
También se puede revisar el proceso en ejecución y sus opciones efectivas listando los procesos del **master node** y buscando **Kube Scheduler**.

- **running process** → permite inspeccionar la ejecución real
- **effective options** → muestra las opciones que se están usando
- **search for Kube Scheduler** → forma de localizar el proceso

---

## Resumen Visual
```text
Kube Scheduler
├── Función principal
│   ├── decide qué pod va en qué node
│   └── no crea el pod en el nodo
├── Diferencia con kubelet
│   ├── scheduler decide
│   └── kubelet crea el pod
├── Motivos para usar scheduler
│   ├── muchos pods y muchos nodes
│   ├── capacidad diferente entre nodes
│   ├── resource requirements distintos
│   └── dedicated nodes para ciertas aplicaciones
├── Proceso de decisión
│   ├── Fase 1: filtering
│   │   ├── descarta nodes sin suficiente CPU
│   │   └── descarta nodes sin suficiente memory
│   └── Fase 2: ranking
│       ├── usa priority function
│       ├── asigna score de 0 a 10
│       └── elige el best fit
├── Criterios y temas relacionados
│   ├── resource requirements
│   ├── limits
│   ├── taints and tolerations
│   ├── node selectors
│   └── affinity rules
├── Personalización
│   └── custom scheduler
├── Instalación
│   ├── descargar binary
│   ├── extraer
│   ├── ejecutar como service
│   └── indicar scheduler configuration file
└── Dónde ver opciones
    ├── con KubeADM
    │   ├── pod en kube-system
    │   └── <span class="truncated-code-wrapper" data-full-text="/etc/kubernetes/manifests" title="/etc/kubernetes/manifests"><code class="truncated-code">/etc/kubernetes…</code><span class="copy-code-inline-btn" data-copy="/etc/kubernetes/manifests"></span></span>
    └── proceso en master node
        └── effective options
```text
