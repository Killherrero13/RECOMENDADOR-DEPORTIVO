import unittest
from datetime import date, datetime
from resumen.config import MADRID_TZ
from resumen.eventos import recomendar_eventos, evaluar_evento
from resumen.colores import tema_evento


def evento(comp, hora='18:00'):
    return dict(local='Equipo A',visitante='Equipo B',deporte='Fútbol',competicion=comp,
                hora=hora,fecha='2026-10-28',canales=['Canal no incluido'])


class CopasAutorizadasTests(unittest.TestCase):
    def test_tres_copas_y_sus_nombres_alternativos(self):
        for comp in ['Copa de Alemania 2ª Ronda','DFB-Pokal 2ª Ronda','DFB Pokal',
                     'EFL Carabao Cup Octavos de final','Carabao Cup','EFL Cup',
                     'Copa Libertadores Semifinales','CONMEBOL Libertadores']:
            with self.subTest(comp=comp):
                r=recomendar_eventos([evento(comp)],fecha=date(2026,10,28))
                self.assertEqual(len(r['filtrados']),1)

    def test_bases_con_nivel_nacional_y_continental(self):
        for comp in ['Copa de Alemania','DFB-Pokal','EFL Carabao Cup']:
            r=evaluar_evento(evento(comp))
            self.assertEqual(r['desglose']['base'],4.5)
            self.assertEqual(tema_evento(evento(comp))[2],'Copa')
        self.assertEqual(evaluar_evento(evento('Copa Libertadores'))['desglose']['base'],5.6)
        self.assertEqual(tema_evento(evento('CONMEBOL Libertadores'))[2],'Copa Libertadores')
        self.assertEqual(tema_evento(evento('Copa Libertadores'))[2],'Copa Libertadores')
        self.assertGreater(evaluar_evento(evento('Copa Libertadores Final'))['score'],
                           evaluar_evento(evento('Copa Libertadores'))['score'])

    def test_otras_copas_no_se_han_incorporado(self):
        for comp in ['Copa Sudamericana','Copa de Portugal','Taça de Portugal','KNVB Beker','Scottish League Cup']:
            self.assertEqual(recomendar_eventos([evento(comp)],fecha=date(2026,10,28))['filtrados'],[])

    def test_se_conservan_los_filtros_y_la_disponibilidad(self):
        for comp in ['Copa Libertadores Femenina','Copa Libertadores Sub-20']:
            self.assertEqual(recomendar_eventos([evento(comp)],fecha=date(2026,10,28))['filtrados'],[])
        r=recomendar_eventos([evento('Copa Libertadores','02:00')],
                            ahora=datetime(2026,10,28,5,tzinfo=MADRID_TZ))
        self.assertEqual(r['filtrados'],[])
        e=evento('Copa Libertadores','23:00')
        r=recomendar_eventos([e],ahora=datetime(2026,10,28,5,tzinfo=MADRID_TZ))
        self.assertTrue(r['filtrados'][0]['vision_parcial'])
