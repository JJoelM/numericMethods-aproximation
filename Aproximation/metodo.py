import numpy as np


def interpolacion_lineal(f_lambd, a, b, tol, max_iter, use_tol):
    """
    Calcula la raíz de una función usando el método de interpolación lineal (Regula Falsi).

    Args:
        f_lambd (callable): La función lambda ya compilada.
        a (float): Extremo izquierdo del intervalo.
        b (float): Extremo derecho del intervalo.
        tol (float): Tolerancia para el criterio de parada.
        max_iter (int): Número máximo de iteraciones.
        use_tol (bool): Si es True, usa la tolerancia como criterio de parada.
    """
    # La validación se hace una sola vez en la interfaz
    # if f_lambd(a) * f_lambd(b) > 0:
    #     raise ValueError("El intervalo no encierra raíz (f(a) y f(b) del mismo signo).")

    resultados = []
    xr_old = a  # Usamos 'a' o 'b' para tener un valor inicial en la primera iteración

    for i in range(1, max_iter + 1):
        fa = f_lambd(a)
        fb = f_lambd(b)

        # Verificación de denominador para evitar división por cero
        if abs(fa - fb) < np.finfo(float).eps:  # np.finfo().eps es un número demasiao chiquito
            print("Advertencia: f(a) y f(b) son muy similares, el método puede fallar.")
            break

        xr = b - fb * (a - b) / (fa - fb)
        fr = f_lambd(xr)

        # Cálculo de error más robusto
        if xr != 0:
            error = abs((xr - xr_old) / xr)
        else:
            error = abs(xr - xr_old)  # Usamos error absoluto si xr es 0

        resultados.append((i, a, b, xr, fr, error))

        # Criterio de parada si se encuentra la raíz exacta
        if abs(fr) < np.finfo(float).eps:
            break  # Éxito, raíz encontrada

        if use_tol and error is not None and error < tol:
            break

        if fa * fr < 0:
            b = xr
        else:
            a = xr

        xr_old = xr

    return resultados
