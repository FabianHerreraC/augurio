# Augurio Colectivo

Spec completo del proyecto para su continuación en Claude Code. Este documento contiene todo lo necesario para entender el contexto, la arquitectura, el estado actual y el trabajo pendiente sin depender de conversaciones previas.

## 1. Contexto del proyecto

### 1.1 Marco general

El proyecto es un ejercicio en vivo llamado **Augurio Colectivo**, diseñado para el taller **Cognición Aumentada. La Universidad El Bosque en la era de la inteligencia artificial**. El taller dura dos horas, es para máximo diez participantes y se realiza con el rector, tres vicerrectores (Académico, Administrativo, de Investigaciones), un representante del claustro y una persona adicional de la Universidad El Bosque en Bogotá.

El taller lo dirige Fabian Herrera, director del pregrado en Creación Digital de la Universidad El Bosque, autor de un marco conceptual llamado *cognición aumentada*, publicado en `https://fabianherrerac.github.io/cognicion-aumentada/`.

### 1.2 Propósito del ejercicio

El taller se organiza en dos módulos de una hora. El primero, *Vivir el paradigma*, contiene este ejercicio: cada participante responde en silencio tres preguntas críticas sobre la Universidad y el sistema devuelve, a los pocos minutos, un material aumentado que integra las voces del grupo con una muestra externa de referencia. El objetivo pedagógico es que los asistentes experimenten, sin explicación previa, cómo la orquestación de personas y máquinas produce una cognición colectiva que ningún participante generó por sí solo. La frase que resume el momento es "sin hablar, hablaron".

El ejercicio debe entregar tres cosas al cierre:
1. Una arquitectura clara de las capacidades funcionales y cognitivas que ofrece la IA en sus herramientas más avanzadas.
2. Una reflexión práctica sobre cómo esas capacidades podrían habitar en la Universidad y en el trabajo de cada área.
3. Unas líneas críticas para considerar al decidir en torno a la IA, en cuanto a riesgos, límites y prioridades.

### 1.3 Las tres preguntas del formulario

Están fijadas y son las mismas para todos los participantes:

1. **La singularidad.** ¿Qué hace a la Universidad El Bosque verdaderamente única frente a las demás? Frase de contexto: *nombra lo que solo aquí ocurre. Si desapareciera, El Bosque dejaría de ser El Bosque.*
2. **El dolor propio.** ¿Cuál es el dolor más importante que la Universidad debe resolverse a sí misma en 2026? Frase de contexto: *la herida que nos hacemos solos y venimos aplazando, no la que viene de afuera.*
3. **El proyecto.** ¿Cuál es el proyecto más importante que la Universidad El Bosque debe realizar en 2026? Frase de contexto: *si solo uno pudiera avanzar este año, cuál tendría que ser.*

### 1.4 Devolución esperada del sistema

El sistema devuelve dos capas de material.

**Capa colectiva**, compartida y proyectada:
- Conclusión colectiva del grupo, síntesis de lo que emerge al leer las seis respuestas juntas.
- Agrupamiento, descripción de cómo se agrupan las voces del grupo, qué constelaciones o tensiones aparecen.

**Capa personal**, visible solo para cada participante tras un selector de usuario:
- Posición en el colectivo, cómo se sitúa esa voz en el conjunto.
- Comparativo con una muestra externa de referencia pre-cargada.
- Lectura crítica de la propuesta, en registro afilado sobre la idea pero cuidadoso con la persona.

## 2. Arquitectura del sistema

### 2.1 Componentes

Tres piezas conectadas por webhooks:

- **Google Sheets** llamado `augurio`, funciona como base de datos y como pizarra transparente del ejercicio.
- **n8n** en la nube (`https://fabianh.app.n8n.cloud`), orquesta tres flujos independientes.
- **Web estática autocontenida**, un solo archivo HTML que sirve a los dos momentos del ejercicio.

### 2.2 Flujo de datos

**Captura.** Cada participante abre la web en la vista de captura, elige su usuario, responde las tres preguntas y envía. La web hace POST al webhook `augurio-captura`, que escribe la fila en la pestaña `respuestas` de Sheets.

