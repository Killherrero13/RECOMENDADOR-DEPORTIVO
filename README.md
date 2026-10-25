# Resumen deportivo personal

## Mejoras funcionales: segunda tanda

La agenda respeta tu disponibilidad desde las 06:30 hasta las 00:00, ampliando las noches de
viernes y sábado hasta las 01:00 del sábado/domingo. Incluye la tabla del día siguiente si
está publicada; si falta, lo indica en el correo en lugar de inventar la cobertura nocturna.

Cada evento incluye fecha y final estimado. Si excede tu hora límite pero puedes ver al menos
30 minutos, aparece marcado como visionado parcial con la hora de corte. La madrugada pierde
un punto y el visionado parcial medio punto; siguen siendo candidatos si su interés es alto.
Al ejecutar manualmente se descartan los terminados y se señalan los eventos en curso.

El plan fija el imprescindible y recorre los candidatos restantes de mayor a menor puntuación,
comprobando solapamientos con duraciones estimadas por deporte. La presentación se mantiene
cronológica; las alternativas siguen ordenadas por puntuación. No se garantiza la combinación
con la mayor suma global de puntos, y las duraciones reales pueden variar.

Hay 57 pruebas: se comprueban también el cruce de medianoche, viernes/sábado/domingo,
los límites de disponibilidad, el visionado parcial, la lectura de la tabla de mañana y los
solapamientos por deporte. La selección de camiseta y los nuevos pesos deportivos/canales
todavía están pendientes; consulta `PREFERENCIAS.md` para ver el estado completo.

Prueba sin envío: `python -m resumen --modo eventos --salida vista_previa`.
Desde Actions, el modo `eventos` envía el resumen real con la nueva agenda y tus secretos actuales.

---

## Mejoras funcionales: primera tanda

Se han corregido las fases de eliminatorias, el bonus duplicado de Estudiantes, los alias de
equipos y el reconocimiento de competiciones. La calidad de un partido cuenta sus participantes
en lugar de etiquetas coincidentes. Se conservan todos los eventos seleccionados en el plan y
las alternativas se ordenan por puntuación antes de limitarse a ocho.

Las preferencias indicadas por el usuario y el estado de cada mejora están en `PREFERENCIAS.md`.
El horario de disponibilidad, los nuevos pesos deportivos, los canales concretos y la recomendación
de camiseta por evento todavía no se han aplicado. El envío diario sigue a las 08:30.

Hay 49 pruebas. Las siete pruebas de referencia mantienen congelado el comportamiento original;
las pruebas del recomendador actual comprueban ya las correcciones aprobadas, sin exigir que
se reproduzcan los errores originales. Las secciones de migración siguientes se conservan como
registro histórico; las referencias a alternativas por hora corresponden a aquella versión.

Para probar el nuevo resumen sin enviar correo:

```powershell
.\.venv\Scripts\python.exe -m resumen --modo eventos --salida vista_previa
```

Desde GitHub, ejecutar manualmente «Resumen deportivo diario» en modo `eventos` envía un
correo real con la nueva lógica. No es necesario cambiar secretos ni la configuración horaria.

---

## GitHub Actions: ejecución diaria y desde el móvil

Repositorio: https://github.com/Killherrero13/RECOMENDADOR-DEPORTIVO

El workflow «Resumen deportivo diario» ejecuta ambos procesos a las **08:30 Europe/Madrid**.
La zona horaria del propio schedule contempla invierno y verano; GitHub puede iniciar
la ejecución con retraso. El correo llegará después de completar las consultas y el envío.
El workflow debe estar en la rama predeterminada del repositorio para programarse.

### Configura estos cuatro secretos

En Settings → Secrets and variables → Actions → New repository secret:

| Nombre exacto | Valor |
| --- | --- |
| `FOOTBALL_API_KEY` | La clave de football-data que ya probaste |
| `SMTP_USERNAME` | La dirección Gmail desde la que enviaste la prueba |
| `SMTP_PASSWORD` | La contraseña de aplicación de Google que ya funcionó |
| `EMAIL_TO` | La dirección donde quieres recibir el resumen |

