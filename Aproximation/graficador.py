import matplotlib.pyplot as plt
import numpy as np


def graficar_funcion(f_lambd, resultados, fx_str, a, b):
    xs = np.linspace(a, b, 400)
    ys = f_lambd(xs)

    plt.figure(figsize=(7, 5))
    plt.axhline(0, color='black', linewidth=0.8)
    plt.plot(xs, ys, label=f"f(x) = {fx_str}", color="blue")
    plt.scatter([r[3] for r in resultados], [r[4] for r in resultados],
                c='red', zorder=5, label="Aproximaciones")
    plt.legend()
    plt.title("Método de Interpolación Lineal")
    plt.xlabel("x")
    plt.ylabel("f(x)")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.show()
