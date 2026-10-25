import copy
import random
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from resumen.config import MADRID_TZ
from resumen.camisetas import cargar_coleccion, ErrorCamisetas
from resumen.seleccion_camisetas import recomendar_camisetas
from resumen.ejecucion import ejecutar
from resumen.informe import generar_informe

def camiseta(equipo, modelo='Primera'):
    return {'Equipo':equipo, 'Modelo':modelo, 'Jugador':''}

class SeleccionCamisetasTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,10,25,9,tzinfo=MADRID_TZ)

    def partido(self, local, visitante='Rival', **extra):
        return {'home':local,'away':visitante,'hora':self.now.replace(hour=18),
                'competition':'Premier League',**extra}

    def evento(self, local, visitante='Rival', **extra):
        return {'local':local,'visitante':visitante,'hora':'18:00','fecha':'2026-10-25',
                'deporte':'Fútbol','competicion':'LaLiga EA Sports','canales':['DAZN'],**extra}

    def seleccionar(self, coleccion, partidos=None, eventos=None):
        return recomendar_camisetas(coleccion,partidos or [],eventos or [],self.now,random.Random(42))

    def test_recomendada_por_evento_y_alternativa_otro_equipo(self):
        collection=[camiseta('Atlético de Madrid','Primera'),camiseta('Atlético de Madrid','Segunda'),camiseta('Ajax')]
        before=copy.deepcopy(collection)
        result=self.seleccionar(collection,eventos=[self.evento('At. Madrid','Real Madrid')])
        self.assertEqual(result['recomendada']['Equipo'],'Atlético de Madrid')
        self.assertEqual(result['aleatoria']['Equipo'],'Ajax')
        self.assertEqual(result['partido_asociado']['home'],'At. Madrid')
        self.assertEqual(collection,before)

    def test_favoritos_tienen_prioridad_y_entre_ellos_puntua_el_evento(self):
        collection=[camiseta('Liverpool'),camiseta('Aston Villa'),camiseta('Atlético de Madrid')]
        events=[self.evento('Liverpool',score=30),self.evento('Aston Villa',score=10),
                self.evento('At. Madrid',score=11)]
        self.assertEqual(self.seleccionar(collection,eventos=events)['recomendada']['Equipo'],'Atlético de Madrid')
        events[1]['score']=12
        self.assertEqual(self.seleccionar(collection,eventos=events)['recomendada']['Equipo'],'Aston Villa')

    def test_alias_de_la_coleccion_y_de_la_api(self):
        for shirt, name in [('FC Porto','Porto'),('Sporting Lisboa','Sporting CP'),
                            ('Manchester United','Manchester Utd.'),('Napoles','SSC Napoli'),
                            ('España','Spain'),('Arsenal','Arsenal FC'),
                            ('FC Bayern','FC Bayern München'),('Union Belin','1. FC Union Berlin')]:
            with self.subTest(equipo=shirt):
                result=self.seleccionar([camiseta(shirt)],partidos=[self.partido(name)])
                self.assertIsNotNone(result['recomendada'])

    def test_no_confunde_celtic_celtics_inter_miami_o_casablanca(self):
        for shirt,name in [('Celtic de Glasgow','Boston Celtics'),('Inter Miami','Inter Milan'),('Casablanca','Wydad Casablanca')]:
            self.assertIsNone(self.seleccionar([camiseta(shirt)],partidos=[self.partido(name)])['recomendada'])
        result=self.seleccionar([camiseta('Valencia')],eventos=[self.evento('Valencia',deporte='Baloncesto')])
        self.assertIsNone(result['recomendada'])

    def test_sin_coincidencias_solo_aleatoria_de_la_coleccion(self):
        collection=cargar_coleccion()
        result=self.seleccionar(collection,partidos=[self.partido('Equipo sin camiseta')])
        self.assertIsNone(result['recomendada'])
        self.assertIn(result['aleatoria'],collection)
        self.assertEqual(result['camiseta'],result['aleatoria'])

    def test_coleccion_de_una_prenda_no_duplica(self):
        collection=[camiseta('Aston Villa')]
        result=self.seleccionar(collection,partidos=[self.partido('Aston Villa FC')])
        self.assertIsNotNone(result['recomendada'])
        self.assertIsNone(result['aleatoria'])

    def test_no_usa_manana_ni_partidos_antiguos_ni_cancelados(self):
        collection=[camiseta('Aston Villa')]
        for extra in [{'hora':self.now+timedelta(days=1)}, {'hora':self.now-timedelta(hours=3)},
                      {'status':'CANCELLED'},{'status':'POSTPONED'},{'status':'SUSPENDED'}]:
            self.assertIsNone(self.seleccionar(collection,partidos=[self.partido('Aston Villa',**extra)])['recomendada'])

    @patch('resumen.ejecucion.obtener_api_key',return_value='ficticia')
    @patch('resumen.ejecucion.generar_resultado',side_effect=ErrorCamisetas('API HTTP 503'))
    @patch('resumen.ejecucion.generar_resultado_eventos')
    def test_api_fallida_aprovecha_agenda_y_conserva_error(self,events,shirts,key):
        events.return_value={'eventos_disponibles':[self.evento('At. Madrid')], 'plan':{}, 'alternativas':[]}
        result=ejecutar('ambos',self.now)
        self.assertEqual(result['camiseta']['recomendada']['Equipo'],'Atlético de Madrid')
        self.assertIn('camiseta',result['errores'])
        text=generar_informe(result)['texto']
        self.assertIn('Partido:',text)
        self.assertIn('Alternativa al azar',text)

    @patch('resumen.ejecucion.obtener_api_key',return_value='ficticia')
    @patch('resumen.ejecucion.generar_resultado')
    @patch('resumen.ejecucion.generar_resultado_eventos',side_effect=RuntimeError('detalle'))
    def test_agenda_fallida_usa_api_y_modo_camiseta_tambien(self,events,shirts,key):
        shirts.return_value={'fecha':'2026-10-25','partidos':[self.partido('Aston Villa FC')]}
        result=ejecutar('ambos',self.now)
        self.assertEqual(result['camiseta']['recomendada']['Equipo'],'Aston Villa')
        events.reset_mock()
        result=ejecutar('camiseta',self.now)
        self.assertEqual(result['camiseta']['recomendada']['Equipo'],'Aston Villa')
        events.assert_not_called()

    @patch('resumen.ejecucion.obtener_api_key',side_effect=ErrorCamisetas('Sin acceso'))
    def test_sin_fuentes_mantiene_aleatoria_y_aviso(self,key):
        result=ejecutar('camiseta',self.now)
        self.assertIsNone(result['camiseta']['recomendada'])
        self.assertIn(result['camiseta']['aleatoria'],cargar_coleccion())
        self.assertTrue(result['errores'])

if __name__ == '__main__':
    unittest.main()
