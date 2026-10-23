# Definición · Caso C: Finanzas

Comercial Andina S.A.S. es una empresa **ficticia** del taller (320 empleados, seis tiendas, ~60.000 inscritos al programa de fidelización). El objetivo es estimar qué clientes de crédito podrían incurrir en **mora (0/1)**, exclusivamente como demostración de apoyo para acciones preventivas de seguimiento. No autoriza negar créditos, modificar cupos ni decidir automáticamente sobre clientes.

## Datos

Se generan 2.000 filas **sintéticas**, sin datos personales, con semilla fija 20261017. La probabilidad de mora depende de atrasos previos, porcentaje de utilización, antigüedad, ingreso, compras y ruido. Se valida la proporción de positivos entre 20 y 35 %, que haya ocho columnas obligatorias, nulos <= 5 %, objetivo 0/1 y estos rangos: `edad` 18–100; `ingreso_mensual_millones` y `cupo_aprobado_millones` mayores que cero; `uso_cupo_pct` 0–100; `meses_como_cliente`, `pagos_atrasados_previos` y `compras_credito_6m` no negativos.

## Criterio de éxito

**Recall >= 0,50**, intencionalmente conservador por datos sintéticos. Se prioriza recall frente a accuracy porque no identificar una mora (falso negativo) impediría un contacto preventivo; subir recall produce más falsos positivos y exige revisión humana. El umbral en una implantación real lo acordaría el negocio.

## Indicadores de negocio del piloto (metas ilustrativas, no resultados)

1. Tasa de mora de la cartera: **línea base por medir** con información real; meta hipotética de reducción relativa de 5 % en seis meses.
2. Casos de riesgo revisados oportunamente: línea base 0 % si no hay sistema de alertas; meta >=90 % revisados en dos días hábiles.

## Prioridad: impacto / esfuerzo (hipótesis: escala 1–5)

Seguimiento de mora: 5/2 (2,50); promociones personalizadas: 3/3 (1,00); recomendador de catálogo: 3/4 (0,75). Se prioriza mora por impacto potencial y viabilidad de un piloto pequeño.
