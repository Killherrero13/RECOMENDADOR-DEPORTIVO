"""Calidad conjunta: complemento mínimo, nunca suma de señales equivalentes."""


def valorar_cruce(evento, contexto, cartel):
    resultado = {'ajuste': 0.0, 'objetivo': 0.0, 'motivos': []}
    if contexto.get('estado') != 'validado':
        return resultado
    datos = evento['contexto']
    objetivo = 0.0
    motivo = ''
    if datos.get('tipo') == 'tenis':
        mejor, peor = sorted(datos[k]['ranking'] for k in ('local', 'visitante'))
        # Cuenta el nivel de ambos. Un top-10 frente al 150 no activa el cruce.
        objetivo = (2.8 if peor <= 10 else 2.5 if peor <= 20 else
                    2.2 if mejor <= 10 and peor <= 30 else 1.8 if peor <= 30 else 0)
        motivo = f'Calidad conjunta: ranking ATP {mejor} y {peor}; se valora a ambos jugadores'
    elif evento['deporte'] == 'Baloncesto' and datos.get('competicion') == 'euro':
        posiciones = [datos[k]['posicion'] for k in ('local', 'visitante')]
        objetivo = 2.0 if max(posiciones) <= 5 else 1.2 if max(posiciones) <= 8 else 0
        motivo = 'Calidad conjunta: ambos equipos en la zona alta de la Euroliga'
    # Catálogo y contexto ya pueden reconocer el mismo atractivo: solo completar.
    ajuste = round(max(0.0, objetivo - cartel - contexto['ajuste']), 2)
    return {'ajuste': ajuste, 'objetivo': objetivo,
            'motivos': [motivo] if ajuste else []}