**Procesamiento.** El facilitador dispara desde la vista de revelación un POST al webhook `augurio-procesar`. Ese flujo lee todas las filas de `respuestas` y todas las de `muestra` (pre-cargada a mano antes del taller), arma un prompt único con ambos bloques, llama a la API de Anthropic, parsea el JSON de respuesta y escribe una fila por usuario en la pestaña `resultados`.

**Lectura.** La misma vista de revelación consulta por GET el webhook `augurio-resultados`, que devuelve el contenido completo de la pestaña `resultados`. La web muestra el bloque colectivo arriba, siempre visible, y despliega el bloque personal solo cuando el participante selecciona su usuario en un selector.

### 2.3 Modelo de privacidad

El selector de usuario es una **cortina, no una cerradura**. No hay autenticación. Cualquiera podría elegir el rol de otro. Para el contexto de seis personas de confianza en la sala es suficiente, pero el spec debe conservar esta claridad. No se debe vender como confidencial de verdad.

## 3. Estado actual del proyecto

### 3.1 Google Sheets `augurio`

Existe y está configurado. Tres pestañas con encabezados en la fila 1:

- **respuestas**: `timestamp`, `rol`, `q1_unica`, `q2_dolor`, `q3_proyecto`
- **muestra**: `rol`, `q1_unica`, `q2_dolor`, `q3_proyecto`
- **resultados**: `rol`, `posicion`, `comparativo`, `critica`, `colectivo_conclusion`, `colectivo_agrupamiento`, `colectivo_grafo`

La pestaña `muestra` contiene datos dummy en la fase de pruebas. Antes del taller debe poblarse a mano con diez respuestas externas de referencia que sirvan de contraste para el bloque personal.

### 3.2 n8n

Los tres flujos existen y funcionan de punta a punta. Todos usan la misma credencial de Google Sheets ya conectada.

**Flujo 1. Captura.**
- **Webhook**: POST, path `augurio-captura`, Respond en `Using Respond to Webhook node`.
- **Google Sheets · Append Row** en `respuestas`, mapeo manual: `timestamp` con `{{$now}}`, `rol` con `{{ $json.body.rol }}`, `q1_unica` con `{{ $json.body.q1 }}`, `q2_dolor` con `{{ $json.body.q2 }}`, `q3_proyecto` con `{{ $json.body.q3 }}`.
- **Respond to Webhook**: JSON `{ "ok": true }`.

**Flujo 2. Procesamiento.**
- **Webhook**: POST, path `augurio-procesar`.
- **Google Sheets · Get Row(s)** de `respuestas`, sin filtros.
- **Google Sheets · Get Row(s)** de `muestra`, sin filtros, en serie después del anterior.
- **Code (JavaScript)**, modo *Run Once for All Items*. Arma el `prompt` con las respuestas y la muestra, y devuelve además un `payload` como objeto listo para la API. Código actual:

```javascript
const respuestas = $('respuestas').all().map(i => i.json);
const muestra = $('muestra').all().map(i => i.json);

const bloqueRespuestas = respuestas.map(r =>
  `[${r.rol}]\n1. Única: ${r.q1_unica}\n2. Dolor: ${r.q2_dolor}\n3. Proyecto: ${r.q3_proyecto}`
).join('\n\n');

const bloqueMuestra = muestra.map(r =>
  `- Única: ${r.q1_unica} | Dolor: ${r.q2_dolor} | Proyecto: ${r.q3_proyecto}`
).join('\n');

const listaRoles = respuestas.map(r => r.rol).join(', ');

const prompt = `Eres un analista senior que sintetiza las respuestas de un grupo directivo de la Universidad El Bosque en Bogotá. Este es un ejercicio de cognición aumentada: seis a diez personas respondieron en silencio tres preguntas y el sistema devuelve una lectura que ninguna de ellas produjo sola. Tu trabajo es hacer visible lo que emerge del conjunto y darle a cada persona una devolución honesta.