Enlace directo: https://github.com/Killherrero13/RECOMENDADOR-DEPORTIVO/settings/secrets/actions

No se necesita `EMAIL_FROM`: el remitente será `SMTP_USERNAME`. No subas archivos `.env`,
contraseñas ni claves al repositorio. No se imprimen los secretos en los logs.
Los secretos solo se entregan al paso de ejecución real; las pruebas no los reciben.

### Primera ejecución desde GitHub

1. Abre Actions → «Resumen deportivo diario» → Run workflow.
2. Deja la rama predeterminada y selecciona `ambos`.
3. Pulsa Run workflow una vez. Esa ejecución envía un correo real.
4. Comprueba el estado de la ejecución y la recepción en Gmail.

Después podrás lanzarlo igual desde el navegador del móvil y elegir `ambos`, `eventos` o `camiseta`.
Cada lanzamiento manual envía un correo nuevo; no se aplica deduplicación entre lanzamientos.
No hace falta mantener encendido tu ordenador.

### Qué comprueba GitHub

- «Comprobaciones sin correo» se ejecuta al subir cambios o abrir una propuesta de cambios.
  Instala dependencias y ejecuta las 41 pruebas sin contactar con las fuentes ni Gmail.
- El workflow diario también ejecuta las pruebas antes de consultar y enviar.
- Si falla una fuente, se envía lo disponible con aviso y la ejecución queda en rojo.
- Si falla Gmail, la ejecución queda en rojo. Revisa la bandeja antes de repetir para evitar duplicados.
- Solo se permite una ejecución del resumen a la vez; una nueva no cancela un envío en curso.
- Los jobs tienen límite de diez minutos y permisos de lectura del repositorio.
- No se publican los resúmenes como artefactos de GitHub. Quedan el correo y los logs de diagnóstico.

Activa las notificaciones de fallos de Actions en tu configuración de GitHub. Si el repositorio
es público, GitHub puede desactivar la programación tras 60 días sin actividad: comprueba el
workflow si deja de llegar el correo. En privado, revisa también el cupo mensual de tu cuenta.

La recepción real con Gmail en local fue confirmada por el usuario. La Fase 6 solo quedará
validada tras una ejecución manual correcta en GitHub y después la primera ejecución programada.

Documentación: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onschedule

---

## Fase 5: envío por Gmail

Se incorpora `resumen/correo.py`, usando solo bibliotecas estándar de Python.
El envío es opcional: únicamente ocurre al añadir `--enviar`.
La presentación de la Fase 4 fue revisada y aceptada por el usuario.

### Primera prueba real: un correo de demostración

1. Activa la verificación en dos pasos en la cuenta Gmail que enviará el resumen.
2. En https://myaccount.google.com/apppasswords crea una contraseña de aplicación
   con nombre «Resumen deportivo». No utilices tu contraseña habitual de Google.
3. Desde la carpeta del proyecto, ejecuta:

```powershell
.\probar_correo.ps1
```

