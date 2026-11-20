---
titulo: Memoria de agentes y Skills
tipo: documento
---

# 028 Memoria de agentes y Skills

## Visión General

El **memory scope** determina qué estado conoce un agente al comenzar una nueva sesión y cuánto cuesta conservarlo. Las **Skills** resuelven un problema relacionado pero distinto: permiten reutilizar instrucciones específicas de una tarea y cargarlas cuando son necesarias.

---

## Patrones de diseño de agentes

La transcripción relaciona la memoria con otros patrones tratados anteriormente:

- **Tool-use loop** → el modelo solicita una herramienta, recibe el resultado y continúa.
- **Multi-step task decomposition** → divide un objetivo en subtareas ordenadas.
- **Planning-and-execution** → separa la planificación de la ejecución. Esta separación permite insertar una revisión humana después del plan.
- **Memory scope** → determina qué estado sobrevive cuando termina el ciclo y comienza otra sesión.

---

## Elección del memory scope

La elección del **memory scope** equilibra dos riesgos:

- **Demasiado estado en contexto** → el historial aumenta el coste de tokens de las llamadas a medida que crece la conversación.
- **Demasiado poco estado persistente** → el agente pierde información entre sesiones porque lo que no se guarda desaparece al terminar la conversación.

### In-context memory

La **in-context memory** mantiene el estado en la conversación activa y lo conserva entre turnos de una misma sesión.

- **Cuándo usarla** → sesiones cortas cuyo estado cabe en la context window y no necesita sobrevivir a un reinicio.
- **Coste** → no requiere recuperar información de un almacenamiento externo, pero el coste de tokens aumenta con la conversación.
- **Qué se pierde** → todo el estado al terminar la sesión, ejecutar un clear o iniciar una conversación nueva.

### External storage

El **external storage** guarda el estado en una base de datos y lo recupera al inicio de una sesión o cuando se necesita.

- **Cuándo usarlo** → información que debe sobrevivir entre sesiones, trasladarse entre usuarios o compartirse entre instancias de agentes.
- **Coste** → latencia de las llamadas a la base de datos y trabajo de implementación de la lógica de lectura y escritura.
- **Continuidad** → el estado escrito en el almacenamiento puede recuperarse posteriormente.

### Summarized memory

La **summarized memory** genera una versión condensada de conversaciones anteriores y la incorpora al inicio de la siguiente sesión.

- **Cuándo usarla** → agentes conversacionales de larga duración cuyo historial completo superaría el presupuesto de contexto.
- **Coste** → menos tokens por sesión que reproducir todo el historial, pero requiere generar el resumen.
- **Qué se pierde** → cualquier detalle que el summarizer no haya conservado.

El **summarizer prompt** debe especificar qué información es importante; de lo contrario, puede perderse estado necesario para la tarea.

### Stateless

Un agente **stateless** no mantiene memoria persistente: cada sesión es independiente.

- **Cuándo usarlo** → agentes que reciben un trabajo, lo completan y terminan, o pipelines cuyas sesiones son independientes.
- **Coste** → no hay sobrecarga de almacenamiento ni recuperación de memoria.
- **Qué se pierde** → todo el contexto previo. Una sesión posterior no puede recuperar información de una anterior.

---

## Diseñar la memoria desde el principio

La elección de memoria debe hacerse durante el **diseño del agente**, no esperar a que sea necesaria una refactorización en producción.

- Un agente que ayuda al mismo usuario durante varios días necesita conservar estado entre sesiones, por ejemplo mediante resúmenes o historial fuera de la context window.
- Un agente que recibe una tarea independiente, la termina y se cierra puede funcionar de forma **stateless**.

### Riesgo de mantener todo el historial en contexto

Un prototipo puede guardar toda la conversación en el **messages array** y enviarla en cada llamada. Sin embargo, a medida que crece la sesión:

- Aumenta el coste de tokens.
- Aumenta la latencia.
- La context window puede alcanzar su límite y el agente dejar de responder.

En ese momento puede ser necesario trasladar el estado a **external storage** y añadir a cada turno solo la información necesaria.