Las tres preguntas fueron:
1. Única: qué hace única a la Universidad El Bosque frente a las demás.
2. Dolor: el dolor más importante que la Universidad debe resolverse a sí misma en 2026.
3. Proyecto: el proyecto más importante que debe realizar en 2026.

RESPUESTAS DEL GRUPO:
${bloqueRespuestas}

MUESTRA EXTERNA DE REFERENCIA (voces de fuera del comité, para contraste):
${bloqueMuestra}

Analiza y devuelve un objeto con tres partes: una lectura COLECTIVA, un GRAFO de agrupamiento y una lectura PERSONAL por cada participante.

Para la parte COLECTIVA:
- "conclusion": la síntesis de lo que emerge al leer las respuestas juntas. No resumas una por una; nombra el patrón de fondo, la idea que sobrevuela al grupo y que nadie escribió sola. Dos o tres frases densas, sin relleno.
- "agrupamiento": cómo se agrupan las voces. Nombra las constelaciones (quiénes convergen y en torno a qué) y las tensiones (dónde el grupo se divide o se contradice). Puedes usar los roles para señalar los polos. Concreto, no genérico.

Para el GRAFO de agrupamiento:
- "ideasCentrales": entre 2 y 4 ideas que se repiten de verdad en las respuestas del grupo (cada una debe aparecer en al menos dos voces). Cada una con "id" ("c1", "c2"...), "label" corto de una a tres palabras, y "desc": un párrafo de 3 a 4 frases que diga qué es la idea, cómo aparece en las voces del grupo y qué tensión o pregunta carga.
- "ideasAusentes": entre 2 y 3 temas relevantes para una universidad en 2026 que nadie del grupo mencionó. Cada una con "id" ("a1", "a2"...), "label" corto, y "desc": un párrafo de 3 a 4 frases que explique qué quedó fuera y por qué ese silencio importa.
- "conexiones": pares { "from": rol, "to": id de idea central } que indican qué participante sostiene qué idea central en sus respuestas. Entre 1 y 3 conexiones por participante. Usa exactamente los roles de la lista (${listaRoles}) y los ids de "ideasCentrales". Las ideas ausentes no llevan conexiones.

Para CADA participante, en el orden en que aparecen (${listaRoles}):
- "rol": copia exactamente el identificador entre corchetes tal como aparece arriba. No lo traduzcas ni lo cambies.
- "posicion": dónde se sitúa esta voz dentro del grupo. Con quién coincide, de quién se aparta, si ocupa un lugar central o un extremo. Habla del conjunto, no repitas su respuesta.
- "comparativo": qué revela contrastar esta voz con la muestra externa. En qué se alinea con la mirada de afuera y en qué se distancia. Si aporta un ángulo que la muestra no tiene, dilo.
- "critica": lectura afilada de su propuesta. Muestra el supuesto que la volvería frágil y la condición bajo la cual se sostiene. Sé exigente con la idea y cuidadoso con la persona: cuestiona el argumento, nunca a quien lo escribió.

Reglas:
- Responde en español.
- Si una respuesta quedó demasiado corta, vaga o vacía, dilo con tacto ("la respuesta quedó escueta para leerla a fondo") en vez de inventar densidad que no estaba.
- Devuelve una entrada en "personas" por cada rol del grupo, ni más ni menos.
- Devuelve SOLO el JSON válido, sin texto antes ni después y sin bloques de código. Esta es la forma exacta:
{
  "colectivo": { "conclusion": "", "agrupamiento": "" },
  "grafo": {
    "ideasCentrales": [ { "id": "c1", "label": "", "desc": "" } ],
    "ideasAusentes": [ { "id": "a1", "label": "", "desc": "" } ],
    "conexiones": [ { "from": "", "to": "" } ]
  },
  "personas": [
    { "rol": "", "posicion": "", "comparativo": "", "critica": "" }
  ]
}`;

return [{
  json: {
    prompt,
    payload: {
      model: "claude-sonnet-4-6",
      max_tokens: 8000,
      messages: [{ role: "user", content: prompt }]
    }
  }
}];
```

