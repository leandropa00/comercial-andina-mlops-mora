"""Genera registros SINTÉTICOS: mora depende de cuatro entradas + ruido.

Variables causales: atrasos, uso del cupo, antigüedad e ingresos.
Edad, cupo aprobado y compras son covariables descriptivas no causales.
"""
from pathlib import Path
import argparse
import csv
import math

COLUMNAS = ['edad', 'ingreso_mensual_millones', 'cupo_aprobado_millones', 'uso_cupo_pct', 'meses_como_cliente', 'pagos_atrasados_previos', 'compras_credito_6m', 'mora']

def generar(destino=Path('datos/mora_sintetica.csv'), filas=2000, semilla=20261017):
    estado = semilla
    def aleatorio():
        nonlocal estado
        estado = (1664525 * estado + 1013904223) % (2 ** 32)
        return estado / (2 ** 32)
    def entero(a, b):
        return a + int(aleatorio() * (b - a + 1))
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    positivos = 0
    with destino.open('w', newline='', encoding='utf-8') as archivo:
        writer = csv.writer(archivo)
        writer.writerow(COLUMNAS)
        for _ in range(filas):
            edad = entero(18, 75)
            ingreso = round(1.2 + 12 * aleatorio(), 2)
            cupo = round(1 + 26 * aleatorio(), 2)
            uso = round(5 + 95 * aleatorio(), 2)
            meses = entero(1, 150)
            atrasos = entero(0, 4) if aleatorio() < 0.48 else 0
            compras = entero(0, 24)
            ruido = sum(aleatorio() for _ in range(12)) - 6
            z = -1.45 + 0.56*atrasos + 0.025*(uso-50) - 0.011*(meses-45) - 0.115*(ingreso-5) + 0.5*ruido
            mora = int(aleatorio() < 1/(1 + math.exp(-z)))
            positivos += mora
            writer.writerow([edad, f'{ingreso:.2f}', f'{cupo:.2f}', f'{uso:.2f}', meses, atrasos, compras, mora])
    tasa = positivos/filas
    if not 0.20 <= tasa <= 0.35:
        raise ValueError(f'Tasa positiva fuera de 20-35%: {tasa:.2%}')
    print(f'Datos sintéticos: {filas} filas; {positivos} positivos ({tasa:.2%})')
    return destino

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--filas', type=int, default=2000)
    p.add_argument('--semilla', type=int, default=20261017)
    p.add_argument('--salida', type=Path, default=Path('datos/mora_sintetica.csv'))
    a=p.parse_args()
    generar(a.salida, a.filas, a.semilla)
