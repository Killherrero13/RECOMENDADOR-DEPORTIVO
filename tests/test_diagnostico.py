import copy
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from resumen.config import MADRID_TZ
from resumen.contexto_fuentes import enriquecer_eventos, tabla_euroliga, identidad_club
from resumen.diagnostico import ResultadoContexto, preparar_diagnostico, reproducir
from resumen.eventos import recomendar_eventos
from resumen.informe import generar_informe, guardar_informe
from resumen.__main__ import demostracion


def evento():
    return dict(local='Equipo A',visitante='Equipo B',competicion='Serie A Italiana',deporte='Fútbol',
                fecha='2026-10-28',hora='20:00',canales=[])


class DiagnosticoTests(unittest.TestCase):
    ahora=datetime(2026,10,28,10,tzinfo=MADRID_TZ)

    def test_instantanea_reproduce_notas_y_plan_sin_consultas(self):
        r=recomendar_eventos([evento()],ahora=self.ahora)
        original=copy.deepcopy(r)
        s=preparar_diagnostico(r,self.ahora)
        with patch('requests.get',side_effect=AssertionError('No debe consultar')):
            replay=reproducir(s)
        self.assertEqual(r,original)
        self.assertEqual([e['score'] for e in r['filtrados']],[e['score'] for e in replay['filtrados']])
        self.assertEqual(r['plan'],replay['plan'])
        s['modelo']='otro-modelo'
        with self.assertRaises(ValueError):reproducir(s)

    def test_no_serializa_datos_personales_ni_secretos(self):
        e=evento();e['smtp_password']='SECRETO'
        e['contexto']={'api_key':'NO_GUARDAR','token':'NO_GUARDAR'}
        r=recomendar_eventos([e],ahora=self.ahora)
        r['email']='PRIVADO'
        s=str(preparar_diagnostico(r,self.ahora))
        self.assertNotIn('SECRETO',s)
        self.assertNotIn('NO_GUARDAR',s)
        self.assertNotIn('PRIVADO',s)

    @patch('resumen.contexto_fuentes.tabla_futbol')
    def test_contexto_parcial_retiene_el_motivo_y_no_puntua(self,tabla):
        datos=ResultadoContexto()
        datos['Equipo A']={'nombre':'Equipo A','id':'1','posicion':1}
        datos.fallo('Equipo B','identidad_no_resuelta')
        tabla.return_value=datos
        e=evento();base=recomendar_eventos([e],ahora=self.ahora)['filtrados'][0]['score']
        enriquecer_eventos([e],self.ahora)
        self.assertNotIn('contexto',e)
        d=e['diagnostico_contexto']
        self.assertEqual(d['estado'],'parcial')
        self.assertEqual(d['participantes']['visitante'],'identidad_no_resuelta')
        self.assertEqual(d['datos_parciales']['local']['id'],'1')
        self.assertEqual(recomendar_eventos([e],ahora=self.ahora)['filtrados'][0]['score'],base)

    def test_alias_y_codigo_oficial_sin_cambiar_clasificacion_editorial(self):
        from resumen.perfiles import identidad_basket, REFERENTES_EUROLIGA
        for nombre,code,canonical in [('Hapoel Tel Aviv BC','HTA','hapoel tel aviv'),
            ('Anadolu Efes Istanbul','IST','efes'),('BC Partizan Beograd','PAR','partizan'),
            ('ASVEL Lyon-Villeurbanne','ASV','asvel'),('Virtus Bologna','VIR','virtus'),
            ('Žalgiris Kaunas','ZAL','zalgiris')]:
            self.assertEqual(identidad_basket(nombre),canonical)
            self.assertIn(canonical,identidad_club({'code':code,'name':'Nombre patrocinado'}))
            self.assertNotIn(canonical,REFERENTES_EUROLIGA)

    @patch('resumen.contexto_fuentes.descargar_json')
    def test_tabla_e_historial_de_misma_jornada_completa(self,descarga):
        games=[]
        tabla=[]
        for i in range(10):
            a='VIR' if i==0 else f'A{i}'
            b=f'B{i}'
            for ronda in (1,2):
                games.append(dict(round=ronda,played=(ronda==1 or i==0),
                    season={'code':'E2026'},phaseType={'code':'RS'},
                    utcDate='2026-10-20T18:00Z' if ronda==1 else '2026-10-27T18:00Z' if i==0 else '2026-10-29T18:00Z',
                    local={'club':{'code':a},'score':90},road={'club':{'code':b},'score':80}))
            tabla.extend([dict(club={'code':a,'name':'Nombre '+a},position=i+1,gamesPlayed=1,gamesWon=1,gamesLost=0),
                          dict(club={'code':b,'name':'Nombre '+b},position=i+11,gamesPlayed=1,gamesWon=0,gamesLost=1)])
        descarga.side_effect=[{'data':games,'total':20},{'teams':tabla}]
        r=tabla_euroliga(['Virtus Bologna'],self.ahora)
        self.assertEqual(r['Virtus Bologna']['jugados'],1)
        self.assertEqual(r['Virtus Bologna']['ronda'],1)
        self.assertIn('/rounds/1/',r['Virtus Bologna']['fuentes'][1])

    @patch('resumen.fuente_eventos.enriquecer_eventos',return_value=[])
    @patch('resumen.fuente_eventos.extraer_jornada')
    @patch('resumen.fuente_eventos.descargar_html',return_value='HTML')
    def test_contexto_consulta_solo_eventos_filtrados(self,html,extraer,enriquecer):
        from resumen.fuente_eventos import generar_resultado_eventos
        descartado={**evento(),'competicion':'Copa de Portugal'}
        extraer.return_value=([evento(),descartado],[])
        r=generar_resultado_eventos(self.ahora)
        self.assertEqual(len(enriquecer.call_args.args[0]),1)
        self.assertEqual(r['diagnostico']['cobertura']['relevantes'],1)
        informe=generar_informe(dict(fecha='2026-10-28',eventos=r,camiseta=None,errores={}))
        with tempfile.TemporaryDirectory() as carpeta:
            guardar_informe(informe,carpeta)
            self.assertTrue((Path(carpeta)/'diagnostico.json').exists())
            self.assertTrue((Path(carpeta)/'diagnostico.html').exists())
