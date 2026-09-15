# Motor de Precificacao Dinamica para Imoveis de Temporada

Solucao preditiva ponta a ponta voltada a otimizacao de receita (RevPAR) para alugueis de temporada no litoral nordestino, combinando atributos imobiliarios, sazonalidade, dados meteorologicos e dinamicas oceanograficas.

---

## Acesso Rapido a Aplicacao em Producao

* Aplicacao Interativa (Streamlit Cloud): https://precificacao-temporada-nordeste-4p5nzuiqcl3psvel3uzyrs.streamlit.app/
* Documentacao Interativa da API (FastAPI / Swagger): https://precificacao-temporada-nordeste.onrender.com/docs

A infraestrutura conta com monitoramento automatizado a cada 10 minutos via UptimeRobot no endpoint /health, eliminando a latencia de partida a frio (cold start) e garantindo inferencia em tempo real com resposta inferior a 200 ms.

---

## 1. Contexto e Problema de Negocio

No mercado de hospedagem por temporada, a fixacao estatica de diarias gera duas ineficiencias estruturais:
* Subprecificacao em picos de demanda: Perda de margem em periodos de alta atratividade (marés baixas para piscinas naturais, tempo ensolarado e fins de semana).
* Sobreprecificacao em periodos de baixa demanda: Queda de ocupacao em cenarios de chuva ou periodos uteis sem apelo turistico.

Objetivo: Recomendar a tarifa diaria ideal para anfitrioes de flats e pousadas, equilibrando ocupacao e maximizacao de receita media por acomodacao disponivel.

---

## 2. Arquitetura da Solucao

O sistema adota uma arquitetura desacoplada de microsservicos:

1. Camada de Apresentacao (Streamlit Community Cloud): Interface visual para simulacao de cenarios, selecao de comodidades, datas e parametros climaticos.
2. Camada de Servico (FastAPI no Render): Recebe as requisicoes HTTP, valida os tipos de dados via schemas Pydantic e aciona o modelo em threadpool dedicada.
3. Pipeline de Machine Learning (Scikit-Learn): Estimador serializado carregado em memoria na inicializacao (lifespan), garantindo pre-processamento e inferencia imediatos.

---

## 3. Parametros e Engenharia de Atributos

A precificacao considera:
* Estrutura do Imovel: Municipio, tipologia (Flat, Pousada, Resort), numero de quartos, distancia em metros ate a praia e presenca de piscina.
* Calendario: Identificacao automatica de fins de semana e proximidade de feriados.
* Condicoes Exogenas: Temperatura maxima, indice pluviometrico (dia chuvoso) e maré favoravel para piscinas naturais.

---

## 4. Estrutura do Repositorio

├── models/
│   └── pipeline_precificacao_dinamica.pkl
├── src/
│   ├── api.py
│   ├── app.py
│   └── schemas.py
├── .gitignore
├── README.md
└── requirements.txt


---

## 5. Contrato da API

### POST /predict
Recebe os parametros operacionais e retorna a tarifa estimada.

Exemplo de Entrada:
json
{
  "cidade": "Porto de Galinhas",
  "tipo_imovel": "Flat",
  "qtd_quartos": 1,
  "distancia_m": 150,
  "temperatura_max": 28.5,
  "precipitacao_mm": 2.0,
  "dias_para_feriado": 999.0,
  "tem_piscina": 1,
  "eh_fim_de_semana": 1,
  "dia_chuvoso": 0,
  "mare_ideal_piscinas": 1
}
Exemplo de Retorno (200 OK):

JSON
{
  "diaria_estimada": 1404.55,
  "moeda": "BRL",
  "cidade": "Porto de Galinhas",
  "tipo_imovel": "Flat"
}

--- 

## 6. Reproducao Local
Clone o repositorio:

Bash
git clone [https://github.com/SEU_USUARIO/precificacao-temporada-nordeste.git](https://github.com/SEU_USUARIO/precificacao-temporada-nordeste.git)
cd precificacao-temporada-nordeste
Crie e ative o ambiente virtual:

Bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
Instale as dependencias:

Bash
pip install -r requirements.txt
Execute o servidor de inferencia:

Bash
uvicorn api:app --app-dir src --reload
Em outro terminal, execute o painel:

Bash
streamlit run src/app.py