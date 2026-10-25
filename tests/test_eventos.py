import ast
import copy
import json
import unittest
from datetime import date
from unittest.mock import Mock, patch

import requests
from bs4 import BeautifulSoup

from referencia import ROOT, ejecutar_eventos
from resumen.eventos import recomendar_eventos
from resumen.fuente_eventos import ErrorEventos, descargar_html, extraer_eventos

class EventosTests(unittest.TestCase):
    def test_algoritmo_completo_coincide_con_original(self):
        events = json.loads((ROOT/'tests/fixtures/eventos.json').read_text(encoding='utf-8'))
        original_input = copy.deepcopy(events)
        old = ejecutar_eventos(copy.deepcopy(events))
        new = recomendar_eventos(events)
        for actual, original in [('filtrados','filtered_events'), ('plan','daily_plan'),
                                 ('seleccionados','selected_events'), ('alternativas','other_top_events')]:
            self.assertEqual(new[actual], old[original])
        self.assertEqual(events, original_input)

    def test_dia_sin_recomendaciones(self):
        self.assertEqual(recomendar_eventos([]), {'filtrados': [], 'plan': {}, 'seleccionados': [], 'alternativas': []})

    def test_html_guardado_coincide_con_scraping_original(self):
        html = (ROOT/'tests/fixtures/eventos_real_2026-10-25.html').read_text(encoding='utf-8')
        source = (ROOT/'referencia/eventos_colab.py').read_text(encoding='utf-8')
        tree = ast.parse(source)
        start = next(i for i,n in enumerate(tree.body) if isinstance(n,ast.Assign)
                     and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='soup')
        end = next(i for i,n in enumerate(tree.body) if isinstance(n,ast.Assign)
                   and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='TOP_ATP')
        nodes = [n for n in tree.body[start:end] if not isinstance(n,ast.Expr)]
        ns = {'html':html, 'BeautifulSoup':BeautifulSoup}
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'<scraping original>','exec'),ns)
        actual = extraer_eventos(html,date(2026,10,25))
        self.assertEqual(actual,ns['events'])
        self.assertEqual(len(actual),283)
        old = ejecutar_eventos(copy.deepcopy(actual))
        new = recomendar_eventos(actual)
        self.assertEqual(new['filtrados'],old['filtered_events'])
        self.assertEqual(new['plan'],old['daily_plan'])
        self.assertEqual(new['alternativas'],old['other_top_events'])

    def test_estructura_invalida_y_fecha_incorrecta(self):
        for html in ('<html>Acceso denegado</html>', '<table class="tablaPrincipal"></table>',
                     '<table class="tablaPrincipal"><tr class="cabeceraTabla"><td>25/10/2026</td></tr></table>'):
            with self.assertRaises(ErrorEventos):
                extraer_eventos(html,date(2026,10,25))
        html = (ROOT/'tests/fixtures/eventos_real_2026-10-25.html').read_text(encoding='utf-8')
        with self.assertRaisesRegex(ErrorEventos,'se esperaba'):
            extraer_eventos(html,date(2026,10,26))

    @patch('resumen.fuente_eventos.requests.get')
    def test_descarga_y_errores_http(self,get):
        get.return_value=Mock(status_code=200,text='<html>Ejemplo</html>')
        self.assertEqual(descargar_html(),'<html>Ejemplo</html>')
        self.assertEqual(get.call_args.kwargs['timeout'],(5,20))
        for code in (403,429):
            get.return_value=Mock(status_code=code)
            with self.assertRaisesRegex(ErrorEventos,str(code)):
                descargar_html()

    @patch('resumen.fuente_eventos.time.sleep')
    @patch('resumen.fuente_eventos.requests.get')
    def test_reintentos_limitados(self,get,sleep):
        get.side_effect=[requests.Timeout(),Mock(status_code=503),Mock(status_code=200,text='OK')]
        self.assertEqual(descargar_html(),'OK')
        self.assertEqual(get.call_count,3)
        get.reset_mock()
        get.side_effect=requests.ConnectionError('detalle interno')
        with self.assertRaisesRegex(ErrorEventos,'tres intentos'):
            descargar_html()
        self.assertEqual(get.call_count,3)

if __name__ == '__main__':
    unittest.main()
