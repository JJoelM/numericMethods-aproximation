import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations, implicit_multiplication_application
)


def punto_fijo(g_str, x0, tol, max_iter, use_aitken, f_str="0"):
    """
    Calcula la raíz de una función usando el método de iteración de punto fijo.

    Args:
        g_str (str): La función de iteración g(x) como string.
        x0 (float): Valor inicial.
        tol (float): Tolerancia para el criterio de parada.
        max_iter (int): Número máximo de iteraciones.
        use_aitken (bool): Si es True, usa la aceleración de Aitken.
        f_str (str): La función original f(x) para verificación final (opcional).

    Returns:
        tuple: (resultados, x_vals_iter, g_lambd, f_lambd, g_expr)
    """
    # Configuración para parsear las funciones
    transformations = (standard_transformations + (implicit_multiplication_application,))
    x_sym = sp.symbols('x')
    try:
        g_expr = parse_expr(g_str, transformations=transformations)
        f_expr = parse_expr(f_str, transformations=transformations)
        g_lambd = sp.lambdify(x_sym, g_expr, "numpy")
        f_lambd = sp.lambdify(x_sym, f_expr, "numpy")
    except Exception as e:
        raise ValueError(f"Error al interpretar la función g(x): {e}")

    resultados = []
    # Almacena la secuencia de puntos para graficar la "escalera"
    x_vals_iter = [x0]

    if not use_aitken:
        # --- Método de Punto Fijo estándar ---
        x_actual = x0
        for i in range(1, max_iter + 1):
            x_siguiente = g_lambd(x_actual)
            error = abs(x_siguiente - x_actual)

            resultados.append((i, x_siguiente, error))
            x_vals_iter.append(x_siguiente)

            if error < tol:
                break

            x_actual = x_siguiente
    else:
        # --- Método con Aceleración de Aitken ---
        x_i = x0
        for i in range(1, max_iter + 1):
            # Necesitamos tres puntos para la fórmula de Aitken
            x_i_1 = g_lambd(x_i)
            x_i_2 = g_lambd(x_i_1)

            x_vals_iter.extend([x_i_1, x_i_2])

            denominador = (x_i_2 - x_i_1) - (x_i_1 - x_i)

            if abs(denominador) < 1e-12:  # Evitar división por cero
                print("El denominador de Aitken es cero. Deteniendo.")
                break

            x_aitken = x_i - ((x_i_1 - x_i) ** 2) / denominador
            error = abs(x_aitken - x_i)

            resultados.append((i, x_aitken, error))

            if error < tol:
                break

            x_i = x_aitken

    return resultados, x_vals_iter, g_lambd, f_lambd, g_expr
