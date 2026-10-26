import unittest
from resumen.planning import crear_planning


def evento(nombre, hora, nota=5):
    return dict(local=nombre, visitante='Rival', hora=hora, score=nota,
                deporte='Fútbol', competicion='Liga')


class PlanningTest(unittest.TestCase):
    def planning(self, eventos, seleccion):
        return crear_planning(eventos, seleccion, lambda e: e['local'])

    def test_aperitivo_cambio_y_fondo(self):
        principal = evento('Principal', '20:30', 8)
        aperitivo = evento('Aperitivo', '19:45')
        fondo = evento('Fondo', '15:00')
        bloques = self.planning([principal, aperitivo, fondo], [principal])
        self.assertEqual([b['tipo'] for b in bloques], ['De fondo · opcional', 'Aperitivo opcional', 'Cita principal'])
        self.assertEqual(bloques[1]['hasta'], '20:30')
        self.assertIn('no verías', bloques[1]['detalle'])

    def test_no_aperitivo_menor_de_media_hora(self):
        p = evento('Principal', '20:30', 8)
        e = evento('Corto', '20:15')
        self.assertEqual(len(self.planning([p, e], [p])), 1)

    def test_no_rellena_noche_ni_baja_calidad(self):
        eventos = [evento('Tarde', '23:00'), evento('Flojo', '12:00', 3)]
        self.assertEqual(self.planning(eventos, []), [])

    def test_dia_tranquilo_solo_una_opcion_voluntaria(self):
        bloques = self.planning([evento('Uno', '12:00'), evento('Dos', '16:00')], [])
        self.assertEqual(len(bloques), 1)
        self.assertIn('opcional', bloques[0]['tipo'])

    def test_no_solapes_y_cambio_entre_principales(self):
        p = evento('Primero', '19:00', 7)
        q = evento('Segundo', '20:45', 8)
        bloques = self.planning([p, q], [p, q])
        self.assertEqual(bloques[0]['hasta'], bloques[1]['desde'])
        self.assertIn('final sin ver', bloques[0]['detalle'])

    def test_no_duplicados_ni_alteracion_de_notas(self):
        p = evento('Principal', '20:30', 8)
        e = evento('Secundario', '19:00')
        bloques = self.planning([p, e], [p])
        self.assertEqual(len({b['evento'] for b in bloques}), len(bloques))
        self.assertEqual(e['score'], 5)
