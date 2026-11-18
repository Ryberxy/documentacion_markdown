---
titulo: Pensamiento extendido
tipo: documento
---

# 023 Pensamiento extendido

## Visión General

El **extended thinking** permite que Claude realice un proceso de razonamiento antes de proporcionar su respuesta final. Su uso requiere ajustar el **effort** a la complejidad de la tarea y gestionar correctamente los bloques de razonamiento cuando se utilizan herramientas.

---

## Funcionamiento de extended thinking

Al activar **extended thinking**, el modelo genera razonamiento antes de responder. En la respuesta de la API, este razonamiento aparece en un **thinking block** situado antes del bloque que contiene la respuesta final.

En los modelos más recientes, el contenido del thinking block se omite por defecto. Para verlo, se debe solicitar un resumen legible mediante la configuración **display**.

### Activación y profundidad del razonamiento

- **thinking** → parámetro que activa el razonamiento cuando no está activado por defecto.
- **Razonamiento adaptativo** → el modelo decide cuánto razonamiento necesita cada solicitud.
- **effort** → configuración que permite ajustar la profundidad del razonamiento.
- **budget_tokens** → control anterior basado en un presupuesto fijo de tokens. Está obsoleto y devuelve un error **400** en las generaciones más recientes de modelos.

### Coste

Los **thinking tokens** tienen el mismo coste que los **output tokens**. Por ello, usar un effort alto para una tarea sencilla puede aumentar el coste sin aportar una precisión necesaria.

---

## Cuándo utilizar extended thinking

La decisión de activar extended thinking debe ajustarse a la tarea y al valor que aporta el razonamiento adicional.

### Razonamiento complejo

Conviene activarlo en tareas que requieren gestionar varios pasos o restricciones, como:

- Derivaciones matemáticas.
- Problemas de lógica de varios pasos.
- Planificación de acciones dependientes entre sí.

En estos casos, el nivel de **effort** debe corresponder con la profundidad del problema.

### Tareas mecánicas o de consulta

Para tareas como **classification**, **format conversion**, extracción de un campo o respuestas factuales breves, se recomienda dejarlo desactivado.

Un **prompt** con una restricción de salida es una alternativa más económica para estas tareas.

### Agentic loops

En los **agentic loops**, donde el modelo planifica varias llamadas a herramientas, conviene activar extended thinking y presupuestar el razonamiento para la fase de planificación, en lugar de hacerlo por cada llamada.

Razonar antes de elaborar un plan puede reducir la selección incorrecta de herramientas. En estos ciclos también debe respetarse la regla de devolución de los thinking blocks.

---

## Devolución de thinking blocks a la API

Cuando extended thinking está activado y la conversación utiliza herramientas, cada **thinking block** recibido debe devolverse a la API en el siguiente turno exactamente como llegó.

Cada bloque incluye una **signature** que permite comprobar que el razonamiento no ha sido alterado. Si el bloque se edita, resume o elimina, la signature deja de coincidir y la API rechaza la solicitud.

### Redacted thinking blocks

Los **redacted thinking blocks** contienen información cifrada que no está destinada a ser leída por personas. Aun así, también deben devolverse sin modificaciones.

### Acumulación de contexto

Eliminar thinking blocks para ahorrar contexto puede romper la siguiente solicitud. Si preocupa la acumulación de razonamiento en el contexto, la alternativa indicada es trabajar en **context engineering**.

Esta devolución es un requisito estructural de la API, no una decisión de prompting.

---

## Relación con la selección del modelo

Esta lección se centra en activar el razonamiento y ajustar el **effort**. La selección del modelo es una decisión distinta que se trata en el módulo anterior, **MSO Foundations**.

---

