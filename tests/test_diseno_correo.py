import copy
import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from resumen.__main__ import demostracion
from resumen.informe import generar_informe, guardar_informe
from resumen.correo import crear_mensaje
from resumen.config import ConfigCorreo

class DisenoCorreoTests(unittest.TestCase):
    def setUp(self):
        self.result=demostracion('ambos')

    def test_lista_completa_incluye_puntuaciones_bajas_y_orden_cronologico(self):
        all_events=self.result['eventos']['filtrados']
        low=copy.deepcopy(all_events[0])
        low.update(hora='07:00',local='Evento de interés bajo',score=2,
                   inicio=all_events[0]['inicio'].replace(hour=7))
        self.result['eventos']['filtrados']=[*all_events,low]
        report=generar_informe(self.result)
        html=BeautifulSoup(report['html'],'html.parser')
        rows=html.select('#todos-eventos .evento-filtrado')
        self.assertEqual(len(rows),len(all_events)+1)
        self.assertIn('Evento de interés bajo',rows[0].get_text())
        attachment=BeautifulSoup(report['listado_html'],'html.parser')
        self.assertEqual([r.get_text() for r in rows], [r.get_text() for r in attachment.select('.evento-filtrado')])
        self.assertIn('Evento de interés bajo',report['texto'])

    def test_enlace_a_lista_completa_y_origen(self):
        html=BeautifulSoup(generar_informe(self.result)['html'],'html.parser')
        self.assertIsNotNone(html.find('a',href='#todos-eventos'))
        self.assertIsNotNone(html.find(id='todos-eventos'))
        self.assertIsNotNone(html.find('a',href='https://www.futbolenlatv.es/deporte'))
        self.assertFalse(html.find(['script','iframe','form']))
        self.assertFalse(html.find('img')) # Sin imágenes remotas ni dependencias de carga.

    def test_conserva_canales_mas_en_lugar_de_ocultarlos(self):
        e=self.result['eventos']['plan']['imprescindible']
        e['canales']=['M+ Vamos (8 y 50)','DAZN LaLiga (M55 O113)']
        e['channel']=None
        report=generar_informe(self.result)
        self.assertIn('M+ Vamos (8 y 50)',BeautifulSoup(report['html'],'html.parser').get_text())
        self.assertIn('DAZN LaLiga (M55 O113)',report['texto'])

    def test_lista_sin_eventos_y_modo_camiseta_sin_adjunto(self):
        result=demostracion('eventos')
        result['eventos'].update(filtrados=[],plan={},alternativas=[],seleccionados=[])
        report=generar_informe(result)
        self.assertIn('Todos los eventos filtrados (0)',report['html'])
        self.assertIsNotNone(report['listado_html'])
        shirt_report=generar_informe(demostracion('camiseta'))
        self.assertIsNone(shirt_report['listado_html'])
        config=ConfigCorreo('a@example.com','ficticia','a@example.com','b@example.com')
        self.assertFalse(list(crear_mensaje(shirt_report,config).iter_attachments()))

    def test_escape_de_datos_en_tarjetas_y_adjunto(self):
        e=self.result['eventos']['filtrados'][0]
        e['local']='<img src=x onerror=alert(1)>'
        e['canales']=['<script>alert(1)</script>']
        report=generar_informe(self.result)
        for content in (report['html'],report['listado_html']):
            soup=BeautifulSoup(content,'html.parser')
            self.assertFalse(soup.find(['script','img']))
            self.assertIn('<img src=x onerror=alert(1)>',soup.get_text())

    def test_se_guarda_el_listado_y_adjunto_es_html(self):
        report=generar_informe(self.result)
        with tempfile.TemporaryDirectory() as folder:
            guardar_informe(report,folder)
            self.assertEqual((Path(folder)/'todos_eventos.html').read_text(encoding='utf-8'),report['listado_html'])
        config=ConfigCorreo('a@example.com','ficticia','a@example.com','b@example.com')
        attachment=list(crear_mensaje(report,config).iter_attachments())[0]
        self.assertEqual(attachment.get_content_type(),'text/html')
        self.assertEqual(attachment.get_filename(),'todos_eventos.html')

if __name__ == '__main__':
    unittest.main()
