import copy
import hashlib
import json
import random
import unittest
from unittest.mock import Mock

from referencia import ROOT, cargar_camisetas, ejecutar_eventos

def leer(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))

class ReferenciaTests(unittest.TestCase):
    def test_copias_originales_integras(self):
        for name, expected in leer('referencia/sha256.json').items():
            self.assertEqual(hashlib.sha256((ROOT / 'referencia' / name).read_bytes()).hexdigest(), expected)

    def test_coleccion_completa_y_mismo_orden(self):
        original = cargar_camisetas()['camisetas']
        exported = leer('data/camisetas.json')
        self.assertEqual(len(exported), 64)
        self.assertEqual(exported, original)

    def test_seleccion_aleatoria_original_con_semilla(self):
        ns = cargar_camisetas()
        matches = [{'home': 'Ejemplo', 'away': 'Rival'}]
        ns['obtener_partidos_hoy'] = Mock(return_value=matches)
        ns['random'] = random.Random(42)
        expected = random.Random(42).choices(ns['camisetas'], k=1)[0]
        shirt, result = ns['seleccionar_camiseta']()
        self.assertEqual(shirt, expected)
        self.assertIs(result, matches)
        ns['obtener_partidos_hoy'].assert_called_once_with()

    def test_dia_completo_con_resultado_revisado(self):
        ns = ejecutar_eventos(leer('tests/fixtures/eventos.json'))
        actual = {
            'puntuaciones': [{'hora': e['hora'], 'local': e['local'],
                             'score': round(e['score'], 6), 'channel': e['channel']}
                            for e in ns['filtered_events']],
            'plan': {k: e['hora'] for k, e in ns['daily_plan'].items()},
            'seleccionados': [e['hora'] for e in ns['selected_events']],
            'alternativas': [e['hora'] for e in ns['other_top_events']],
        }
        self.assertEqual(actual, leer('tests/fixtures/resultado_esperado.json'))

    def test_sin_eventos_es_un_resultado_valido(self):
        ns = ejecutar_eventos([])
        self.assertEqual(ns['daily_plan'], {})
        self.assertEqual(ns['selected_events'], [])
        self.assertEqual(ns['other_top_events'], [])

    def test_limite_de_solapamiento(self):
        ns = ejecutar_eventos([])
        selected = [{'hora': '10:00'}]
        self.assertTrue(ns['can_add_event']({'hora': '11:30'}, selected))
        self.assertFalse(ns['can_add_event']({'hora': '11:29'}, selected))

    def test_comportamientos_existentes_documentados(self):
        ns = ejecutar_eventos([])
        self.assertEqual(ns['knockout_bonus']({'competicion': 'Semifinal'}), 2.5)
        self.assertFalse(ns['valid_time']('08:59'))
        self.assertTrue(ns['valid_time']('09:00'))
        self.assertTrue(ns['valid_time']('23:30'))
        self.assertFalse(ns['valid_time']('23:31'))
        self.assertFalse(ns['valid_time']('PD'))
        events = [{'hora': h, 'score': s, 'deporte': 'Fútbol'}
                  for h, s in [('15:00', 8), ('17:00', 9), ('21:00', 10)]]
        plan, selected = ns['build_daily_plan'](copy.deepcopy(events))
        self.assertEqual(len(selected), 3)
        self.assertEqual(plan['tarde']['hora'], '17:00')
        self.assertEqual(len(plan), 2)  # El evento de las 15:00 queda oculto.

if __name__ == '__main__':
    unittest.main()
