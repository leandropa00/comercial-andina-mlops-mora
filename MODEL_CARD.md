# Ficha del modelo · Comercial Andina

**Estado:** prototipo académico sobre datos sintéticos, sin validación externa y sin uso de producción real.

- **Qué hace:** clasifica mora (0/1) y entrega una probabilidad ilustrativa en la API; no determina una obligación real.
- **Datos:** 2.000 registros ficticios, semilla 20261017, sin datos personales; generación probabilística con señal débil y ruido.
- **Entradas:** edad, ingreso mensual, cupo, uso de cupo, antigüedad, atrasos previos y compras a crédito semestrales.
- **Variantes:** baseline, regresión logística, regresión logística balanceada y bosque balanceado.
- **Evaluación:** partición estratificada 75/25, semilla 42; accuracy, precision, recall, F1. Umbral recall >=0,50.
- **Resultados locales comprobados:** se elige `logistica_balanceada`: accuracy 0,678; precision 0,426; recall 0,685; F1 0,525. El baseline registra recall 0 y es rechazado. La ejecución remota de MLflow debe contrastarse en GitHub Actions.
- **Límite principal:** datos artificiales diseñados con reglas propias, por lo que no hay evidencia de utilidad comercial, ausencia de sesgo o precisión en clientes reales.
- **No permitido:** aprobar/rechazar créditos, asignar tasas o cupos automáticamente o utilizar la predicción como juicio individual.
- **Reentrenamiento:** si KS p < 0,01 sobre alguna variable durante dos ventanas semanales, o recall real <0,50 en una muestra etiquetada, o cada seis meses. Reentrenamiento sujeto a nueva validación; si no supera el umbral, no se despliega y se mantiene el artefacto anterior bajo control del responsable.
- **Responsables del ejercicio:** Mateo Aguirre, Santiago García y Leandro Panesso Atehortúa.
