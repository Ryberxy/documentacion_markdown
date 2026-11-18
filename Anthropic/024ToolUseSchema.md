---
titulo: Tool use y diseño de schemas
tipo: documento
---

# 024 Tool use y diseño de schemas

## Visión General

El **tool use** permite que Claude seleccione acciones a partir de sus definiciones, mientras que la aplicación ejecuta las herramientas y devuelve los resultados. El diseño de los **schemas**, la estructura de los mensajes y la gestión del ciclo de llamadas determinan que Claude pueda seleccionar y utilizar correctamente las herramientas.

---

## Funcionamiento del ciclo de tool use

Claude no ejecuta las herramientas directamente. Lee sus definiciones, decide cuál necesita y comunica a la aplicación qué herramienta debe llamar y con qué argumentos.

El ciclo sigue estos pasos:

1. **Definir el schema** → la aplicación proporciona el nombre, la descripción y el input schema de la herramienta.
2. **Enviar el mensaje** → se envía la solicitud junto con las definiciones de las herramientas.
3. **Recibir un tool_use block** → Claude indica qué herramienta quiere utilizar y con qué argumentos.
4. **Ejecutar la herramienta** → la aplicación llama a la función correspondiente.
5. **Devolver el resultado** → la aplicación envía el resultado a Claude.
6. **Continuar** → Claude utiliza el resultado para seguir procesando la solicitud.

El ciclo no es automático: la aplicación debe ejecutar la herramienta y devolver correctamente su resultado. Los errores suelen aparecer en el límite entre lo que gestiona Claude y lo que gestiona el código de la aplicación.

Si Claude selecciona sistemáticamente una herramienta incorrecta, se debe revisar la definición del **schema**.

---

## Estructura de los mensajes

Una conversación con tool use se compone de listas de **blocks estructurados**, no solo de texto. Los cuatro tipos principales son **text**, **tool_use**, **tool_result** y **thinking**.

### text block

El **text block** contiene la respuesta en prosa de Claude.

Claude puede devolver un text block y un tool_use block en el mismo turno. En ese caso, la aplicación debe conservar el **content array completo** al añadir el turno al historial de la conversación. Eliminar el texto corrompe el contexto que Claude utiliza en los turnos posteriores.

### tool_use block

El **tool_use block** lo genera Claude e incluye:

- **Nombre de la herramienta**.
- **ID único** de la llamada.
- **Argumentos de entrada** que deben pasarse a la función.

Cada tool_use block debe tener un **tool_result block** correspondiente en el turno de usuario inmediatamente posterior.

### tool_result block

El **tool_result block** contiene el resultado devuelto por la aplicación tras ejecutar la herramienta.

- **tool_use_id** → debe coincidir exactamente con el ID del tool_use block original.
- **Contenido del resultado** → información devuelta por la herramienta.
- **is_error** → indicador opcional que se establece en `true` cuando la llamada falla.

El ID permite asociar cada resultado con su llamada, incluso cuando un mismo turno contiene varias llamadas y sus resultados llegan en un orden diferente.

Si falta un resultado, los IDs no coinciden o el tool_result aparece después del turno de usuario inmediatamente siguiente, la API rechaza la solicitud por un error de validación. Este requisito es estructural y no se corrige modificando el prompt.

### thinking block

El **thinking block** contiene el razonamiento de Claude y solo aparece cuando está activado **extended thinking**.

El bloque debe devolverse a la API sin cambios en los turnos posteriores. Su **signature** verifica que el razonamiento no se haya modificado: editarlo o resumirlo provoca que la API rechace el mensaje.

Los **redacted thinking blocks** siguen la misma regla. Aunque su contenido esté cifrado y no sea legible, deben devolverse tal como se recibieron.

---

## Anatomía de un tool schema

Un **tool schema** tiene tres partes: **name**, **description** e **input_schema**. Claude las utiliza para decidir qué herramienta llamar y qué argumentos proporcionar.

### name

El **name** es un identificador breve y específico.

Por ejemplo, `get_account_balance` comunica mejor el propósito de la herramienta que `get_data`.

### description

La **description** es fundamental para seleccionar la herramienta correcta. Debe indicar:

- **Cuándo utilizarla** → qué necesidad o situación debe activar la herramienta.
- **Cuándo no utilizarla** → qué situaciones deben quedar excluidas.

Una descripción genérica como «usar para buscar información» no permite distinguirla de otras herramientas similares.

Una descripción más precisa indicaría que la herramienta recupera el saldo actual de un **account ID** específico y que no debe utilizarse para consultar el historial de transacciones.

### input_schema

El **input_schema** define los parámetros que acepta la función mediante **JSON Schema**.

