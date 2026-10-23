"""Compara todas las variables numéricas mediante Kolmogorov-Smirnov."""
import argparse
import json
from pathlib import Path
import pandas as pd
from scipy.stats import ks_2samp
from validar_datos import VARIABLES

def comparar(referencia,reciente,alfa=0.01):
    base=pd.read_csv(referencia)
    nueva=pd.read_csv(reciente)
    salida=[]
    for nombre in VARIABLES:
        if nombre not in base or nombre not in nueva:
            raise ValueError(f'Columna ausente: {nombre}')
        x=pd.to_numeric(base[nombre],errors='coerce').dropna()
        y=pd.to_numeric(nueva[nombre],errors='coerce').dropna()
        if len(x)<20 or len(y)<20:
            raise ValueError(f'Muestra insuficiente: {nombre}')
        resultado=ks_2samp(x,y)
        salida.append({'variable':nombre,'estadistico_ks':round(float(resultado.statistic),6),
                       'p_valor':round(float(resultado.pvalue),12),'deriva':bool(resultado.pvalue<alfa)})
    return salida

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--referencia',type=Path,default=Path('datos/mora_sintetica.csv'))
    p.add_argument('--reciente',type=Path,required=True)
    p.add_argument('--alfa',type=float,default=0.01)
    a=p.parse_args()
    res=comparar(a.referencia,a.reciente,a.alfa)
    for row in res: print(json.dumps(row,ensure_ascii=False))
    if any(x['deriva'] for x in res): raise SystemExit(1)