El asistente pide la cuenta remitente, el destino (Enter para enviártelo a ti mismo)
y la contraseña de aplicación oculta. Envía un único email marcado `[DEMO]` con HTML y texto.
No consulta football-data ni la web de eventos. Las variables temporales se restauran al terminar;
no se escribe la contraseña en archivos. No pegues esa contraseña en el chat.
Si PowerShell impide ejecutar el archivo, puedes ejecutar esta alternativa que aplica solo a ese proceso:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\probar_correo.ps1
```

Si tu entorno no existe aún, créalo con las instrucciones de la Fase 2.
Comprueba recepción y presentación en Gmail desde el móvil. Si no lo ves, revisa Spam y Enviados.
El mensaje «Gmail ha aceptado el correo para su entrega» confirma aceptación SMTP;
la recepción en la bandeja debe comprobarse por separado.

Google requiere verificación en dos pasos para las contraseñas de aplicación; la opción puede no
estar disponible con Protección Avanzada o determinadas cuentas administradas. Si falta esa opción,
indícalo antes de continuar: habría que valorar OAuth u otro servicio de envío.
Fuente: https://support.google.com/accounts/answer/185833?hl=es

### Configuración para ejecución normal y futuro GitHub Actions

Variables obligatorias: `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_TO`.
`EMAIL_FROM` es opcional y debe coincidir con `SMTP_USERNAME` si se indica.
Solo se admite un destinatario para esta automatización personal.
El servidor se fija a `smtp.gmail.com`, puerto 465, con TLS desde el inicio y validación del certificado.
No se necesitan más paquetes de Python.

Con las variables configuradas en el entorno:

```powershell
# Genera y envía ambos resultados reales; requiere también FOOTBALL_API_KEY.
.\.venv\Scripts\python.exe -m resumen --modo ambos --enviar --salida vista_previa
# Solo eventos reales; no necesita FOOTBALL_API_KEY.
.\.venv\Scripts\python.exe -m resumen --modo eventos --enviar
```

Sin `--enviar` no se conecta con Gmail. Tampoco se consultan las fuentes deportivas si
se solicita envío pero falta la configuración de correo.
Si falla una fuente se envía el resumen parcial; si fallan ambas se envía el aviso de fallo.
En ambos casos la ejecución termina en error, aunque el correo se haya enviado.
Un fallo SMTP también produce salida 1. No se reintenta automáticamente un envío, para evitar
duplicados cuando la conexión se interrumpe después de entregar el mensaje al servidor.
Los errores de autenticación o entrega no muestran contraseñas ni respuestas crudas del servidor.

### Verificación

41 pruebas automáticas correctas, incluidas ocho nuevas para configuración, mensaje multipart,
conexión cifrada, autenticación, fallos sanitizados, destinatario rechazado, envío explícito
y envío parcial con estado de error. SMTP está simulado en las pruebas: no se ha enviado ningún
correo real desde este entorno. Se ha comprobado también la sintaxis del asistente PowerShell.

La prueba real de recepción queda pendiente de tu ejecución. No avanzaremos al workflow diario
hasta confirmar que recibes y lees correctamente ese primer correo.

---

## Fase 4: resumen combinado y vista previa

El nuevo coordinador ejecuta los procesos de forma independiente. Genera una única presentación
en HTML adaptable al ancho de pantalla y texto, sin enviar correo. Las reglas de recomendación
no han cambiado. Las fases 2 y 3 fueron probadas y confirmadas como correctas por el usuario.

### Revisión visual sin credenciales

Desde esta carpeta:

```powershell
.\.venv\Scripts\python.exe -m resumen --sin-conexion --salida vista_previa
Start-Process .\vista_previa\resumen.html
```

El ejemplo está marcado como DEMO y contiene datos ficticios. También puedes abrir directamente
`vista_previa/resumen.html`, ya generado en esta entrega. Al estrechar la ventana a un ancho
similar al de un móvil, el texto debe ajustarse sin desplazamiento horizontal.
La apariencia final en cada aplicación de correo se comprobará al enviar el primer mensaje en la Fase 5.

### Tres modos

```powershell
# Ambos procesos; requiere FOOTBALL_API_KEY configurada en el entorno.
.\.venv\Scripts\python.exe -m resumen --modo ambos --salida vista_previa
# Solo eventos; no requiere clave.
.\.venv\Scripts\python.exe -m resumen --modo eventos --salida vista_previa
# Solo camiseta y los partidos de la API.
.\.venv\Scripts\python.exe -m resumen --modo camiseta --salida vista_previa
```

El modo por defecto ahora es `ambos`. Para introducir la clave sin guardarla en el historial,
utiliza el bloque de PowerShell de la Fase 2, cambiando su orden de ejecución por:

```powershell
.\.venv\Scripts\python.exe -m resumen --modo ambos --salida vista_previa
```

`--salida` guarda `resumen.html` y `resumen.txt`, sobrescribiendo la vista previa anterior.
Sin esa opción se muestra solo la versión de texto en la terminal.

### Contenido y fallos parciales

- Camiseta elegida y aviso honesto de que no tiene partido asociado.
- Imprescindible, plan principal y alternativas, conservando su orden original por hora.
- En modo combinado con eventos disponibles no se repite la lista de partidos de football-data.
- En modo camiseta, o si falla eventos, sí se muestran los partidos disponibles de football-data.
- Un fallo de una fuente no impide intentar la otra. Se incluye un aviso y el asunto lleva
  `[CON ERRORES]`. También se guarda la vista previa parcial y se devuelve código 1.
- Si fallan ambas fuentes, se genera el aviso de fallo total, también con código 1.
- Código 0 significa que todos los procesos solicitados terminaron correctamente.
- Los errores inesperados se registran con el tipo de excepción, sin incluir su detalle potencialmente sensible.
- Los textos de fuentes externas se escapan antes de insertarlos en HTML.

Comprobación automática: 33 pruebas correctas, incluidos los tres modos, guardado UTF-8,
equivalencia de contenido HTML/texto, escape HTML y fallos parciales y totales simulados.
No se ha ejecutado aquí el modo combinado con tu credencial real: las fuentes por separado ya
están validadas, y la integración se prueba con datos controlados sin acceder a tu clave.

Tu siguiente paso es revisar la vista previa y confirmar que el contenido y la presentación
te sirven. La siguiente fase añadirá el envío SMTP; todavía no hay configuración ni envíos de correo.

---

## Fase 3: eventos fuera de Colab

Se han separado descarga y extracción (`resumen/fuente_eventos.py`), preferencias
(`resumen/preferencias_eventos.py`) y recomendación (`resumen/eventos.py`).
Las funciones de puntuación y agenda, los filtros y sus constantes se han conservado del original.
No se realizan consultas al importar los módulos.

### Tu prueba

Desde esta carpeta, utilizando el entorno creado en la Fase 2:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m resumen --modo eventos
```

