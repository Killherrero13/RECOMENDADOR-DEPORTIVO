import unittest
from bs4 import BeautifulSoup
from resumen.__main__ import demostracion
from resumen.informe import generar_informe


class DisenoCamisetasTests(unittest.TestCase):
    def test_dos_elecciones_en_un_solo_bloque(self):
        r = demostracion('ambos')
        html = generar_informe(r)['html']
        soup = BeautifulSoup(html,'html.parser')
        bloque = soup.find(id='bloque-camisetas')
        self.assertEqual(len(soup.select('#bloque-camisetas')),1)
        self.assertEqual(len(bloque.select('.tarjeta-camiseta')),2)
        self.assertIn('RECOMENDADA POR PARTIDO',bloque.get_text())
        self.assertIn('ELECCIÓN AL AZAR',bloque.get_text())
        self.assertIn('Partido:',bloque.get_text())

    def test_sin_partido_solo_azar_y_escapado(self):
        r = demostracion('camiseta')
        r['camiseta'].update(recomendada=None,partido_asociado=None)
        r['camiseta']['camiseta']['Equipo'] = '<script>equipo</script>'
        informe = generar_informe(r)
        soup = BeautifulSoup(informe['html'],'html.parser')
        bloque = soup.find(id='bloque-camisetas')
        self.assertEqual(len(bloque.select('.tarjeta-camiseta')),1)
        self.assertNotIn('RECOMENDADA POR PARTIDO',bloque.get_text())
        self.assertIn('ELECCIÓN AL AZAR',bloque.get_text())
        self.assertIsNone(soup.find('script'))
        self.assertIn('Camiseta al azar',informe['texto'])
