from pathlib import Path
import pandas as pd
from monitoreo import comparar
ORIGEN=Path('datos/mora_sintetica.csv')

def test_alerta_una_sola_variable(tmp_path):
    df=pd.read_csv(ORIGEN)
    df['uso_cupo_pct']=(df['uso_cupo_pct']+30).clip(upper=100)
    target=tmp_path/'produccion.csv'
    df.to_csv(target,index=False)
    res=comparar(ORIGEN,target)
    assert [x['variable'] for x in res if x['deriva']]==['uso_cupo_pct']

def test_sin_deriva():
    assert all(not x['deriva'] for x in comparar(ORIGEN,ORIGEN))
