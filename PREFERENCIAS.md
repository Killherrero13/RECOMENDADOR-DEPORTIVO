# Preferencias acordadas

Confirmadas por el usuario el 25/10/2026. Este documento distingue lo acordado de lo ya implementado.

## Camisetas — pendiente de la siguiente tanda

Mostrar una camiseta vinculada a un evento del equipo cuando exista una candidata en la colección,
y una alternativa al azar. Si no hay candidata vinculada, mostrar solo la alternativa al azar.
Se adopta la opción de mostrar ambas cuando sea posible, de entre las opciones indicadas por el usuario.
No hay restricción de repeticiones ni historial solicitado en esta primera mejora.

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

## Televisión — pendiente

- DAZN y Movistar Plus+ Lite, según lo indicado por el usuario.
- No excluir automáticamente eventos por el canal: puede disponer de otras formas de verlos.
- No asumir que todo canal de Movistar ni todo contenido de DAZN está incluido en su suscripción.
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
Pendiente después: camisetas, ajuste de favoritos/deportes/canales, explicación breve de las
recomendaciones y evaluación de retirar football-data.
