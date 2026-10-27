import unittest
from resumen.colores import tema_evento
from resumen.diseno_correo import tarjeta_evento
from resumen.eventos import recomendar_eventos
from resumen.horarios import orden_inicio


def evento(local='Equipo A', visitante='Equipo B', comp='LaLiga', deporte='Fútbol', hora='18:00'):
    return dict(local=local,visitante=visitante,competicion=comp,deporte=deporte,hora=hora,score=7,canales=[])


class ColoresTests(unittest.TestCase):
    def test_equipos_prevalecen_y_sin_falsos_positivos(self):
        self.assertEqual(tema_evento(evento('At. Madrid',comp='Champions League'))[1],'#b51c2b')
        self.assertEqual(tema_evento(evento('España',comp='Eurocopa'))[1],'#b51c2b')
        self.assertEqual(tema_evento(evento('Aston Villa',comp='Europa League'))[1],'#760d35')
        self.assertNotEqual(tema_evento(evento('CD Atlético Paso'))[1],'#b51c2b')
        self.assertEqual(tema_evento(evento('Boston Celtics',comp='NBA',deporte='Baloncesto'))[1],'#007a33')

    def test_competiciones_y_tenis_distintos(self):
        casos=[('Champions League','Fútbol'),('Europa League','Fútbol'),('Conference League','Fútbol'),
               ('LaLiga','Fútbol'),('NBA','Baloncesto'),('Liga Endesa','Baloncesto'),('Euroliga','Baloncesto'),('ATP 500','Tenis')]
        self.assertEqual(len({tema_evento(evento(comp=c,deporte=d))[0] for c,d in casos}),len(casos))

    def test_dorado_conserva_color_de_equipo(self):
        html=tarjeta_evento(evento('Aston Villa',comp='Champions League'),destacado=True)
        self.assertIn('3px solid #c89b36',html)
        self.assertIn('background:#f4e3ea',html)

    def test_alternativas_cronologicas(self):
        eventos=[evento(comp='Champions League Final',hora=h) for h in ['20:00','19:30','19:00','18:30','18:00']]
        for e in eventos: e.pop('score')
        r=recomendar_eventos(eventos)
        self.assertTrue(r['alternativas'])
        self.assertEqual([orden_inicio(e) for e in r['alternativas']],sorted(orden_inicio(e) for e in r['alternativas']))