- **HTTP Request** a Anthropic. Método POST, URL `https://api.anthropic.com/v1/messages`. Headers: `x-api-key` con la key, `anthropic-version` con `2023-06-01`, `content-type` con `application/json`. Body en modo JSON con la sola expresión `{{ $json.payload }}` en modo expresión.
- **Code (JavaScript)** de parseo:

```javascript
const texto = $json.content[0].text;

let data;
try {
  data = JSON.parse(texto);
} catch (e) {
  const limpio = texto.replace(/```json/g, '').replace(/```/g, '').trim();
  data = JSON.parse(limpio);
}

const col = data.colectivo || {};

// El grafo viaja como string JSON. "usuarios" no lo genera el modelo:
// se inyecta aquí desde personas para garantizar ids exactos.
let grafoStr = "";
if (data.grafo && Array.isArray(data.grafo.ideasCentrales)) {
  const g = data.grafo;
  g.usuarios = data.personas.map(p => ({
    id: p.rol,
    label: p.rol.charAt(0).toUpperCase() + p.rol.slice(1)
  }));
  grafoStr = JSON.stringify(g);
}

return data.personas.map(p => ({
  json: {
    rol: p.rol,
    posicion: p.posicion,
    comparativo: p.comparativo,
    critica: p.critica,
    colectivo_conclusion: col.conclusion,
    colectivo_agrupamiento: col.agrupamiento,
    colectivo_grafo: grafoStr
  }
}));
```

- **Google Sheets · Append or Update Row** en `resultados`, columna de coincidencia `rol`, mapeo manual con cada campo del item, incluido `colectivo_grafo`. (Antes era Append Row; se cambió para evitar filas duplicadas al reprocesar.)
- **Respond to Webhook**: JSON `{ "ok": true }`.

**Flujo 3. Lectura.**
- **Webhook**: GET, path `augurio-resultados`, Respond en `Using Respond to Webhook node`.
- **Google Sheets · Get Row(s)** de `resultados`, sin filtros.
- **Respond to Webhook**: `All Incoming Items` o `{{ $json }}`.

**URLs de producción confirmadas**:
- Captura: `https://fabianh.app.n8n.cloud/webhook/augurio-captura`
- Procesamiento: `https://fabianh.app.n8n.cloud/webhook/augurio-procesar`
- Lectura: `https://fabianh.app.n8n.cloud/webhook/augurio-resultados`

Los tres flujos deben quedar **activos** en n8n antes del taller. Sin activación, las URLs de producción no ejecutan.

### 3.3 Web estática

Existe un archivo `augurio.html` autocontenido y funcional. Un solo HTML sin dependencias externas, sin build, con CSS y JavaScript inline. Se hospeda en cualquier estático (GitHub Pages, Netlify, Vercel). Tres vistas controladas por parámetro de URL:

- Sin parámetro, portada con dos botones.
- `?vista=captura`, formulario de las tres preguntas con selector de usuario.
- `?vista=revelacion`, bloque colectivo arriba y bloque personal tras selector, más un panel de facilitador con botones para procesar y recargar.

Identificadores de usuario: `usuario1` a `usuario10`. Etiquetas visibles: `Usuario1` a `Usuario10`. El rol elegido se persiste en `localStorage` con la clave `augurio_rol`.

### 3.4 Estética

Referencia visual: el portafolio de Fabian Herrera, `https://fabianherrerac.github.io/`. Fondo negro casi total, tipografía grande en mayúsculas para titulares, numeración pequeña volada tipo `1. 2. 3.`, etiqueta ovalada blanca en la esquina superior derecha, texto rotado en el lomo izquierdo.

Sistema aplicado en la web:
- Fondo `#0A0A0A`, tinta `#FFFFFF`, gris de apoyo `#8A8A88`, línea `#242422`, campo `#141412`.
- Acento verde `#17F7A1`, reservado para lo accionable y la crítica: botón de enviar, foco de los campos, marcador de la pregunta activa, botones del panel de facilitador y borde de la tarjeta de lectura crítica en la revelación.
- Híbrido tipográfico: mayúsculas grandes para titulares y numeración, caja baja para lo que escriben y leen las personas, para que sea legible en respuestas largas.
- Etiqueta ovalada en la esquina superior derecha muestra el usuario activo en tiempo real.

### 3.5 Grafo de agrupamiento

La vista de revelación dibuja el agrupamiento como un grafo de fuerzas en canvas: puntos blancos para participantes, verdes (`#17F7A1`) para ideas que se repiten, rosas (`#FF4885`) con anillo punteado para ideas ausentes. Clic en una idea abre una tarjeta con su descripción; los puntos se pueden arrastrar sin que se desconecten las líneas.

Los datos viajan en la columna `colectivo_grafo` de `resultados` como string JSON con este contrato:

```json
{
  "usuarios": [ { "id": "usuario1", "label": "Usuario1" } ],
  "ideasCentrales": [ { "id": "c1", "label": "", "desc": "" } ],
  "ideasAusentes": [ { "id": "a1", "label": "", "desc": "" } ],
  "conexiones": [ { "from": "usuario1", "to": "c1" } ]
}
```

Notas del contrato:
- `usuarios` no lo genera el modelo: lo inyecta el nodo de parseo a partir de `personas`, para garantizar que los ids coincidan.
- Cada `desc` es un párrafo de 3 a 4 frases.
- Comportamiento de la web: si `colectivo_grafo` falta o no parsea, la revelación real oculta el grafo y muestra solo el texto de agrupamiento. El modo `?vista=revelacion&demo=1` usa una muestra embebida (`SAMPLE_GRAFO`) y datos de resultados de ejemplo, sin tocar n8n.

## 4. Trabajo pendiente

### 4.1 Iterar el prompt de procesamiento

El prompt actual en el nodo Code del flujo de procesamiento es funcional pero mínimo. Está pensado para ser afinado. La estructura de JSON de salida es un contrato que no se puede romper, porque el parseo y las columnas de Sheets dependen de que los campos se llamen exactamente `colectivo.conclusion`, `colectivo.agrupamiento`, y en cada persona `rol`, `posicion`, `comparativo`, `critica`.

Trabajo por hacer:
- Redactar instrucciones más ricas para cada campo, especialmente para la lectura crítica, que debe ser afilada sobre la idea pero cuidadosa con la persona, con el registro de "mostrar el supuesto que la volvería frágil y la condición bajo la cual se sostiene".
- Añadir guía sobre cómo tratar respuestas cortas o vagas: marcar cuando algo quedó demasiado escueto en vez de inventar densidad que no estaba.
- Considerar añadir instrucción para responder en español y sin bloques de código en la salida.
- Considerar subir `max_tokens` si el material queda corto para diez participantes.

### 4.2 Poblar la pestaña `muestra`

Antes del taller, escribir diez filas con respuestas externas de referencia. Estas voces son el contraste contra el que se lee cada bloque personal en el campo `comparativo`. Deben venir de personas fuera del comité, con diversidad de ángulos (docentes, egresados, estudiantes, pares de otras universidades).

### 4.3 Verificar CORS

La web hace fetch desde el navegador hacia los tres webhooks de n8n. Es posible que el navegador bloquee las llamadas por política de origen cruzado. Si aparece un error de CORS al probar la captura desde la web ya hospedada, hay que resolver del lado de n8n. Opciones:

- Añadir un nodo *Set* o *Function* previo al *Respond to Webhook* que devuelva headers CORS. En particular `Access-Control-Allow-Origin: *`, `Access-Control-Allow-Methods: GET, POST, OPTIONS`, `Access-Control-Allow-Headers: Content-Type`.
- Asegurar que los webhooks acepten peticiones OPTIONS. En n8n cloud algunos webhooks aceptan OPTIONS de forma automática, otros requieren un flujo dedicado.

### 4.4 Modo de respaldo pre-renderizado

Hay una promesa de un modo de respaldo por si el flujo de procesamiento falla en vivo. No está implementado. Idea: un parámetro adicional como `?fallback=1` que cargue un JSON de resultados pre-cargado desde un archivo estático, para poder seguir el ejercicio aunque la API se caiga. Este trabajo es opcional pero valioso como cinturón de seguridad.

### 4.5 Panel de facilitador

En la vista de revelación hay un panel al final con dos botones (`Generar material aumentado` y `Recargar resultados`), atenuado por defecto y que se resalta al pasar el mouse. Se puede ocultar tras una tecla o un parámetro para que no aparezca en el proyector, si se decide. Está a la vista para pragmatismo del día.

### 4.6 Estilo de la portada y detalles de motion

La portada actual es funcional pero muy sobria. Se puede enriquecer con detalles del portafolio de Fabian: la flecha triangular a la izquierda, texto rotado más presente, alguna animación de entrada discreta. No es prioritario pero sumaría carácter.

### 4.7 Prevención de duplicados en `resultados`

**Resuelto (2026-07-02)**: el nodo de escritura usa `Append or Update` con `rol` como columna de coincidencia, y la web además lee siempre la fila más reciente por rol. Se conserva el texto original como contexto.

El Append actual acumula. Si el facilitador dispara el procesamiento dos veces, la pestaña `resultados` queda con filas duplicadas y la web mostraría el primer resultado que encuentre por usuario, que no siempre será el más reciente. Salidas posibles:

- Cambiar la operación del último nodo de Sheets de `Append Row` a `Append or Update` con `rol` como columna de coincidencia. Reemplaza en vez de duplicar.
- O añadir al inicio del flujo de procesamiento un nodo que limpie la pestaña `resultados` antes de escribir de nuevo.
- O, en la web, filtrar por el timestamp más reciente por usuario.

## 5. Convenciones y decisiones importantes

- **Idioma**: todo el contenido visible al participante está en español.
- **Roles**: identificador interno en minúscula (`usuario1`), etiqueta visible con la inicial en mayúscula (`Usuario1`). El identificador es la llave que empata Sheets, el prompt y el filtro en la web.
- **JSON de Claude**: contrato inamovible en nombres de campos.
- **Modelo Anthropic**: `claude-sonnet-4-6`, balance de velocidad y calidad para la ventana de tiempo del ejercicio en vivo.
- **Estética**: mayúsculas para titulares, caja baja para contenido de personas, acento `#17F7A1` reservado, no decorativo.
- **Privacidad**: cortina, no cerradura.
- **Preferencia de estilo del autor**: Fabian prefiere respuestas concisas, con bullets solo para sintetizar, sin guiones largos como aposiciones explicativas, en español, con una pregunta de cierre en inglés y con feedback sobre su italiano en cada intercambio. Esto aplica a la conversación con Claude, no al contenido del producto.

## 6. Cómo probar el sistema completo

1. Activar los tres flujos en n8n.
2. Poblar la pestaña `muestra` con al menos dos filas para pruebas.
3. Hospedar `augurio.html` en un estático.
4. Abrir `?vista=captura` en dos pestañas distintas, elegir dos usuarios distintos, enviar dos respuestas.
5. Verificar en la pestaña `respuestas` que aparecen dos filas.
6. Abrir `?vista=revelacion`, pulsar "Generar material aumentado" en el panel de facilitador.
7. Esperar unos segundos y pulsar "Recargar resultados".
8. Verificar que el bloque colectivo aparece arriba con conclusión y agrupamiento.
9. Seleccionar cada usuario en el selector y verificar que aparece su bloque personal con posición, comparativo y crítica.

## 7. Archivo actual de la web

El archivo `augurio.html` de referencia (416 líneas) existe y funciona. Contiene los tres estados, la estética descrita y el router por parámetro. Debe conservarse su estructura general al iterar. Cambios previsibles: mejora de textos, ajustes de espaciado, ocultamiento del panel de facilitador tras tecla, modo de respaldo.

## 8. Enlaces útiles

- Portafolio y referente visual: `https://fabianherrerac.github.io/`
- Ensayo base del marco conceptual: `https://fabianherrerac.github.io/cognicion-aumentada/`
- n8n del proyecto: `https://fabianh.app.n8n.cloud/`
- Documentación de la API de Anthropic: `https://docs.claude.com/en/api/overview`
