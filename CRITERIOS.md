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
