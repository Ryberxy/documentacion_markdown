---
titulo: Selección de modelos y context engineering
tipo: documento
---

# 026 Selección de modelos y context engineering

## Visión General

La **selección del modelo** determina el punto de partida de coste, latencia y capacidad de una aplicación. En sesiones de varios turnos, el **context engineering** permite gestionar qué información entra en la context window, qué se resume y qué se mantiene fuera para que la sesión pueda continuar dentro de sus límites.

---

## Selección del modelo

La familia Claude presenta modelos con diferentes compromisos entre **coste**, **latencia** y **capacidad**.

Según la transcripción, la familia abarca cuatro niveles:

- **Sonnet** → opción equilibrada para comenzar en la mayoría de las cargas de trabajo de producción.
- **Haiku** → orientado a velocidad y eficiencia de costes para tareas dentro de sus capacidades.
- **Opus** → para trabajos exigentes que superan las capacidades necesarias de Sonnet.
- **Fable** → presentado como el modelo de mayor capacidad, orientado a tareas especialmente exigentes, como razonamiento complejo, programación avanzada, síntesis de investigación y agentic workflows sofisticados.

La transcripción indica que se debe **confirmar la oferta y los identificadores actuales** en la documentación de la plataforma al desarrollar la aplicación.

### Cambiar de modelo mediante evaluaciones

El punto de partida recomendado es **Sonnet**. Los cambios deben basarse en un **eval set**:

- **Pasar a Opus** → cuando las evaluaciones indiquen que Sonnet no alcanza el nivel de calidad requerido.
- **Pasar a Haiku** → cuando las evaluaciones demuestren que la posible pérdida de calidad es aceptable para la tarea, no solo para ahorrar costes.

---

## La context window

La **context window** es el espacio de información que Claude puede recibir y utilizar a la vez. Como analogía, puede entenderse como el espacio disponible en su **memoria de trabajo**.

Ocupan espacio en ella:

- Los mensajes y prompts enviados.
- El historial de la conversación.
- Los resultados de herramientas.
- Los documentos incorporados.
- Las respuestas generadas por Claude.

En una sesión con varios pasos, los resultados de herramientas se añaden al contexto y pueden acumularse rápidamente.

### Al alcanzar el límite

La transcripción distingue dos situaciones:

- **La solicitud ya supera la context window** → la Messages API la rechaza con un error de validación antes de generar la respuesta.
- **La solicitud cabe, pero la generación alcanza el límite** → los modelos actuales devuelven el output generado hasta ese momento con el **stop_reason** `model_context_window_exceeded`.

En ninguno de los dos casos se elimina silenciosamente el contenido más antiguo. Para continuar una sesión más allá del límite, la aplicación debe gestionar el historial, por ejemplo, recortándolo o resumiéndolo antes de la siguiente solicitud.

### Diferencias entre desarrollo y producción

En desarrollo, las sesiones suelen ser cortas y las entradas pequeñas. En producción, las sesiones pueden tener más turnos y los resultados de herramientas pueden ser entre **tres y cinco veces más largos** que los test fixtures.

Por ello, una ventana que parecía suficiente durante las pruebas puede llenarse mucho antes en producción y provocar una interrupción del servicio.

---

## Estrategias para gestionar el presupuesto de contexto

Cada token del contexto añade coste de entrada y latencia. En sesiones largas, ambos efectos se acumulan.

Las siguientes estrategias permiten controlar cuánto historial se mantiene disponible.

### Pruning

El **pruning** permite volver a un mensaje anterior y continuar desde ese punto, eliminando la conversación posterior.

Es útil después de:

- Una ruta de trabajo improductiva.
- Intercambios de debugging que ya no ayudarán a la siguiente tarea.

**Continuidad perdida** → se elimina el trabajo posterior al punto de retorno. Si Claude aprendió algo útil durante ese tramo, tendrá que volver a obtenerlo.

### Compaction

La **compaction** resume el historial de la conversación en una versión más breve que conserva información relevante.

Opciones mencionadas:

- **`/compact`** → compaction en Claude Code.
- **Server-side compaction** → estrategia beta de la API en la que la plataforma realiza el resumen.
- **Manual summarization** → alternativa gestionada por el cliente en la API.

Es útil cuando la sesión se acerca al límite, pero se desea continuar con la misma tarea conservando lo aprendido.

**Continuidad perdida** → los detalles que no aparezcan en el resumen dejarán de estar disponibles para Claude.

### Clearing

El **clearing** inicia una conversación nueva con el contexto vacío:

- En Claude Code se utiliza **`/clear`**.
- En la API se inicia una **nueva sesión**.

Es útil cuando la siguiente tarea es completamente distinta y el contexto anterior podría introducir sesgos o confusión.

**Continuidad perdida** → se elimina todo el contexto de la sesión. La información que deba conservarse entre sesiones debe guardarse en un lugar persistente, como un archivo **CLAUDE.md**.

### Subagent handoffs

Un **subagent handoff** delega una subtarea a un subagent con su propia context window aislada. El subagent realiza el trabajo y devuelve un resumen.

Es útil para subtareas independientes, especialmente de exploración, cuando el resultado es breve pero los pasos intermedios llenarían el contexto principal.

**Continuidad perdida** → el agente principal no conserva la visibilidad de todos los pasos intermedios que llevaron a la conclusión.

---

## Prompt caching y token counting

Además de gestionar qué información se mantiene en contexto, la transcripción presenta dos funciones de la API para controlar el coste y medir la presión sobre la ventana.

### Prompt caching

El **prompt caching** almacena el trabajo de procesamiento realizado sobre un prefijo estable de la solicitud para reutilizarlo en solicitudes posteriores.

