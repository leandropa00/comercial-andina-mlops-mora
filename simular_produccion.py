"""Cambia únicamente el uso del cupo para simular deriva identificable."""
from pathlib import Path
import argparse
import pandas as pd

def generar(origen,salida):
    df=pd.read_csv(origen)
    df['uso_cupo_pct']=(df['uso_cupo_pct']+30).clip(upper=100)
    Path(salida).parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(salida,index=False)
    print(f'Deriva sintética de uso_cupo_pct en {len(df)} filas')

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--origen',type=Path,default=Path('datos/mora_sintetica.csv'))
    p.add_argument('--salida',type=Path,default=Path('datos/produccion_deriva.csv'))
    a=p.parse_args()
    generar(a.origen,a.salida)
