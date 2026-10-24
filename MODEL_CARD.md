# Ficha del modelo · Comercial Andina

**Estado:** prototipo académico sobre datos sintéticos, sin validación externa y sin uso de producción real.

- **Qué hace:** clasifica mora (0/1) y entrega una probabilidad ilustrativa en la API; no determina una obligación real.
- **Datos:** 2.000 registros ficticios, 515 positivos (25,75 %), semilla 20261017, sin datos personales; generación probabilística con señal débil y ruido.
- **Entradas:** edad, ingreso mensual, cupo, uso de cupo, antigüedad, atrasos previos y compras a crédito semestrales.
- **Variantes:** baseline, regresión logística, regresión logística balanceada y bosque balanceado.
- **Evaluación:** partición estratificada 75/25, semilla 42; accuracy, precision, recall, F1. Umbral recall >=0,50.
- **Resultados locales comprobados:** se elige `logistica_balanceada`: accuracy 0,688; precision 0,438; recall 0,736; F1 0,549. El baseline registra recall 0 y es rechazado. La ejecución remota de MLflow debe contrastarse en GitHub Actions.
- **Límite principal:** datos artificiales diseñados con reglas propias, por lo que no hay evidencia de utilidad comercial, ausencia de sesgo o precisión en clientes reales.
- **No permitido:** aprobar/rechazar créditos, asignar tasas o cupos automáticamente o utilizar la predicción como juicio individual.
- **Reentrenamiento:** si KS p < 0,01 sobre alguna variable durante dos ventanas semanales, o recall real <0,50 en una muestra etiquetada, o cada seis meses. Reentrenamiento sujeto a nueva validación; si no supera el umbral, no se despliega y se mantiene el artefacto anterior bajo control del responsable.
- **Responsables del ejercicio:** Mateo Aguirre, Santiago García y Leandro Panesso Atehortúa.

## Conservación de versiones y trazabilidad
El reentrenamiento escribe una versión temporal y reemplaza el artefacto de inferencia solo después de aprobar la puerta. Los candidatos aprobados se registran también como artefactos joblib en sus ejecuciones MLflow. Una corrida rechazada conserva `modelo.joblib` y no promueve cambios. El dataset sintético etiqueta mora mediante cuatro entradas (atrasos previos, uso del cupo, antigüedad, ingresos) y ruido; el resto de campos no participa directamente en la ecuación generadora.
