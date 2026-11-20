---
titulo: Construcción de agentes para producción
tipo: documento
---

# 027 Construcción de agentes para producción

## Visión General

Un **agente** es un ciclo de tool use de varios pasos que persigue un objetivo y gestiona su contexto. Su construcción requiere decidir si realmente se necesita un agente, seleccionar cómo ejecutar el ciclo y definir herramientas, condiciones de salida, puntos de revisión humana y restricciones de datos.

---

## Workflow o agente

Antes de construir un agente se debe determinar si un **workflow** más sencillo puede resolver el problema. Los agentes añaden complejidad de coordinación, costes de contexto y más posibilidades de fallo.

### Cuándo elegir un workflow

Un **workflow** es adecuado cuando:

- Los pasos pueden enumerarse en código.
- Todas las ejecuciones siguen la misma secuencia.
- Las entradas pertenecen a un conjunto conocido y limitado.
- El coste de los errores exige guardrails en cada paso.
- Se necesita observabilidad mediante herramientas estándar.

### Cuándo elegir un agente

Un **agente** es adecuado cuando:

- Se conocen el objetivo y las herramientas, pero no la ruta exacta.
- La secuencia de acciones no puede enumerarse de antemano.
- Las entradas varían de forma impredecible.
- La tarea requiere combinar herramientas de manera flexible.
- Se acepta el comportamiento no determinista y las acciones están limitadas por las herramientas registradas.

La progresión recomendada es comenzar con el patrón más sencillo que resuelva el problema:

1. Una llamada individual a la API.
2. Un workflow.
3. Un agente.

Se debe avanzar al siguiente nivel solo cuando el anterior no pueda gestionar la variabilidad necesaria.

---

## Patrón del agente y opciones de implementación

En un sistema de un solo agente, el patrón básico es un ciclo que llama herramientas, gestiona el contexto y continúa hasta alcanzar una condición de salida.

Las arquitecturas **multi-agent**, con agentes separados para planificación, ejecución y evaluación que intercambian artefactos estructurados, añaden decisiones de diseño y se tratan más adelante en el curso.

Hay tres opciones para implementar el ciclo. La diferencia principal es cuánto de la infraestructura y del runtime mantiene la aplicación.

### Raw Messages API loop

Con un **raw Messages API loop**, el código de la aplicación ejecuta cada iteración:

- Envía la solicitud.
- Lee los tool-use blocks.
- Ejecuta las herramientas.
- Añade los resultados al historial.

La aplicación es responsable del ciclo completo, la ejecución de herramientas, la gestión de contexto, los retries y las condiciones de salida.

Es apropiado cuando se necesita control total, existen restricciones que una biblioteca no cubre o se desea aprender cómo funciona el ciclo antes de introducir una abstracción.

**Coste de mantenimiento** → las funciones que podría proporcionar un SDK, como la gestión de contexto y de herramientas en paralelo, deben implementarse y probarse.

### Agent SDK

El **Agent SDK** ejecuta el ciclo dentro del proceso de la aplicación y proporciona estructura para registrar herramientas, configurar el system prompt y gestionar las iteraciones.

La aplicación sigue participando en la ejecución de herramientas. Esta opción permite utilizar una estructura ya construida manteniendo el control del proceso.

### Claude Managed Agents

Con **Claude Managed Agents**, Anthropic ejecuta el ciclo y el sandbox en el servidor. Según la transcripción, este servicio se encuentra en **public beta**.

La aplicación define el agente como un recurso de API versionado, incluyendo:

- Modelo.
- System prompt.
- Herramientas.
- MCP servers.
- Skills.

Después, se refiere al agente mediante su ID, envía eventos de usuario y recibe los resultados mediante **server-sent events**.

La elección entre estas opciones debe tener en cuenta las restricciones de despliegue y cumplimiento, no solo la rapidez de creación de un prototipo.

---

## Cuándo utilizar Claude Managed Agents

Managed Agents puede ser adecuado para:

- **Tareas de larga duración** → sesiones que se ejecutan durante minutos u horas.
- **Sandbox gestionado** → cuando se quiere evitar construir y proteger un entorno de ejecución propio.
- **Menor infraestructura propia** → cuando no se desea implementar el ciclo ni la capa de ejecución de herramientas.

### Responsabilidades que cambian

| Área | Anthropic gestiona | La aplicación asume |
|---|---|---|
| **Ejecución e infraestructura** | El ciclo, el sandbox, los retries internos y el runtime de herramientas. | La definición versionada del agente y la capa que envía eventos y consume resultados. |
| **Duración y estado** | La ejecución prolongada y el estado de la sesión en el servidor. | Las implicaciones de almacenamiento y las políticas de tratamiento de datos aplicables. |
| **Sandbox** | Su creación y eliminación. | La dependencia de las herramientas y del modelo de ejecución disponibles en el sandbox gestionado. |