Esta ejecución no requiere clave API ni envía correo. Contrasta el imprescindible, el plan
y las alternativas con el cuaderno ejecutado el mismo día. Si coinciden, queda validada la fase.
La ejecución de camisetas sigue disponible con `--modo camiseta` (también es el modo por defecto).
Para un ejemplo ficticio sin conexión, añade `--sin-conexion` a cualquiera de los dos modos.
El modo combinado se incorporará en la Fase 4.

### Verificación realizada

- 25 pruebas automáticas correctas: las 19 anteriores y seis de eventos.
- Descarga real HTTP 200 el 25/10/2026, con tres tablas: hoy y próximos días.
- 283 eventos en la primera tabla, cuya cabecera indica 25/10/2026.
- Se guardó ese HTML en `tests/fixtures/eventos_real_2026-10-25.html` para repetir las pruebas sin conexión.
- Los 283 eventos extraídos coinciden con el scraping original sobre el mismo HTML.
- Los filtros, puntuaciones, plan y alternativas coinciden con el original tanto en el día
  ficticio de referencia como en el HTML real guardado.
- Se comprueba que la recomendación no modifica los eventos de entrada.

La muestra HTML es solo material de prueba; nunca se utiliza como sustituto de una descarga fallida.
Todavía queda comprobar el acceso desde los servidores de GitHub Actions en la fase de despliegue.

### Errores y límites

La descarga usa tiempos máximos y hasta tres intentos para errores de conexión y HTTP 5xx.
HTTP 403/429, tabla ausente, fecha ausente o distinta de la esperada y tabla sin eventos
reconocibles producen un mensaje claro y salida 1, en lugar de una agenda vacía silenciosa.
Una tabla vacía se trata de manera conservadora como error de fuente; aún no tenemos una
muestra fiable de cómo representa la web un día sin emisiones.
Una tabla con eventos válidos pero ninguno que supere los filtros sí genera un resultado vacío válido.