- **Parámetros required** → necesarios para que la llamada tenga sentido.
- **Parámetros opcionales** → pueden omitirse cuando la herramienta funciona sin ellos.

El solapamiento entre los tipos de parámetros de distintas herramientas es una fuente habitual de selecciones incorrectas.

---

## Decisiones de diseño del schema

Un schema ambiguo, insuficientemente descrito o con campos obligatorios mal definidos puede producir llamadas sintácticamente correctas que seleccionen la herramienta equivocada, proporcionen entradas incorrectas o generen ciclos innecesarios.

### Dependencias entre subtareas

- **Llamadas secuenciales** → se utilizan cuando la salida de una herramienta es necesaria para construir la siguiente llamada. La segunda llamada se realiza después de recibir el primer resultado.
- **Llamadas paralelas** → pueden utilizarse cuando las subtareas son independientes. Claude puede emitir varios tool_use blocks en un turno y la aplicación ejecutarlos de forma concurrente.
- **disable_parallel_tool_use** → permite forzar una sola llamada a herramienta por turno si es necesario.

Según la transcripción, los modelos actuales de Claude utilizan llamadas paralelas por defecto cuando las llamadas son independientes.

### Campos obligatorios

Un campo debe incluirse en el array **required** únicamente cuando la llamada no tenga sentido sin él.

Marcar todos los campos como obligatorios puede llevar a Claude a inventar valores que no conoce.

### Campos opcionales

Los campos con valores predeterminados razonables, o cuya ausencia tenga significado, deben ser opcionales.

Se dejan fuera del array **required** y se les asignan valores predeterminados en la firma de la función. Así, Claude puede omitir información que no tiene en lugar de adivinarla.

### Longitud de las descripciones

Se recomienda escribir **tres o cuatro frases por herramienta** que expliquen:

- Qué hace.
- Cuándo debe utilizarla Claude.
- Qué devuelve.
- Ejemplos de entradas válidas cuando el formato sea importante.

Una descripción demasiado corta puede no aportar información suficiente para distinguir herramientas. Una demasiado larga puede ocultar las condiciones que determinan cuándo utilizarlas.

### Solapamiento entre herramientas

Cuando dos herramientas aceptan parámetros con la misma estructura, sus descripciones deben identificar el **dominio** o la **condición de activación** de cada una.

Claude se apoya principalmente en el nombre y la descripción para seleccionar herramientas; los tipos de parámetros son una señal secundaria. Si las firmas son idénticas, las descripciones adquieren aún más importancia.

---

## Ejemplo: selección de herramientas similares

El siguiente es un ejemplo ilustrativo construido para mostrar cómo diferenciar herramientas; no procede de un sistema de producción concreto.

Un desarrollador registra dos herramientas:

- **search_knowledge_base** → busca información en una base de conocimiento.
- **get_cached_result** → recupera un resultado obtenido previamente.

Si ambas descripciones empiezan con «usar para buscar información», Claude puede seleccionar la herramienta equivocada, aunque los nombres sean diferentes.

### Añadir condiciones de exclusión

Las descripciones pueden diferenciarse indicando cuándo usar cada herramienta y cuándo no:

- **search_knowledge_base** → usar para buscar en la base de conocimiento cuando la pregunta requiera consultar información actual. No usar si un resultado de una búsqueda anterior en la sesión ya cubre la pregunta.
- **get_cached_result** → usar para recuperar un resultado ya obtenido en la sesión. Solo usar si `search_knowledge_base` se llamó antes en la misma conversación para la misma consulta.

Estas condiciones dependen de que se envíe el **historial completo de la conversación** en cada solicitud. Si se eliminan turnos anteriores, Claude no puede evaluar las condiciones y la lógica de exclusión puede fallar silenciosamente.

### Cuándo combinar herramientas

Registrar más herramientas aumenta la cantidad de opciones que Claude debe evaluar. Las condiciones de exclusión son útiles cuando las herramientas son realmente distintas.

Si dos herramientas hacen cosas muy similares y necesitan descripciones cada vez más largas para diferenciarlas, se recomienda combinarlas en una sola herramienta con un **parámetro de tipo**.

---

## MCP como alternativa a escribir schemas manualmente

El **Model Context Protocol (MCP)** es una capa de comunicación estandarizada que traslada las definiciones y la ejecución de herramientas desde el código de la aplicación a servidores dedicados.

Si existe un **MCP server** para el servicio necesario, la aplicación puede conectarse a él en lugar de construir toda la integración manualmente.

### Ejemplo de integración con GitHub

Una integración completa con GitHub puede incluir repositorios, pull requests, issues, proyectos y otras funciones.

