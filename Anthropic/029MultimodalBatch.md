---
titulo: Ingesta multimodal y procesamiento por lotes
tipo: documento
---

# 029 Ingesta multimodal y procesamiento por lotes

## Visión General

La **ingesta multimodal** permite enviar imágenes y PDFs a Claude, teniendo en cuenta que estos archivos consumen parte del presupuesto de contexto. Para procesar cientos o miles de entradas sin esperar cada respuesta individualmente, la **Message Batches API** ofrece procesamiento asíncrono a cambio de una mayor latencia.

---

## Coste de imágenes en tokens

Las imágenes consumen parte de la **context window** antes de que Claude procese el texto del prompt.

Según la transcripción, Claude divide cada imagen en **patches** de 28 × 28 píxeles. Cada patch equivale a un **visual token**:

    visual tokens = ⌈ancho / 28⌉ × ⌈alto / 28⌉

Por ejemplo, una imagen de **1.000 × 1.000 píxeles** consume aproximadamente:

    ⌈1000 / 28⌉ × ⌈1000 / 28⌉
    = 36 × 36
    = 1.296 visual tokens

Diez capturas de alta resolución pueden consumir tanto contexto como un system prompt detallado.

### Límites y redimensionado

Cada modelo tiene una resolución de imagen nativa máxima, expresada mediante:

- **Long-edge limit** → límite del lado más largo.
- **Visual-token limit** → límite de tokens visuales.

Los límites varían según el modelo. Si una imagen supera cualquiera de ellos, se reduce antes de procesarla y el cálculo de tokens se aplica a las dimensiones resultantes.

La transcripción recomienda confirmar los límites vigentes por modelo en la sección **Resolution and token cost** de la documentación de Vision.

### Medición durante el diseño

Antes de implementar un pipeline de imágenes, se debe medir el coste de una imagen representativa de producción frente al límite de contexto del modelo.

Si el pipeline supera el presupuesto, una posible solución es incorporar un paso de **redimensionado de imágenes**.

---

## Formas de enviar imágenes

La transcripción menciona tres formas de enviar una imagen:

- **Inline base64**.
- **URL reference**.
- **Files API**.

### Inline base64

La imagen se codifica como una cadena **base64** y sus datos se incluyen directamente en el message block.

- **Ventaja** → resulta apropiado para una imagen puntual cuando añadir una subida previa supondría complejidad innecesaria.
- **Coste** → la carga codificada completa viaja en cada solicitud, aumentando su tamaño y la latencia para imágenes grandes.
- **Reutilización** → si la misma imagen se envía repetidamente, se multiplica ese coste; conviene considerar otro método.

---

## Envío de PDFs

Para enviar un PDF se utiliza un block de tipo **document**, en lugar de **image**.

La estructura de **source** puede utilizar:

- **base64**.
- Una **URL**.
- Un **file_id** de Files API.

El document block no requiere un campo `name`. Puede incluir opcionalmente:

- **title** → nombre legible del documento.
- **context** → metadatos adicionales.

Ejemplo de PDF enviado mediante base64:

    {
      "type": "document",
      "source": {
        "type": "base64",
        "media_type": "application/pdf",
        "data": "<base64-encoded-pdf-bytes>"
      },
      "title": "contract_review.pdf"
    }

También deben tenerse en cuenta el coste en tokens y la posibilidad de reutilizar archivos mediante **Files API**.

---

## Prompting para entradas multimodales

Las técnicas de **prompting** también se aplican al análisis de imágenes y PDFs. Una instrucción genérica como «describe esta imagen» no proporciona una estructura concreta y puede producir una respuesta superficial.

El análisis visual presenta ambigüedades específicas que el prompt puede abordar:

- **Objetos solapados**.
- **Profundidad y relaciones espaciales**.
- **Oclusión parcial**.

Por ejemplo, el prompt puede indicar que, si varios objetos se solapan, Claude describa cada uno por separado y señale el solapamiento.

---

## Message Batches API

La **Message Batches API** permite procesar grandes volúmenes de solicitudes de forma asíncrona.

Según la transcripción, un batch admite hasta **100.000 solicitudes o 256 MB**, lo que se alcance primero.

### Flujo de procesamiento

1. **Enviar el batch** con las solicitudes.
2. **Recibir un batch_id**.
3. **Consultar periódicamente** si el procesamiento ha terminado.
4. **Descargar los resultados** cuando el batch esté completo.

El coste por token de las solicitudes batch es menor que el de las solicitudes síncronas.

### Compensación: latencia

La duración del procesamiento es **no determinista** y puede alcanzar las **24 horas**, aunque a menudo es menor.

Por ello, el procesamiento batch es adecuado para tareas offline, pero no para interacciones en tiempo real.

---

## API síncrona o Message Batches API

| Caso de uso | Patrón adecuado | Motivo |
|---|---|---|
| Un usuario sube una foto y espera una clasificación inmediata. | **API síncrona** | Se necesita una respuesta en tiempo real. |
| Un pipeline nocturno clasifica 5.000 registros de clientes. | **Message Batches API** | La latencia no es una restricción y resulta útil reducir costes. |
| Una evaluación prueba un prompt con 2.000 ejemplos. | **Message Batches API** | Es una tarea offline sin requisito de respuesta inmediata. |
| Un chatbot responde a un mensaje de usuario. | **API síncrona** | El usuario está esperando la respuesta. |

---

## Combinar multimodalidad y batch

La combinación es adecuada para cargas de trabajo **offline** que reutilizan archivos y necesitan output estructurado sobre miles de entradas.

Un ejemplo es un pipeline nocturno que clasifica imágenes según una taxonomía fija:

- **Files API** → evita subidas redundantes de los mismos archivos.
- **Message Batches API** → procesa las solicitudes de forma asíncrona.
- **Structured output** → mantiene los resultados en un formato procesable por máquinas.

### Riesgos principales

- **Latencia inadecuada** → usar batch en una interacción donde el usuario espera una respuesta inmediata puede funcionar en pruebas y fallar en producción.
- **Coste de contexto subestimado** → cargar varias imágenes o PDFs grandes en una solicitud puede superar el presupuesto de tokens.

La transcripción recomienda medir el coste de tokens con entradas del tamaño real de producción antes de construir el pipeline.

---

