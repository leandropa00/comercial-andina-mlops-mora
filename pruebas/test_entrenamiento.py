from pathlib import Path
import pytest
from entrenar import ejecutar,experimentar,particion
DATOS=Path('datos/mora_sintetica.csv')

def test_modelo_base_no_pasa_umbral():
    base,_=experimentar('baseline',particion(DATOS),tracking=False)
    assert base['recall']==0
    assert not base['aprobado']

def test_cuatro_experimentos_y_artefacto(tmp_path):
    elegido,filas=ejecutar(DATOS,tmp_path,tracking=False)
    assert len(filas)==4
    assert any(not x['aprobado'] for x in filas)
    assert any(x['aprobado'] for x in filas)
    assert elegido['recall']>=0.50
    assert (tmp_path/'modelo.joblib').is_file()

def test_puerta_rechaza_modelo_y_elimina_artefacto(tmp_path):
    with pytest.raises(RuntimeError,match='PUERTA DE CALIDAD RECHAZADA'):
        ejecutar(DATOS,tmp_path,umbral=1.01,tracking=False)
    assert not (tmp_path/'modelo.joblib').exists()


def test_modelo_aprobado_se_conserva_ante_reentrenamiento_rechazado(tmp_path):
    _, _ = ejecutar(DATOS, tmp_path, tracking=False)
    original = (tmp_path / 'modelo.joblib').read_bytes()
    with pytest.raises(RuntimeError, match='PUERTA DE CALIDAD RECHAZADA'):
        ejecutar(DATOS, tmp_path, umbral=1.01, tracking=False)
    assert (tmp_path / 'modelo.joblib').read_bytes() == original

def test_hiperparametros_configurables():
    from entrenar import modelo
    regresion = modelo('logistica_balanceada', c_balanceada=0.8, balancear=False)
    assert regresion.named_steps['modelo'].C == 0.8
    assert regresion.named_steps['modelo'].class_weight is None
