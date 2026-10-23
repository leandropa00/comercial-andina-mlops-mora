"""API FastAPI de apoyo preventivo; nunca para decisión automática de crédito."""
from functools import lru_cache
from pathlib import Path
import os
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title='Comercial Andina — Demo de riesgo de mora', version='1.0',description='Datos sintéticos; uso académico. Revisión humana obligatoria.')

class ClienteCredito(BaseModel):
    model_config = ConfigDict(extra='forbid')
    edad: int = Field(ge=18,le=100)
    ingreso_mensual_millones: float = Field(gt=0)
    cupo_aprobado_millones: float = Field(gt=0)
    uso_cupo_pct: float = Field(ge=0,le=100)
    meses_como_cliente: int = Field(ge=0)
    pagos_atrasados_previos: int = Field(ge=0)
    compras_credito_6m: int = Field(ge=0)

@lru_cache(maxsize=1)
def cargar_modelo():
    archivo=Path(os.getenv('MODEL_PATH',str(Path(__file__).resolve().parent/'modelos'/'modelo.joblib')))
    if not archivo.exists():
        raise FileNotFoundError(f'No existe un modelo aprobado: {archivo}')
    return joblib.load(archivo)

@app.get('/salud')
def salud():
    try:
        modelo=cargar_modelo()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503,detail=str(e)) from e
    return {'estado':'ok','modelo':modelo['modelo']}

@app.post('/predecir')
def predecir(cliente:ClienteCredito):
    try:
        a=cargar_modelo()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503,detail=str(e)) from e
    df=pd.DataFrame([cliente.model_dump()])[a['variables']]
    p=float(a['pipeline'].predict_proba(df)[0][1])
    return {'mora':int(p>=0.5),'probabilidad_mora':round(p,4),'modelo':a['modelo'],
            'advertencia':'Datos sintéticos; apoyo académico, no usar para decisiones crediticias reales.'}

@app.get('/')
def inicio():
    return {'servicio':'riesgo-mora-academico','documentacion':'/docs','salud':'/salud'}
