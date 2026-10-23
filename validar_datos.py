"""Rechaza de forma explícita datos corruptos antes del entrenamiento."""
from pathlib import Path
import pandas as pd

VARIABLES = ['edad', 'ingreso_mensual_millones', 'cupo_aprobado_millones', 'uso_cupo_pct', 'meses_como_cliente', 'pagos_atrasados_previos', 'compras_credito_6m']
OBJETIVO = 'mora'

def validar(ruta):
    df = pd.read_csv(Path(ruta))
    faltantes = sorted(set(VARIABLES + [OBJETIVO])-set(df.columns))
    if faltantes:
        raise ValueError(f'Faltan columnas: {faltantes}')
    if len(df) < 1500:
        raise ValueError(f'El dataset sintético debe tener al menos 1.500 filas; hay {len(df)}')
    nulos = df[VARIABLES+[OBJETIVO]].isna().mean()
    if (nulos>0.05).any():
        raise ValueError(f'Nulos superiores al 5%: {nulos[nulos>0.05].index.tolist()}')
    if not df[OBJETIVO].dropna().isin([0,1]).all():
        raise ValueError('mora solo puede ser 0 o 1')
    if not df.edad.dropna().between(18,100).all():
        raise ValueError('edad fuera de rango [18,100]')
    if not df.uso_cupo_pct.dropna().between(0,100).all():
        raise ValueError('uso_cupo_pct fuera de rango [0,100]')
    for nombre in ['ingreso_mensual_millones','cupo_aprobado_millones']:
        if not (df[nombre].dropna()>0).all():
            raise ValueError(f'{nombre} debe ser mayor a 0')
    for nombre in ['meses_como_cliente','pagos_atrasados_previos','compras_credito_6m']:
        if not (df[nombre].dropna()>=0).all():
            raise ValueError(f'{nombre} no puede ser negativo')
    tasa = float(df[OBJETIVO].mean())
    if not 0.20<=tasa<=0.35:
        raise ValueError(f'Tasa positiva fuera del 20-35%: {tasa:.2%}')
    return df

if __name__ == '__main__':
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('--datos',type=Path,default=Path('datos/mora_sintetica.csv'))
    a=p.parse_args()
    df=validar(a.datos)
    print(f'Datos válidos: {len(df)} filas, {len(df.columns)} columnas, mora {df.mora.mean():.2%}, nulos máximo {df.isna().mean().max():.2%}')
