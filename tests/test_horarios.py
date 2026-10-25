import unittest
from datetime import date, datetime
from unittest.mock import patch

from resumen.config import MADRID_TZ
from resumen.eventos import build_daily_plan, can_add_event, recomendar_eventos
from resumen.horarios import preparar_horario
from resumen.fuente_eventos import extraer_jornada, generar_resultado_eventos
from resumen.informe import linea_evento

def evento(hora, deporte='Fútbol', comp='Champions League', **extra):
    return {'hora':hora,'deporte':deporte,'competicion':comp,'local':'Arsenal',
            'visitante':'Chelsea','canales':['Movistar+'], **extra}

def tabla(fecha, horas):
    rows=''.join(f'<tr><td class="hora">{hora}</td><td class="detalles"><img title="Baloncesto">NBA</td><td class="local">Celtics</td><td class="visitante">Warriors</td><td class="canales"><li>DAZN</li></td></tr>' for hora in horas)
    return f'<table class="tablaPrincipal"><tr class="cabeceraTabla"><td>{fecha}</td></tr>{rows}</table>'

class HorariosTests(unittest.TestCase):
    def test_inicio_de_jornada_y_medianoche_laborable(self):
        dia=date(2026,10,26)
        for hora, esperado in [('06:29',False),('06:30',True),('23:30',True),('23:31',False),('00:30',False)]:
            with self.subTest(hora=hora):
                e=evento(hora)
                self.assertEqual(preparar_horario(e,dia),esperado)
        e=evento('23:30')
        preparar_horario(e,dia)
        self.assertTrue(e['vision_parcial'])
        self.assertEqual(e['fin_vision'].strftime('%d/%m %H:%M'),'27/10 00:00')

    def test_noches_viernes_sabado_hasta_la_una(self):
        for dia,siguiente in [(date(2026,10,23),'2026-10-24'),(date(2026,10,24),'2026-10-25')]:
            e=evento('00:30',deporte='Baloncesto',comp='NBA',fecha=siguiente)
            self.assertTrue(preparar_horario(e,dia))
            self.assertTrue(e['vision_parcial'])
            self.assertTrue(e['madrugada'])
            self.assertEqual(e['fin_vision'].strftime('%H:%M'),'01:00')
            self.assertFalse(preparar_horario(evento('00:31',fecha=siguiente),dia))
            self.assertFalse(preparar_horario(evento('01:00',fecha=siguiente),dia))
        self.assertFalse(preparar_horario(evento('00:30',fecha='2026-10-26'),date(2026,10,25)))

    def test_lanzamiento_manual_elimina_terminados_e_indica_en_curso(self):
        now=datetime(2026,10,26,19,0,tzinfo=MADRID_TZ)
        result=recomendar_eventos([evento('15:00'),evento('18:00'),evento('20:00')],ahora=now)
        self.assertEqual([e['hora'] for e in result['filtrados']],['18:00','20:00'])
        self.assertTrue(result['filtrados'][0]['en_curso'])
        self.assertIn('En curso',linea_evento(result['filtrados'][0]))
        # A las 00:10 del sábado todavía se puede ver una parte del evento de las 00:00.
        midnight=datetime(2026,10,24,0,10,tzinfo=MADRID_TZ)
        self.assertTrue(preparar_horario(evento('00:00'),midnight.date(),midnight))

    def test_evento_alto_no_pierde_por_llegar_mas_tarde(self):
        items=[{**evento(h,local=name),'score':score} for h,name,score in
               [('10:00','Temprano',7),('10:30','Mejor',12),('21:00','Top',15)]]
        _,selected=build_daily_plan(items)
        self.assertEqual([e['local'] for e in selected],['Mejor','Top'])

    def test_duraciones_por_deporte_y_solapes(self):
        dia=date(2026,10,26)
        nba=evento('18:00','Baloncesto','NBA')
        futbol=evento('20:00')
        tenis=evento('18:00','Tenis','ATP 500')
        motor=evento('18:00','Automovilismo','Fórmula 1')
        for e in (nba,futbol,tenis,motor):self.assertTrue(preparar_horario(e,dia))
        self.assertEqual([e['duracion_estimada'] for e in (nba,futbol,tenis,motor)],[150,120,150,180])
        self.assertTrue(can_add_event(futbol,[nba])) # 30 minutos permitidos.
        self.assertFalse(can_add_event(futbol,[motor])) # 60 minutos, se rechaza.

    def test_orden_cronologico_con_cambio_de_fecha_y_sin_duplicar(self):
        now=datetime(2026,10,24,8,30,tzinfo=MADRID_TZ)
        es=[evento('23:00',local='Noche'),evento('00:00','Baloncesto','NBA',local='Celtics',visitante='Warriors',fecha='2026-10-25')]
        result=recomendar_eventos(es,ahora=now)
        self.assertEqual([e['fecha'] for e in result['filtrados']],['2026-10-24','2026-10-25'])
        text=linea_evento(result['filtrados'][1])
        self.assertIn('25/10 00:00',text)
        self.assertIn('hasta 01:00',text)

    def test_lee_tabla_siguiente_solo_cuando_corresponde(self):
        html=tabla('24/10/2026',['18:00'])+tabla('25/10/2026',['00:00','00:30','02:00'])
        es,avisos=extraer_jornada(html,date(2026,10,24))
        self.assertFalse(avisos)
        self.assertEqual([(e['fecha'],e['hora']) for e in es],[('2026-10-24','18:00'),('2026-10-25','00:00'),('2026-10-25','00:30')])
        _,avisos=extraer_jornada(tabla('24/10/2026',['18:00']),date(2026,10,24))
        self.assertTrue(avisos)
        es,avisos=extraer_jornada(tabla('26/10/2026',['18:00']),date(2026,10,26))
        self.assertEqual(len(es),1)
        self.assertFalse(avisos)

    @patch('resumen.fuente_eventos.descargar_html')
    def test_integracion_fuente_con_fecha_y_hora(self,descarga):
        descarga.return_value=tabla('24/10/2026',['12:00','23:00'])+tabla('25/10/2026',['00:00'])
        result=generar_resultado_eventos(datetime(2026,10,24,20,tzinfo=MADRID_TZ))
        self.assertEqual([e['hora'] for e in result['filtrados']],['23:00','00:00'])
        self.assertFalse(result['avisos'])

if __name__ == '__main__':
    unittest.main()
