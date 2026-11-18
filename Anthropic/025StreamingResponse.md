---
titulo: Streaming de respuestas y gestión de output parcial
tipo: documento
---

# 025 Streaming de respuestas y gestión de output parcial

## Visión General

El **streaming** permite recibir una respuesta de la API en fragmentos mientras el modelo la genera, en lugar de esperar a que esté completa. La aplicación debe reconstruir los bloques a partir de los eventos recibidos y gestionar las interrupciones para evitar guardar un estado incompleto.

---

## Qué cambia con streaming

En una solicitud sin streaming, la API devuelve un **mensaje completo** con todos sus content blocks ya formados.

En una solicitud con **streaming**, la API envía una secuencia de **eventos** que describen cómo se construye el mensaje. La aplicación escucha esos eventos y reconstruye los bloques.

El mensaje completo resultante es idéntico al de una llamada sin streaming. La diferencia es que la aplicación debe ensamblar los fragmentos y decidir qué hacer si la secuencia termina antes de completarse.

### Eventos y estado parcial

Cada evento es un mensaje independiente que describe un cambio, por ejemplo:

- El inicio de un bloque.
- La incorporación de un fragmento de texto o input.
- La finalización de un bloque.
- La finalización del mensaje completo.

El **handler** procesa cada evento y aplica el cambio al **estado parcial** que está construyendo. El modelo no mantiene abierto un objeto vivo para la aplicación.

---

## Secuencia de eventos

### message_start

El evento **message_start** indica que comienza un mensaje nuevo.

Incluye la estructura inicial del mensaje, con el contenido vacío y los datos iniciales de **usage**.

El handler prepara un **content array** vacío para recopilar los bloques.

### content_block_start

El evento **content_block_start** indica que se abre un nuevo content block e informa de su **tipo** y su **índice**.

El handler reserva una posición en el content array para ese bloque.

Un **tool_use block** comienza con el nombre de la herramienta y su ID, pero todavía no incluye el input completo.

### content_block_delta

El evento **content_block_delta** aporta un fragmento incremental de un bloque. Puede contener:

- Un fragmento de **text**.
- Un fragmento de **JSON input** para una llamada a herramienta.
- Un fragmento de **thinking**.

El handler añade el fragmento al bloque correspondiente según su índice.

En una llamada a herramienta, el input llega como una cadena JSON parcial repartida entre varios eventos. No debe analizarse como JSON hasta que el bloque se cierre.

### content_block_stop

El evento **content_block_stop** indica que el bloque de ese índice está completo.

El handler finaliza el bloque. Si es un **tool_use block**, este es el primer momento en que el JSON acumulado está suficientemente completo para analizarlo.

### message_delta

El evento **message_delta** comunica cambios a nivel de mensaje, incluidos el **stop_reason** y los recuentos finales de **usage**.

El handler registra el stop_reason para determinar si el modelo ha terminado o se ha detenido por otro motivo.

### message_stop

El evento **message_stop** indica que el stream ha terminado.

En ese momento, el content array ensamblado constituye el mensaje completo y puede tratarse como una respuesta sin streaming.

---

## No actuar sobre bloques parciales

La regla para evitar corromper el estado es **no actuar sobre un bloque parcial**.

En particular, el input de un **tool_use block** llega como una cadena JSON dividida entre varios eventos **content_block_delta**. Si la aplicación intenta analizar el JSON o ejecutar la herramienta antes de recibir **content_block_stop**, puede encontrar JSON no válido o ejecutar la herramienta con argumentos incompletos.

El procedimiento es:

1. Recopilar los fragmentos del bloque.
2. Esperar a **content_block_stop**.
3. Finalizar el bloque y analizar el JSON completo.

### Guardar el turno en el historial

Un turno de assistant recibido mediante streaming debe añadirse al **historial de la conversación** solo después de recibir **message_stop** y ensamblar todos sus bloques.

Un turno interrumpido está incompleto. Si se guarda un **tool_use block** a medio construir, las reglas de correspondencia con **tool_result** pueden provocar que la API rechace la siguiente solicitud.

---

## Gestión de interrupciones

Un stream puede terminar antes de **message_stop** por una conexión de red interrumpida, un **timeout** o una desconexión del cliente.

Mostrar al usuario un **text block** parcial puede causar un problema visual. En cambio, guardar un **tool_use block** parcial en el historial es un problema estructural que puede afectar al siguiente turno.

### Qué hacer ante una interrupción

- **Tratar el contenido como provisional** → el turno solo es utilizable cuando llega `message_stop`.
- **Descartar el turno parcial** → no guardarlo en el historial.
- **Reintentar la solicitud** → iniciar de nuevo la solicitud interrumpida.
- **Comprobar stop_reason** → antes de continuar un ciclo, revisar el valor recibido en `message_delta`.

Si **stop_reason** es `tool_use`, las llamadas a herramientas ensambladas están listas para ejecutarse. Cualquier otro valor indica que el flujo no debe continuar por la vía de tool use.

---

## Cuándo utilizar streaming

### Casos adecuados

El **streaming** resulta útil para:

- **Respuestas largas** → permite mostrar el contenido mientras se genera.
- **Interfaces de usuario** → evita que la persona espere ante una pantalla en blanco.

### Coste y complejidad

La aplicación debe:

- Ensamblar los bloques a partir de eventos.
- Evitar actuar sobre bloques parciales.
- Gestionar explícitamente las interrupciones.

### Alternativa sin streaming

Para respuestas cortas o **backend jobs** en los que nadie espera el resultado, una llamada sin streaming es más sencilla y evita el riesgo de estado parcial.

---

