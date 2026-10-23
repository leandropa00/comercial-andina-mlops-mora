from pathlib import Path
import pytest
import pandas as pd
from validar_datos import validar
ORIGEN=Path('datos/mora_sintetica.csv')

def test_dataset_valido():
    df=validar(ORIGEN)
    assert len(df)==2000
    assert 0.20<=df.mora.mean()<=0.35

def test_datos_corruptos_generan_error(tmp_path):
    df=pd.read_csv(ORIGEN)
    df.loc[0,'uso_cupo_pct']=150
    archivo=tmp_path/'bad.csv'
    df.to_csv(archivo,index=False)
    with pytest.raises(ValueError,match='uso_cupo_pct'):
        validar(archivo)

def test_etiqueta_invalida_rechazada(tmp_path):
    df=pd.read_csv(ORIGEN)
    df.loc[0,'mora']=2
    archivo=tmp_path/'bad.csv'
    df.to_csv(archivo,index=False)
    with pytest.raises(ValueError,match='solo puede ser'):
        validar(archivo)