La transcripción destaca que el coste de esta refactorización no es solo técnico: hacerla bajo presión de producción retrasa el trabajo previsto para el agente.

Antes de decidir, conviene medir el **uso real de tokens** frente al límite de la ventana. Sin caching ni compaction, las sesiones largas pueden acumular costes más rápido de lo previsto a partir de los primeros turnos.

---

## Skills: instrucciones reutilizables bajo demanda

Una **Skill** es un conjunto reutilizable de instrucciones en Markdown que enseña a Claude cómo abordar un tipo específico de tarea.

Las Skills no sustituyen la decisión sobre qué estado debe persistir entre sesiones. Resuelven otro problema: reutilizar instrucciones sin incorporar su contenido completo a todas las conversaciones.

### Estructura de una Skill

Una Skill se encuentra en un archivo **SKILL.md** dentro de un directorio identificado. El archivo contiene:

- **Frontmatter** → incluye un `name` y una `description`.
- **Instrucciones** → contenido que Claude carga cuando la Skill es relevante.

La **description** se utiliza como criterio de coincidencia con la solicitud.

### Carga bajo demanda

Claude lee el nombre y la descripción de las Skills disponibles y los compara con la solicitud. Las instrucciones completas se cargan solo cuando existe una coincidencia.

Así, las instrucciones de una Skill que no es relevante no ocupan la context window de esa tarea.

Ejemplos de uso:

- Formatos de salida específicos de un dominio.
- Checklists de revisión especializados.
- Workflows aplicables solo a algunas tareas.

---

## Skills, CLAUDE.md e instrucciones en contexto

### Skill

- **Carga** → bajo demanda, cuando la solicitud coincide con su descripción.
- **Coste de contexto** → el nombre y la descripción se cargan al inicio; el contenido completo se carga cuando corresponde.
- **Uso adecuado** → conocimiento e instrucciones para tareas específicas y recurrentes.

### CLAUDE.md

- **Uso adecuado** → estándares de proyecto que deben aplicarse de forma general, como convenciones de código, formatos de salida o restricciones compartidas.
- **Claude Code CLI** → el archivo se carga en cada sesión, independientemente de la tarea.
- **Agent SDK** → la carga de configuraciones del filesystem, incluido CLAUDE.md, depende de **settingSources**.

La transcripción recomienda configurar **settingSources** explícitamente y comprobar el comportamiento predeterminado vigente en la referencia de Agent SDK, en lugar de depender de un valor por defecto.

### Instrucciones en contexto

- **Carga** → permanecen presentes durante los turnos de la sesión.
- **Coste** → crece con la duración de la conversación.
- **Persistencia** → no sobreviven al final de la sesión.
- **Uso adecuado** → trabajo exploratorio puntual o tareas limitadas a una conversación corta.

---

## Skills en la Messages API

Según la transcripción, las **Skills** están disponibles en la **Messages API** mediante una integración beta, con una configuración diferente a la de Claude Code o Agent SDK.

La configuración descrita requiere dos **beta headers**:

- `code-execution-2025-08-25`
- `skills-2025-10-02`

Las Skills invocadas de esta forma se ejecutan dentro del **code execution container**, no en el entorno de la aplicación que realiza la llamada. Esto afecta a las herramientas y al acceso al filesystem que pueden utilizar.

Los beta headers están versionados y pueden cambiar. Antes de utilizar esta configuración en producción, la transcripción recomienda confirmar en la documentación actual:

- Los valores de los headers.
- Si la función continúa en beta o ha alcanzado disponibilidad general.
- Si el code execution container sigue siendo el entorno de ejecución.

---

## Skills y subagents

Los **subagents** comienzan con un contexto limpio y no heredan automáticamente las Skills ni el historial de conversación de la sesión principal.

Si un subagent necesita una Skill, esta debe incluirse explícitamente en su configuración.

Sin embargo, los subagents sí heredan el **contexto de permisos** de la sesión principal: el alcance de los permisos no se reinicia al delegar.

---

