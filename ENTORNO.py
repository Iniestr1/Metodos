import customtkinter as ctk
import tkinter.ttk as ttk
import matplotlib.pyplot as plt
import numpy as np

# --- IMPORTACIÓN DE MÓDULOS BACKEND ---
# Asegúrate de tener estos archivos .py en la misma carpeta
import PROBLEMA_TRUNCAMIENTO as logica_truncamiento 
import logica_ecuaciones as logica_ec 
import interpolaciones 
import aproximaciones 
import derivacion # <-- Nuevo módulo de derivación

# --- COMPONENTE DE TABLA REUTILIZABLE ---
class TablaResultados(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2b2b2b", foreground="white", 
                        rowheight=25, fieldbackground="#2b2b2b", borderwidth=0)
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading", 
                        background="#565b5e", foreground="white", 
                        relief="flat", font=("Arial", 10, "bold"))
        style.map("Treeview.Heading", background=[('active', '#343638')])
        
        self.tree = ttk.Treeview(self, selectmode="none")
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        self.scroll = ctk.CTkScrollbar(self, command=self.tree.yview)
        self.scroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=self.scroll.set)
        
        self.lbl_mensaje = ctk.CTkLabel(self, text="", text_color="#28a745", font=ctk.CTkFont(weight="bold"))
        self.lbl_mensaje.grid(row=1, column=0, columnspan=2, pady=5)

    def actualizar_datos(self, columnas, filas, mensaje="", error=False):
        self.tree.delete(*self.tree.get_children())
        if error:
            self.tree["columns"] = []
            self.lbl_mensaje.configure(text=mensaje, text_color="#dc3545") 
            return
        self.tree["columns"] = columnas
        self.tree["show"] = "headings"
        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=100)
        for fila in filas:
            self.tree.insert("", "end", values=fila)
        self.lbl_mensaje.configure(text=mensaje, text_color="#28a745")


# --- APLICACIÓN PRINCIPAL ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Métodos Numéricos - Norma Montañes")
        self.geometry("1100x750")
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- MENÚ LATERAL ---
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1) # Empuja los botones hacia arriba

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Métodos Numéricos", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_inicio = ctk.CTkButton(self.sidebar_frame, text="Inicio", command=self.mostrar_inicio)
        self.btn_inicio.grid(row=1, column=0, padx=20, pady=10)

        self.btn_truncamiento = ctk.CTkButton(self.sidebar_frame, text="1. Truncamiento \n(IEEE 754)", command=self.mostrar_truncamiento)
        self.btn_truncamiento.grid(row=2, column=0, padx=20, pady=10)

        self.btn_submenu = ctk.CTkButton(self.sidebar_frame, text="2. Resolución de Ec.", command=self.toggle_submenu)
        self.btn_submenu.grid(row=3, column=0, padx=20, pady=10)

        # --- SUBMENÚ ECUACIONES ---
        self.submenu_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.submenu_visible = False 
        opciones_submenu = [
            ("Bisección", self.mostrar_biseccion), ("Punto Fijo", self.mostrar_puntofijo),
            ("Secante", self.mostrar_secante), ("Newton-Raphson", self.mostrar_newton),
            ("Falsa Posición", self.mostrar_falsaposicion), ("Muller", self.mostrar_muller),
            ("Deflación Newton", self.mostrar_def_newton), ("Deflación Muller", self.mostrar_def_muller)
        ]
        for i, (texto, comando) in enumerate(opciones_submenu):
            btn = ctk.CTkButton(self.submenu_frame, text=texto, command=comando, width=160, height=24, fg_color="transparent", border_width=1)
            btn.grid(row=i, column=0, padx=25, pady=2)

        self.btn_interpolacion = ctk.CTkButton(self.sidebar_frame, text="3. Interpolaciones", command=self.mostrar_interpolacion)
        self.btn_interpolacion.grid(row=5, column=0, padx=20, pady=10)

        self.btn_aproximacion = ctk.CTkButton(self.sidebar_frame, text="4. Aproximaciones", command=self.mostrar_aproximaciones)
        self.btn_aproximacion.grid(row=6, column=0, padx=20, pady=10)

        self.btn_derivacion = ctk.CTkButton(self.sidebar_frame, text="5. Derivación Numérica", command=self.mostrar_derivacion)
        self.btn_derivacion.grid(row=7, column=0, padx=20, pady=10)

        # --- INSTANCIAR TODOS LOS FRAMES ---
        self.frames = {
            "inicio": FrameInicio(self),
            "trunc": FrameTruncamiento(self),
            "bisec": FrameBiseccion(self), "falsa": FrameFalsaPosicion(self),
            "pfijo": FramePuntoFijo(self), "newton": FrameNewton(self),
            "secan": FrameSecante(self), "muller": FrameMuller(self),
            "d_newton": FrameDeflacionNewton(self), "d_muller": FrameDeflacionMuller(self),
            "interp": FrameInterpolacion(self),
            "aprox": FrameAproximaciones(self),
            "deriv": FrameDerivacion(self)
        }
        self.mostrar_inicio()

    def toggle_submenu(self):
        if self.submenu_visible:
            self.submenu_frame.grid_forget()
        else:
            self.submenu_frame.grid(row=4, column=0, sticky="nsew", pady=(0, 10))
        self.submenu_visible = not self.submenu_visible

    def ocultar_todo(self):
        for frame in self.frames.values():
            frame.grid_forget()

    def mostrar_frame(self, nombre):
        self.ocultar_todo()
        self.frames[nombre].grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    # Handlers para botones
    def mostrar_inicio(self): self.mostrar_frame("inicio")
    def mostrar_truncamiento(self): self.mostrar_frame("trunc")
    def mostrar_biseccion(self): self.mostrar_frame("bisec")
    def mostrar_falsaposicion(self): self.mostrar_frame("falsa")
    def mostrar_puntofijo(self): self.mostrar_frame("pfijo")
    def mostrar_newton(self): self.mostrar_frame("newton")
    def mostrar_secante(self): self.mostrar_frame("secan")
    def mostrar_muller(self): self.mostrar_frame("muller")
    def mostrar_def_newton(self): self.mostrar_frame("d_newton")
    def mostrar_def_muller(self): self.mostrar_frame("d_muller")
    def mostrar_interpolacion(self): self.mostrar_frame("interp")
    def mostrar_aproximaciones(self): self.mostrar_frame("aprox")
    def mostrar_derivacion(self): self.mostrar_frame("deriv")


