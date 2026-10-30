"""Regresión de jornadas completas; entradas públicas fechadas, sin red ni correo."""
import copy
import json
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from resumen.eventos import recomendar_eventos, evaluar_evento
from resumen.horarios import intervalo, orden_inicio
from resumen.diagnostico import preparar_diagnostico, reproducir
from resumen.config import MADRID_TZ
from resumen.puntuacion import umbral_plan


class CalibracionJornadasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jornadas=[]
        for dia in ('2026-10-27','2026-10-28'):
            entrada=json.loads((Path(__file__).parent/'fixtures'/f'calibracion_{dia}.json').read_text(encoding='utf-8'))
            corte=datetime.fromisoformat(entrada['corte'])
            with patch('requests.get',side_effect=AssertionError('La calibración no consulta fuentes')):
                resultado=recomendar_eventos(copy.deepcopy(entrada['eventos']),ahora=corte)
            cls.jornadas.append((entrada,corte,resultado))

    def test_conserva_los_87_eventos_de_control(self):
        self.assertEqual([len(r['filtrados']) for _,_,r in self.jornadas],[32,55])
        for entrada,_,r in self.jornadas:
            self.assertEqual(len(entrada['eventos']),len(r['filtrados']))

    def test_controles_no_se_inflan(self):
        controles={('T. Fritz','R. Hijikata'):4.5,('Parma','Udinese'):5.5,
                   ('Calamocha','CE Europa'):4.7}
        observados={}
        for _,_,r in self.jornadas:
            for e in r['filtrados']:
                pareja=e['local'],e['visitante']
                if pareja in controles: observados[pareja]=e['score']
        self.assertEqual(observados,controles)

    def test_plan_y_alternativas_respetan_encaje(self):
        for _,_,r in self.jornadas:
            seleccion=r['seleccionados']
            self.assertLessEqual(len(seleccion),4)
            for i,e in enumerate(seleccion):
                self.assertGreaterEqual(e['score'],umbral_plan(e))
                a,b=intervalo(e)
                self.assertGreaterEqual(b-a,30)
                for otro in seleccion[i+1:]:
                    c,d=intervalo(otro)
                    self.assertLessEqual(min(b,d)-max(a,c),30)
            self.assertEqual(r['alternativas'],sorted(r['alternativas'],key=orden_inicio))

    def test_planning_flexible_sin_bloques_que_se_pisen(self):
        for _,_,r in self.jornadas:
            bloques=sorted(r.get('planning',[]),key=lambda b:b['inicio'])
            anterior=None
            for b in bloques:
                minutos=lambda t:int(t[:2])*60+int(t[3:])
                duracion=(minutos(b['hasta'])-minutos(b['desde']))%1440
                self.assertGreater(duracion,0)
                if anterior is not None: self.assertGreaterEqual(b['inicio'],anterior)
                anterior=b['inicio']+duracion

    def test_nota_no_depende_de_canales_o_vision_parcial(self):
        for entrada,_,_ in self.jornadas:
            for e in entrada['eventos']:
                a=evaluar_evento(e)['score']
                b=evaluar_evento({**e,'canales':['DAZN'],'vision_parcial':True,'madrugada':True})['score']
                self.assertEqual(a,b)
                self.assertTrue(0<=a<=10)

    def test_datos_utilizados_anteriores_al_corte_y_al_evento(self):
        for _,corte,r in self.jornadas:
            for e in r['filtrados']:
                if e['evaluacion_contexto']['estado']!='validado': continue
                c=e['contexto'];consulta=datetime.fromisoformat(c['consultado'])
                self.assertLessEqual(consulta,corte)
                self.assertLessEqual(consulta,e['inicio'])
                for k in ('local','visitante'):
                    if c[k].get('ultimo_partido'):
                        ultimo=datetime.fromisoformat(c[k]['ultimo_partido'])
                        self.assertLessEqual(ultimo+timedelta(hours=3),consulta)

    def test_instantaneas_reproducibles_sin_red(self):
        for _,corte,r in self.jornadas:
            s=preparar_diagnostico(r,corte)
            with patch('requests.get',side_effect=AssertionError('No debe consultar')):
                replay=reproducir(s)
            self.assertEqual([e['score'] for e in r['filtrados']],[e['score'] for e in replay['filtrados']])
            firmas=lambda plan:{k:(e['fecha'],e['hora'],e['local'],e['visitante'],e['score']) for k,e in plan.items()}
            self.assertEqual(firmas(r['plan']),firmas(replay['plan']))
            self.assertEqual(r.get('planning'),replay.get('planning'))

    def test_contexto_posterior_no_modifica_la_base(self):
        for entrada,_,_ in self.jornadas:
            for e in entrada['eventos']:
                if not e.get('contexto'): continue
                otro=copy.deepcopy(e)
                inicio=datetime.fromisoformat(f"{e['fecha']}T{e['hora']}").replace(tzinfo=MADRID_TZ)
                otro['contexto']['consultado']=(inicio+timedelta(minutes=1)).isoformat()
                sin_contexto={k:v for k,v in e.items() if k!='contexto'}
                self.assertEqual(evaluar_evento(otro)['score'],evaluar_evento(sin_contexto)['score'])
