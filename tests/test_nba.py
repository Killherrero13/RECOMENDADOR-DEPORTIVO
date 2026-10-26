import copy
import unittest
from datetime import datetime
from unittest.mock import patch, Mock
from resumen.config import MADRID_TZ
from resumen.nba import evaluar_partidos, generar_nba, descargar, ErrorNBA, puntuacion, categoria_nba
from resumen.__main__ import demostracion
from resumen.informe import generar_informe
from resumen.ejecucion import ejecutar


def partido(id='1', fecha='2026-10-26T00:00Z', final=True, puntos=('103','102')):
    return {'id': id, 'date': fecha, 'status': {'type': {'completed': final}},
            'competitions': [{'competitors': [
                {'homeAway': 'home', 'score': puntos[0], 'team': {'name': 'Celtics', 'displayName': 'Boston Celtics'}},
                {'homeAway': 'away', 'score': puntos[1], 'team': {'name': 'Trail Blazers', 'displayName': 'Portland Trail Blazers'}}]}]}


class NBATests(unittest.TestCase):
    ahora = datetime(2026,10,26,5,tzinfo=MADRID_TZ)

    def test_finales_ventana_duplicados_y_nombre_compuesto(self):
        p = partido()
        datos = evaluar_partidos([p,p,partido('2',final=False),partido('3','2026-10-24T00:00Z'),
                                  partido('4','2026-10-26T06:00Z')], self.ahora)
        self.assertEqual(len(datos['partidos']),1)
        self.assertEqual(datos['partidos'][0]['visitante'],'Portland Trail Blazers')
        self.assertEqual(datos['partidos'][0]['recomendacion'],'Ver completo')
        self.assertIn('1 encuentros', str(datos['avisos']))
        self.assertEqual(set(datos['partidos'][0]),{'local','visitante','fecha','recomendacion'})

    def test_datos_invalidos_no_son_dia_vacio(self):
        datos = evaluar_partidos([partido(puntos=('103','103')), {}], self.ahora)
        self.assertEqual(datos['partidos'],[])
        self.assertIn('cobertura incompleta',str(datos['avisos']))

    def test_sin_spoilers_en_html_texto_ni_adjunto(self):
        r = demostracion('eventos')
        r['nba'] = evaluar_partidos([partido(),partido('2',puntos=('127','89'))],self.ahora)
        informe = generar_informe(r)
        for medio in ['html','texto','listado_html']:
            for secreto in ['103','102','127','89','score','winner','puntuacion']:
                self.assertNotIn(secreto,informe[medio])
        self.assertIn('NBA en diferido',informe['html'])
        self.assertIn('Puedes saltártelo',informe['texto'])

    @patch('resumen.nba.descargar')
    def test_consulta_fechas_utc_incluye_ambos_dias(self, descargar):
        descargar.return_value = []
        generar_nba(self.ahora)
        self.assertEqual([c.args[0].isoformat() for c in descargar.call_args_list],['2026-10-25','2026-10-26'])

    @patch('resumen.nba.requests.get')
    def test_error_fuente_no_se_confunde_con_sin_partidos(self,get):
        get.return_value = Mock(status_code=200)
        get.return_value.json.return_value = {}
        with self.assertRaises(ErrorNBA): descargar(self.ahora.date())

    @patch('resumen.ejecucion.generar_nba',side_effect=ErrorNBA('Fuente no disponible'))
    @patch('resumen.ejecucion.generar_resultado_eventos')
    def test_fallo_parcial_conserva_agenda(self,eventos,nba):
        eventos.return_value = demostracion('eventos')['eventos']
        r = ejecutar('eventos',self.ahora,incluir_nba=True)
        self.assertIsNotNone(r['eventos'])
        self.assertIn('nba',r['errores'])

    def test_cambio_de_hora_y_fecha_con_zona_obligatoria(self):
        with self.assertRaises(ValueError): evaluar_partidos([],datetime(2026,10,26))
        r = evaluar_partidos([partido(fecha='2026-10-25T00:00Z')],datetime(2026,10,25,5,tzinfo=MADRID_TZ))
        self.assertEqual(len(r['partidos']),1)

    def test_tres_etiquetas_y_orden_alfabetico(self):
        a = partido('1',puntos=('103','102'))
        b = partido('2',puntos=('118','110'))
        c = partido('3',puntos=('120','80'))
        a['competitions'][0]['competitors'][0]['team']['displayName'] = 'Z equipo'
        b['competitions'][0]['competitors'][0]['team']['displayName'] = 'A equipo'
        c['competitions'][0]['competitors'][0]['team']['displayName'] = 'M equipo'
        datos = evaluar_partidos([a,b,c],self.ahora)['partidos']
        self.assertEqual([p['recomendacion'] for p in datos],['Resumen','Puedes saltártelo','Ver completo'])

    @patch('resumen.nba.time.sleep')
    @patch('resumen.nba.requests.get')
    def test_reintento_limitado(self,get,sleep):
        import requests
        get.side_effect = requests.Timeout()
        with self.assertRaises(ErrorNBA): descargar(self.ahora.date())
        self.assertEqual(get.call_count,3)
        self.assertEqual(sleep.call_count,2)

    def test_curva_suave_y_sin_premio_por_anotacion(self):
        notas = [puntuacion('Neutral A','Neutral B',100+d,100) for d in range(1,31)]
        self.assertTrue(all(a > b for a,b in zip(notas,notas[1:])))
        self.assertLess(max(a-b for a,b in zip(notas,notas[1:])),.06)
        self.assertEqual(puntuacion('Celtics','Jazz',95,90),puntuacion('Celtics','Jazz',135,130))
        self.assertEqual(categoria_nba(puntuacion('Neutral A','Neutral B',109,100)),'Resumen')

    def test_favorito_puede_subir_sin_imponer_completo(self):
        self.assertEqual(categoria_nba(puntuacion('Celtics','Jazz',105,100)),'Ver completo')
        self.assertEqual(categoria_nba(puntuacion('Neutral A','Jazz',105,100)),'Resumen')
        self.assertEqual(categoria_nba(puntuacion('Celtics','Jazz',130,100)),'Puedes saltártelo')

    def test_todo_nba_en_un_bloque_naranja(self):
        from bs4 import BeautifulSoup
        r = demostracion('eventos')
        r['nba'] = evaluar_partidos([partido()],self.ahora)
        soup = BeautifulSoup(generar_informe(r)['html'],'html.parser')
        bloque = soup.find(id='bloque-nba')
        self.assertIsNotNone(bloque)
        self.assertIn('Fuente: ESPN',bloque.get_text())
        self.assertEqual(len(soup.select('.tarjeta-nba')),len(bloque.select('.tarjeta-nba')))
        self.assertIn('#ffdfc1',bloque.select_one('.tarjeta-nba')['style'])
