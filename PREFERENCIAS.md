# Preferencias acordadas

Confirmadas por el usuario el 25/10/2026. Este documento distingue lo acordado de lo ya implementado.

## Camisetas — implementado en la tanda 3

Mostrar una camiseta vinculada a un evento del equipo cuando exista una candidata en la colección,
y una alternativa al azar. Si no hay candidata vinculada, mostrar solo la alternativa al azar.
Se adopta la opción de mostrar ambas cuando sea posible, de entre las opciones indicadas por el usuario.
No hay restricción de repeticiones ni historial solicitado en esta primera mejora.

- Se cruzan los partidos de hoy de football-data con los eventos de fútbol disponibles en la agenda,
  aunque no superen el umbral del plan deportivo. En modo `camiseta` solo se consulta football-data.
- Se priorizan camisetas de Atlético y Aston Villa si juegan; entre las candidatas se elige por
  puntuación del evento y después por hora. Con varias camisetas del equipo, el modelo se elige al azar.
- La alternativa se elige de otro equipo cuando hay prendas disponibles; si solo hay un equipo,
  puede ser otro modelo. Si solo hay una prenda, no se duplica.
- Solo se usan partidos de la fecha de Madrid de hoy, no los de mañana. Se mantiene el corte
  de dos horas desde el inicio y se descartan cancelados, aplazados o suspendidos cuando la API lo informa.
- Una caída de la API no impide aprovechar la agenda o mostrar una camiseta al azar. Se mantiene
  el aviso del fallo y el estado de error de la ejecución.
- Los alias específicos de la colección están en `data/alias_camisetas.json`; no se hacen
  coincidencias aproximadas por subcadenas. Nombres ambiguos como «Casablanca» u «Orlando» no se
  relacionan automáticamente con un club de nombre más largo; sus camisetas siguen entrando en el azar.
- No se ha eliminado la API ni su secreto: aún complementa la cobertura de la agenda y permite el modo camiseta.

## Horario y agenda — implementado en la tanda 2

- Entre semana: desde las 06:30 hasta las 00:00.
- La ampliación nocturna se interpreta como las noches de viernes y sábado, hasta las 01:00
  del sábado/domingo. La noche del domingo acaba a las 00:00 del lunes.
- Cada evento lleva fecha y final estimado. La tabla del día siguiente se consulta en el mismo
  HTML cuando la jornada permite esa ampliación; si no está disponible, se avisa en el resumen.
- Se exige un mínimo de 30 minutos disponibles. Si no cabe el evento completo, se marca
  «Visionado parcial: hasta…»; nunca se presenta como si pudieras verlo entero.
- La madrugada resta 1 punto y el visionado parcial 0,5: pueden recomendarse, pero son secundarios
  frente a una opción de interés similar que sí puedas ver completa durante el día.
- La selección recorre candidatos por puntuación tras fijar el imprescindible. Mantiene el máximo
  de cuatro eventos y hasta 30 minutos de solapamiento. No promete el óptimo global de puntuación.
- Duraciones estimadas: fútbol 120 min, baloncesto 120 min, NBA 150 min, tenis 150 min,
  automovilismo 180 min, balonmano 90 min y otros 120 min.
- La programación de envío se mantiene a las 08:30 Europe/Madrid; la vista de eventos pasados
  se tiene en cuenta. Se excluyen los terminados; los que aún dejan 30 minutos se indican «En curso».

## Intereses — pendientes de ajuste específico

- Equipos favoritos: Atlético de Madrid, Aston Villa y Boston Celtics.
- Orden habitual de deportes: fútbol, baloncesto, tenis y después el resto.
- La relevancia del evento puede superar ese orden: una final importante de baloncesto
  puede estar por encima de un partido ordinario de fútbol.
- Eliminar el bonus duplicado de Estudiantes no equivale a eliminarlo como equipo de interés:
  de momento conserva un único bonus original de cuatro puntos.

## Televisión — destacado visual implementado; ajuste de puntuación pendiente

- DAZN prácticamente completo y canal Movistar Plus+, según el acceso declarado por el usuario.
- DAZN se destaca con una etiqueta amarilla y Movistar Plus+ con una azul, ambas con ✓.
- M+ LALIGA, Liga de Campeones, Vamos o Deportes no se marcan automáticamente como incluidos.
- No excluir automáticamente eventos por el canal: puede disponer de otras formas de verlos.
- El destacado sigue la declaración del usuario; no verifica derechos contra el proveedor.
- Mostrar el canal concreto y distinguir accesibilidad conocida de la que debe comprobarse.

## Tanda 1 implementada

- Fases de eliminatorias específicas y detección de ida/vuelta como palabras completas.
- Un único bonus de Estudiantes.
- Alias y acentos de equipos reconocidos de forma consistente para afinidad, derbis y calidad.
- Calidad calculada por los dos participantes, sin duplicar Inter Milan por dos etiquetas.
- Eurocopa, Copa América y Mundial no se eliminan por falta de su nombre en la lista permitida.
- Eredivisie bien escrita; Serie A Brasil y Hypermotion se valoran en su categoría específica.
- Todos los eventos seleccionados se conservan en el plan aunque compartan franja.
- Las ocho alternativas se eligen por puntuación, con hora como desempate.

La tanda 2 añade selección de agenda por interés, duraciones por deporte y disponibilidad con fechas.
La tanda 3 añade las dos opciones de camiseta y el partido asociado.
Pendiente después: ajuste de favoritos/deportes/puntuación de canales y explicación breve de las
recomendaciones. Se mantiene football-data por decisión expresa del usuario: complementa la agenda
para vincular las camisetas a los partidos del día. No se plantea retirar la API ni su secreto.
