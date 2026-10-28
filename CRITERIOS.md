# Criterios de puntuación · versión 2

Esta es una primera calibración de preferencias, no una medición objetiva de calidad ni un pronóstico.
Los valores son estables entre días: añadir otro partido no recalcula la nota de los existentes.

## Nota personal sobre diez

La nota combina el interés deportivo y la afinidad. Se redondea a una décima y queda entre 0 y 10.
El interés deportivo considera competición, cartel y fase, con techo de 8,5. La afinidad puede
completar la nota; no convierte todos los partidos de un favorito en un diez.

| Banda | Interpretación |
| --- | --- |
| 8–10 | Cita destacada |
| 6–7,9 | Buena opción |
| 4–5,9 | De fondo |
| Menos de 4 | Prescindible para este perfil |

El correo reserva «Imprescindible» para notas de 8 o más. Una cabecera «Lo mejor del día»
no afirma que ese evento tenga un interés excepcional. Un día sin candidatos de plan se
presenta como «Día tranquilo»; no se suben notas para llenar huecos.

## Bases deportivas iniciales

| Grupo | Base |
| --- | ---: |
| Mundial de fútbol | 6,2 |
| Eurocopa / Copa América | 5,8 |
| Champions / Europa League | 5,6 |
| Primera división europea principal | 5,0 |
| Conference League | 4,8 |
| Copa nacional | 4,5 |
| Segunda española / segunda alemana | 4,3 |
| Portugal / Eredivisie | 4,3 |
| Primera argentina / brasileña | 3,3 |
| Otra competición de fútbol admitida | 3,5 |
| NBA / Euroliga | 5,0 |
| ACB / Endesa / Copa del Rey de baloncesto | 4,5 |
| Mundial / Eurobasket / Juegos de baloncesto | 5,8 |
| Grand Slam de tenis | 5,8 |
| Masters 1000 | 5,0 |
| ATP 500 | 4,4 |
| ATP 250 | 3,8 |
| Tenis sin categoría reconocida | 3,2 |

El cartel añade hasta 2 puntos en fútbol y hasta 1,5 en baloncesto, según los dos participantes.
La lista de referentes es una selección de interés para este perfil, no una clasificación deportiva actual.
En tenis se añade 0,5 por un participante de referencia o 1,2 por dos; no se inventa un ranking en directo.
Una final añade 2,4; una semifinal 1,6; cuartos/playoffs genéricos 1,0; octavos 0,6.
El techo deportivo evita que se acumulen bonificaciones ilimitadas.

Atlético y Aston Villa tienen afinidad explícita de +1,3; Celtics también +1,3. Las afinidades
históricas de otros equipos y jugadores se conservan con un peso reducido. Se añade +0,2 por
la preferencia habitual de fútbol y +0,1 por baloncesto. Son ventajas suaves: una final de otro
deporte puede superar un partido ordinario de fútbol.

## Acceso y horario: encaje en la agenda

No cambian la nota personal:

- Una emisión por tus plataformas o por un canal abierto reconocido mejora el encaje en +0,2.
- Un canal distinto no resta puntos: puedes disponer de otra vía para verlo.
- La madrugada reduce el encaje en 0,6; un visionado parcial, en 0,5.
- Los filtros de disponibilidad siguen descartando lo terminado o con menos de 30 minutos visibles.

Se seleccionan hasta cuatro eventos con nota mínima de 6,5, priorizando el encaje y respetando
solapamientos. Las alternativas parten de 4,5 y se ordenan por encaje; en igualdad, por nota y hora.
El listado completo sigue mostrando todos los filtrados, también por debajo de esos umbrales.
El plan sigue usando intervalos completos o limitados por disponibilidad: aperitivos antes de
otra cita y seguimiento de marcador se implementarán en una fase posterior.

## Información todavía no utilizada

No se han añadido rachas, bajas, probabilidades, marcadores en directo ni clasificación actual.
Solo se puntúan datos disponibles en la programación y las preferencias registradas. El contexto
competitivo necesitará fuentes verificables y no se presume cuando falta.

Reglas editables en `resumen/puntuacion.py`. Comparaciones con ejemplos aportados y casos de control
acompañan esta fase para ajustar los pesos con criterio antes de añadir más funciones.


