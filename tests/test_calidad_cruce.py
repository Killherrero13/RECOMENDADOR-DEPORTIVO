import copy
import unittest

from resumen.eventos import evaluar_evento


def tenis(rangos=(18, 10)):
    e = dict(local='L. Tien', visitante='A. De Miñaur', deporte='Tenis',
             competicion='ATP Viena', descripcion='ATP 500 Primera ronda',
             fecha='2026-10-28', hora='17:00', canales=[])
    e['contexto'] = dict(tipo='tenis', competicion='atp', temporada=2026,
                         consultado='2026-10-28T08:00:00+01:00',
                         publicado='2026-10-26T08:00:00+01:00', fuentes=['https://example.org/atp'],
                         local=dict(nombre=e['local'], ranking=rangos[0]),
                         visitante=dict(nombre=e['visitante'], ranking=rangos[1]))
    return e


class CalidadCruceTests(unittest.TestCase):
    def test_jugador_sin_catalogo_cuenta_por_ranking_validado(self):
        e = tenis()
        r = evaluar_evento(e)
        self.assertGreater(r['desglose']['calidad_cruce'], 0)
        self.assertAlmostEqual(r['desglose']['cartel'] + r['evaluacion_contexto']['ajuste']
                               + r['desglose']['calidad_cruce'], 2.5)

    def test_cruce_simetrico(self):
        e = tenis(); inverso = copy.deepcopy(e)
        for a, b in (('local', 'visitante'),):
            inverso[a], inverso[b] = e[b], e[a]
            inverso['contexto'][a], inverso['contexto'][b] = e['contexto'][b], e['contexto'][a]
        self.assertEqual(evaluar_evento(e)['score'], evaluar_evento(inverso)['score'])

    def test_estrella_no_compensa_rival_de_ranking_bajo(self):
        self.assertEqual(evaluar_evento(tenis((150, 2)))['desglose']['calidad_cruce'], 0)

    def test_contexto_invalido_no_habilita_bonus(self):
        for campo, valor in [('temporada', 2025), ('publicado', '2026-10-29T08:00:00+01:00')]:
            e = tenis(); e['contexto'][campo] = valor
            self.assertEqual(evaluar_evento(e)['desglose']['calidad_cruce'], 0)
        e = tenis(); del e['contexto']
        self.assertEqual(evaluar_evento(e)['desglose']['calidad_cruce'], 0)

    def test_no_depende_del_acceso_ni_del_horario(self):
        e = tenis(); otro = {**e, 'canales': ['DAZN'], 'vision_parcial': True}
        self.assertEqual(evaluar_evento(e)['score'], evaluar_evento(otro)['score'])
        self.assertNotEqual(evaluar_evento(e)['prioridad'], evaluar_evento(otro)['prioridad'])

    def test_catalogo_fuerte_no_se_duplica(self):
        e = tenis((2, 3))
        e.update(local='C. Alcaraz', visitante='J. Sinner')
        for k in ('local', 'visitante'): e['contexto'][k]['nombre'] = e[k]
        self.assertEqual(evaluar_evento(e)['desglose']['calidad_cruce'], 0)

    def test_euroliga_completa_sin_sumar_zona_alta_dos_veces(self):
        from resumen.calidad_cruce import valorar_cruce
        e = {'deporte': 'Baloncesto', 'contexto': {'competicion': 'euro',
             'local': {'posicion': 3}, 'visitante': {'posicion': 5}}}
        c = {'estado': 'validado', 'ajuste': 1.3}
        self.assertEqual(valorar_cruce(e, c, 1.5)['ajuste'], 0)
        self.assertEqual(valorar_cruce(e, c, 0)['ajuste'], .7)
