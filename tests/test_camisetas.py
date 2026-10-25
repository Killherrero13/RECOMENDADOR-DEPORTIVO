import os
import random
import subprocess
import sys
import unittest
from datetime import date, datetime
from unittest.mock import Mock, patch

import requests

from referencia import ROOT, cargar_camisetas as original
from resumen import camisetas as c
from resumen.config import ErrorConfiguracion, MADRID_TZ, obtener_api_key

def match(utc):
    return {'utcDate': utc, 'homeTeam': {'name': 'Local'},
            'awayTeam': {'name': 'Visitante'}, 'competition': {'name': 'Liga'}}

class CamisetasTests(unittest.TestCase):
    def setUp(self):
        self.ahora = datetime(2026, 10, 25, 9, tzinfo=MADRID_TZ)

    def test_coleccion_y_seleccion_coinciden_con_original(self):
        ns = original()
        self.assertEqual(c.cargar_coleccion(), ns['camisetas'])
        for seed in range(20):
            ns['random'] = random.Random(seed)
            ns['obtener_partidos_hoy'] = lambda: []
            self.assertEqual(c.seleccionar_camiseta(c.cargar_coleccion(), [], random.Random(seed)),
                             ns['seleccionar_camiseta']())

    def test_secreto_obligatorio(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ErrorConfiguracion):
                obtener_api_key()

    def test_entrada_sin_conexion_y_error_sin_clave(self):
        env = dict(os.environ)
        env.pop('FOOTBALL_API_KEY', None)
        demo = subprocess.run([sys.executable, '-X', 'utf8', '-m', 'resumen', '--sin-conexion'],
                              cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(demo.returncode, 0, demo.stderr)
        self.assertIn('DATOS FICTICIOS', demo.stdout)
        missing = subprocess.run([sys.executable, '-X', 'utf8', '-m', 'resumen', '--modo', 'camiseta'], cwd=ROOT, env=env,
                                 capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(missing.returncode, 1)
        self.assertIn('Falta la variable de entorno', missing.stderr)
        self.assertNotIn('Traceback', missing.stderr)

    def test_fechas_incluyen_medianoche_y_cambio_horario(self):
        payload = {'matches': [match('2026-10-24T21:59:00Z'), match('2026-10-24T22:00:00Z'),
                               match('2026-10-25T00:30:00Z'), match('2026-10-25T01:30:00Z'),
                               match('2026-10-25T22:59:00Z'), match('2026-10-25T23:00:00Z')]}
        result = c.interpretar_partidos(payload, self.ahora.date())
        self.assertEqual([p['hora'].strftime('%H:%M') for p in result], ['00:00','02:30','02:30','23:59'])
        self.assertEqual([p['hora'].fold for p in result[1:3]], [0, 1])
        self.assertEqual(c.parametros_fecha(date(2026,10,25)), {'dateFrom':'2026-10-24','dateTo':'2026-10-26'})
        self.assertEqual(c.parametros_fecha(date(2026,3,29)), {'dateFrom':'2026-03-28','dateTo':'2026-03-30'})
        summer = c.interpretar_partidos({'matches':[match('2026-07-01T22:30:00Z')]}, date(2026,7,2))
        self.assertEqual(summer[0]['hora'].strftime('%H:%M'), '00:30')

    @patch('resumen.camisetas.requests.get')
    def test_consulta_valida_y_sin_partidos(self, get):
        get.return_value = Mock(status_code=200)
        get.return_value.json.return_value = {'matches': []}
        self.assertEqual(c.obtener_partidos_hoy('clave-ficticia', self.ahora), [])
        self.assertEqual(get.call_args.kwargs['timeout'], (5,20))
        self.assertFalse(get.call_args.kwargs['allow_redirects'])
        self.assertEqual(get.call_args.kwargs['params'], c.parametros_fecha(self.ahora.date()))

    @patch('resumen.camisetas.requests.get')
    def test_errores_http_no_se_confunden_con_lista_vacia(self, get):
        for status in (401,403,429,302):
            get.return_value = Mock(status_code=status)
            with self.assertRaisesRegex(c.ErrorCamisetas, str(status)):
                c.obtener_partidos_hoy('clave-ficticia', self.ahora)

    @patch('resumen.camisetas.time.sleep')
    @patch('resumen.camisetas.requests.get')
    def test_reintento_transitorio_y_recuperacion(self, get, sleep):
        ok = Mock(status_code=200)
        ok.json.return_value = {'matches': []}
        get.side_effect = [requests.Timeout('clave-ficticia'), Mock(status_code=503), ok]
        self.assertEqual(c.obtener_partidos_hoy('clave-ficticia', self.ahora), [])
        self.assertEqual(get.call_count, 3)
        self.assertEqual(sleep.call_count, 2)

    @patch('resumen.camisetas.time.sleep')
    @patch('resumen.camisetas.requests.get')
    def test_fallo_de_red_limitado_y_sin_filtrar_secreto(self, get, sleep):
        get.side_effect = requests.ConnectionError('clave-ficticia')
        with self.assertLogs(c.logger, level='WARNING') as logs:
            with self.assertRaises(c.ErrorCamisetas) as error:
                c.obtener_partidos_hoy('clave-ficticia', self.ahora)
        self.assertEqual(get.call_count, 3)
        self.assertNotIn('clave-ficticia', str(error.exception) + ''.join(logs.output))

    @patch('resumen.camisetas.requests.get')
    def test_json_invalido(self, get):
        get.return_value = Mock(status_code=200)
        get.return_value.json.side_effect = ValueError('respuesta inválida')
        with self.assertRaisesRegex(c.ErrorCamisetas, 'JSON'):
            c.obtener_partidos_hoy('clave-ficticia', self.ahora)

    def test_datos_incompletos_son_error(self):
        for payload in ({}, {'matches':None}, {'matches':[{}]}, {'matches':[match('sin fecha')]}):
            with self.assertRaises(c.ErrorCamisetas):
                c.interpretar_partidos(payload, self.ahora.date())

    def test_filtro_de_dos_horas_original(self):
        matches = [{'hora':self.ahora.replace(hour=h, minute=m)} for h,m in [(6,59),(7,0),(18,0)]]
        self.assertEqual(c.partidos_visibles(matches, self.ahora), matches[1:])

    @patch('resumen.camisetas.obtener_partidos_hoy', return_value=[])
    def test_resultado_estructurado(self, get):
        result = c.generar_resultado('clave-ficticia', self.ahora)
        self.assertEqual(result['fecha'], '2026-10-25')
        self.assertIn(result['camiseta'], c.cargar_coleccion())
        self.assertEqual(result['partidos'], [])

if __name__ == '__main__':
    unittest.main()