Se conservan las horas publicadas por la web, que no incluyen zona horaria explícita en cada fila;
se usa la fecha de Madrid para validar la cabecera. No se ha añadido exclusión de eventos ya
pasados ni corregido los comportamientos de puntuación y agenda documentados en la Fase 1.
Las alternativas mantienen su orden original por hora.

---

## Fase 2: camisetas fuera de Colab

El módulo `resumen/camisetas.py` lee la colección JSON, consulta football-data y devuelve
un resultado estructurado. La elección sigue siendo aleatoria y no se vincula a los partidos.
Los originales de `referencia/` permanecen intactos.

Necesitas Python 3.12 o posterior. Desde esta carpeta, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m resumen --sin-conexion
```

La última orden muestra una demostración ficticia; no consulta la API ni necesita clave.
En Linux utiliza `.venv/bin/python` en lugar de `.\.venv\Scripts\python.exe`.
Las dependencias de esta fase son `requests` y, solo en Windows, `tzdata`.
Beautiful Soup se incorporará cuando migremos eventos.

### Prueba real pendiente

Para probar la API real sin guardar la clave en archivos ni en el historial de órdenes,
desde esa misma carpeta en PowerShell:

```powershell
$claveTemporal = Read-Host 'Introduce tu FOOTBALL_API_KEY' -AsSecureString
$env:FOOTBALL_API_KEY = [System.Net.NetworkCredential]::new('', $claveTemporal).Password
try {
    .\.venv\Scripts\python.exe -m resumen
} finally {
    Remove-Item Env:FOOTBALL_API_KEY -ErrorAction SilentlyContinue
    Remove-Variable claveTemporal -ErrorAction SilentlyContinue
}
```

La clave se usa durante la ejecución y se elimina de esa sesión al acabar. No la pegues en el chat.
`.env.example` documenta el nombre; el programa no carga archivos `.env` automáticamente.
Más adelante configuraremos el mismo nombre como GitHub Secret.

Resultado esperado: camiseta, fecha de Madrid y partidos disponibles con su hora y competición.
Una lista vacía es válida; un problema de autenticación, límite, conexión o respuesta inválida
produce un mensaje de error y código de salida 1. El correo todavía no está implementado.
Para completar la comprobación real, comunica si la ejecución termina correctamente; si falla,
comparte solo el mensaje de error del programa, sin la clave.

### Robustez implementada

- Tiempo máximo de conexión de 5 segundos y de lectura de 20 segundos por petición.
- Hasta tres intentos para fallos de conexión, espera agotada y HTTP 5xx, con pausas de 1 y 2 segundos.
- HTTP 401, 403 y 429 se explican sin repetir consultas innecesarias.
- No se siguen redirecciones con la cabecera de autenticación.
- No se imprimen la clave, las cabeceras, el cuerpo HTTP ni las excepciones de red originales.
- Validación del JSON y de los campos necesarios de cada partido del día.
- Consulta por fechas UTC suficientemente amplia y filtrado por día de Madrid. Esto corrige
  la omisión de encuentros cercanos a medianoche, sin cambiar la selección de camiseta.
- Se mantiene el filtro de presentación de dos horas desde el inicio del partido.

La API v4 documenta `dateTo` como exclusivo:
https://docs.football-data.org/general/v4/index.html
La cobertura de partidos sigue dependiendo de tu suscripción a football-data.
No se han añadido pesos, historial ni filtros por estado del partido.

Las pruebas adicionales comprueban la equivalencia de selección con 20 semillas, cambio de hora,
medianoche, errores HTTP, reintentos, respuestas inválidas y resultado estructurado.
La prueba real de API fue realizada por el usuario y confirmada como correcta.

---

## Referencia de la Fase 1

Esta entrega fija una referencia verificable antes de migrar los programas de Colab.
Todavía no es una automatización: no consulta servicios, no usa credenciales y no envía correo.

## Archivos

- `referencia/`: copias byte a byte de los dos archivos recibidos y sus huellas SHA-256.
- `data/camisetas.json`: las 64 camisetas originales, conservando orden, campos y tipos.
- `tests/fixtures/eventos.json`: 13 eventos ficticios para comprobar filtros y agenda.
- `tests/fixtures/resultado_esperado.json`: resultado de referencia revisado, con 9 eventos tras el filtrado.
- `tests/referencia.py`: carga la lógica original mediante el árbol sintáctico de Python; omite las consultas, los imports externos y la ejecución de Colab.
- `tests/test_referencia.py`: siete pruebas sin conexión con la biblioteca estándar.

## Cómo comprobar esta fase

Con Python 3.12, desde esta carpeta:

```console
python -m unittest discover -s tests -v
```

No hay paquetes que instalar para esta fase. Las cadenas de formato del original de eventos requieren Python 3.12 o posterior.
No ejecutes las copias de `referencia/` para esta comprobación: conservan las dependencias y consultas de los originales.

## Resultado del día ficticio

| Hora | Evento | Puntuación | Resultado |
| --- | --- | --- | --- |
| 09:00 | Alcaraz – Sinner, ATP 500 Semifinal | 12 | Mañana |
| 11:00 | Estudiantes – Valencia, Liga Endesa | 15,5 | Imprescindible |
| 13:00 | Arsenal – Chelsea, Premier League | 9,144 | Mediodía |
| 15:00 | At. Madrid – Real Madrid, LaLiga | 11,96 | Tarde |
| 16:00 | Fórmula 1 Carrera | 4,5 | Fuera del plan y alternativas |
| 17:00 | Liverpool – Arsenal, Champions League Semifinal | 14,104 | Alternativa |
| 17:15 | FC Barcelona – Valencia, LaLiga | 9,4876 | Alternativa |
| 20:00 | Aston Villa – Chelsea, Premier League | 9,084 | Alternativa |
| 22:00 | Celtics – Warriors, NBA | 11,8 | Alternativa |

Se excluyen el evento de las 08:00, la hora `PD`, el evento femenino y Primera Federación, según los filtros originales.

## Comportamiento que se conserva

- La camiseta se elige al azar entre las 64 entradas, sin pesos ni relación con los partidos; puede repetirse entre días.
- No existe persistencia ni historial de uso.
- Estudiantes suma dos veces el bonus de 4 puntos.
- `Semifinal` recibe 2,5 puntos porque contiene `final`.
- La agenda toma el imprescindible por puntuación y después recorre el resto por hora; se limita a cuatro seleccionados.
- Dos seleccionados de una misma franja pueden sobrescribirse en el plan visible.
- Las alternativas se ordenan por hora, no por puntuación global.
- El solapamiento permitido es de hasta 30 minutos, con duración estimada de 120 minutos para todos los deportes.
- El filtro efectivo empieza a las 09:00 aunque `DAY_START` indique las 07:00.

Estos comportamientos quedan documentados; no se han corregido en esta fase.

## Alcance de la verificación

Las pruebas comprueban integridad, extracción de la colección, selección aleatoria controlada,
filtros, puntuaciones, agenda, alternativas, ausencia de eventos y límite de solapamiento.
El resultado esperado se obtuvo del original y se revisó; sirve como referencia para contrastar
la futura implementación, no como demostración de que las reglas actuales sean las deseadas.
No se ha verificado aún la API real, el HTML real, SMTP ni la ejecución en GitHub Actions.

## Tu revisión antes de la Fase 2

1. Revisa la colección JSON y la tabla del día ficticio.
2. Confirma que podemos conservar estos comportamientos como referencia de la migración.
3. Si quieres repetir la prueba, utiliza el comando anterior; si no tienes Python local, no es necesario instalarlo para revisar esta entrega.

La extracción original se conserva como referencia. El proceso de camisetas ya se ha preparado en
la Fase 2 descrita arriba. Las credenciales se configuran en el entorno correspondiente, nunca en este documento ni en el chat.
