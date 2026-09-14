from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import pandas as pd
import joblib
import os

try:
    from src.schemas import ImovelInput, PrevisaoOutput
except ModuleNotFoundError:
    from schemas import ImovelInput, PrevisaoOutput

ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    caminho_modelo = os.path.join(os.path.dirname(__file__), '../models/pipeline_precificacao_dinamica.pkl')
    
    if not os.path.exists(caminho_modelo):
        caminho_modelo = 'models/pipeline_precificacao_dinamica.pkl'
        
    print(f"Carregando artefato de Machine Learning: {caminho_modelo}")
    ml_models["pipeline"] = joblib.load(caminho_modelo)
    print("Pipeline de precificação pronto para inferência!")
    
    yield
    
    ml_models.clear()
    print("Servidor finalizado e recursos liberados.")

app = FastAPI(
    title="API de Precificação Dinâmica - Temporada Nordeste",
    description="Serviço backend para precificação automatizada com base em clima, marés e infraestrutura.",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health", tags=["Status"])
async def health_check():
    modelo_carregado = "pipeline" in ml_models and ml_models["pipeline"] is not None
    return {"status": "online", "modelo_carregado": modelo_carregado}

@app.post("/predict", response_model=PrevisaoOutput, tags=["Predição"])
def prever_diaria(payload: ImovelInput):
    """
    Recebe os atributos do imóvel, executa o pipeline e devolve a diária estimada.
    Nota: Definido como síncrono (def) para rodar em threadpool sem travar o event-loop.
    """
    if "pipeline" not in ml_models or ml_models["pipeline"] is None:
        raise HTTPException(status_code=503, detail="Modelo preditivo não disponível na memória.")
    
    # Converte o payload validado para DataFrame
    dados_df = pd.DataFrame([payload.model_dump()])
    
    # Inferência com o pipeline Scikit-Learn
    predicao = ml_models["pipeline"].predict(dados_df)[0]
    
    return PrevisaoOutput(
        diaria_estimada=round(float(predicao), 2),
        moeda="BRL",
        cidade=payload.cidade,
        tipo_imovel=payload.tipo_imovel
    )