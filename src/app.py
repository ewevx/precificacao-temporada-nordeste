import streamlit as st
import datetime
import requests
import os

# 1. Configuração da Página
st.set_page_config(
    page_title="Simulador de Precificação Dinâmica | Temporada Nordeste",
    page_icon="🏖️",
    layout="wide"
)

# Pega a URL da nuvem se configurada; caso contrário, usa o localhost
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/predict")

# 2. Cabeçalho e Título
st.title("🏖️ Precificação Inteligente de Temporada")
st.markdown("""
Simule a diária ideal do seu imóvel no litoral nordestino com base em características estruturais, 
distância da praia, sazonalidade e condições climáticas/maregráficas.
""")
st.divider()

# 3. Estruturação dos Controles em Colunas
col_esq, col_dir = st.columns([1.2, 1], gap="large")

with col_esq:
    st.subheader("📍 Características do Imóvel")
    
    col_cidade, col_tipo = st.columns(2)
    with col_cidade:
        cidade = st.selectbox(
            "Destino / Cidade",
            options=["Porto de Galinhas", "Maragogi", "Pipa", "Joao Pessoa", "Natal"],
            index=0,
            help="Selecione o município litorâneo onde o flat está localizado."
        )
    with col_tipo:
        tipo_imovel = st.selectbox(
            "Classificação do Imóvel",
            options=["Flat", "Pousada", "Resort", "Outro"],
            index=0
        )
        
    col_quartos, col_dist = st.columns(2)
    with col_quartos:
        qtd_quartos = st.number_input(
            "Quantidade de Quartos",
            min_value=1,
            max_value=10,
            value=1,
            step=1
        )
    with col_dist:
        distancia_m = st.slider(
            "Distância da Praia (metros)",
            min_value=0,
            max_value=3000,
            value=150,
            step=25,
            help="0 metros indica imóvel pé na areia / beira-mar."
        )

    st.subheader("🏊 Comodidades e Conveniência")
    tem_piscina = st.checkbox("Possui Piscina Privativa ou Compartilhada", value=True)

    st.subheader("📅 Data da Reserva e Condições")
    data_reserva = st.date_input(
        "Data de Check-in",
        value=datetime.date.today(),
        min_value=datetime.date.today(),
        help="Usado para definir finais de semana e sazonalidade."
    )

    with st.expander("🌦️ Ajuste de Condições Meteorológicas e Maré (Opcional)"):
        temperatura_max = st.slider("Temperatura Máxima Prevista (°C)", 20.0, 40.0, 28.5, 0.5)
        precipitacao_mm = st.slider("Precipitação Prevista (mm de chuva)", 0.0, 50.0, 2.0, 0.5)
        mare_ideal = st.checkbox("Maré Baixa no Dia (<= 0.5m - Piscinas Naturais)", value=True)

# 4. Engenharia de Variáveis para Envio à API
eh_fim_de_semana = 1 if data_reserva.weekday() in [4, 5, 6] else 0
dia_chuvoso = 1 if precipitacao_mm > 10.0 else 0

payload = {
    "cidade": cidade,
    "tipo_imovel": tipo_imovel,
    "qtd_quartos": int(qtd_quartos),
    "distancia_m": float(distancia_m),
    "temperatura_max": float(temperatura_max),
    "precipitacao_mm": float(precipitacao_mm),
    "dias_para_feriado": 999.0,
    "tem_piscina": 1 if tem_piscina else 0,
    "eh_fim_de_semana": eh_fim_de_semana,
    "dia_chuvoso": dia_chuvoso,
    "mare_ideal_piscinas": 1 if mare_ideal else 0
}

# 5. Comunicação com a API e Exibição do Resultado
with col_dir:
    st.subheader("💡 Estimativa de Diária")
    
    try:
        # Timeout estendido para evitar falha no primeiro carregamento
        response = requests.post(API_URL, json=payload, timeout=15)
        
        if response.status_code == 200:
            resultado = response.json()
            diaria = resultado["diaria_estimada"]
            
            st.metric(
                label="Diária Sugerida pelo Modelo",
                value=f"R$ {diaria:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                delta="Simulação Ativa em Tempo Real"
            )
            st.success("Cálculo realizado via FastAPI + Machine Learning Pipeline!")
            
        else:
            st.error(f"Erro na validação da API (Código {response.status_code})")
            st.write(response.json())
            
    except requests.exceptions.ReadTimeout:
        st.warning("⏱️ A API demorou para responder. Tente alterar o seletor novamente.")
    except requests.exceptions.ConnectionError:
        st.warning("⚠️ O servidor backend FastAPI não está acessível na porta 8000.")
        st.info("Certifique-se de que o comando `uvicorn api:app --reload` está rodando em outro terminal.")

    st.caption("Payload enviado à API:")
    st.json(payload)