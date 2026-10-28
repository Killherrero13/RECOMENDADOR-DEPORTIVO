# Cierre de calibración · 28/10/2026

Se comparó el modelo anterior a estas entregas (db7bb90) con las reglas publicadas en a0d7022 sobre las jornadas guardadas del 27 y 28 de octubre: 32 y 55 eventos. Cada ejecución usa los mismos datos y el mismo corte en ambas versiones. Ambos modelos incluyen las copas autorizadas. Esta comparación aísla reglas, no reproduce literalmente los correos previos ni mide otra vez la recuperación de identidades y fuentes.

| Jornada | Eventos | Notas que cambian | Mejor evento | Cambio de citas seleccionadas |
| --- | ---: | ---: | --- | --- |
| 27/10 | 32 | 1 | Valencia–Fenerbahçe, se mantiene | Ninguno |
| 28/10 | 55 | 7 | Liverpool–Chelsea, se mantiene | Entra Musetti–Tiafoe |

Paul–Rublev sube 6,4→6,5; Musetti–Tiafoe 6,3→6,6; Tien–De Miñaur 5,3→6,9. Los cuatro cruces coperos con datos nuevos o regla específica y Xerez–Cádiz completan los ocho cambios. Tien no entra en las citas seleccionadas porque coincide con una cita de mayor prioridad. Se mantienen las bases, los límites y la separación de nota, afinidad y encaje.

Controles: Fritz–Hijikata conserva 4,9; Parma–Udinese 5,5; Calamocha–Europa 4,7. La mayor parte de la jornada permanece estable (79/87). El ranking de visionado se ordena por prioridad, luego nota y hora; avanzar entre empates no implica una mejora de calidad.

## Regresión reproducible

Las entradas están en tests/fixtures/calibracion_2026-10-27.json y calibracion_2026-10-28.json. Contienen agenda pública, contexto fechado y corte; no contienen credenciales, correo personal ni resultados NBA. No se descargan fuentes ni se envía correo al reproducirlas.

Ejecutar desde el repositorio:

```powershell
python -m unittest discover -s tests -q
```

La batería cubre admisión de los 87 eventos, controles de notas, límites y solapamiento de las citas, alternativas cronológicas, bloques de planning sin solapamientos, independencia de la nota respecto a canales/horarios, datos anteriores al corte, rechazo de consultas posteriores al evento y reproducción de las decisiones desde instantáneas. Las pruebas específicas de NBA y camisetas se mantienen en sus módulos.

## Alcance y observación

Dos jornadas permiten detectar regresiones concretas, no demostrar una calibración universal. El 27 contiene un evento ya empezado que sigue disponible en parte: se conserva por la regla de visionado en curso y no se le aplica contexto posterior. Los datos ausentes siguen siendo ausentes; no se sustituyen por narrativas.

Quedan como ampliaciones futuras: documentar las rivalidades pendientes; cubrir formato y categorías de otras copas; mejorar la admisión de tenistas sin perfil editorial antes de consultar rankings; y añadir estilos o lesiones con fuentes y caducidad. No forman parte del cierre de estos ajustes.

Durante los próximos 3–5 días conviene reunir feedback de los correos reales con evento, nota recibida, nota deseada y razón concreta. Priorizar errores repetidos de reconocimiento, datos o selección sobre discrepancias aisladas de unas décimas. No se ha creado ninguna automatización de seguimiento ni activado un envío de prueba.

Para volver al estado anterior de una entrega, revertir su commit en Git y ejecutar las comprobaciones antes de publicar. Los commits de las cuatro entregas son ef067f7 (datos e identidad), 1c67323 (calidad conjunta), d2030fc (rivalidades) y a0d7022 (Copa). Las instantáneas guardan el identificador del modelo para impedir una reproducción silenciosa con otras reglas.