### Restricciones de datos

La transcripción indica que las sesiones de Managed Agents mantienen estado y se almacenan en el servidor. Por ello, señala que esta opción no es elegible para **Zero Data Retention (ZDR)** ni para un **HIPAA Business Associate Agreement (BAA)**.

Para cargas de trabajo con **PHI** o requisitos de ZDR, indica utilizar Agent SDK o un raw loop en una configuración cubierta.

### De prototipo a producción

Una progresión posible es crear un prototipo local con **Agent SDK** y después pasar a Managed Agents.

La definición conceptual del agente puede trasladarse, pero debe expresarse de nuevo:

- **Agent SDK** → configuración en código y en el filesystem.
- **Managed Agents** → recurso de API versionado.

No se presenta como una exportación directa.

---

## Los cuatro pasos del agent loop

El ciclo tiene los mismos pasos generales independientemente de la opción de implementación. Lo que cambia es cuánto implementa la aplicación y cuánto proporciona la herramienta elegida.

### 1. Registrar herramientas

Cada herramienta debe tener su schema y estar registrada para que Claude sepa que está disponible.

### 2. Configurar el system prompt

El **system prompt** debe delimitar la tarea del agente y nombrar las herramientas disponibles.

Un prompt amplio puede producir una selección de herramientas menos fiable. Uno centrado en la tarea y sus herramientas favorece un comportamiento más consistente.

### 3. Gestionar el tool-use loop

Cada llamada que Claude emite debe ejecutarse y recibir su correspondiente **tool-result block**.

En un raw loop o con Agent SDK, la aplicación debe gestionar la ejecución que le corresponda. En Managed Agents, el runtime de ejecución se gestiona en el servidor.

### 4. Definir condiciones de salida

El ciclo necesita un criterio explícito que determine cuándo ha terminado la tarea.

Sin condiciones de salida, el agente puede seguir solicitando herramientas más allá de lo necesario. La finalización no debe depender únicamente de que Claude decida detenerse.

---

## Checklist del loop

Antes de poner en funcionamiento el agente, se debe comprobar:

1. **Herramientas registradas** → están incluidas todas las necesarias y el system prompt no menciona herramientas inexistentes.
2. **System prompt delimitado** → describe la tarea y las herramientas disponibles, incluida la orientación necesaria para utilizarlas.
3. **Tool-use loop implementado** → cada tool-use block recibe un tool-result block antes del siguiente turno de assistant. Todas las llamadas de un mismo turno deben resolverse juntas.
4. **Punto de HITL definido** → existe al menos un punto del ciclo donde puede intervenir una persona.
5. **Condiciones de salida definidas** → existe un criterio claro de parada que no depende de que Claude se ofrezca a terminar.

---

## Human-in-the-loop

Un checkpoint de **human-in-the-loop (HITL)** pausa la ejecución del agente y la dirige a una revisión humana antes de continuar.

Para decidir dónde colocarlo, se debe considerar cuál sería el peor resultado posible si el paso se ejecutase sin revisión.

### Antes de una operación destructiva

Se activa antes de una operación de **write**, **delete** o **send**.

Está orientado a acciones de alto riesgo o irreversibles, donde una llamada incorrecta puede no poder deshacerse.

### Después de la planificación

Se activa cuando el agente ha generado un plan y está a punto de ejecutarlo.

Permite detectar planes incorrectos que producirían un resultado equivocado aunque todos sus pasos se ejecutasen correctamente.

### Ante un resultado inesperado

Se activa cuando el resultado de una herramienta contiene:

- Un indicador de error.
- Un resultado vacío.
- Un valor fuera de los límites esperados.

Ayuda a detectar problemas que la lógica de **retry** por sí sola puede no resolver.

---

## Orquestación de herramientas

La selección de herramientas depende tanto de sus **descripciones** como del **número de herramientas registradas**.

### Over-tooling

El **over-tooling** ocurre cuando se registran demasiadas herramientas, especialmente si sus descripciones se solapan. Esto puede provocar selecciones erráticas.

La transcripción lo presenta como el problema más frecuente en agentes de producción. Recomienda comenzar con el conjunto mínimo necesario y añadir herramientas solo cuando se confirme una carencia concreta.

### Under-tooling

El **under-tooling** ocurre cuando se registran muy pocas herramientas. El agente puede verse obligado a inventar una ruta para completar la tarea o devolver un resultado incompleto.

---

## Observabilidad y complejidad

