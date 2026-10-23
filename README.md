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

`.github/workflows/ci.yml` entrena y verifica los cuatro runs, ejecuta 11 pruebas, demuestra rechazo controlado, intenta construir/ejecutar Docker y exige que una deriva simulada sea detectada. **El resultado de CI remoto debe verificarse en la pestaña Actions; no se declara aquí como exitoso por adelantado.**

`monitoreo.py` ejecuta KS para cada entrada numérica con nivel de significancia 0,01; si detecta deriva sale con código 1. El monitor sintético cambia solo `uso_cupo_pct` y no demuestra degradación real del modelo.

Reentrenamiento: KS significativo en dos ventanas semanales, recall observado <0,50 o revisión semestral. Si un modelo nuevo no pasa la puerta de calidad, no se promociona.

## Gestión y adopción

El tablero académico modela dos sprints semanales simulados: **17–23** y **24–30 de octubre de 2026**. Las retrospectivas y actividades futuras no deben confundirse con eventos históricos realizados. El plan de adopción incluye matriz poder/interés, comunicaciones, capacitación y objetivos de uso.

**Uso de IA:** ChatGPT (OpenAI) se utilizó para apoyar diseño, generación y validación del código y redacción. Los estudiantes deben revisar, ejecutar y defender el resultado.