### Fase 1: reconocimiento de equipos y jugadores
Catálogo editorial de perfiles en resumen/perfiles.py, sin afirmar rankings ni forma actuales. Alias exactos por deporte normalizan Barça Basket, FC Bayern Basketball, Fenerbahce Istanbul, Panathinaikos BC, AX Olimpia Milano y otros. Euroliga y ACB tienen referentes separados; Euroleague equivale a Euroliga. No se aumenta su base: dos referentes mantienen +1,5 y uno +0,8. NBA en diferido y fútbol no cambian.

Tenis: figura editorial +1,2 por jugador, referente +0,5 y cruce entre dos reconocidos +0,5 adicional. Se incluyen Paul y Khachanov, además de Shelton, Tiafoe y Musetti. La afinidad conserva su peso, usando el máximo de ambos jugadores y coincidencia por palabras, independiente del orden. El mismo catálogo decide reconocimiento y filtrado. Ronda y categoría mantienen sus pesos. No hay bonus por nacionalidad, juventud, ranking, rachas ni contexto no disponible. Landaluce queda pendiente de fase 2; desconocido no significa jugador de bajo nivel.


### Fase 2: contexto deportivo con fecha y fuentes
En ejecución conectada se consulta contexto antes de calcular notas y planning. No requiere claves nuevas. Cuando el contexto modifica la nota, las tarjetas y el adjunto muestran ajuste efectivo, consulta y fuentes. El texto y la comparación conservan también la trazabilidad de datos validados sin bonus. El modo de demostración sigue sin hacer consultas.

Cobertura: ligas españolas de Primera/Segunda, Premier League, Serie A italiana, Bundesliga y Ligue 1 (ESPN), Euroliga (calendario oficial y clasificación de la última jornada completa), y contraste de categorías en primera ronda de Copa del Rey 2026/27. También ranking ATP fechado (ESPN), con identidad exacta de ambos jugadores y categoría ATP identificada. El catálogo de alias usa coincidencias exactas y nombres alternativos de la fuente, sin aproximaciones por subcadenas. Si identidad u horario difieren, no se asigna contexto.

Validación: temporada correcta, fecha anterior al evento y consulta con antigüedad máxima de 36 horas respecto al inicio. Los resultados deben ser finales y haber empezado al menos tres horas antes del corte. En ligas, el total de partidos y balance de cada club debe coincidir con la clasificación. En Euroliga, el calendario completo y los resultados anteriores al corte deben coincidir con el balance de la tabla; si hay partidos adicionales de una jornada incompleta, se conserva la nota básica para los equipos cuyo balance ya no coincide. No se trasladan tablas actuales a partidos ya iniciados. Con menos de cinco partidos de liga por equipo no se aplican ajustes de clasificación/forma.

Señales y límites: zona alta de ambos equipos (puestos 1–5) +1,0; zona alta y al menos una racha de tres victorias +1,3; ambos con tres victorias seguidas +1,0; un equipo entre los tres primeros +0,5; top-3 invicto con al menos 80% de victorias +1,2; cuatro victorias en los últimos cinco +0,6; tres victorias seguidas +0,5. Se usa SOLO la señal mayor, con techo de +1,5; no se suman posición, invicto y forma. Los cinco últimos se ordenan del más reciente al más antiguo y pertenecen a esa competición.

Copa: +0,6 únicamente cuando un partido identificado por nombres, roles, fecha e inicio enfrenta a un local fuera de Primera con un visitante de Primera, con eliminatoria a partido único confirmada para la edición. La pertenencia se verifica con IDs de los clubes y la lista completa de veinte equipos de Primera. No se infiere una categoría concreta del modesto ni se aplica un bonus general de Copa. Otras ediciones, rondas, datos ambiguos y partidos sin contraste no reciben ese extra.

Ausencias y fallos: se conserva la nota básica, sin castigo y con aviso de cobertura agregada. Consultas agrupadas por liga, hasta tres ligas en paralelo y presupuesto de 45 segundos (una petición ya iniciada puede añadir unos segundos). Un fallo del contexto no cambia el envío del resto de la agenda. La NBA en diferido no cambia. Continúan pendientes la forma reciente y resultados detallados de tenis, estilos de juego, vulnerabilidad específica en Copa y nuevas competiciones. La disponibilidad y los solapamientos solo afectan al encaje, no a la nota.

