import matplotlib.pyplot as plt
import numpy as np


def graficar_punto_fijo(g_lambd, resultados, x_vals_iter, g_str, use_aitken):
    """
    Genera una gráfica del método de punto fijo, mostrando la convergencia.
    """
    if not resultados:
        print("No hay resultados para graficar.")
        return

    x_aprox = [res[1] for res in resultados]
    raiz_final = x_aprox[-1]
    x0 = x_vals_iter[0]

    # Rango para la gráfica, centrado en las iteraciones
    x_min = min(min(x_vals_iter), raiz_final) - 1
    x_max = max(max(x_vals_iter), raiz_final) + 1
    x_vals = np.linspace(x_min, x_max, 400)

    # Evaluar g(x) de forma segura
    try:
        y_vals_g = g_lambd(x_vals)
    except Exception:
        y_vals_g = np.array([g_lambd(x) for x in x_vals])

    fig, ax = plt.subplots(figsize=(8, 8))

    # 1. Graficar y = x (línea de identidad)
    ax.plot(x_vals, x_vals, 'k--', label="y = x")

    # 2. Graficar y = g(x)
    ax.plot(x_vals, y_vals_g, 'b-', label=f"y = g(x) = {g_str}")

    if not use_aitken:
        # 3a. Graficar la "escalera" de convergencia para el método normal
        for i in range(len(x_vals_iter) - 1):
            x_i = x_vals_iter[i]
            x_i_mas_1 = x_vals_iter[i + 1]
            # Línea vertical de (xi, xi) a (xi, g(xi))
            ax.plot([x_i, x_i], [x_i, x_i_mas_1], 'r-', linewidth=0.8)
            # Línea horizontal de (xi, g(xi)) a (g(xi), g(xi))
            ax.plot([x_i, x_i_mas_1], [x_i_mas_1, x_i_mas_1], 'r-', linewidth=0.8)
        # Resaltar la trayectoria con un marcador
        ax.plot([], [], 'r-', label='Trayectoria')  # Para la leyenda

    # 4. Puntos de la iteración
    ax.plot(x_aprox, [g_lambd(x) for x in x_aprox], 'ro', markersize=4, label="Aproximaciones $x_n$")
    ax.plot(x0, g_lambd(x0), 'go', markersize=7, label="Punto inicial $x_0$")
    ax.plot(raiz_final, g_lambd(raiz_final), 'm*', markersize=10, label=f"Raíz ≈ {raiz_final:.6f}")

    ax.set_title("Método de Iteración de Punto Fijo" + (" con Aitken" if use_aitken else ""))
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True)
    ax.legend()
    ax.axhline(0, color='gray', linewidth=0.5)
    ax.axvline(0, color='gray', linewidth=0.5)

    plt.show()