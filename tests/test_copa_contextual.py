import copy
import unittest
from datetime import datetime
from unittest.mock import patch

from resumen.config import MADRID_TZ
from resumen.contexto import valorar_contexto
from resumen.contexto_fuentes import completar_contextos_copa, ErrorContexto
from resumen.eventos import evaluar_evento


def copa():
    e=dict(local='Alcoyano',visitante='Mallorca',deporte='Fútbol',competicion='Copa del Rey 1ª Ronda',
           fecha='2026-10-28',hora='20:00',canales=[])
    e['contexto']=dict(tipo='copa',competicion='esp.copa_del_rey',temporada=2026,
        consultado='2026-10-28T08:00:00+01:00',
        local=dict(nombre='Alcoyano',id='6827',categoria='Fuera de Primera y Segunda'),
        visitante=dict(nombre='Mallorca',id='84',categoria='Segunda'),
        copa=dict(partido_unico=True,contraste_primera=False,contraste_segunda=True,
                  fuentes=['https://example.org/copa']))
    return e


class CopaContextualTests(unittest.TestCase):
    def test_segunda_menor_que_primera_sin_bonus_general(self):
        e=copa()
        self.assertEqual(valorar_contexto(e)['ajuste'],.3)
        e['contexto']['copa']['contraste_primera']=True
        self.assertEqual(valorar_contexto(e)['ajuste'],.6)
        e['contexto']['copa'].update(contraste_primera=False,contraste_segunda=False)
        self.assertEqual(valorar_contexto(e)['ajuste'],0)

    def test_segunda_exige_categorias_explicitas(self):
        e=copa();del e['contexto']['local']['categoria']
        self.assertEqual(valorar_contexto(e)['ajuste'],0)

    def test_racha_validada_limitada_y_no_racha_inventada(self):
        e=copa();c=e['contexto']['copa']
        c['forma_visitante']=dict(nombre='Mallorca',id='84',jugados=8,forma='LLWLD',
                                ultimo_partido='2026-10-25T20:00:00Z',fuentes=['https://example.org/hist'])
        self.assertEqual(valorar_contexto(e)['ajuste'],.6)
        for campo, valor in [('id','otro'),('jugados',4),('forma','LLL'),('ultimo_partido',None),('ultimo_partido','2026-10-28T10:00:00Z')]:
            otro=copy.deepcopy(e);otro['contexto']['copa']['forma_visitante'][campo]=valor
            self.assertEqual(valorar_contexto(otro)['ajuste'],.3)
        c['contraste_segunda']=False
        self.assertEqual(valorar_contexto(e)['ajuste'],0)

    @patch('resumen.contexto_fuentes.tabla_futbol',side_effect=ErrorContexto('caída'))
    @patch('resumen.contexto_fuentes.descargar_json',side_effect=ErrorContexto('caída'))
    def test_fuente_opcional_caida_conserva_primera(self,descarga,tabla):
        e=copa();e['contexto']['copa']['contraste_primera']=True
        completar_contextos_copa([e],datetime(2026,10,28,8,tzinfo=MADRID_TZ),{'84'},'https://example.org/primera')
        self.assertEqual(valorar_contexto(e)['ajuste'],.6)
        self.assertEqual(e['contexto']['copa']['estado_categorias'],'Segunda sin validar')

    @patch('resumen.contexto_fuentes.tabla_futbol',return_value={})
    @patch('resumen.contexto_fuentes.descargar_json')
    def test_clasificacion_segunda_completa_y_temporada_correcta(self,descarga,tabla):
        entries=[{'team':{'id':str(i)}} for i in range(63,85)]
        datos=dict(season={'year':2026},children=[{'standings':{'entries':entries}}])
        descarga.return_value=datos
        e=copa();completar_contextos_copa([e],datetime(2026,10,28,8,tzinfo=MADRID_TZ),{'1'},'url')
        self.assertEqual(valorar_contexto(e)['ajuste'],.3)
        datos['season']['year']=2025
        e=copa();completar_contextos_copa([e],datetime(2026,10,28,8,tzinfo=MADRID_TZ),{'1'},'url')
        self.assertEqual(valorar_contexto(e)['ajuste'],0)

    def test_rivalidad_no_se_repite_en_narrativa_copera(self):
        e=copa();e.update(local='Xerez CD',visitante='Cádiz CF')
        e['contexto']['local']['nombre']='Xerez CD';e['contexto']['visitante']['nombre']='Cádiz CF'
        r=evaluar_evento(e)
        self.assertEqual(r['desglose']['rivalidad'],.6)
        self.assertEqual(r['evaluacion_contexto']['ajuste'],.3)
        self.assertEqual(r['score'],5.6)

    def test_tope_copero_y_sin_castigo_por_historial_ausente(self):
        e=copa();c=e['contexto']['copa'];c['contraste_primera']=True
        base=valorar_contexto(e)['ajuste']
        c['forma_visitante']=dict(nombre='Mallorca',id='84',jugados=10,forma='LLLLL',
                                ultimo_partido='2026-10-25T20:00:00Z',fuentes=['https://example.org/hist'])
        self.assertAlmostEqual(valorar_contexto(e)['ajuste'],.9)
        c['forma_visitante']['forma']='WWWWW'
        self.assertEqual(valorar_contexto(e)['ajuste'],base)

    def test_categorias_no_cambian_nota_por_acceso_o_vision_parcial(self):
        e=copa()
        self.assertEqual(evaluar_evento(e)['score'],evaluar_evento({**e,'canales':['DAZN'],'vision_parcial':True})['score'])
