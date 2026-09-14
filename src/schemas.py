from pydantic import BaseModel, Field
from typing import Literal

class ImovelInput(BaseModel):
    cidade: Literal[
        "Porto de Galinhas", 
        "Maragogi", 
        "Pipa", 
        "Joao Pessoa", 
        "Natal"
    ] = Field(..., description="Destino turístico do imóvel")

    tipo_imovel: Literal["Flat", "Pousada", "Resort", "Outro"] = Field(
        ..., description="Classificação da propriedade"
    )

    qtd_quartos: int = Field(..., ge=1, le=10, description="Quantidade de quartos")
    distancia_m: float = Field(..., ge=0.0, description="Distância da praia em metros")
    temperatura_max: float = Field(..., ge=15.0, le=45.0, description="Temperatura máxima em °C")
    precipitacao_mm: float = Field(..., ge=0.0, description="Precipitação em mm")
    dias_para_feriado: float = Field(default=999.0, ge=0.0, description="Dias restantes até o próximo feriado")
    tem_piscina: int = Field(..., ge=0, le=1, description="1 para Sim, 0 para Não")
    eh_fim_de_semana: int = Field(..., ge=0, le=1, description="1 para Sim, 0 para Não")
    dia_chuvoso: int = Field(..., ge=0, le=1, description="1 para Sim, 0 para Não")
    mare_ideal_piscinas: int = Field(..., ge=0, le=1, description="1 para Sim, 0 para Não")

    model_config = {
        "json_schema_extra": {
            "example": {
                "cidade": "Porto de Galinhas",
                "tipo_imovel": "Flat",
                "qtd_quartos": 1,
                "distancia_m": 150.0,
                "temperatura_max": 28.5,
                "precipitacao_mm": 2.0,
                "dias_para_feriado": 999.0,
                "tem_piscina": 1,
                "eh_fim_de_semana": 1,
                "dia_chuvoso": 0,
                "mare_ideal_piscinas": 1
            }
        }
    }

class PrevisaoOutput(BaseModel):
    diaria_estimada: float = Field(..., description="Valor calculado da diária em reais")
    moeda: str = Field(default="BRL", description="Moeda corrente")
    cidade: str = Field(..., description="Destino consultado")
    tipo_imovel: str = Field(..., description="Tipo do imóvel consultado")