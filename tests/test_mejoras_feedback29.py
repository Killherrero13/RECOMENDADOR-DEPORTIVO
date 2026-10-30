import copy
import unittest
from datetime import datetime
from unittest.mock import patch

from resumen.config import MADRID_TZ
from resumen.eventos import evaluar_evento, knockout_bonus, recomendar_eventos
from resumen.contexto import valorar_contexto
from resumen.contexto_fuentes import contextos_tenis, alias_futbol
from resumen.rivalidades import valorar_rivalidad
from resumen.diagnostico import preparar_diagnostico


def tenis(a='B. Shelton',b='J. Kym'):
    return dict(local=a,visitante=b,deporte='Tenis',competicion='Torneo de Basilea 2ª Ronda',
                fecha='2026-10-29',hora='19:30',canales=[])


def contexto(e,local=4,visitante=None):
    e['contexto']=dict(tipo='tenis',competicion='atp',temporada=2026,
        consultado='2026-10-29T08:00:00+01:00',publicado='2026-10-22T07:00:00+00:00',
        fuentes=['https://example.org/atp'],local=dict(nombre=e['local'],id='1',ranking=local))
    if visitante is not None:e['contexto']['visitante']=dict(nombre=e['visitante'],id='2',ranking=visitante)
    return e


class Feedback29Tests(unittest.TestCase):
    def test_parcial_conserva_nivel_sin_inventar_cruce(self):
        e=contexto(tenis());r=evaluar_evento(e)
        self.assertEqual(r['evaluacion_contexto']['estado'],'parcial')
        self.assertEqual(r['desglose']['calidad_cruce'],0)
        self.assertEqual(r['desglose']['jerarquia_atp'],.7)
        self.assertAlmostEqual(r['score'],5.8)
        self.assertAlmostEqual(r['desglose']['deportivo'],6.2)
        s=preparar_diagnostico({'filtrados':[{**e,**r}]},datetime(2026,10,29,8,tzinfo=MADRID_TZ))
        self.assertEqual(s['cobertura']['parciales'],1)

    @patch('resumen.contexto_fuentes.descargar_json')
    def test_alias_struff_y_rival_ausente_no_borran_datos(self,descarga):
        ranks=[dict(current=i,athlete=dict(id=str(i),displayName=f'Jugador {i}',shortname=f'J. {i}')) for i in range(1,151)]
        ranks[3]['athlete'].update(displayName='Ben Shelton',shortname='B. Shelton')
        ranks[46]['athlete'].update(displayName='Jan-Lennard Struff',shortname='J. Struff')
        descarga.return_value={'rankings':[dict(type='atp',update='2026-10-22T07:00Z',ranks=ranks)]}
        a=tenis();b=tenis('JL. Struff','Jugador 10')
        self.assertEqual(contextos_tenis([a,b],datetime(2026,10,29,8,tzinfo=MADRID_TZ)),1)
        self.assertNotIn('visitante',a['contexto'])
        self.assertEqual(a['diagnostico_contexto']['estado'],'parcial')
        self.assertEqual(b['contexto']['local']['ranking'],47)

    def test_segunda_ronda_solo_en_edicion_y_cuadro_confirmados(self):
        e=tenis()
        self.assertEqual(knockout_bonus(e),1)
        for cambios in [dict(fecha='2027-10-29'),dict(competicion='ATP 500 desconocido 2ª Ronda'),
                        dict(competicion='Torneo de Basilea Dobles 2ª Ronda'),dict(deporte='Fútbol')]:
            self.assertEqual(knockout_bonus({**e,**cambios}),0)

    def test_perfiles_nuevos_no_reciben_bonus_automatico_de_dos_referentes(self):
        e=tenis('T. Fritz','D. Shapovalov');r=evaluar_evento(e)
        self.assertEqual(r['desglose']['cartel'],1)
        self.assertNotIn('rival sin perfil',' '.join(r['motivos']))

    def test_ranking_individual_y_conjunto_no_se_suman_dos_veces(self):
        e=contexto(tenis('L. Tien','A. De Miñaur'),18,10)
        r=evaluar_evento(e)
        self.assertEqual(r['evaluacion_contexto']['ajuste'],0)
        self.assertAlmostEqual(r['desglose']['cartel']+r['desglose']['calidad_cruce'],2.5)

    def test_fuera_de_corte_no_activa_jerarquia(self):
        e=contexto(tenis());e['contexto']['consultado']='2026-10-29T23:00:00+01:00'
        self.assertEqual(evaluar_evento(e)['desglose']['jerarquia_atp'],0)

    def test_alias_copa_y_liga_son_exactos(self):
        for a,b in [('US Lecce','Lecce'),('CD Cieza','Cieza'),('CD Castellón','Castellón'),
                    ('Ribadesella CF','Ribadesella'),('Auriense Cented','Auriense Cented Academy')]:
            self.assertEqual(alias_futbol(a),alias_futbol(b))
        self.assertNotEqual(alias_futbol('CD Cieza B'),alias_futbol('Cieza'))

    def test_xerez_id_confirmado_no_depende_de_la_fecha_del_alias(self):
        e=dict(local='Xerez',visitante='Cádiz CF',deporte='Fútbol',competicion='Copa del Rey 1ª Ronda',
               fecha='2026-10-29',hora='21:00')
        e['contexto']=dict(tipo='copa',competicion='esp.copa_del_rey',temporada=2026,
                          consultado='2026-10-29T08:00:00+01:00',local=dict(nombre='Xerez',id='3835'),
                          visitante=dict(nombre='Cádiz CF',id='3842'),
                          copa=dict(partido_unico=True,contraste_primera=False,fuentes=['https://example.org/copa']))
        self.assertEqual(valorar_rivalidad(e)['ajuste'],.6)
        otro=copy.deepcopy(e);otro['contexto']['local']['id']='otro'
        self.assertEqual(valorar_rivalidad(otro)['ajuste'],0)

    def test_mineiro_rivalidad_no_castiga_nota_por_horario(self):
        e=dict(local='Atlético Mineiro',visitante='Cruzeiro',deporte='Fútbol',competicion='Serie A Brasil',
               fecha='2026-10-29',hora='23:30',canales=[])
        a=evaluar_evento(e);b=evaluar_evento({**e,'vision_parcial':True})
        self.assertEqual(a['score'],b['score'])
        self.assertEqual(a['desglose']['rivalidad'],.6)
        self.assertEqual(round(a['prioridad']-b['prioridad'],1),.5)

    def test_tenistas_fuera_del_catalogo_se_consultan_antes_de_descartarse(self):
        e=tenis('Jugador nuevo A','Jugador nuevo B')
        ahora=datetime(2026,10,29,8,tzinfo=MADRID_TZ)
        self.assertFalse(recomendar_eventos([e],ahora=ahora)['filtrados'])
        self.assertEqual(len(recomendar_eventos([e],ahora=ahora,preseleccion_tenis=True)['filtrados']),1)
        contexto(e,18,27)
        self.assertEqual(len(recomendar_eventos([e],ahora=ahora)['filtrados']),1)
        e['contexto']['consultado']='2026-10-29T23:00:00+01:00'
        self.assertFalse(recomendar_eventos([e],ahora=ahora)['filtrados'])
