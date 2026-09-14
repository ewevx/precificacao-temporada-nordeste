import pandas as pd
import requests
import holidays
from datetime import datetime, timedelta

def criar_tabela_contexto():
    hoje = datetime.now()
    datas = [(hoje + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(15)]
    
    cidades = {
        "Porto de Galinhas": {"lat": -8.503, "lon": -35.004},
        "Maragogi": {"lat": -9.012, "lon": -35.222},
        "Pipa": {"lat": -6.228, "lon": -35.048},
        "Joao Pessoa": {"lat": -7.115, "lon": -34.863},
        "Natal": {"lat": -5.794, "lon": -35.211}
    }
    
    feriados_nacionais = holidays.Brazil(years=[hoje.year, hoje.year + 1])
    
    # IMPORTANTE: Crie uma conta gratuita em stormglass.io e cole sua chave aqui
    STORMGLASS_API_KEY = "eb62559e-ae21-11f1-8e3a-0242ac120004-eb625616-ae21-11f1-8e3a-0242ac120004" 
    
    dados_contexto = []
    print("Extraindo Temperatura, Chuva e Tábua de Marés...")
    
    for cidade, coords in cidades.items():
        print(f"Buscando dados para {cidade}...")
        
        # 1. CLIMA (Precipitação e Temperatura Máxima) - Open-Meteo
        url_clima = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&daily=precipitation_sum,temperature_2m_max&start_date={datas[0]}&end_date={datas[-1]}&timezone=America/Sao_Paulo"
        resp_clima = requests.get(url_clima).json().get('daily', {})
        
        chuvas = resp_clima.get('precipitation_sum', [0]*60)
        temps_max = resp_clima.get('temperature_2m_max', [0]*60)
        
        # 2. MARÉS - Stormglass
        mares_ideais = {data: 0 for data in datas}
        
        if STORMGLASS_API_KEY != "COLE_SUA_CHAVE_AQUI":
            url_mare = f"https://api.stormglass.io/v2/tide/extremes/point?lat={coords['lat']}&lng={coords['lon']}&start={datas[0]}&end={datas[-1]}"
            resp_mare = requests.get(url_mare, headers={'Authorization': STORMGLASS_API_KEY})
            
            if resp_mare.status_code == 200:
                for extremo in resp_mare.json().get('data', []):
                    # Filtra apenas marés baixas menores ou iguais a 0.5 metros
                    if extremo['type'] == 'low' and extremo['height'] <= 0.5:
                        dia = extremo['time'][:10]
                        mares_ideais[dia] = 1

        for i, data_str in enumerate(datas):
            dados_contexto.append({
                'data': data_str,
                'cidade': cidade,
                'eh_feriado': 1 if data_str in feriados_nacionais else 0,
                'temperatura_max': temps_max[i] if temps_max[i] is not None else 0,
                'precipitacao_mm': chuvas[i] if chuvas[i] is not None else 0,
                'dia_chuvoso': 1 if (chuvas[i] or 0) > 10.0 else 0,
                'mare_ideal_piscinas': mares_ideais.get(data_str, 0)
            })

    df_contexto = pd.DataFrame(dados_contexto)
    df_contexto.to_csv('../data/raw/contexto_clima_feriados.csv', index=False)
    print("Enriquecimento concluído! Tabela salva com Temperatura e Marés reais.")

if __name__ == "__main__":
    criar_tabela_contexto()