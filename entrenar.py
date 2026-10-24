"""Cuatro experimentos, MLflow + puerta de calidad por recall."""
from pathlib import Path
import argparse
import csv
import json
import os
import tempfile
import joblib
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from validar_datos import validar, VARIABLES, OBJETIVO

CANDIDATOS = ('baseline','logistica','logistica_balanceada','bosque_balanceado')
NOMBRE_EXP = 'comercial-andina-mora-sintetica'

def modelo(nombre, c_logistica=0.3, c_balanceada=1.0, arboles=120, profundidad_bosque=6, balancear=True):
    if nombre=='baseline':
        clf=DummyClassifier(strategy='most_frequent')
    elif nombre=='logistica':
        clf=LogisticRegression(C=c_logistica,max_iter=800,random_state=42)
    elif nombre=='logistica_balanceada':
        clf=LogisticRegression(C=c_balanceada,max_iter=800,class_weight='balanced' if balancear else None,random_state=42)
    elif nombre=='bosque_balanceado':
        clf=RandomForestClassifier(n_estimators=arboles,max_depth=profundidad_bosque,min_samples_leaf=12,class_weight='balanced' if balancear else None,random_state=42,n_jobs=1)
    else:
        raise ValueError(f'Algoritmo no reconocido: {nombre}')
    pasos=[('imputacion',SimpleImputer(strategy='median'))]
    if nombre.startswith('logistica'):
        pasos.append(('escala',StandardScaler()))
    pasos.append(('modelo',clf))
    return Pipeline(pasos)

def particion(ruta):
    df=validar(ruta)
    return train_test_split(df[VARIABLES],df[OBJETIVO].astype(int),test_size=0.25,random_state=42,stratify=df[OBJETIVO])

def experimentar(nombre, datos, umbral=0.50, tracking=True, configuracion=None):
    xtrain,xtest,ytrain,ytest=datos
    clf=modelo(nombre, **(configuracion or {}))
    clf.fit(xtrain,ytrain)
    pred=clf.predict(xtest)
    metricas={
        'accuracy':round(float(accuracy_score(ytest,pred)),6),
        'precision':round(float(precision_score(ytest,pred,zero_division=0)),6),
        'recall':round(float(recall_score(ytest,pred,zero_division=0)),6),
        'f1':round(float(f1_score(ytest,pred,zero_division=0)),6),
    }
    aprobado=metricas['recall']>=umbral
    params={key.replace('modelo__',''):str(val) for key,val in clf.get_params().items() if key.startswith('modelo__') and key.count('__')==1}
    if tracking:
        import mlflow
        mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI','sqlite:///mlflow.db'))
        mlflow.set_experiment(NOMBRE_EXP)
        with mlflow.start_run(run_name=nombre):
            mlflow.log_params({'algoritmo':nombre,'random_state':42,'umbral_recall':umbral,**params})
            mlflow.log_metrics({**metricas,'aprobado':int(aprobado)})
            mlflow.set_tags({'origen_datos':'sintetico','puerta':'aprobado' if aprobado else 'rechazado'})
            # Persistir el modelo candidato aprobado en su ejecución de MLflow.
            # No se publica ningún modelo reprobado.
            if aprobado:
                with tempfile.TemporaryDirectory() as tmp:
                    candidato = Path(tmp) / 'modelo_candidato.joblib'
                    joblib.dump(clf, candidato)
                    mlflow.log_artifact(str(candidato), artifact_path='modelos')
    fila={'algoritmo':nombre,**metricas,'aprobado':aprobado,'parametros':params}
    return fila,clf

def ejecutar(ruta=Path('datos/mora_sintetica.csv'),salida=Path('modelos'),umbral=0.50,candidatos=CANDIDATOS,tracking=True,configuracion=None):
    salida=Path(salida)
    salida.mkdir(parents=True,exist_ok=True)
    archivo=salida/'modelo.joblib'
    # NO borrar la versión vigente: solo sustituirla tras pasar el umbral.
    datos=particion(ruta)
    resultados=[]
    aceptados=[]
    for nombre in candidatos:
        fila,clf=experimentar(nombre,datos,umbral=umbral,tracking=tracking,configuracion=configuracion)
        resultados.append(fila)
        print(json.dumps(fila,ensure_ascii=False))
        if fila['aprobado']:
            aceptados.append((fila,clf))
    (salida/'experimentos.json').write_text(json.dumps(resultados,ensure_ascii=False,indent=2),encoding='utf-8')
    with (salida/'experimentos.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['algoritmo','accuracy','precision','recall','f1','aprobado','parametros'])
        writer.writeheader()
        for fila in resultados:
            writer.writerow({**fila,'parametros':json.dumps(fila['parametros'],sort_keys=True)})
    if not aceptados:
        raise RuntimeError(f'PUERTA DE CALIDAD RECHAZADA: recall < {umbral} para todos los experimentos')
    elegido,clf=max(aceptados,key=lambda par:(par[0]['f1'],par[0]['precision']))
    # Escribir temporal y promover atómicamente. Una puerta fallida conserva la versión anterior.
    with tempfile.NamedTemporaryFile(prefix='.modelo_candidato_',suffix='.joblib',dir=salida,delete=False) as tmp:
        temporal=Path(tmp.name)
    try:
        joblib.dump({'pipeline':clf,'variables':VARIABLES,'objetivo':OBJETIVO,
                     'modelo':elegido['algoritmo'],'metricas':{k:elegido[k] for k in ['accuracy','precision','recall','f1']},
                     'umbral':umbral,'origen':'sintetico'},temporal)
        os.replace(temporal,archivo)
    finally:
        temporal.unlink(missing_ok=True)
    print(f'MODELO APROBADO: {elegido["algoritmo"]}; recall={elegido["recall"]:.4f}')
    return elegido,resultados

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--datos',type=Path,default=Path('datos/mora_sintetica.csv'))
    p.add_argument('--salida',type=Path,default=Path('modelos'))
    p.add_argument('--umbral',type=float,default=0.5)
    p.add_argument('--modelo',choices=CANDIDATOS,action='append')
    p.add_argument('--sin-mlflow',action='store_true',help='Entrena y valida sin registro MLflow (build de inferencia)')
    p.add_argument('--c-logistica',type=float,default=0.3,help='Regularización C de la logística estándar')
    p.add_argument('--c-balanceada',type=float,default=1.0,help='Regularización C de la logística balanceada')
    p.add_argument('--arboles',type=int,default=120,help='Número de árboles del bosque')
    p.add_argument('--profundidad-bosque',type=int,default=6)
    p.add_argument('--sin-balanceo',action='store_true',help='Desactivar class_weight en variantes balanceadas')
    a=p.parse_args()
    if a.c_logistica<=0 or a.c_balanceada<=0 or a.arboles<1 or a.profundidad_bosque<1:
        p.error('Los parámetros de regularización, árboles y profundidad deben ser positivos')
    config={'c_logistica':a.c_logistica,'c_balanceada':a.c_balanceada,
            'arboles':a.arboles,'profundidad_bosque':a.profundidad_bosque,
            'balancear':not a.sin_balanceo}
    ejecutar(a.datos,a.salida,a.umbral,a.modelo or CANDIDATOS,tracking=not a.sin_mlflow,configuracion=config)
