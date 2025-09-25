import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox
import sympy as sp
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from metodo import interpolacion_lineal
from graficador import graficar_funcion
from validador_intervalos import buscar_intervalos as buscar_intervalos
from punto_fijo import punto_fijo
from graficador_punto_fijo import graficar_punto_fijo


def lanzar_interfaz():
    def actualizar_campos_metodo(event=None):
        metodo = combo_metodo.get()

        # Ocultar todos los campos específicos primero
        for widget in campos_interpolacion + campos_punto_fijo:
            widget.grid_remove()

        # Mostrar campos según el método seleccionado
        if metodo == "Interpolación Lineal":
            for widget in campos_interpolacion:
                widget.grid()
            # Actualizar columnas de la tabla
            configurar_tabla(["Iter", "a", "b", "xr", "f(xr)", "Error"])
        elif metodo == "Punto Fijo":
            for widget in campos_punto_fijo:
                widget.grid()
            # Actualizar columnas de la tabla
            configurar_tabla(["Iter", "x_n", "Error"])

    def configurar_tabla(columnas):
        tabla['columns'] = columnas
        for col in columnas:
            tabla.heading(col, text=col)
            tabla.column(col, anchor="center", width=100)

    def validar_ecuacion():
        fx_str = entrada_funcion.get()
        try:
            f = sp.sympify(fx_str)
            latex_str = sp.latex(f)
            fig, ax = plt.subplots(figsize=(3.5, 0.8))
            ax.axis("off")
            ax.text(0.5, 0.5, f"${latex_str}$", fontsize=18, ha="center", va="center")
            for widget in frame_preview.winfo_children(): widget.destroy()
            canvas = FigureCanvasTkAgg(fig, master=frame_preview)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig)
        except Exception as e:
            for widget in frame_preview.winfo_children(): widget.destroy()
            lbl_error_preview = tk.Label(frame_preview, text=f"Error: {e}", fg="red")
            lbl_error_preview.pack()

    # ---- Popup selección de intervalos ----
    def seleccionar_intervalos_multi(intervalos):
        popup = tk.Toplevel()
        popup.title("Seleccionar intervalos")
        popup.geometry("400x320")
        popup.grab_set()
        tk.Label(popup, text="Seleccione los intervalos con raíz:").pack(pady=8)
        lista = tk.Listbox(popup, selectmode=tk.EXTENDED, height=12)
        for idx, (a, b) in enumerate(intervalos): lista.insert(idx, f"[{a:.6g}, {b:.6g}]")
        lista.pack(padx=10, pady=5, fill="both", expand=True)
        seleccion = {"valores": None}

        def confirmar():
            sel = lista.curselection()
            seleccion["valores"] = [intervalos[i] for i in sel] if sel else []
            popup.destroy()

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=10, fill="x")
        tk.Button(btn_frame, text="Aceptar", command=confirmar).pack(side="left", padx=20)
        tk.Button(btn_frame, text="Cancelar", command=lambda: popup.destroy()).pack(side="right", padx=20)
        popup.wait_window()
        return seleccion["valores"]

    # ---- Ejecución del método ----
    def ejecutar():
        metodo = combo_metodo.get()
        fx_str = entrada_funcion.get()
        try:
            max_iter = int(entrada_iter.get())
            tol = float(entrada_tol.get())

            # Limpiar tabla
            for row in tabla.get_children(): tabla.delete(row)

            if metodo == "Interpolación Lineal":
                a = float(entrada_a.get())
                b = float(entrada_b.get())
                delta = float(entrada_delta.get())
                use_tol = var_condicion.get() == 1

                x = sp.Symbol('x')
                f_expr = sp.sympify(fx_str)
                f_lambd = sp.lambdify(x, f_expr, "numpy")

                intervalos = buscar_intervalos(fx_str, a, b, delta=delta)
                if not intervalos: messagebox.showerror("Error", "No se encontraron raíces en el intervalo."); return

                seleccionados = seleccionar_intervalos_multi(intervalos) if len(intervalos) > 1 else intervalos
                if seleccionados is None or not seleccionados: messagebox.showinfo("Info",
                                                                                   "Operación cancelada."); return

                resultados_totales = []
                for a_i, b_i in seleccionados:
                    if f_lambd(a_i) * f_lambd(b_i) > 0: continue
                    resultados = interpolacion_lineal(f_lambd, a_i, b_i, tol, max_iter, use_tol)
                    resultados_totales.extend(resultados)
                    for it, a_, b_, xr, fr, err in resultados:
                        tabla.insert("", "end", values=(it, f"{a_:.6f}", f"{b_:.6f}", f"{xr:.6f}", f"{fr:.2e}",
                                                        f"{err:.2e}" if err is not None else "-"))

                if not resultados_totales: messagebox.showwarning("Sin resultados",
                                                                  "Ningún intervalo seleccionado era válido."); return

                boton_graficar.config(command=lambda: graficar_funcion(f_lambd, resultados_totales, str(f_expr), a, b))

            elif metodo == "Punto Fijo":
                g_str = entrada_g.get()
                x0 = float(entrada_x0.get())
                use_aitken = var_aitken.get() == 1

                resultados, x_vals_iter, g_lambd, f_lambd, g_expr = punto_fijo(g_str, x0, tol, max_iter, use_aitken,
                                                                               fx_str)

                if not resultados: messagebox.showerror("Error", "El método no convergió o no se ejecutó."); return

                for it, xn, err in resultados:
                    tabla.insert("", "end", values=(it, f"{xn:.8f}", f"{err:.8f}"))

                # Verificar f(raiz) al final
                raiz_final = resultados[-1][1]
                print(f"Verificación final: f({raiz_final:.6f}) = {f_lambd(raiz_final):.6f}")

                boton_graficar.config(
                    command=lambda: graficar_punto_fijo(g_lambd, resultados, x_vals_iter, str(g_expr), use_aitken))

        except ValueError as ve:
            messagebox.showerror("Error en parámetros", str(ve))
        except Exception as e:
            messagebox.showerror("Error inesperado", str(e))

    # ---- Ventana principal y Widgets ----
    ventana = tb.Window(themename="cosmo")
    ventana.title("Métodos Numéricos - Aproximación de raíces")
    ventana.geometry("1000x700")

    # --- Frame función y método ---
    frame_func = tk.Frame(ventana)
    frame_func.pack(fill="x", padx=10, pady=5)
    frame_func.columnconfigure(1, weight=1)

    ttk.Label(frame_func, text="Método:").grid(row=0, column=0, sticky="w")
    combo_metodo = ttk.Combobox(frame_func, values=["Interpolación Lineal", "Punto Fijo"], state="readonly")
    combo_metodo.set("Interpolación Lineal")
    combo_metodo.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5)
    combo_metodo.bind("<<ComboboxSelected>>", actualizar_campos_metodo)  # <-- Evento clave

    ttk.Label(frame_func, text="f(x):").grid(row=1, column=0, sticky="w")
    entrada_funcion = tb.Entry(frame_func, bootstyle="info")
    entrada_funcion.grid(row=1, column=1, sticky="ew", padx=5)
    tb.Button(frame_func, text="Evaluar f(x)", command=validar_ecuacion, bootstyle="secondary-outline").grid(row=1,
                                                                                                             column=2,
                                                                                                             padx=5)

    # --- Frame de preview ---
    frame_preview = tk.Frame(ventana, bd=1, relief="solid", height=60)
    frame_preview.pack(fill="x", padx=10, pady=5)
    frame_preview.pack_propagate(False)

    # --- Frame de parámetros (aquí estarán TODOS los campos) ---
    frame_params = tk.Frame(ventana)
    frame_params.pack(fill="x", padx=10, pady=5)
    frame_params.columnconfigure(1, weight=1)

    # Campos para Interpolación Lineal
    lbl_a = ttk.Label(frame_params, text="Intervalo a:")
    entrada_a = tb.Entry(frame_params)
    lbl_b = ttk.Label(frame_params, text="Intervalo b:")
    entrada_b = tb.Entry(frame_params)
    lbl_delta = ttk.Label(frame_params, text="Delta:")
    entrada_delta = tb.Entry(frame_params)
    entrada_delta.insert(0, "0.5")
    var_condicion = tk.IntVar()
    check_tol = tb.Checkbutton(frame_params, text="Usar tolerancia", variable=var_condicion)
    campos_interpolacion = [lbl_a, entrada_a, lbl_b, entrada_b, lbl_delta, entrada_delta, check_tol]

    # Campos para Punto Fijo
    lbl_g = ttk.Label(frame_params, text="g(x):")
    entrada_g = tb.Entry(frame_params, bootstyle="info")
    lbl_x0 = ttk.Label(frame_params, text="Punto inicial x0:")
    entrada_x0 = tb.Entry(frame_params)
    var_aitken = tk.IntVar()
    check_aitken = tb.Checkbutton(frame_params, text="Usar Aceleración de Aitken", variable=var_aitken)
    campos_punto_fijo = [lbl_g, entrada_g, lbl_x0, entrada_x0, check_aitken]

    # Posicionamiento de todos los campos (se mostrarán/ocultarán)
    lbl_a.grid(row=0, column=0, sticky="w")
    entrada_a.grid(row=0, column=1, sticky="ew", pady=2)
    lbl_b.grid(row=1, column=0, sticky="w")
    entrada_b.grid(row=1, column=1, sticky="ew", pady=2)
    lbl_delta.grid(row=2, column=0, sticky="w")
    entrada_delta.grid(row=2, column=1, sticky="ew", pady=2)
    check_tol.grid(row=6, column=0, columnspan=2, sticky="w")

    lbl_g.grid(row=0, column=0, sticky="w")
    entrada_g.grid(row=0, column=1, sticky="ew", pady=2)
    lbl_x0.grid(row=1, column=0, sticky="w")
    entrada_x0.grid(row=1, column=1, sticky="ew", pady=2)
    check_aitken.grid(row=2, column=0, columnspan=2, sticky="w")

    # Campos comunes
    ttk.Label(frame_params, text="Iter max:").grid(row=4, column=0, sticky="w")
    entrada_iter = tb.Entry(frame_params)
    entrada_iter.grid(row=4, column=1, sticky="ew", pady=2)
    ttk.Label(frame_params, text="Tolerancia:").grid(row=5, column=0, sticky="w")
    entrada_tol = tb.Entry(frame_params)
    entrada_tol.grid(row=5, column=1, sticky="ew", pady=2)

    # --- Frame botones y tabla ---
    frame_botones = tk.Frame(ventana)
    frame_botones.pack(fill="x", padx=10, pady=5)
    tb.Button(frame_botones, text="Ejecutar", command=ejecutar, bootstyle="success").pack(side="left", fill="x",
                                                                                          expand=True, padx=5)
    boton_graficar = tb.Button(frame_botones, text="Graficar", bootstyle="primary-outline")
    boton_graficar.pack(side="left", fill="x", expand=True, padx=5)

    frame_tabla = tk.Frame(ventana)
    frame_tabla.pack(fill="both", expand=True, padx=10, pady=5)
    tabla = ttk.Treeview(frame_tabla, show="headings")
    scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=scrollbar.set)
    tabla.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # --- Inicialización de la UI ---
    actualizar_campos_metodo()
    ventana.mainloop()


# --- Punto de entrada ---
if __name__ == "__main__":
    lanzar_interfaz()