Con schemas manuales, sería necesario escribir y mantener un schema y una función de ejecución para cada función. Un MCP server para GitHub puede proporcionar esas herramientas ya definidas.

La aplicación recibe la lista de herramientas del servidor y Claude selecciona entre ellas usando el mismo mecanismo basado en descripciones. La diferencia es quién ha escrito y mantiene las definiciones.

---

## MCP dentro del ciclo de tool use

La incorporación de MCP no cambia el ciclo básico:

1. Claude emite un **tool_use block**.
2. La aplicación ejecuta la herramienta.
3. La aplicación devuelve un **tool_result block**.
4. Se mantienen las mismas reglas de correspondencia entre bloques.

La diferencia está en la preparación:

- El **MCP client** envía un **ListToolsRequest** al servidor.
- El servidor devuelve la lista de herramientas disponibles.
- La aplicación pasa esas definiciones a Claude.

Desde la perspectiva de Claude, las herramientas recibidas mediante MCP no se distinguen de las definidas manualmente.

---

## Coste de contexto y carga de herramientas MCP

Las definiciones de herramientas de los MCP servers ocupan espacio en la **context window**, incluso cuando no se utilizan en el turno actual.

Al conectar varios servidores, sus definiciones pueden consumir parte del presupuesto de contexto antes del primer mensaje. Se recomienda registrar solo los servidores necesarios y comprobar el coste frente al límite de la ventana de contexto.

### Configuración con API MCP Connector

Al utilizar el **API MCP Connector**, la carga se controla mediante un objeto **mcp_toolset** dentro del array **tools**.

- **default_config** → configuración que se aplica por defecto a todas las herramientas del servidor.
- **configs** → permite sobrescribir la configuración de herramientas individuales mediante su nombre.
- **defer_loading** → retrasa la carga de la definición de una herramienta hasta que el modelo la necesita, reduciendo el coste inicial de contexto.
- **enabled** → activa o desactiva herramientas individuales para que el modelo vea solo las seleccionadas.

El MCP Connector requiere el **beta header** `mcp-client-2025-11-20` en la solicitud. Sin él, la configuración de `mcp_toolset` no se aplica como se describe.

---

## Transportes de MCP

El transporte depende de dónde se encuentre el servidor.

### Servidores locales: stdio

Los servidores locales utilizan **stdio**:

- La aplicación inicia el servidor como un **subprocess**.
- La comunicación se realiza mediante la entrada y la salida estándar.

### Servidores remotos: Streamable HTTP

Los servidores remotos utilizan **Streamable HTTP**:

- La aplicación se conecta por red mediante HTTP.
- Las solicitudes **POST** transportan mensajes del cliente al servidor.
- Un stream **SSE** opcional basado en **GET** permite mensajes iniciados por el servidor.

El transporte anterior basado únicamente en **SSE** está obsoleto. Las nuevas integraciones deben utilizar Streamable HTTP.

### Limitación del MCP Connector de la API

El **MCP Connector** de Anthropic en la API solo admite servidores expuestos mediante HTTP.

Los servidores locales **stdio** no pueden conectarse directamente mediante el connector de la API: requieren gestionar la conexión MCP mediante el **SDK** o utilizar **Claude Desktop** o **Claude Code** como cliente.

Una vez establecida la conexión y recibidas las definiciones, el código de la aplicación trata ambos transportes de la misma manera.

---

## Cuándo usar MCP o schemas manuales

### Usar MCP

Conviene utilizar **MCP** cuando existe un servidor mantenido para el servicio necesario y cubre las operaciones requeridas.

Antes de usarlo, se debe comprobar que el servidor se mantiene actualizado respecto a la API del servicio. En esta situación, escribir y mantener schemas propios añade trabajo de implementación sin proporcionar funcionalidades adicionales.

### Escribir schemas manualmente

Conviene escribir **schemas manuales** cuando:

- No existe un MCP server que cubra el caso de uso.
- Se necesita un control preciso sobre el alcance de las herramientas o la calidad de sus descripciones.

Antes de optar por schemas manuales solo para controlar el alcance, se debe considerar que el API MCP Connector permite establecer **allowlists** y **denylists** de herramientas mediante **MCPToolset**.

### Combinar ambos enfoques

MCP y los schemas manuales no son excluyentes:

- **MCP server** → proporciona cobertura de herramientas.
- **Ajuste de descripciones** → aporta precisión en las herramientas utilizadas activamente.
- **Allowlisting** → reduce el conjunto de herramientas que Claude debe evaluar.

Reducir el conjunto de herramientas y mejorar sus descripciones son dos medidas distintas que pueden utilizarse conjuntamente.

---

