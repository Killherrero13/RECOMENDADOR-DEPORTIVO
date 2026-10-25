# Preferencias acordadas

Confirmadas por el usuario el 25/10/2026. Este documento distingue lo acordado de lo ya implementado.

## Camisetas — pendiente de la siguiente tanda

Mostrar una camiseta vinculada a un evento del equipo cuando exista una candidata en la colección,
y una alternativa al azar. Si no hay candidata vinculada, mostrar solo la alternativa al azar.
Se adopta la opción de mostrar ambas cuando sea posible, de entre las opciones indicadas por el usuario.
No hay restricción de repeticiones ni historial solicitado en esta primera mejora.

## Horario y agenda — pendiente

- Entre semana: desde las 06:30 hasta las 00:00.
- Fines de semana: mismo horario, con margen para eventos nocturnos hasta la 01:00;
  la madrugada no es la opción preferida. NBA es un ejemplo de excepción interesante.
- Hay que representar fechas y final estimado, no solo la hora de inicio, antes de implementar
  la ventana que cruza medianoche. Un partido de las 00:30 pertenece a una fecha concreta.
- La programación de envío se mantiene a las 08:30 Europe/Madrid; la vista de eventos pasados
  debe tenerse en cuenta al aplicar la nueva disponibilidad.

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

Pendiente después: selección de agenda por interés, duraciones por deporte, preferencias
anteriores, explicación breve de las recomendaciones y evaluación de retirar football-data.
