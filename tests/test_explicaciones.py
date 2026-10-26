import unittest
from resumen.explicaciones import explicar_agenda
from resumen.diseno_correo import explicacion_html


def evento(nombre, hora, score=7):
    return dict(local=nombre, visitante='Rival', hora=hora, score=score,
                deporte='Fútbol', competicion='Liga', canales=['DAZN'],
                motivos=['Liga principal', 'Juega uno de tus favoritos'])


class ExplicacionesTest(unittest.TestCase):
    def test_motivos_personales_y_acceso_sin_cambiar_nota(self):
        e = evento('Equipo', '19:00')
        explicar_agenda([e], {'imprescindible': e}, lambda x: x['local'])
        self.assertEqual(e['score'], 7)
        self.assertEqual(e['explicacion']['motivos'][0], 'Juega uno de tus favoritos')
        self.assertIn('DAZN', str(e['explicacion']))
        self.assertIn('Elegido', e['explicacion']['papel'])

    def test_solapamiento_real_y_opcion_sin_solapamiento(self):
        elegido = evento('Principal', '20:30', 8)
        coincide = evento('Alternativa', '21:00')
        libre = evento('Libre', '12:00')
        explicar_agenda([coincide, libre], {'imprescindible': elegido}, lambda x: x['local'])
        self.assertIn('Principal', coincide['explicacion']['papel'])
        self.assertIn('Coincide', coincide['explicacion']['papel'])
        self.assertNotIn('Coincide', libre['explicacion']['papel'])
        self.assertIn('plazas limitadas', libre['explicacion']['papel'])

    def test_umbral_no_se_confunde_con_solapamiento(self):
        e = evento('Secundario', '12:00', 5)
        explicar_agenda([e], {}, lambda x: x['local'])
        self.assertIn('umbral', e['explicacion']['papel'])
        self.assertNotIn('Coincide', e['explicacion']['papel'])

    def test_escape_html_y_sin_datos_inventados(self):
        e = evento('Equipo', '12:00')
        e['motivos'] = ['<script>']
        explicar_agenda([e], {}, lambda x: x['local'])
        html = explicacion_html(e)
        self.assertIn('&lt;script&gt;', html)
        self.assertNotIn('<script>', html)
        self.assertNotIn('líder', html)
