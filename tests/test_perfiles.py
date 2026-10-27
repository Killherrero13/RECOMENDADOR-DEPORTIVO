import unittest
from datetime import date
from resumen.eventos import evaluar_evento, recomendar_eventos
from resumen.perfiles import identidad_basket, perfil_tenis


def evento(local, visitante, comp='Torneo de Viena 1ª Ronda', deporte='Tenis'):
    return dict(local=local,visitante=visitante,competicion=comp,deporte=deporte,
                hora='15:00',fecha='2026-10-27',canales=[])


class PerfilesTests(unittest.TestCase):
    def test_alias_basket_no_afecta_al_marcador(self):
        a=evento('FC Bayern Basketball','Barça Basket','Euroliga Liga Regular','Baloncesto')
        b=evento('Bayern','FC Barcelona','Euroleague Liga Regular','Baloncesto')
        self.assertEqual(evaluar_evento(a)['score'],evaluar_evento(b)['score'])
        self.assertEqual(identidad_basket('AX Olimpia Milano'),'milano')
        self.assertEqual(identidad_basket('Armani Olimpia Milan'),'milano')
        self.assertEqual(identidad_basket('Fenerbahçe Istanbul'),'fenerbahce')
        self.assertEqual(identidad_basket('Panathinaikos BC'),'panathinaikos')

    def test_referentes_europeos_no_se_trasladan_a_acb(self):
        euro=evento('Panathinaikos BC','AX Olimpia Milano','Euroliga','Baloncesto')
        acb={**euro,'competicion':'Liga Endesa'}
        self.assertGreater(evaluar_evento(euro)['desglose']['cartel'],evaluar_evento(acb)['desglose']['cartel'])
        control=evento('Dubai Basketball','Paris Basketball','Euroliga','Baloncesto')
        self.assertEqual(evaluar_evento(control)['score'],5.1)

    def test_calidad_de_ambos_y_figura_no_equivalen_a_cualquiera(self):
        fuerte=evento('K. Khachanov','C. Alcaraz')
        sin_perfil=evento('Jugador sin perfil','C. Alcaraz')
        dos=evento('T. Paul','A. Rublev')
        uno=evento('Jugador sin perfil','A. Rublev')
        self.assertGreater(evaluar_evento(fuerte)['score'],evaluar_evento(sin_perfil)['score'])
        self.assertGreater(evaluar_evento(dos)['score'],evaluar_evento(uno)['score'])
        self.assertEqual(evaluar_evento(evento('H. Hurkacz','Z. Bergs'))['score'],4.9)
        self.assertIsNone(perfil_tenis('Jugador Paulson'))
        self.assertIsNone(perfil_tenis('M. Landaluce'))

    def test_orden_jugadores_no_cambia_afinidad(self):
        e=evento('A. Rublev','D. Medvedev')
        inverso={**e,'local':e['visitante'],'visitante':e['local']}
        self.assertEqual(evaluar_evento(e),evaluar_evento(inverso))

    def test_referentes_nuevos_pasan_el_filtro_sin_llamarse_top20(self):
        e=evento('Tommy Paul','Karen Khachanov')
        r=recomendar_eventos([e],fecha=date(2026,10,27))
        self.assertEqual(len(r['filtrados']),1)
        self.assertFalse(any('top' in m.casefold() for m in r['filtrados'][0]['motivos']))

    def test_sin_perfiles_primera_ronda_no_se_infla(self):
        e=evento('Jugador A','Jugador B')
        self.assertEqual(recomendar_eventos([e],fecha=date(2026,10,27))['filtrados'],[])