En un workflow, la ruta está definida mediante lógica explícita en el código. En un agente, la ruta surge del razonamiento del modelo sobre el contexto acumulado.

Esto añade **complejidad de comportamiento**. La transcripción señala que la observabilidad de un agente requiere herramientas que permitan examinar la **transcripción**, en lugar de depender únicamente del logging operativo estándar.

---

## Restricciones de datos y elección de infraestructura

Las restricciones de datos deben identificarse antes de diseñar prompts, herramientas o memoria. Pueden determinar:

- El **endpoint** utilizado.
- Las **credenciales**.
- La **región** configurada.
- El destino de los **logs**.
- La opción de despliegue permitida.

La siguiente información refleja los ejemplos y condiciones indicados en la transcripción. Las configuraciones, coberturas y autorizaciones deben confirmarse antes de implementarlas.

### Secreto profesional entre abogado y cliente

El **attorney-client privilege** puede descartar superficies o endpoints que la organización no haya aprobado para documentos protegidos o no pueda auditar de extremo a extremo.

La transcripción presenta como posible opción una aplicación propia con:

- Llamadas directas mediante **API o SDK**.
- Autenticación mediante **SSO**.
- Un **LLM gateway** aprobado por la organización.
- Logging completo de solicitudes y respuestas hacia un destino aprobado.
- Tool calls y tool results dentro de la ruta auditada.

Indica que el contenido de las conversaciones de tráfico directo de API no queda registrado por Anthropic por defecto para ese propósito, por lo que la organización debe implementar el logging en su aplicación y confirmar el diseño final con su equipo de cuenta de Anthropic.

### HIPAA y PHI

Para datos sujetos a **HIPAA**, la transcripción indica que la **PHI** no debe enviarse a endpoints, rutas de entrega, logs o sistemas de retención que no estén cubiertos por un **BAA** para la configuración concreta.

Presenta como posibles rutas:

- **API o SDK directo** en una configuración cubierta por un BAA.
- Una ruta cloud mediante **AWS Bedrock** o **GCP Vertex**, en una cuenta elegible del proveedor.

La transcripción señala que la cobertura directa se organiza con Anthropic mediante una organización específica habilitada para HIPAA. También indica que no todas las funciones están cubiertas y que deben confirmarse la configuración y la lista vigente de funcionalidades elegibles.

Según la transcripción, el BAA no cubre **Console**, **Workbench**, funciones beta ni planes de consumidor.

### GDPR y residencia de datos

Los requisitos de **GDPR** o residencia de datos pueden descartar rutas que no permitan fijar la región de ejecución o que puedan procesar solicitudes fuera del límite geográfico aprobado.

La transcripción presenta **Bedrock** y **Vertex** con la región fijada en la configuración del cliente como posibles rutas. También indica que la API directa de Anthropic no proporciona residencia de datos en la UE y recomienda utilizar Bedrock o Vertex para ese requisito.

### FedRAMP y gobierno

Para **FedRAMP** y cargas de trabajo gubernamentales, la transcripción indica que los endpoints deben pertenecer a un entorno cloud autorizado al nivel requerido. Esto también afecta a las rutas de desarrollo y pruebas, no solo a producción.

La transcripción menciona estas rutas a su fecha de publicación:

- **Claude for Government** → autorización directa FedRAMP High mediante Palantir Federal Cloud Service – Supporting Services.
- **Claude mediante Amazon Bedrock GovCloud** → aprobado para FedRAMP High y cargas de trabajo DoD IL4/5.
- **Claude mediante Vertex AI Assured Workloads** → autorizado para FedRAMP.

También señala que **Claude Enterprise en AWS Marketplace** no está autorizado para FedRAMP. Se debe verificar el estado actual de las autorizaciones en el sitio de confianza de Anthropic antes de configurar el sistema.

### Políticas internas de residencia de datos

Una política interna puede limitar los proveedores cloud y endpoints aprobados, aunque otro proveedor ofrezca la capacidad técnica necesaria.

La aplicación debe utilizar el **SDK client**, endpoint y proveedor que la organización haya aprobado.

### Alcance de SOC 2

La transcripción distingue **SOC 2** de las restricciones anteriores: se refiere a cómo se construyen y operan los sistemas, no directamente a qué endpoint debe llamar el código. Se trata en el módulo 4 junto con otros requisitos de seguridad y auditoría.

---

## Continuación del curso

El módulo 4 profundiza en:

- Patrones **secure-by-design** para IAM y privacidad.
- Defensas frente a **prompt injection** desde entradas no confiables.
- **Runtime guardrails**.
- Endurecimiento de agentes.

El objetivo de esta sección es identificar las restricciones en el momento en que afectan a la elección del endpoint, la configuración del SDK client y las credenciales.

---