Ranking ATP: publicación no futura y de antigüedad máxima diez días. Contexto deportivo +0,6 si ambos son top-10, +0,4 si uno es top-10 y el otro top-30, o +0,2 si ambos son top-30. No son acumulativos. Joven español de 18–22 años en top-100 ante top-10: +0,6 a AFINIDAD, no al interés deportivo. No se afirma progresión reciente a partir de edad o ranking. Se muestran fecha de publicación y consulta; sin identidad unívoca o ranking vigente se conserva la base. El distintivo Contexto muestra la diferencia efectiva sobre la nota básica tras aplicar límites.

### Entrega 2: calidad conjunta (28/10/2026)
Solo tras validar ambos participantes, se completa el atractivo deportivo que ya aportan catálogo y contexto. Objetivos conjuntos de tenis: 2,8 si ambos son top-10; 2,5 si ambos top-20; 2,2 si uno top-10 y el otro top-30; 1,8 si ambos top-30. Se usa el primer tramo aplicable. En Euroliga: 2,0 si ambos están entre los cinco primeros, o 1,2 si ambos están entre los ocho primeros, con al menos cinco partidos por club.

Complemento = máximo entre cero y objetivo menos cartel menos ajuste contextual. No sustituye ni rebaja el reconocimiento histórico, ni añade por segunda vez señales de ranking, zona alta o forma ya remuneradas. La fase y la afinidad personal siguen separadas. El ranking indica nivel conjunto, nunca probabilidad de victoria o igualdad asegurada. Un jugador destacado frente a un rival fuera de esos tramos no activa este complemento. Sin datos válidos se conserva el modelo anterior. Fútbol y NBA en diferido no cambian en esta entrega.

En el desglose, calidad_cruce es la parte del ajuste contextual total debida a este complemento: no debe sumarse otra vez a contexto. El identificador del modelo incluye este módulo para que las instantáneas detecten cambios de reglas.

### Entrega 3: rivalidades documentadas (28/10/2026)
Registro en data/rivalidades.json: parejas de identidades editoriales por deporte, tipo (derbi local o rivalidad histórica), nombre, fuente y fecha de revisión. Coincidencia exacta y simétrica; no se usan subcadenas, similitud ni proximidad geográfica inferida. La fecha es la revisión del catálogo, no una estadística deportiva de ese día. No se hacen consultas adicionales al generar el correo.

El registro comienza con 21 parejas: 17 de fútbol y cuatro de baloncesto. Las parejas heredadas que no se han documentado quedan pendientes y no reciben bonus. FOOTBALL_DERBIES se conserva solo como referencia de auditoría; ya no decide la nota. Los pesos de las parejas verificadas preexistentes conservan su equivalente anterior (antiguo peso por 0,3), con techo +0,6. Las nuevas: Xerez CD–Cádiz +0,6; Clásico de baloncesto, derbi griego y derbi de Belgrado +0,6; derbi de Tel Aviv +0,4. La afinidad personal permanece aparte y no se incrementa aquí.

La rivalidad suma una sola vez al interés deportivo, fuera de cartel y contexto, con sus límites finales habituales. Ser Copa no repite el bonus. El desglose rivalidad indica el bonus solicitado, que puede quedar limitado por el techo deportivo. Se muestran etiqueta, fuente y fecha en HTML y texto; las instantáneas conservan la evaluación y versionan el módulo y el registro.

Xerez CD y Xerez Deportivo son identidades distintas. La abreviatura Xerez solo se resuelve como Xerez CD en el cruce de Copa del Rey frente a Cádiz del 28/10/2026 a las 21:00, respaldado por la ficha federativa contrastada. Para futuras fechas hace falta nombre inequívoco o una nueva resolución documentada. Filiales, categorías juveniles y otros deportes no heredan el bonus por contener el nombre de un primer equipo. No se añaden competiciones ni se modifica la NBA en diferido.