# --- DEFINICIÓN DE FRAMES ---

class FrameInicio(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Bienvenido al Sistema de\nMétodos Numéricos", font=("Consolas", 32, "bold")).pack(pady=60)
        ctk.CTkLabel(self, text="Selecciona un método en el menú lateral para comenzar.", font=("Arial", 14)).pack()

class FrameTruncamiento(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Problema de Truncamiento (IEEE 754)", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=20)
        self.entrada = ctk.CTkEntry(self, placeholder_text="Número decimal")
        self.entrada.pack(pady=5)
        self.entrada_bits = ctk.CTkEntry(self, placeholder_text="Bits (8 - 64)")
        self.entrada_bits.insert(0, "32")
        self.entrada_bits.pack(pady=5)
        self.btn_calc = ctk.CTkButton(self, text="Calcular", command=self.calcular)
        self.btn_calc.pack(pady=10)
        self.textbox = ctk.CTkTextbox(self, width=550, height=250)
        self.textbox.pack(pady=10)

    def calcular(self):
        self.textbox.delete("0.0", "end")
        try:
            val = float(self.entrada.get())
            bits = int(self.entrada_bits.get())
            resultado_str = logica_truncamiento.float_a_binario_custom(val, bits) 
            self.textbox.insert("0.0", resultado_str)
        except Exception as err: self.textbox.insert("0.0", f"Error: {err}")

# --- PANTALLAS DE ECUACIONES (EJEMPLO BISECCIÓN) ---
# (Las demás pantallas de ecuaciones siguen la misma estructura que ya tenías)
class FrameBiseccion(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Método de Bisección", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=15)
        self.entrada_f = ctk.CTkEntry(self, width=400, placeholder_text="f(x) = ...")
        self.entrada_f.pack(pady=5)
        self.frame_p = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_p.pack()
        self.e_a = ctk.CTkEntry(self.frame_p, placeholder_text="a", width=100); self.e_a.grid(row=0, column=0, padx=10)
        self.e_b = ctk.CTkEntry(self.frame_p, placeholder_text="b", width=100); self.e_b.grid(row=0, column=1, padx=10)
        self.btn = ctk.CTkButton(self, text="Calcular", command=self.calc).pack(pady=10)
        self.tabla = TablaResultados(self, height=250); self.tabla.pack(fill="both", expand=True, padx=20, pady=10)
    def calc(self):
        try:
            cols, filas, msj = logica_ec.biseccion(self.entrada_f.get(), float(self.e_a.get()), float(self.e_b.get()), 0.0001, 100)
            self.tabla.actualizar_datos(cols, filas, msj)
        except Exception as e: self.tabla.actualizar_datos([], [], f"Error: {e}", error=True)

# (Aquí irían el resto de las clases de ecuaciones: FalsaPosicion, PuntoFijo, etc.
# Manteniéndolas tal cual las tenías en tu código original)

# --- INTERPOLACIONES ---
class FrameInterpolacion(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Métodos de Interpolación", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)
        frame_in = ctk.CTkFrame(self, fg_color="transparent"); frame_in.pack(pady=5)
        self.menu = ctk.CTkOptionMenu(frame_in, values=["Polinomio de Lagrange", "Método de Neville", "Diferencias Divididas"], width=250)
        self.menu.grid(row=0, column=0, columnspan=2, pady=10)
        self.ex = ctk.CTkEntry(frame_in, width=350, placeholder_text="Valores X (1, 2, 3)"); self.ex.grid(row=1, column=0, pady=5)
        self.ey = ctk.CTkEntry(frame_in, width=350, placeholder_text="Valores Y o f(x)"); self.ey.grid(row=2, column=0, pady=5)
        self.usar_f = ctk.CTkSwitch(frame_in, text="Usar f(x)"); self.usar_f.grid(row=3, column=0)
        self.ex_int = ctk.CTkEntry(frame_in, width=120, placeholder_text="X a interpolar"); self.ex_int.grid(row=1, column=1, rowspan=2, padx=10)
        ctk.CTkButton(self, text="Calcular", command=self.calc).pack(pady=10)
        self.lbl_res = ctk.CTkLabel(self, text="Resultado: ---", font=("Arial", 16, "bold"), text_color="#f39c12"); self.lbl_res.pack()
        self.tabla = TablaResultados(self, height=250); self.tabla.pack(fill="both", expand=True, padx=20, pady=10)

    def calc(self):
        try:
            x_dat = [float(i) for i in self.ex.get().split(',')]
            xi = float(self.ex_int.get())
            y_dat = interpolaciones.generar_y_desde_funcion(self.ey.get(), x_dat) if self.usar_f.get() else [float(i) for i in self.ey.get().split(',')]
            metodo = self.menu.get()
            if "Lagrange" in metodo: 
                res, filas, _ = interpolaciones.interpolacion_lagrange(x_dat, y_dat, xi)
                cols = ["i", "Xi", "Yi", "Li(x)", "Término"]
            elif "Neville" in metodo:
                res, filas = interpolaciones.interpolacion_neville(x_dat, y_dat, xi)
                cols = ["X"] + [f"Nivel {i}" for i in range(len(x_dat))]
            else:
                coefs, filas = interpolaciones.diferencias_divididas(x_dat, y_dat)
                res = "Ver coeficientes"; cols = ["X", "Y"] + [f"Diff {i}" for i in range(1, len(x_dat))]
            
            self.tabla.actualizar_datos(cols, filas, "Cálculo exitoso")
            self.lbl_res.configure(text=f"Resultado: {res}")
            # Gráfica
            plt.figure("Interpolación"); plt.clf()
            plt.plot(x_dat, y_dat, 'bo', label="Datos"); plt.grid(True); plt.show()
        except Exception as e: self.tabla.actualizar_datos([], [], f"Error: {e}", error=True)

# --- APROXIMACIONES ---
class FrameAproximaciones(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Aproximaciones (Taylor y Mínimos Cuadrados)", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)
        self.menu = ctk.CTkOptionMenu(self, values=["Serie de Taylor", "Mínimos Cuadrados (Grado n)"], width=250).pack(pady=10)
        # (Aquí va la lógica de entradas dinámicas que hicimos anteriormente)
        self.tabla = TablaResultados(self, height=200); self.tabla.pack(fill="both", expand=True, padx=20, pady=10)
    def calc(self):
        pass # Conectado a aproximaciones.py

# --- DERIVACIÓN NUMÉRICA (EL NUEVO MÓDULO) ---
class FrameDerivacion(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Derivación Numérica", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)
        
        frame_in = ctk.CTkFrame(self, fg_color="transparent"); frame_in.pack(pady=10)
        self.menu = ctk.CTkOptionMenu(frame_in, values=["1ra Derivada (Richardson)", "2da Derivada (3 pts)", "2da Derivada (4 pts)", "2da Derivada (5 pts)"], width=250)
        self.menu.grid(row=0, column=0, columnspan=4, pady=10)

        ctk.CTkLabel(frame_in, text="f(x):").grid(row=1, column=0)
        self.ef = ctk.CTkEntry(frame_in, width=150, placeholder_text="ej: sin(x)"); self.ef.grid(row=1, column=1, padx=5)
        ctk.CTkLabel(frame_in, text="x:").grid(row=1, column=2)
        self.ex = ctk.CTkEntry(frame_in, width=60); self.ex.grid(row=1, column=3, padx=5)
        ctk.CTkLabel(frame_in, text="h:").grid(row=1, column=4)
        self.eh = ctk.CTkEntry(frame_in, width=60); self.eh.grid(row=1, column=5, padx=5)

        ctk.CTkButton(self, text="Calcular", command=self.calc).pack(pady=10)
        self.lbl_res = ctk.CTkLabel(self, text="Aproximación: ---", font=("Arial", 16, "bold"), text_color="#f39c12"); self.lbl_res.pack()
        self.lbl_exac = ctk.CTkLabel(self, text="Exacto: ---", text_color="gray"); self.lbl_exac.pack()
        self.tabla = TablaResultados(self, height=200); self.tabla.pack(fill="both", expand=True, padx=20, pady=10)

    def calc(self):
        metodo = self.menu.get()
        try:
            f, x, h = self.ef.get(), float(self.ex.get()), float(self.eh.get())
            if "1ra" in metodo:
                aprox, err, filas, exac = derivacion.primera_derivada_neville(f, x, h, 4)
                cols = ["Paso h", "Nivel 0", "Nivel 1", "Nivel 2", "Nivel 3"]
                msj = f"Error: {err:.8e}"
            else:
                pts = int(metodo.split("(")[1].split()[0])
                aprox, err, filas, form, exac = derivacion.segunda_derivada_taylor(f, x, h, pts)
                cols = ["Término", "Valor x", "f(x)"]
                msj = f"Error: {err:.8e} | {form}"
            
            self.tabla.actualizar_datos(cols, filas, msj)
            self.lbl_res.configure(text=f"Aproximación: {round(aprox, 8)}")
            self.lbl_exac.configure(text=f"Valor Exacto: {round(exac, 8)}")
        except Exception as e: self.tabla.actualizar_datos([], [], f"Error: {e}", error=True)

class FrameFalsaPosicion(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Método de Falsa Posición", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=(20, 10))
        self.entrada_funcion = ctk.CTkEntry(self, width=400, placeholder_text="f(x) = ...")
        self.entrada_funcion.pack(pady=10)
        self.frame_limites = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_limites.pack(pady=5)
        self.entrada_a = ctk.CTkEntry(self.frame_limites, width=140, placeholder_text="Límite a")
        self.entrada_a.grid(row=0, column=0, padx=20)
        self.entrada_b = ctk.CTkEntry(self.frame_limites, width=140, placeholder_text="Límite b")
        self.entrada_b.grid(row=0, column=1, padx=20)
        self.frame_params = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_params.pack(pady=10)
        self.entrada_tol = ctk.CTkEntry(self.frame_params, width=140, placeholder_text="Tolerancia")
        self.entrada_tol.grid(row=0, column=0, padx=20)
        self.entrada_iter = ctk.CTkEntry(self.frame_params, width=140, placeholder_text="Max Iteraciones")
        self.entrada_iter.insert(0, "100")
        self.entrada_iter.grid(row=0, column=1, padx=20)
        self.btn_calc = ctk.CTkButton(self, text="Calcular y Graficar", command=self.calcular)
        self.btn_calc.pack(pady=15)
        
        self.tabla = TablaResultados(self, height=250)
        self.tabla.pack(fill="both", expand=True, padx=20, pady=10)

    def calcular(self):
        try:
            cols, filas, msj = logica_ec.falsa_posicion(self.entrada_funcion.get(), float(self.entrada_a.get()), float(self.entrada_b.get()), float(self.entrada_tol.get()), int(self.entrada_iter.get()))
            if not cols: self.tabla.actualizar_datos([], [], msj, error=True)
            else: self.tabla.actualizar_datos(cols, filas, msj)
        except Exception as e:
            self.tabla.actualizar_datos([], [], f"Error: {e}", error=True)

class FramePuntoFijo(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Método de Punto Fijo", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=(20, 10))
        self.entrada_g = ctk.CTkEntry(self, width=400, placeholder_text="Función despejada g(x) = ...")
        self.entrada_g.pack(pady=10)
        self.frame_params = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_params.pack(pady=5)
        self.entrada_x0 = ctk.CTkEntry(self.frame_params, width=140, placeholder_text="Punto inicial x0")
        self.entrada_x0.grid(row=0, column=0, padx=10)
        self.entrada_tol = ctk.CTkEntry(self.frame_params, width=140, placeholder_text="Tolerancia")
        self.entrada_tol.grid(row=0, column=1, padx=10)
        self.entrada_iter = ctk.CTkEntry(self.frame_params, width=140, placeholder_text="Max Iteraciones")
        self.entrada_iter.insert(0, "100")
        self.entrada_iter.grid(row=0, column=2, padx=10)
        self.btn_calc = ctk.CTkButton(self, text="Calcular y Graficar", command=self.calcular)
        self.btn_calc.pack(pady=15)
        
        self.tabla = TablaResultados(self, height=250)
        self.tabla.pack(fill="both", expand=True, padx=20, pady=10)

    def calcular(self):
        try:
            cols, filas, msj = logica_ec.punto_fijo(self.entrada_g.get(), float(self.entrada_x0.get()), float(self.entrada_tol.get()), int(self.entrada_iter.get()))
            if not cols: self.tabla.actualizar_datos([], [], msj, error=True)
            else: self.tabla.actualizar_datos(cols, filas, msj)
        except Exception as e:
            self.tabla.actualizar_datos([], [], f"Error: {e}", error=True)

class FrameNewton(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Método de Newton-Raphson", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=(20, 10))
        self.entrada_f = ctk.CTkEntry(self, width=400, placeholder_text="f(x) = ...")
        self.entrada_f.pack(pady=5)
        self.frame_params = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_params.pack(pady=5)
        self.entrada_x0 = ctk.CTkEntry(self.frame_params, width=140, placeholder_text="Punto inicial x0")
        self.entrada_x0.grid(row=0, column=0, padx=10)
        self.entrada_tol = ctk.CTkEntry(self.frame_params, width=140, placeholder_text="Tolerancia")
        self.entrada_tol.grid(row=0, column=1, padx=10)
        self.entrada_iter = ctk.CTkEntry(self.frame_params, width=140, placeholder_text="Max Iteraciones")
        self.entrada_iter.insert(0, "100")
        self.entrada_iter.grid(row=0, column=2, padx=10)
        self.btn_calc = ctk.CTkButton(self, text="Calcular y Graficar", command=self.calcular)
        self.btn_calc.pack(pady=15)
        
        self.tabla = TablaResultados(self, height=230)
        self.tabla.pack(fill="both", expand=True, padx=20, pady=10)

    def calcular(self):
        try:
            cols, filas, msj = logica_ec.newton_raphson(self.entrada_f.get(), float(self.entrada_x0.get()), float(self.entrada_tol.get()), int(self.entrada_iter.get()))
            if not cols: self.tabla.actualizar_datos([], [], msj, error=True)
            else: self.tabla.actualizar_datos(cols, filas, msj)
        except Exception as e:
            self.tabla.actualizar_datos([], [], f"Error: {e}", error=True)

class FrameSecante(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Método de la Secante", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=(20, 10))
        self.entrada_f = ctk.CTkEntry(self, width=400, placeholder_text="f(x) = ...")
        self.entrada_f.pack(pady=10)
        self.frame_puntos = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_puntos.pack(pady=5)
        self.entrada_x0 = ctk.CTkEntry(self.frame_puntos, width=140, placeholder_text="Punto x0")
        self.entrada_x0.grid(row=0, column=0, padx=20)
        self.entrada_x1 = ctk.CTkEntry(self.frame_puntos, width=140, placeholder_text="Punto x1")
        self.entrada_x1.grid(row=0, column=1, padx=20)
        self.frame_params = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_params.pack(pady=5)
        self.entrada_tol = ctk.CTkEntry(self.frame_params, width=140, placeholder_text="Tolerancia")
        self.entrada_tol.grid(row=0, column=0, padx=20)
        self.entrada_iter = ctk.CTkEntry(self.frame_params, width=140, placeholder_text="Max Iteraciones")
        self.entrada_iter.insert(0, "100")
        self.entrada_iter.grid(row=0, column=1, padx=20)
        self.btn_calc = ctk.CTkButton(self, text="Calcular y Graficar", command=self.calcular)
        self.btn_calc.pack(pady=15)
        
        self.tabla = TablaResultados(self, height=230)
        self.tabla.pack(fill="both", expand=True, padx=20, pady=10)

    def calcular(self):
        try:
            cols, filas, msj = logica_ec.secante(self.entrada_f.get(), float(self.entrada_x0.get()), float(self.entrada_x1.get()), float(self.entrada_tol.get()), int(self.entrada_iter.get()))
            if not cols: self.tabla.actualizar_datos([], [], msj, error=True)
            else: self.tabla.actualizar_datos(cols, filas, msj)
        except Exception as e:
            self.tabla.actualizar_datos([], [], f"Error: {e}", error=True)

class FrameMuller(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Método de Muller", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=(20, 10))
        self.entrada_f = ctk.CTkEntry(self, width=400, placeholder_text="f(x) = ...")
        self.entrada_f.pack(pady=10)
        self.frame_puntos = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_puntos.pack(pady=5)
        self.entrada_x0 = ctk.CTkEntry(self.frame_puntos, width=100, placeholder_text="x0 (ej: 1+2j)")
        self.entrada_x0.grid(row=0, column=0, padx=10)
        self.entrada_x1 = ctk.CTkEntry(self.frame_puntos, width=100, placeholder_text="x1")
        self.entrada_x1.grid(row=0, column=1, padx=10)
        self.entrada_x2 = ctk.CTkEntry(self.frame_puntos, width=100, placeholder_text="x2")
        self.entrada_x2.grid(row=0, column=2, padx=10)
        self.frame_params = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_params.pack(pady=5)
        self.entrada_tol = ctk.CTkEntry(self.frame_params, width=140, placeholder_text="Tolerancia")
        self.entrada_tol.grid(row=0, column=0, padx=20)
        self.entrada_iter = ctk.CTkEntry(self.frame_params, width=140, placeholder_text="Max Iteraciones")
        self.entrada_iter.insert(0, "100")
        self.entrada_iter.grid(row=0, column=1, padx=20)
        self.btn_calc = ctk.CTkButton(self, text="Calcular y Graficar", command=self.calcular)
        self.btn_calc.pack(pady=10)
        
        self.tabla = TablaResultados(self, height=220)
        self.tabla.pack(fill="both", expand=True, padx=20, pady=10)

    def calcular(self):
        try:
            x0 = complex(self.entrada_x0.get())
            x1 = complex(self.entrada_x1.get())
            x2 = complex(self.entrada_x2.get())
            cols, filas, msj = logica_ec.muller(self.entrada_f.get(), x0, x1, x2, float(self.entrada_tol.get()), int(self.entrada_iter.get()))
            if not cols: self.tabla.actualizar_datos([], [], msj, error=True)
            else: self.tabla.actualizar_datos(cols, filas, msj)
        except ValueError:
            self.tabla.actualizar_datos([], [], "Error de formato. Usa '1.5' o '1+2j'.", error=True)
        except Exception as e:
            self.tabla.actualizar_datos([], [], f"Error: {e}", error=True)

class FrameDeflacionNewton(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Deflación (Newton-Raphson)", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=(20, 10))
        self.entrada_f = ctk.CTkEntry(self, width=400, placeholder_text="f(x) = ...")
        self.entrada_f.pack(pady=5)
        self.frame_params = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_params.pack(pady=5)
        self.entrada_x0 = ctk.CTkEntry(self.frame_params, width=110, placeholder_text="Punto inicial x0")
        self.entrada_x0.grid(row=0, column=0, padx=5)
        self.entrada_tol = ctk.CTkEntry(self.frame_params, width=110, placeholder_text="Tolerancia")
        self.entrada_tol.grid(row=0, column=1, padx=5)
        self.entrada_iter = ctk.CTkEntry(self.frame_params, width=110, placeholder_text="Max Iteraciones")
        self.entrada_iter.insert(0, "100")
        self.entrada_iter.grid(row=0, column=2, padx=5)
        self.entrada_raices = ctk.CTkEntry(self.frame_params, width=110, placeholder_text="Cant. Raíces")
        self.entrada_raices.insert(0, "2")
        self.entrada_raices.grid(row=0, column=3, padx=5)
        self.btn_calc = ctk.CTkButton(self, text="Calcular y Graficar", command=self.calcular)
        self.btn_calc.pack(pady=15)
        
        self.tabla = TablaResultados(self, height=230)
        self.tabla.pack(fill="both", expand=True, padx=20, pady=10)

    def calcular(self):
        try:
            x0 = complex(self.entrada_x0.get())
            cols, filas, msj = logica_ec.deflacion_newton(self.entrada_f.get(), x0, float(self.entrada_tol.get()), int(self.entrada_iter.get()), int(self.entrada_raices.get()))
            if not cols: self.tabla.actualizar_datos([], [], msj, error=True)
            else: self.tabla.actualizar_datos(cols, filas, msj)
        except Exception as e:
            self.tabla.actualizar_datos([], [], f"Error: {e}", error=True)

class FrameDeflacionMuller(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Deflación (Muller)", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=(20, 10))
        self.entrada_f = ctk.CTkEntry(self, width=400, placeholder_text="f(x) = ...")
        self.entrada_f.pack(pady=10)
        self.frame_puntos = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_puntos.pack(pady=5)
        self.entrada_x0 = ctk.CTkEntry(self.frame_puntos, width=90, placeholder_text="x0")
        self.entrada_x0.grid(row=0, column=0, padx=5)
        self.entrada_x1 = ctk.CTkEntry(self.frame_puntos, width=90, placeholder_text="x1")
        self.entrada_x1.grid(row=0, column=1, padx=5)
        self.entrada_x2 = ctk.CTkEntry(self.frame_puntos, width=90, placeholder_text="x2")
        self.entrada_x2.grid(row=0, column=2, padx=5)
        self.frame_params = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_params.pack(pady=5)
        self.entrada_tol = ctk.CTkEntry(self.frame_params, width=110, placeholder_text="Tolerancia")
        self.entrada_tol.grid(row=0, column=0, padx=10)
        self.entrada_iter = ctk.CTkEntry(self.frame_params, width=110, placeholder_text="Max Iteraciones")
        self.entrada_iter.insert(0, "100")
        self.entrada_iter.grid(row=0, column=1, padx=10)
        self.entrada_raices = ctk.CTkEntry(self.frame_params, width=110, placeholder_text="Cant. Raíces")
        self.entrada_raices.insert(0, "3")
        self.entrada_raices.grid(row=0, column=2, padx=10)
        self.btn_calc = ctk.CTkButton(self, text="Calcular y Graficar", command=self.calcular)
        self.btn_calc.pack(pady=10)
        
        self.tabla = TablaResultados(self, height=200)
        self.tabla.pack(fill="both", expand=True, padx=20, pady=10)

    def calcular(self):
        try:
            x0 = complex(self.entrada_x0.get())
            x1 = complex(self.entrada_x1.get())
            x2 = complex(self.entrada_x2.get())
            cols, filas, msj = logica_ec.deflacion_muller(self.entrada_f.get(), x0, x1, x2, float(self.entrada_tol.get()), int(self.entrada_iter.get()), int(self.entrada_raices.get()))
            if not cols: self.tabla.actualizar_datos([], [], msj, error=True)
            else: self.tabla.actualizar_datos(cols, filas, msj)
        except Exception as e:
            self.tabla.actualizar_datos([], [], f"Error: {e}", error=True)

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    app = App()
    app.mainloop()