- La primera solicitud escribe el prefijo en la cache.
- Las solicitudes posteriores que envían contenido idéntico hasta ese punto pagan una fracción del coste original.

Los candidatos más adecuados son contenidos que cambian poco entre turnos:

- Un **system prompt** largo.
- Un conjunto grande de definiciones de herramientas.
- Un documento de referencia que se consulta repetidamente.

Para activarlo, se marca un **cache breakpoint** con un campo **cache_control** de tipo `ephemeral` en el último bloque que se desea almacenar. Se pueden establecer hasta **cuatro breakpoints**.

En sesiones de varios turnos con system prompts y tool schemas estables, reutilizar esos prefijos es una medida importante para reducir costes.

### Token counting

El endpoint **count_tokens** permite medir los tokens antes de enviar una solicitud.

Acepta el mismo cuerpo que una llamada a **messages** y devuelve el número de tokens sin ejecutar inferencia.

Puede utilizarse para:

- **Desarrollo** → comprobar el presupuesto con resultados reales de herramientas, no solo con test fixtures.
- **Producción** → detectar y bloquear solicitudes que superarían la context window antes de que fallen.

---

## Puntos de fallo en una ruta RAG

Una ruta **RAG** puede fallar en tres etapas: **chunking**, **embedding match** y ensamblado de los resultados en el prompt.

### Chunking

El **chunking** determina qué fragmento de información puede recuperarse como unidad.

- **Chunks demasiado pequeños** → pueden carecer del contexto necesario.
- **Chunks demasiado grandes** → pueden diluir la coincidencia con texto no relacionado.
- **Solapamiento** → ayuda a conservar hechos que atraviesan los límites entre chunks.

La transcripción propone como punto de partida dividir por frases o secciones, con cierto solapamiento.

### Embedding match

El **embedding match** utiliza una búsqueda por similitud para recuperar chunks semánticamente cercanos a la consulta.

La coincidencia semántica no siempre recupera el fragmento con el término exacto. Por ejemplo, una búsqueda de un identificador específico puede no devolver el chunk relevante si otro resultado semánticamente parecido obtiene una clasificación superior.

Por este motivo, a veces se utiliza una **búsqueda léxica** junto con la semántica.

### Ensamblado en el prompt

Los chunks recuperados deben llegar al modelo con la estructura que espera el prompt. Si no se incorporan correctamente, el modelo puede responder desde su memoria en lugar de utilizar el texto recuperado.

---

## Índice de retrieval frente a búsqueda iterativa

### Fetch-once con índice

La ruta **fetch-once** permite inspeccionar qué chunks se recuperaron para una consulta y probar directamente el retrieval.

Su coste es la infraestructura necesaria para que el índice se:

- Construya.
- Almacene.
- Mantenga sincronizado cuando cambia el corpus.
- Proteja en el lugar donde se encuentre.

La transcripción lo considera apropiado para un **corpus de referencia estable** con consultas sencillas.

### Search across rounds

La ruta **search across rounds** permite que el modelo lea los archivos actuales al realizar la consulta, sin mantener la infraestructura de un índice ni asumir su posible desactualización.

Sus costes son un mayor consumo de **tokens** y **tiempo por consulta**, además de un proceso menos fácil de inspeccionar.

Para un corpus cambiante o preguntas de varios pasos, la búsqueda iterativa suele ser el sistema más sencillo, aunque resulte más costosa por consulta.

La transcripción indica que la mejora de rendimiento comunicada para **single-agent agentic search** frente a un retrieval index depende de la versión y debe confirmarse en la referencia correspondiente al desarrollar la aplicación.

---

## Aplicación de compaction

El resultado de la **compaction** depende de quién construya el resumen y de las instrucciones utilizadas:

- En **Claude Code**, `/compact` decide qué incluir.
- En la API, la **server-side compaction** beta permite que la plataforma resuma la conversación cuando está configurada en la solicitud.
- En una compaction manual en la API, el desarrollador escribe el **summarizer prompt**.

### Importancia del summarizer prompt

Una instrucción genérica como «resume la conversación hasta ahora» puede omitir información necesaria para continuar.

Una instrucción más específica puede pedir que se conserven:

- Todas las **file paths** modificadas.
- Todas las decisiones tomadas.
- Los errores encontrados y sus soluciones.

La pérdida de estado importante por un summarizer prompt insuficientemente detallado es una fuente habitual de fallos en agentes que trabajan durante varias sesiones.

---

## Subagent handoffs para tareas largas

Cuando una tarea es demasiado grande para una sola context window, la estrategia presentada es **descomponerla** y enviar a cada subagent solo el contexto relevante.

Cada subagent recibe:

- Una **tarea delimitada**.
- El contexto mínimo necesario.
- Los resultados directamente relevantes de pasos anteriores.
- Las herramientas necesarias.
- Condiciones claras de finalización.

El **parent agent** recoge los resultados. Este patrón mantiene bajo el coste por turno y facilita el trabajo en tareas de larga duración.

Los subagent handoffs, al igual que la compaction y el pruning, añaden trabajo de implementación. No son necesarios para un prompt sencillo de un solo turno o un flujo corto.

---

## Cuándo aplicar context engineering

El context engineering es especialmente útil en **agentic sessions de varios pasos** que pueden superar el presupuesto de tokens. Es preferible diseñarlo en la arquitectura desde el principio, en lugar de incorporarlo después como solución a un fallo en producción.

Si un pipeline nunca se acerca al límite de la ventana, añadir estas técnicas puede introducir complejidad innecesaria. Antes de hacerlo, se debe **medir el uso real de tokens** frente al límite del modelo.

La siguiente sección del curso profundiza en un caso donde un agente funcionaba con test fixtures, pero alcanzó el límite al procesar documentos reales en producción.

---

