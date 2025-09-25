# numericMethods-aproximation

# Aproximación de Raíces de Funciones con Métodos Numéricos

Este programa permite encontrar raíces de funciones matemáticas en un intervalo dado usando **métodos numéricos**, comenzando con el método de **Interpolación Lineal**. Está desarrollado en **Python** con interfaz gráfica usando **Tkinter** y **ttkbootstrap**.

## Características

- Evaluación y vista previa de la ecuación ingresada en LaTeX.
- Configuración de parámetros:
  - Intervalo [a, b]
  - Número máximo de iteraciones
  - Tolerancia
  - Delta: tamaño de subintervalos para detectar cambios de signo.
- Búsqueda automática de intervalos con raíces.
- Selección múltiple de intervalos a evaluar.
- Ejecución secuencial del método numérico en todos los intervalos seleccionados.
- Visualización de resultados en tabla y graficación de la función con las raíces aproximadas.

## Instalación

1. Clonar este repositorio.
2. Instalar dependencias:

```bash
pip install numpy sympy matplotlib ttkbootstrap
