import os
import datetime
import requests
import streamlit as st

# 1. Configuração da Página
st.set_page_config(
    page_title="Dynamic Pricing Engine | Vacation Rentals",
    page_icon="🏢",
    layout="wide"
)

# Resolução de endpoint (Produção vs Local)
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/predict")

# 2. Estilização CSS Minimalista - Paleta Verde Sofisticada
st.markdown("""
<style>
    /* Tipografia e espaçamentos globais */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    h1, h2, h3 {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 600;
        letter-spacing: -0.02em;
    }
    
    /* Destaque do Título em Verde Nobre */
    h1 {
        color: #059669 !important;
    }
    
    /* Destaque da Diária com Verde Esmeralda Vibrante */
    [data-testid="stMetricValue"] {
        font-size: 2.3rem !important;
        font-weight: 700;
        color: #10b981 !important;
    }
    
    /* Rótulo da métrica */
    [data-testid="stMetricLabel"] {
        font-size: 0.95rem !important;
        color: #6ee7b7 !important;
    }
    
    /* Indicador delta da métrica em tom suave */
    [data-testid="stMetricDelta"] {
        font-weight: 500;
        color: #34d399 !important;
    }

    /* Borda sutil verde nos cards de resumo */
    div[data-testid="stExpander"] {
        border-color: rgba(16, 185, 129, 0.2) !important;
    }

    /* Divisores elegantes com gradiente esmeralda */
    hr {
        margin: 1.5rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, rgba(16,185,129,0.4) 0%, rgba(16,185,129,0.05) 100%);
    }
</style>
""", unsafe_allow_html=True)

# 3. Cabeçalho Institucional
st.title("Precificação Dinâmica de Imóveis por Temporada")
st.caption("Motor preditivo para estimativa de receita e ajuste ótimo de diárias baseado em localização, características estruturais e sensibilidade climática.")
st.divider()

# 4. Painel de Controle e Parâmetros
col_controles, col_resultado = st.columns([1.1, 1], gap="large")

with col_controles:
    st.markdown("##### Especificações do Ativo")
    
    col_cidade, col_tipo = st.columns(2)
    with col_cidade:
        cidade = st.selectbox(
            "Destino",
            options=["Porto de Galinhas", "Maragogi", "Pipa", "Joao Pessoa", "Natal"],
            index=0
        )
    with col_tipo:
        tipo_imovel = st.selectbox(
            "Tipologia",
            options=["Flat", "Pousada", "Resort", "Outro"],
            index=0
        )
        
    col_quartos, col_dist = st.columns(2)
    with col_quartos:
        qtd_quartos = st.number_input(
            "Quartos",
            min_value=1,
            max_value=10,
            value=1,
            step=1
        )
    with col_dist:
        distancia_m = st.slider(
            "Distância da Orla (metros)",
            min_value=0,
            max_value=3000,
            value=150,
            step=25
        )

    tem_piscina = st.checkbox("Infraestrutura de piscina ativa", value=True)

    st.divider()
    st.markdown("##### Período e Dinâmica Exógena")
    
    data_reserva = st.date_input(
        "Data de Check-in",
        value=datetime.date.today(),
        min_value=datetime.date.today()
    )

    with st.expander("Parâmetros Oceanográficos e Meteorológicos"):
        temperatura_max = st.slider("Temperatura Máxima Prevista (°C)", 20.0, 40.0, 28.5, 0.5)
        precipitacao_mm = st.slider("Precipitação Prevista (mm)", 0.0, 50.0, 2.0, 0.5)
        mare_ideal = st.checkbox("Janela de Maré Baixa Adequada", value=True)

# 5. Engenharia de Atributos e Serialização
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

# 6. Painel de Resultados e Validação de Negócio
with col_resultado:
    st.markdown("##### Recomendação de Tarifa")
    
    try:
        response = requests.post(API_URL, json=payload, timeout=15)
        
        if response.status_code == 200:
            resultado = response.json()
            diaria = resultado["diaria_estimada"]
            
            st.metric(
                label="Diária Sugerida (Target)",
                value=f"R$ {diaria:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                delta="Modelo calibrado em produção"
            )
            
            # Quadro de decomposição dos drivers do imóvel
            st.markdown("""
            **Resumo do Cenário Avaliado**
            """)
            st.markdown(f"""
            * **Localização:** {cidade} ({distancia_m}m do mar)
            * **Padrão:** {tipo_imovel} | {qtd_quartos} dormitório(s)
            * **Sazonalidade:** {"Fim de semana" if eh_fim_de_semana else "Dia de semana comercial"}
            * **Condição Marítima:** {"Favorável" if mare_ideal else "Padrão regular"}
            """)
            
        else:
            st.error(f"Instabilidade no serviço de inferência (Código {response.status_code})")
            if response.status_code in [502, 503, 504]:
                st.info("O nó de computação está sendo inicializado. Aguarde alguns segundos para nova leitura.")
            else:
                try:
                    st.json(response.json())
                except Exception:
                    st.code(response.text[:400])
                    
    except requests.exceptions.ReadTimeout:
        st.warning("O tempo limite de resposta foi excedido. Tente atualizar os parâmetros.")
    except requests.exceptions.ConnectionError:
        st.warning("Serviço backend indisponível no endereço configurado.")

    with st.expander("Inspecionar Payload de Entrada (JSON)"):
        st.json(payload)