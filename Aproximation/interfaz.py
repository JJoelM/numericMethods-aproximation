import tkinter as tk
import ttkbootstrap as tb
from tkinter import ttk, messagebox
import sympy as sp
from metodo import interpolacion_lineal
from graficador import graficar_funcion
from validador_intervalos import buscar_intervalos
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


def lanzar_interfaz():
    # ---- Validación de la ecuación ----
    def validar_ecuacion():
        fx_str = entrada_funcion.get()
        try:
            f = sp.sympify(fx_str)
            latex_str = sp.latex(f)

            fig, ax = plt.subplots(figsize=(3.5, 0.8))
            ax.axis("off")
            ax.text(0.5, 0.5, f"${latex_str}$",
                    fontsize=18, ha="center", va="center")

            for widget in frame_preview.winfo_children():
                widget.destroy()

            canvas = FigureCanvasTkAgg(fig, master=frame_preview)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig)

        except Exception as e:
            for widget in frame_preview.winfo_children():
                widget.destroy()
            lbl_error_preview = tk.Label(
                frame_preview,
                text=f"Error al interpretar la ecuación:\n{e}\n\n"
                     "Sugerencias:\n"
                     "- Use `**` para potencias, ej: x**2\n"
                     "- Use `pi` para π y `E` para e\n"
                     "- Funciones: sin(x), cos(x), log(x)",
                fg="red", justify="left", wraplength=350
            )
            lbl_error_preview.pack()

    # ---- Popup selección de intervalos ----
    def seleccionar_intervalos_multi(intervalos):
        popup = tk.Toplevel()
        popup.title("Seleccionar intervalos")
        popup.geometry("400x320")
        popup.grab_set()

        tk.Label(popup, text="Seleccione los intervalos con raíz (Ctrl/Shift para multi):").pack(pady=8)

        lista = tk.Listbox(popup, selectmode=tk.EXTENDED, height=12)
        for idx, (a, b) in enumerate(intervalos):
            lista.insert(idx, f"[{a:.6g}, {b:.6g}]")
        lista.pack(padx=10, pady=5, fill="both", expand=True)

        seleccion = {"valores": None}

        def confirmar():
            sel = lista.curselection()
            if sel:
                seleccion["valores"] = [intervalos[i] for i in sel]
            else:
                seleccion["valores"] = []
            popup.destroy()

        def cancelar():
            seleccion["valores"] = None
            popup.destroy()

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=10, fill="x")
        tk.Button(btn_frame, text="Aceptar", command=confirmar).pack(side="left", padx=20)
        tk.Button(btn_frame, text="Cancelar", command=cancelar).pack(side="right", padx=20)

        popup.wait_window()
        return seleccion["valores"]

    # ---- Ejecución del método ----
    def ejecutar():
        metodo = combo_metodo.get()
        fx_str = entrada_funcion.get()

        try:
            a = float(entrada_a.get())
            b = float(entrada_b.get())
            max_iter = int(entrada_iter.get())
            tol = float(entrada_tol.get())
            use_tol = var_condicion.get() == 1
            delta = float(entrada_delta.get())

            # ---- Parseo de la función ----
            x = sp.Symbol('x')
            try:
                f_expr = sp.sympify(fx_str)
                f_lambd = sp.lambdify(x, f_expr, "numpy")
            except Exception as e:
                messagebox.showerror("Error de función", f"No se pudo interpretar la función: {e}")
                return
            # --------------------------------------------------------

            # Buscar intervalos
            intervalos = buscar_intervalos(fx_str, a, b, delta=delta)

            if not intervalos:
                messagebox.showerror(
                    "Intervalo inválido",
                    "No se detectaron cambios de signo en el rango [a, b].\n"
                    "Pruebe con un delta más pequeño o un intervalo diferente."
                )
                return

            if len(intervalos) > 1:
                seleccionados = seleccionar_intervalos_multi(intervalos)
                if seleccionados is None or not seleccionados:
                    messagebox.showinfo("Info", "Operación cancelada.")
                    return
            else:
                seleccionados = intervalos

            # Limpiar tabla
            for row in tabla.get_children():
                tabla.delete(row)

            resultados_totales = []
            for a_i, b_i in seleccionados:
                # Validamos cada intervalo individualmente antes de pasarlo al método
                if f_lambd(a_i) * f_lambd(b_i) > 0:
                    print(f"Omitiendo intervalo [{a_i}, {b_i}] porque no encierra una raíz.")
                    continue

                if metodo == "Interpolación lineal":
                    resultados = interpolacion_lineal(
                        f_lambd, a_i, b_i, tol, max_iter, use_tol
                    )
                else:
                    raise ValueError("Método no implementado aún")

                resultados_totales.extend(resultados)

                for it, a_, b_, xr, fr, err in resultados:
                    tabla.insert("", "end", values=(
                        it, f"{a_:.6f}", f"{b_:.6f}", f"{xr:.6f}",
                        f"{fr:.2e}", f"{err:.2e}" if err is not None else "-"
                    ))

            if not resultados_totales:
                messagebox.showwarning("Sin resultados",
                                       "Ninguno de los intervalos seleccionados era válido para el método "
                                       "(f(a) y f(b) tenían el mismo signo).")
                return

            # Configurar botón de graficar
            boton_graficar.config(
                command=lambda: graficar_funcion(f_lambd, resultados_totales, str(f_expr), a, b)
            )

        except ValueError as ve:
            messagebox.showerror("Error en parámetros", f"Por favor, revise los valores de entrada. Detalles: {ve}")
        except Exception as e:
            messagebox.showerror("Error inesperado", str(e))

    # ---- Ventana principal ----
    ventana = tb.Window(themename="cosmo")
    ventana.title("Métodos Numéricos - Aproximación de raíces")
    ventana.geometry("1000x700")

    ventana.grid_rowconfigure(3, weight=1)
    ventana.grid_columnconfigure(0, weight=1)

    # ---- Frame entradas función ----
    frame_func = tk.Frame(ventana)
    frame_func.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
    frame_func.grid_columnconfigure(1, weight=1)

    tk.Label(frame_func, text="Método:").grid(row=0, column=0, sticky="w")
    combo_metodo = ttk.Combobox(frame_func, values=["Interpolación lineal"], state="readonly")
    combo_metodo.set("Interpolación lineal")
    combo_metodo.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

    tk.Label(frame_func, text="f(x):").grid(row=1, column=0, sticky="w")
    entrada_funcion = tb.Entry(frame_func, bootstyle="info")
    entrada_funcion.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
    tb.Button(frame_func, text="Evaluar ecuación", command=validar_ecuacion, bootstyle="secondary-outline").grid(row=1, column=2, padx=5)

    # ---- Frame preview y guía ----
    frame_preview = tk.Frame(ventana, bd=1, relief="solid", height=60)
    frame_preview.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
    frame_preview.grid_propagate(False)

    lbl_guia = tk.Label(
        ventana,
        text="Guía rápida:\n"
             "- π: pi, e: E\n"
             "- Potencias: use `**` → ejemplo: x**2\n"
             "- Use `2*x` para 2x\n"
             "- sqrt(x) → raíz cuadrada\n"
             "- Funciones: sin(x), cos(x), log(x)\n",
        justify="left", fg="gray"
    )
    lbl_guia.grid(row=2, column=0, sticky="w", padx=10, pady=5)

    # ---- Frame parámetros ----
    frame_params = tk.Frame(ventana)
    frame_params.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
    for i in range(2):
        frame_params.grid_columnconfigure(i, weight=1)

    tk.Label(frame_params, text="Intervalo a:").grid(row=0, column=0, sticky="w")
    entrada_a = tb.Entry(frame_params)
    entrada_a.grid(row=0, column=1, sticky="ew")

    tk.Label(frame_params, text="Intervalo b:").grid(row=1, column=0, sticky="w")
    entrada_b = tb.Entry(frame_params)
    entrada_b.grid(row=1, column=1, sticky="ew")

    tk.Label(frame_params, text="Delta:").grid(row=2, column=0, sticky="w")
    entrada_delta = tb.Entry(frame_params)
    entrada_delta.grid(row=2, column=1, sticky="ew")
    entrada_delta.insert(0, "0.5")

    tk.Label(frame_params, text="Iter max:").grid(row=3, column=0, sticky="w")
    entrada_iter = tb.Entry(frame_params)
    entrada_iter.grid(row=3, column=1, sticky="ew")

    tk.Label(frame_params, text="Tolerancia:").grid(row=4, column=0, sticky="w")
    entrada_tol = tb.Entry(frame_params)
    entrada_tol.grid(row=4, column=1, sticky="ew")

    var_condicion = tk.IntVar()
    tb.Checkbutton(frame_params, text="Usar tolerancia como condición de parada", variable=var_condicion).grid(row=5, column=0, columnspan=2, sticky="w")

    # ---- Frame botones ----
    frame_botones = tk.Frame(ventana)
    frame_botones.grid(row=4, column=0, sticky="ew", padx=10, pady=5)
    frame_botones.grid_columnconfigure(0, weight=1)
    frame_botones.grid_columnconfigure(1, weight=1)

    tb.Button(frame_botones, text="Ejecutar", command=ejecutar, bootstyle="success-outline").grid(row=0, column=0, sticky="ew", padx=5)
    boton_graficar = tb.Button(frame_botones, text="Graficar", bootstyle="primary-outline")
    boton_graficar.grid(row=0, column=1, sticky="ew", padx=5)

    # ---- Frame tabla ----
    frame_tabla = tk.Frame(ventana)
    frame_tabla.grid(row=5, column=0, sticky="nsew", padx=10, pady=5)
    ventana.grid_rowconfigure(5, weight=1)

    cols = ("Iter", "a", "b", "xr", "f(xr)", "Error")
    tabla = ttk.Treeview(frame_tabla, columns=cols, show="headings")
    for col in cols:
        tabla.heading(col, text=col)
        tabla.column(col, anchor="center")
    tabla.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    ventana.mainloop()
