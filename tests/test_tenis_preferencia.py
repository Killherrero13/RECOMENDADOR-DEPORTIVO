import unittest
from datetime import date

from resumen.eventos import knockout_bonus, evaluar_evento, build_daily_plan
from resumen.puntuacion import umbral_plan


def tenis(comp='Torneo de Viena 1/4 de Final'):
    return dict(local='A. Mannarino',visitante='D. Medvedev',competicion=comp,deporte='Tenis',
                fecha='2026-10-30',hora='13:30',canales=[])


class TenisPreferenciaTests(unittest.TestCase):
    def test_fracciones_se_entienden_antes_de_final(self):
        for fase,valor in [('1/4 de Final',1.5),('1 / 4 de final',1.5),('QF',1.5),
                           ('1/2 de Final',2),('1/8 de Final',1),('1/16 de Final',.8),('Final',2.5)]:
            self.assertEqual(knockout_bonus(tenis('Torneo de Viena '+fase)),valor)

    def test_cuartos_no_se_etiquetan_ni_valoran_como_final(self):
        from resumen.eventos import recomendar_eventos
        r=recomendar_eventos([tenis()],fecha=date(2026,10,30))['filtrados'][0]
        self.assertEqual(r['desglose']['fase'],1)
        self.assertIn('Cuartos de final',r['motivos'])
        self.assertNotIn('Final',r['motivos'])

    def test_preferencia_personal_se_muestra_separada_del_deportivo(self):
        r=evaluar_evento(tenis())
        self.assertEqual(r['desglose']['preferencia_deporte'],-.4)
        self.assertAlmostEqual(r['score'],round(r['desglose']['deportivo']+r['desglose']['afinidad'],1))

    def test_solo_grandes_citas_tenis_entran_al_plan(self):
        normal={**tenis(), 'score':7.4,'prioridad':7.6}
        self.assertEqual(build_daily_plan([normal]),({},[]))
        grande={**normal,'score':7.5,'prioridad':7.5}
        self.assertTrue(build_daily_plan([grande])[1])
        self.assertEqual(umbral_plan({'deporte':'Fútbol'}),6.5)
        self.assertEqual(umbral_plan({'deporte':'Baloncesto'}),6.5)
