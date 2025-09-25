# validador_intervalos_corregido.py
import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations, implicit_multiplication_application
)


def buscar_intervalos(fx_str, a, b, delta=1.0):
    """
    Busca subintervalos en [a, b] donde la función f(x) cambia de signo o toca el cero.

    Esta función está diseñada para encontrar los intervalos que "abrazan" una raíz,
    incluso si la raíz cae exactamente en uno de los puntos de la malla de evaluación.

    Args:
        fx_str (str): La expresión de la función como un string (ej. "x**2 - 4").
        a (float): Límite inferior del intervalo de búsqueda.
        b (float): Límite superior del intervalo de búsqueda.
        delta (float): El tamaño del paso para crear los subintervalos.

    Returns:
        list: Una lista de tuplas, donde cada tupla es un intervalo (x0, x1)
              que contiene al menos una raíz.
    """
    if delta <= 0:
        raise ValueError("El valor de delta debe ser positivo.")

    # Intervalo ordenado
    if a > b:
        a, b = b, a

    # Configuración para parsear la función con SymPy
    transformations = (standard_transformations + (implicit_multiplication_application,))
    x_symbol = sp.symbols('x')
    try:
        f_expr = parse_expr(fx_str, transformations=transformations)
    except Exception as e:
        raise ValueError(f"Error al interpretar la función: {e}")

    # Se convierte la expresión de SymPy a una función numérica de NumPy para eficiencia
    f = sp.lambdify(x_symbol, f_expr, "numpy")

    # Usamos b + delta/2 para asegurar que 'b' se incluya en el rango si es un múltiplo.
    puntos = np.arange(a, b + delta / 2, delta)
    if puntos[-1] > b:
        puntos[-1] = b

    intervalos_con_raiz = []

    # Iteramos sobre los pares de puntos consecutivos (x0, x1)
    for x0, x1 in zip(puntos, puntos[1:]):
        try:
            f0 = f(x0)
            f1 = f(x1)

            # Condición f0 * f1 <= 0
            # 1. Si f0 * f1 < 0: Hay un cambio de signo, por lo tanto, una raíz dentro del intervalo.
            # 2. Si f0 * f1 == 0: Uno de los extremos (o ambos) es una raíz exacta.
            if f0 * f1 <= 0:
                intervalos_con_raiz.append((round(x0, 8), round(x1, 8)))

        except (ValueError, TypeError, ZeroDivisionError):
            # Si la función no está definida en un punto (ej. log(0)), lo ignoramos y continuamos
            continue

    return intervalos_con_raiz
