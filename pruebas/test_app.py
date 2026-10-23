from fastapi.testclient import TestClient
from app import app
client=TestClient(app)
DATO={'edad':34,'ingreso_mensual_millones':4.2,'cupo_aprobado_millones':8,
      'uso_cupo_pct':82,'meses_como_cliente':17,'pagos_atrasados_previos':2,'compras_credito_6m':7}

def test_salud():
    r=client.get('/salud')
    assert r.status_code==200
    assert r.json()['estado']=='ok'

def test_prediccion():
    r=client.post('/predecir',json=DATO)
    assert r.status_code==200
    assert 0<=r.json()['probabilidad_mora']<=1
    assert r.json()['mora'] in [0,1]

def test_rechazo_422():
    assert client.post('/predecir',json={**DATO,'uso_cupo_pct':150}).status_code==422
