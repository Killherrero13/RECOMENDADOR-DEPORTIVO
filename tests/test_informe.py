import copy
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from bs4 import BeautifulSoup

from referencia import ROOT
from resumen.__main__ import demostracion
from resumen.camisetas import ErrorCamisetas
from resumen.ejecucion import ejecutar
from resumen.fuente_eventos import ErrorEventos
from resumen.informe import generar_informe, guardar_informe

class InformeTests(unittest.TestCase):
    def test_html_y_texto_contienen_lo_mismo_y_escapan_html(self):
        result = demostracion('ambos')
        result['camiseta']['camiseta'] = {'Equipo':'<script>alert(1)</script> & Club', 'Modelo':2026, 'Jugador':'"Jugador"'}
        report = generar_informe(result)
        soup = BeautifulSoup(report['html'],'html.parser')
        self.assertFalse(soup.find('script'))
        self.assertIn('&lt;script&gt;',report['html'])
        for value in ['<script>alert(1)</script> & Club','Liverpool','Arsenal','Chelsea','Valencia']:
            self.assertIn(value,report['texto'])
            self.assertIn(value,soup.get_text(' ',strip=True))
        self.assertEqual(soup.find('meta',attrs={'name':'viewport'})['content'],'width=device-width,initial-scale=1')

    def test_ambos_no_duplica_partidos_y_modos_aislados(self):
        combined = generar_informe(demostracion('ambos'))['texto']
        self.assertIn('Camiseta recomendada',combined)
        self.assertIn('Imprescindible',combined)
        self.assertNotIn('Equipo de ejemplo',combined)
        self.assertIn('Equipo de ejemplo',generar_informe(demostracion('camiseta'))['texto'])
        self.assertNotIn('Camiseta recomendada',generar_informe(demostracion('eventos'))['texto'])

    @patch('resumen.ejecucion.obtener_api_key',return_value='ficticia')
    @patch('resumen.ejecucion.generar_resultado_eventos')
    @patch('resumen.ejecucion.generar_resultado')
    def test_fallo_camiseta_conserva_eventos(self,shirt,events,key):
        shirt.side_effect = ErrorCamisetas('API HTTP 503')
        events.return_value = demostracion('eventos')['eventos']
        result = ejecutar('ambos')
        self.assertIsNotNone(result['eventos'])
        self.assertIn('camiseta',result['errores'])
        report = generar_informe(result)
        self.assertIn('[CON ERRORES]',report['asunto'])
        self.assertIn('API HTTP 503',report['texto'])
        self.assertIn('Imprescindible',report['texto'])

    @patch('resumen.ejecucion.obtener_api_key',return_value='ficticia')
    @patch('resumen.ejecucion.generar_resultado_eventos')
    @patch('resumen.ejecucion.generar_resultado')
    def test_fallo_eventos_conserva_camiseta_y_partidos(self,shirt,events,key):
        shirt.return_value = demostracion('camiseta')['camiseta']
        events.side_effect = ErrorEventos('Web HTTP 403')
        report = generar_informe(ejecutar('ambos'))
        self.assertIn('Equipo de ejemplo',report['texto'])
        self.assertIn('Web HTTP 403',report['texto'])

    @patch('resumen.ejecucion.generar_resultado_eventos')
    @patch('resumen.ejecucion.obtener_api_key')
    def test_fallo_total_y_error_inesperado_sanitizado(self,key,events):
        key.side_effect = RuntimeError('SECRETO_NO_MOSTRAR')
        events.side_effect = ErrorEventos('Web HTTP 503')
        with self.assertLogs('resumen.ejecucion',level='ERROR') as logs:
            result = ejecutar('ambos')
        self.assertEqual(len(result['errores']),2)
        report = generar_informe(result)
        self.assertNotIn('SECRETO_NO_MOSTRAR',report['texto'] + ''.join(logs.output))

    @patch('resumen.ejecucion.generar_resultado_eventos')
    @patch('resumen.ejecucion.obtener_api_key')
    def test_modo_eventos_no_requiere_credencial(self,key,events):
        events.return_value = demostracion('eventos')['eventos']
        self.assertFalse(ejecutar('eventos')['errores'])
        key.assert_not_called()

    def test_guardado_utf8_y_resultado_no_modificado(self):
        result = demostracion('ambos')
        before = copy.deepcopy(result)
        report = generar_informe(result)
        with tempfile.TemporaryDirectory() as folder:
            guardar_informe(report,folder)
            self.assertEqual((Path(folder)/'resumen.html').read_text(encoding='utf-8'),report['html'])
            self.assertEqual((Path(folder)/'resumen.txt').read_text(encoding='utf-8'),report['texto'])
        self.assertEqual(result,before)

    def test_cli_tres_modos_y_fallo_devuelve_uno_guardando_aviso(self):
        env = dict(os.environ)
        env.pop('FOOTBALL_API_KEY',None)
        with tempfile.TemporaryDirectory() as folder:
            for mode in ('ambos','eventos','camiseta'):
                run = subprocess.run([sys.executable,'-X','utf8','-m','resumen','--modo',mode,
                                      '--sin-conexion','--salida',folder],cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8')
                self.assertEqual(run.returncode,0,run.stderr)
                self.assertTrue((Path(folder)/'resumen.html').exists())
            failed = subprocess.run([sys.executable,'-X','utf8','-m','resumen','--modo','camiseta',
                                     '--salida',folder],cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(failed.returncode,1)
            self.assertIn('Falta la variable',(Path(folder)/'resumen.html').read_text(encoding='utf-8'))

if __name__ == '__main__':
    unittest.main()
