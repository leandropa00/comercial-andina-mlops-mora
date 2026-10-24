# Comercial Andina — MLOps para riesgo de mora (Caso C)

Trabajo académico de **Mateo Aguirre, Santiago García y Leandro Panesso Atehortúa**. Alineado con la guía de Unidad 3 de Estrategias y Metodologías para la Transformación Digital, Universidad de Caldas.

**El caso de la empresa es ficticio y el dataset es sintético.** Este modelo no debe apoyar decisiones individuales reales de crédito. Se prefirieron datos dummy para ajustarse a las siete variables exigidas y evitar tratar datos personales.

## Ejecución

Requiere Python 3.12 y Docker para la prueba de contenedor.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python generar_datos.py
python validar_datos.py
python entrenar.py
python -m pytest -q pruebas
uvicorn app:app --reload
```

MLflow registra cuatro experimentos en `sqlite:///mlflow.db`. La puerta de calidad exige recall >= 0,50 y **no guarda** modelos rechazados. Los datos, las pruebas y el código están versionados; los artefactos de entrenamiento se generan mediante CI. Consulte `DEFINICION.md` y `MODEL_CARD.md`.

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db
python entrenar.py --modelo baseline --salida /tmp/modelo_rechazado   # Debe fallar
python simular_produccion.py
python monitoreo.py --reciente datos/produccion_deriva.csv            # Debe alertar con exit 1
```

## Servicio FastAPI y contenedor

```bash
uvicorn app:app --port 8000
# En otra terminal:
curl -X POST http://localhost:8000/predecir -H 'Content-Type: application/json' \
  -d '{"edad":34,"ingreso_mensual_millones":4.2,"cupo_aprobado_millones":8,"uso_cupo_pct":82,"meses_como_cliente":17,"pagos_atrasados_previos":2,"compras_credito_6m":7}'
# Después de entrenar:
docker build -t comercial-andina-mora .
docker run --rm -p 8000:8000 comercial-andina-mora
```

La API expone `/salud`, `/predecir` y `/docs`. La misma pipeline de preprocesamiento se empaqueta con el clasificador para evitar *training-serving skew*.

## CI, deriva y límites

`.github/workflows/ci.yml` entrena y verifica los cuatro runs, ejecuta 14 pruebas, demuestra rechazo controlado, construye y ejecuta Docker y exige que una deriva simulada sea detectada. La canalización CI de `main` comprueba además los artefactos de modelos aprobados en MLflow, preserva el modelo vigente cuando un reentrenamiento falla y demuestra una prueba de Pytest fallida deliberadamente antes de restaurar la validación. Los resultados se verifican en la pestaña Actions.

`monitoreo.py` ejecuta KS para cada entrada numérica con nivel de significancia 0,01; si detecta deriva sale con código 1. El monitor sintético cambia solo `uso_cupo_pct` y no demuestra degradación real del modelo.

Reentrenamiento: KS significativo en dos ventanas semanales, recall observado <0,50 o revisión semestral. Si un modelo nuevo no pasa la puerta de calidad, no se promociona y se conserva la versión previamente aprobada.

## Gestión y adopción

El tablero académico modela dos sprints semanales simulados: **17–23** y **24–30 de octubre de 2026**. Las retrospectivas y actividades futuras no deben confundirse con eventos históricos realizados. El plan de adopción incluye matriz poder/interés, comunicaciones, capacitación y objetivos de uso.

## Despliegue de inferencia en Vercel

El archivo `pyproject.toml` usa solo dependencias de inferencia con versiones fijadas. Su comando de build `python entrenar.py --sin-mlflow` reconstruye el modelo desde el dataset sintético versionado y aplica el mismo umbral de calidad. El artefacto `modelos/modelo.joblib` se produce durante el build y **no** se añade a Git. El CI ejecuta además las cuatro variantes y las registra en MLflow por separado.

Vercel detecta `app.py`, enlaza este repositorio y despliega automáticamente la rama `main`. Rutas: `/salud`, `/predecir`, `/docs`. La prueba del dominio público debe registrarse como evidencia después de una publicación exitosa.

## Parámetros y dataset corregido

El dataset de 2.000 filas contiene 515 positivos (25,75 %). La etiqueta `mora` se genera con probabilidad dependiente de **cuatro variables** (`pagos_atrasados_previos`, `uso_cupo_pct`, `meses_como_cliente`, `ingreso_mensual_millones`) más ruido reproducible; las otras variables se conservan como entradas del modelo. La nueva logística balanceada logra recall 0,7364 y F1 0,5491 en 500 filas de prueba.

```bash
python entrenar.py --c-logistica 0.5 --c-balanceada 0.8 --arboles 150 --profundidad-bosque 8
python entrenar.py --sin-balanceo --sin-mlflow
```

La última versión aprobada se reemplaza de forma atómica, únicamente tras pasar el gate. Consulte el [workflow CI](.github/workflows/ci.yml) para evidencias de Pytest, MLflow, Docker y deriva. El segundo sprint académico (24–30 de octubre de 2026) no se declara ejecutado con anterioridad a esas fechas.
