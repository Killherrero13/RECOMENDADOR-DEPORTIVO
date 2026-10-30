import copy
import json
import unittest
from datetime import datetime
from unittest.mock import patch
from resumen.config import MADRID_TZ, ROOT
from resumen.contexto import valorar_contexto
from resumen.contexto_fuentes import enriquecer_eventos
from resumen.eventos import evaluar_evento
from resumen.rivalidades import valorar_rivalidad
from resumen.preferencias_eventos import NBA_TEAM_AFFINITY


def nba():
    return dict(deporte='Baloncesto', local='Philadelphia 76ers', visitante='New York Knicks',
                competicion='NBA Liga Regular', fecha='2026-10-31', hora='00:30', canales=[])


def ficha(nota='NBA Cup - Group Play', estado='pre'):
    return {'id':'401909280', 'date':'2026-10-30T23:30Z', 'competitions':[
        {'date':'2026-10-30T23:30Z', 'status':{'type':{'state':estado}},
         'notes':[{'headline':nota}], 'competitors':[
             {'homeAway':'home','team':{'id':'20','displayName':'Philadelphia 76ers'}, 'score':'999'},
             {'homeAway':'away','team':{'id':'18','displayName':'New York Knicks'}, 'score':'888'}]}]}


class Feedback30Tests(unittest.TestCase):
    def consultar(self, e=None, f=None):
        e = e or nba()
        with patch('resumen.contexto_fuentes.descargar_json', return_value={'events':[f or ficha()]}):
            enriquecer_eventos([e], datetime(2026,10,30,12,tzinfo=MADRID_TZ))
        return e

    def test_copa_identificada_por_partido_y_fecha_utc_sin_marcadores(self):
        e=self.consultar()
        self.assertEqual(e['contexto']['fase'],'grupos')
        self.assertEqual(valorar_contexto(e)['ajuste'],.3)
        self.assertNotIn('999',json.dumps(e))
        self.assertNotIn('"score":',json.dumps(e['contexto']))
        self.assertEqual(evaluar_evento(e)['score'],5.4)

    def test_fecha_y_estado_no_son_suficientes(self):
        e=self.consultar(f=ficha('Regular Season'))
        self.assertEqual(valorar_contexto(e)['ajuste'],0)
        for f in [ficha(estado='post'),{**ficha(),'date':'2026-10-29T23:30Z'}]:
            if f['date'].startswith('2026-10-29'): f['competitions'][0]['date']=f['date']
            self.assertNotIn('contexto',self.consultar(f=f))
        e=nba(); e['visitante']='Miami Heat'
        self.assertNotIn('contexto',self.consultar(e=e))

    def test_ambiguedad_y_fase_desconocida_sin_bonus(self):
        e=nba()
        with patch('resumen.contexto_fuentes.descargar_json',return_value={'events':[ficha(),ficha()]}):
            enriquecer_eventos([e],datetime(2026,10,30,12,tzinfo=MADRID_TZ))
        self.assertNotIn('contexto',e)
        self.assertEqual(valorar_contexto(self.consultar(f=ficha('NBA Cup')))['ajuste'],0)

    def test_temporalidad_identidad_y_fase_no_se_duplican(self):
        e=self.consultar(f=ficha('NBA Cup - Quarterfinal'))
        r=evaluar_evento({**e,'competicion':'NBA Cup Cuartos de Final'})
        self.assertLessEqual(r['desglose']['fase']+r['evaluacion_contexto']['ajuste'],1.0)
        for campo,valor in [('consultado','2026-10-31T01:00:00+01:00'),('temporada',2025),('estado_partido','post')]:
            mal=copy.deepcopy(e);mal['contexto'][campo]=valor
            self.assertEqual(valorar_contexto(mal)['ajuste'],0)

    def test_ficha_defectuosa_no_borra_otra_valida(self):
        mal=ficha();mal['competitions'][0]['date']='fecha no válida'
        e=nba()
        with patch('resumen.contexto_fuentes.descargar_json',return_value={'events':[mal,ficha()]}):
            enriquecer_eventos([e],datetime(2026,10,30,12,tzinfo=MADRID_TZ))
        self.assertEqual(valorar_contexto(e)['ajuste'],.3)

    def test_no_consulta_wnba_ni_iniciado(self):
        for cambio in [{'competicion':'WNBA'},{'fecha':'2026-10-30','hora':'10:00'}]:
            e={**nba(),**cambio}
            with patch('resumen.contexto_fuentes.descargar_json') as consulta:
                enriquecer_eventos([e],datetime(2026,10,30,12,tzinfo=MADRID_TZ))
                consulta.assert_not_called()
            self.assertNotIn('contexto',e)

    def test_instantanea_nba_reproduce_sin_red(self):
        from resumen.eventos import recomendar_eventos
        from resumen.diagnostico import preparar_diagnostico,reproducir
        corte=datetime(2026,10,30,12,tzinfo=MADRID_TZ)
        r=recomendar_eventos([self.consultar()],ahora=corte)
        s=preparar_diagnostico(r,corte)
        with patch('requests.get',side_effect=AssertionError('Sin red en reproducción')):
            replay=reproducir(s)
        self.assertEqual(replay['filtrados'][0]['score'],r['filtrados'][0]['score'])
        self.assertNotIn('"score":',json.dumps(s['eventos'][0]['contexto']))

    def test_preferencias_neutrales_en_ambos_modulos_y_celtics_conservado(self):
        anteriores=json.loads((ROOT/'data/afinidades_nba.json').read_text(encoding='utf-8'))
        for k in ['Knicks','76ers','Heat','Thunder']:
            self.assertEqual(NBA_TEAM_AFFINITY[k.casefold()],0)
            self.assertEqual(anteriores[k],0)
        self.assertEqual(NBA_TEAM_AFFINITY['celtics'],.85)
        self.assertEqual(anteriores['Celtics'],.85)

    def test_rivalidades_cinco_paises_alias_y_selecciones(self):
        for a,b in [('LOSC Lille','RC Lens'),('Juventus','Torino FC'),('FC Barcelona','RCD Espanyol'),
                    ('Newcastle United','Sunderland AFC'),('1. FC Köln','Borussia Mönchengladbach')]:
            self.assertGreater(valorar_rivalidad(dict(local=a,visitante=b,deporte='Fútbol',competicion='Copa'))['ajuste'],0)
        e=dict(local='England',visitante='Scotland',deporte='Fútbol',competicion='Eurocopa')
        self.assertGreater(valorar_rivalidad(e)['ajuste'],0)
        for comp in ['Premier League','Eurocopa Sub-21','Eurocopa Femenina']:
            self.assertEqual(valorar_rivalidad({**e,'competicion':comp})['ajuste'],0)
        self.assertEqual(valorar_rivalidad({**e,'visitante':'España'})['ajuste'],0)

    def test_perfiles_moderados_no_un_salto_global(self):
        def basket(a,b,c='Euroliga'):
            return evaluar_evento(dict(local=a,visitante=b,deporte='Baloncesto',competicion=c,
                                      fecha='2026-10-30',hora='20:00',canales=[]))
        self.assertAlmostEqual(basket('Zalgiris Kaunas','Partizan')['desglose']['cartel'],.7)
        self.assertEqual(basket('Dubai Basketball','Paris Basketball')['desglose']['cartel'],0)
        self.assertEqual(basket('Zalgiris Kaunas','Partizan','Liga Endesa')['desglose']['cartel'],0)

    def test_moderacion_exige_racha_opuesta_y_gran_distancia(self):
        from test_contexto import contextual, equipo
        e=contextual()
        e['contexto']['local']=equipo('Equipo A',1,'WWWWW',8,7,0)
        e['contexto']['visitante']=equipo('Equipo B',18,'LLLLW',8,1,6)
        self.assertEqual(valorar_contexto(e)['ajuste'],.6)
        self.assertEqual(valorar_contexto(e)['moderacion_forma'],.6)
        for cambio in [{'posicion':8},{'forma':'WDLWL'},{'forma':'LLL'}]:
            otro=copy.deepcopy(e);otro['contexto']['visitante'].update(cambio)
            self.assertEqual(valorar_contexto(otro)['ajuste'],1.2)
