import customtkinter as ctk
import tkinter.ttk as ttk
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation

# --- IMPORTACIÓN DE MÓDULOS BACKEND ---
import PROBLEMA_TRUNCAMIENTO as logica_truncamiento 
import logica_ecuaciones as logica_ec 
import interpolaciones 
import aproximaciones 
import derivacion 
import integracion
import integracion_multivariable
import edos
import pendulo
import algebra_lineal

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
        self.title("Métodos Numéricos")
        self.geometry("1100x750")
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- MENÚ LATERAL ---
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(12, weight=1) # Empuja los botones hacia arriba

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

        self.btn_integracion = ctk.CTkButton(self.sidebar_frame, text="6. Integración Numérica", command=self.mostrar_integracion)
        self.btn_integracion.grid(row=8, column=0, padx=20, pady=10)
        
        self.btn_edos = ctk.CTkButton(self.sidebar_frame, text="7. Ecuaciones Diferenciales", command=self.mostrar_edos)
        self.btn_edos.grid(row=9, column=0, padx=20, pady=10)

        self.btn_pendulo = ctk.CTkButton(self.sidebar_frame, text="8. Simulador Péndulo", command=self.mostrar_pendulo)
        self.btn_pendulo.grid(row=10, column=0, padx=20, pady=10)
        
        self.btn_algebra = ctk.CTkButton(self.sidebar_frame, text="9. Álgebra Lineal", command=self.mostrar_algebra)
        self.btn_algebra.grid(row=11, column=0, padx=20, pady=10)

        # --- INSTANCIAR TODOS LOS FRAMES EN UN DICCIONARIO ---
        self.frames = {
            "inicio": FrameInicio(self),
            "trunc": FrameTruncamiento(self),
            "bisec": FrameBiseccion(self), "falsa": FrameFalsaPosicion(self),
            "pfijo": FramePuntoFijo(self), "newton": FrameNewton(self),
            "secan": FrameSecante(self), "muller": FrameMuller(self),
            "d_newton": FrameDeflacionNewton(self), "d_muller": FrameDeflacionMuller(self),
            "interp": FrameInterpolacion(self),
            "aprox": FrameAproximaciones(self),
            "deriv": FrameDerivacion(self),
            "integ": FrameIntegracion(self),
            "edos": FrameEDOs(self),       
            "pendulo": FramePendulo(self),
            "algebra": FrameAlgebraLineal(self)
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
    def mostrar_integracion(self): self.mostrar_frame("integ")
    def mostrar_edos(self): self.mostrar_frame("edos")
    def mostrar_pendulo(self): self.mostrar_frame("pendulo")
    def mostrar_algebra(self): self.mostrar_frame("algebra")


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
        self.lbl_titulo.pack(pady=15)
        
        frame_in = ctk.CTkFrame(self, fg_color="transparent")
        frame_in.pack(pady=5)
        
        ctk.CTkLabel(frame_in, text="Número decimal:").grid(row=0, column=0, padx=5)
        self.entrada = ctk.CTkEntry(frame_in, placeholder_text="ej: -15.625", width=150)
        self.entrada.grid(row=0, column=1, padx=5)
        
        ctk.CTkLabel(frame_in, text="Precisión:").grid(row=0, column=2, padx=5)
        self.menu_bits = ctk.CTkOptionMenu(frame_in, values=["32 bits (Simple)", "64 bits (Doble)"], width=150)
        self.menu_bits.grid(row=0, column=3, padx=5)
        
        self.btn_calc = ctk.CTkButton(self, text="Calcular IEEE 754", command=self.calcular)
        self.btn_calc.pack(pady=15)

        #self.lbl_hex = ctk.CTkLabel(self, text="Hexadecimal: ---", font=("Arial", 16, "bold"), text_color="#f39c12")
        #self.lbl_hex.pack(pady=2)
        self.lbl_bin = ctk.CTkLabel(self, text="Binario: ---", font=("Consolas", 14), text_color="gray")
        self.lbl_bin.pack(pady=(2, 10))
        
        self.tabla = TablaResultados(self, height=180)
        self.tabla.pack(fill="both", expand=True, padx=20, pady=10)

    def calcular(self):
        try:
            num = float(self.entrada.get())
            bits = 32 if "32" in self.menu_bits.get() else 64
            datos, msj = logica_truncamiento.calcular_ieee754(num, bits)
            
            if not datos:
                self.tabla.actualizar_datos([], [], msj, error=True)
                return
            
            cols = ["Componente", "Valor Binario", "Longitud", "Significado Matemático"]
            filas = [
                ["Signo", datos['signo'], "1 bit", datos['sig_signo']],
                ["Característica", datos['caracteristica'], f"{len(datos['caracteristica'])} bits", f"Valor: {datos['val_caracteristica']} (Sesgo: {datos['sesgo']})"],
                ["Mantisa", datos['mantisa'], f"{len(datos['mantisa'])} bits", "Parte fraccionaria normalizada"]
            ]
            
            self.tabla.actualizar_datos(cols, filas, f"Conversión IEEE 754 a {bits} bits calculada.")
            #self.lbl_hex.configure(text=f"Hexadecimal: {datos['hexadecimal']}")
            bin_legible = f"{datos['signo']} - {datos['caracteristica']} - {datos['mantisa']}"
            self.lbl_bin.configure(text=f"Binario: {bin_legible}")

        except ValueError:
            self.tabla.actualizar_datos([], [], "Ingresa un decimal válido.", error=True)
        except Exception as e:
            self.tabla.actualizar_datos([], [], f"Error: {e}", error=True)

# --- ECUACIONES ---
class FrameBiseccion(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Método de Bisección", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=(20, 10))
        self.frame_inputs = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inputs.pack(pady=5)
        ctk.CTkLabel(self.frame_inputs, text="Función f(x):", text_color="gray").grid(row=0, column=0, columnspan=2, padx=10, sticky="w")
        self.entrada_funcion = ctk.CTkEntry(self.frame_inputs, width=300, placeholder_text="ej: x**3 - x - 2")
        self.entrada_funcion.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="w")
        ctk.CTkLabel(self.frame_inputs, text="Límite [a]:", text_color="gray").grid(row=2, column=0, padx=10, sticky="w")
        self.entrada_a = ctk.CTkEntry(self.frame_inputs, width=140)
        self.entrada_a.grid(row=3, column=0, padx=10, pady=(0, 10))
        ctk.CTkLabel(self.frame_inputs, text="Límite [b]:", text_color="gray").grid(row=2, column=1, padx=10, sticky="w")
        self.entrada_b = ctk.CTkEntry(self.frame_inputs, width=140)
        self.entrada_b.grid(row=3, column=1, padx=10, pady=(0, 10))
        ctk.CTkLabel(self.frame_inputs, text="Tolerancia:", text_color="gray").grid(row=4, column=0, padx=10, sticky="w")
        self.entrada_tol = ctk.CTkEntry(self.frame_inputs, width=140, placeholder_text="ej: 0.0001")
        self.entrada_tol.grid(row=5, column=0, padx=10, pady=(0, 10))
        ctk.CTkLabel(self.frame_inputs, text="Max Iteraciones:", text_color="gray").grid(row=4, column=1, padx=10, sticky="w")
        self.entrada_iter = ctk.CTkEntry(self.frame_inputs, width=140)
        self.entrada_iter.insert(0, "100")
        self.entrada_iter.grid(row=5, column=1, padx=10, pady=(0, 10))
        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.pack(pady=5)
        self.btn_calc = ctk.CTkButton(self.frame_botones, text="Calcular", command=self.calcular, fg_color="#28a745", hover_color="#218838")
        self.btn_calc.pack(side="left", padx=10)
        self.btn_limpiar = ctk.CTkButton(self.frame_botones, text="Limpiar", command=self.limpiar, fg_color="#dc3545", hover_color="#c82333", width=80)
        self.btn_limpiar.pack(side="left", padx=10)
        self.tabla = TablaResultados(self, height=220)
        self.tabla.pack(fill="both", expand=True, padx=20, pady=10)

    def limpiar(self):
        self.entrada_funcion.delete(0, 'end'); self.entrada_a.delete(0, 'end'); self.entrada_b.delete(0, 'end')
        self.entrada_tol.delete(0, 'end'); self.entrada_iter.delete(0, 'end'); self.entrada_iter.insert(0, "100")
        self.tabla.actualizar_datos([], [], "")

    def calcular(self):
        try:
            cols, filas, msj = logica_ec.biseccion(self.entrada_funcion.get(), float(self.entrada_a.get()), float(self.entrada_b.get()), float(self.entrada_tol.get()), int(self.entrada_iter.get()))
            if not cols: self.tabla.actualizar_datos([], [], msj, error=True)
            else: self.tabla.actualizar_datos(cols, filas, msj)
        except Exception as e: self.tabla.actualizar_datos([], [], f"Error: {e}", error=True)

class FrameFalsaPosicion(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Método de Falsa Posición", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=(20, 10))
        self.frame_inputs = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inputs.pack(pady=5)
        ctk.CTkLabel(self.frame_inputs, text="Función f(x):", text_color="gray").grid(row=0, column=0, columnspan=2, padx=10, sticky="w")
        self.entrada_funcion = ctk.CTkEntry(self.frame_inputs, width=300)
        self.entrada_funcion.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="w")
        ctk.CTkLabel(self.frame_inputs, text="Límite [a]:", text_color="gray").grid(row=2, column=0, padx=10, sticky="w")
        self.entrada_a = ctk.CTkEntry(self.frame_inputs, width=140)
        self.entrada_a.grid(row=3, column=0, padx=10, pady=(0, 10))
        ctk.CTkLabel(self.frame_inputs, text="Límite [b]:", text_color="gray").grid(row=2, column=1, padx=10, sticky="w")
        self.entrada_b = ctk.CTkEntry(self.frame_inputs, width=140)
        self.entrada_b.grid(row=3, column=1, padx=10, pady=(0, 10))
        ctk.CTkLabel(self.frame_inputs, text="Tolerancia:", text_color="gray").grid(row=4, column=0, padx=10, sticky="w")
        self.entrada_tol = ctk.CTkEntry(self.frame_inputs, width=140)
        self.entrada_tol.grid(row=5, column=0, padx=10, pady=(0, 10))
        ctk.CTkLabel(self.frame_inputs, text="Max Iteraciones:", text_color="gray").grid(row=4, column=1, padx=10, sticky="w")
        self.entrada_iter = ctk.CTkEntry(self.frame_inputs, width=140)
        self.entrada_iter.insert(0, "100")
        self.entrada_iter.grid(row=5, column=1, padx=10, pady=(0, 10))
        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.pack(pady=5)
        self.btn_calc = ctk.CTkButton(self.frame_botones, text="Calcular", command=self.calcular, fg_color="#28a745", hover_color="#218838")
        self.btn_calc.pack(side="left", padx=10)
        self.btn_limpiar = ctk.CTkButton(self.frame_botones, text="Limpiar", command=self.limpiar, fg_color="#dc3545", hover_color="#c82333", width=80)
        self.btn_limpiar.pack(side="left", padx=10)
        self.tabla = TablaResultados(self, height=220)
        self.tabla.pack(fill="both", expand=True, padx=20, pady=10)

    def limpiar(self):
        self.entrada_funcion.delete(0, 'end'); self.entrada_a.delete(0, 'end'); self.entrada_b.delete(0, 'end')
        self.entrada_tol.delete(0, 'end'); self.entrada_iter.delete(0, 'end'); self.entrada_iter.insert(0, "100")
        self.tabla.actualizar_datos([], [], "")

    def calcular(self):
        try:
            cols, filas, msj = logica_ec.falsa_posicion(self.entrada_funcion.get(), float(self.entrada_a.get()), float(self.entrada_b.get()), float(self.entrada_tol.get()), int(self.entrada_iter.get()))
            if not cols: self.tabla.actualizar_datos([], [], msj, error=True)
            else: self.tabla.actualizar_datos(cols, filas, msj)
        except Exception as e: self.tabla.actualizar_datos([], [], f"Error: {e}", error=True)

class FramePuntoFijo(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Método de Punto Fijo", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=(20, 10))
        self.frame_inputs = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inputs.pack(pady=5)
        ctk.CTkLabel(self.frame_inputs, text="Función despejada g(x):", text_color="gray").grid(row=0, column=0, columnspan=3, padx=10, sticky="w")
        self.entrada_g = ctk.CTkEntry(self.frame_inputs, width=300)
        self.entrada_g.grid(row=1, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="w")
        ctk.CTkLabel(self.frame_inputs, text="Punto inicial (x0):", text_color="gray").grid(row=2, column=0, padx=10, sticky="w")
        self.entrada_x0 = ctk.CTkEntry(self.frame_inputs, width=120)
        self.entrada_x0.grid(row=3, column=0, padx=10, pady=(0, 10))
        ctk.CTkLabel(self.frame_inputs, text="Tolerancia:", text_color="gray").grid(row=2, column=1, padx=10, sticky="w")
        self.entrada_tol = ctk.CTkEntry(self.frame_inputs, width=120)
        self.entrada_tol.grid(row=3, column=1, padx=10, pady=(0, 10))
        ctk.CTkLabel(self.frame_inputs, text="Max Iteraciones:", text_color="gray").grid(row=2, column=2, padx=10, sticky="w")
        self.entrada_iter = ctk.CTkEntry(self.frame_inputs, width=120)
        self.entrada_iter.insert(0, "100")
        self.entrada_iter.grid(row=3, column=2, padx=10, pady=(0, 10))
        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.pack(pady=5)
        self.btn_calc = ctk.CTkButton(self.frame_botones, text="Calcular", command=self.calcular, fg_color="#28a745", hover_color="#218838")
        self.btn_calc.pack(side="left", padx=10)
        self.btn_limpiar = ctk.CTkButton(self.frame_botones, text="Limpiar", command=self.limpiar, fg_color="#dc3545", hover_color="#c82333", width=80)
        self.btn_limpiar.pack(side="left", padx=10)
        self.tabla = TablaResultados(self, height=220)
        self.tabla.pack(fill="both", expand=True, padx=20, pady=10)

    def limpiar(self):
        self.entrada_g.delete(0, 'end'); self.entrada_x0.delete(0, 'end'); self.entrada_tol.delete(0, 'end')
        self.entrada_iter.delete(0, 'end'); self.entrada_iter.insert(0, "100")
        self.tabla.actualizar_datos([], [], "")

    def calcular(self):
        try:
            cols, filas, msj = logica_ec.punto_fijo(self.entrada_g.get(), float(self.entrada_x0.get()), float(self.entrada_tol.get()), int(self.entrada_iter.get()))
            if not cols: self.tabla.actualizar_datos([], [], msj, error=True)
            else: self.tabla.actualizar_datos(cols, filas, msj)
        except Exception as e: self.tabla.actualizar_datos([], [], f"Error: {e}", error=True)

class FrameNewton(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Método de Newton-Raphson", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=(20, 10))
        self.frame_inputs = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inputs.pack(pady=5)
        ctk.CTkLabel(self.frame_inputs, text="Función f(x):", text_color="gray").grid(row=0, column=0, columnspan=3, padx=10, sticky="w")
        self.entrada_f = ctk.CTkEntry(self.frame_inputs, width=300)
        self.entrada_f.grid(row=1, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="w")
        ctk.CTkLabel(self.frame_inputs, text="Punto inicial (x0):", text_color="gray").grid(row=2, column=0, padx=10, sticky="w")
        self.entrada_x0 = ctk.CTkEntry(self.frame_inputs, width=120)
        self.entrada_x0.grid(row=3, column=0, padx=10, pady=(0, 10))
        ctk.CTkLabel(self.frame_inputs, text="Tolerancia:", text_color="gray").grid(row=2, column=1, padx=10, sticky="w")
        self.entrada_tol = ctk.CTkEntry(self.frame_inputs, width=120)
        self.entrada_tol.grid(row=3, column=1, padx=10, pady=(0, 10))
        ctk.CTkLabel(self.frame_inputs, text="Max Iteraciones:", text_color="gray").grid(row=2, column=2, padx=10, sticky="w")
        self.entrada_iter = ctk.CTkEntry(self.frame_inputs, width=120)
        self.entrada_iter.insert(0, "100")
        self.entrada_iter.grid(row=3, column=2, padx=10, pady=(0, 10))
        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.pack(pady=5)
        self.btn_calc = ctk.CTkButton(self.frame_botones, text="Calcular", command=self.calcular, fg_color="#28a745", hover_color="#218838")
        self.btn_calc.pack(side="left", padx=10)
        self.btn_limpiar = ctk.CTkButton(self.frame_botones, text="Limpiar", command=self.limpiar, fg_color="#dc3545", hover_color="#c82333", width=80)
        self.btn_limpiar.pack(side="left", padx=10)
        self.tabla = TablaResultados(self, height=220)
        self.tabla.pack(fill="both", expand=True, padx=20, pady=10)

    def limpiar(self):
        self.entrada_f.delete(0, 'end'); self.entrada_x0.delete(0, 'end'); self.entrada_tol.delete(0, 'end')
        self.entrada_iter.delete(0, 'end'); self.entrada_iter.insert(0, "100")
        self.tabla.actualizar_datos([], [], "")

    def calcular(self):
        try:
            cols, filas, msj = logica_ec.newton_raphson(self.entrada_f.get(), float(self.entrada_x0.get()), float(self.entrada_tol.get()), int(self.entrada_iter.get()))
            if not cols: self.tabla.actualizar_datos([], [], msj, error=True)
            else: self.tabla.actualizar_datos(cols, filas, msj)
        except Exception as e: self.tabla.actualizar_datos([], [], f"Error: {e}", error=True)

class FrameSecante(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Método de la Secante", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=(20, 10))
        self.frame_inputs = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inputs.pack(pady=5)
        ctk.CTkLabel(self.frame_inputs, text="Función f(x):", text_color="gray").grid(row=0, column=0, columnspan=2, padx=10, sticky="w")
        self.entrada_f = ctk.CTkEntry(self.frame_inputs, width=300)
        self.entrada_f.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="w")
        ctk.CTkLabel(self.frame_inputs, text="Punto [x0]:", text_color="gray").grid(row=2, column=0, padx=10, sticky="w")
        self.entrada_x0 = ctk.CTkEntry(self.frame_inputs, width=140)
        self.entrada_x0.grid(row=3, column=0, padx=10, pady=(0, 10))
        ctk.CTkLabel(self.frame_inputs, text="Punto [x1]:", text_color="gray").grid(row=2, column=1, padx=10, sticky="w")
        self.entrada_x1 = ctk.CTkEntry(self.frame_inputs, width=140)
        self.entrada_x1.grid(row=3, column=1, padx=10, pady=(0, 10))
        ctk.CTkLabel(self.frame_inputs, text="Tolerancia:", text_color="gray").grid(row=4, column=0, padx=10, sticky="w")
        self.entrada_tol = ctk.CTkEntry(self.frame_inputs, width=140)
        self.entrada_tol.grid(row=5, column=0, padx=10, pady=(0, 10))
        ctk.CTkLabel(self.frame_inputs, text="Max Iteraciones:", text_color="gray").grid(row=4, column=1, padx=10, sticky="w")
        self.entrada_iter = ctk.CTkEntry(self.frame_inputs, width=140)
        self.entrada_iter.insert(0, "100")
        self.entrada_iter.grid(row=5, column=1, padx=10, pady=(0, 10))
        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.pack(pady=5)
        self.btn_calc = ctk.CTkButton(self.frame_botones, text="Calcular", command=self.calcular, fg_color="#28a745", hover_color="#218838")
        self.btn_calc.pack(side="left", padx=10)
        self.btn_limpiar = ctk.CTkButton(self.frame_botones, text="Limpiar", command=self.limpiar, fg_color="#dc3545", hover_color="#c82333", width=80)
        self.btn_limpiar.pack(side="left", padx=10)
        self.tabla = TablaResultados(self, height=220)
        self.tabla.pack(fill="both", expand=True, padx=20, pady=10)

    def limpiar(self):
        self.entrada_f.delete(0, 'end'); self.entrada_x0.delete(0, 'end'); self.entrada_x1.delete(0, 'end')
        self.entrada_tol.delete(0, 'end'); self.entrada_iter.delete(0, 'end'); self.entrada_iter.insert(0, "100")
        self.tabla.actualizar_datos([], [], "")

    def calcular(self):
        try:
            cols, filas, msj = logica_ec.secante(self.entrada_f.get(), float(self.entrada_x0.get()), float(self.entrada_x1.get()), float(self.entrada_tol.get()), int(self.entrada_iter.get()))
            if not cols: self.tabla.actualizar_datos([], [], msj, error=True)
            else: self.tabla.actualizar_datos(cols, filas, msj)
        except Exception as e: self.tabla.actualizar_datos([], [], f"Error: {e}", error=True)

class FrameMuller(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Método de Muller", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=(20, 10))
        self.frame_inputs = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inputs.pack(pady=5)
        ctk.CTkLabel(self.frame_inputs, text="Función f(x):", text_color="gray").grid(row=0, column=0, columnspan=3, padx=10, sticky="w")
        self.entrada_f = ctk.CTkEntry(self.frame_inputs, width=300)
        self.entrada_f.grid(row=1, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="w")
        ctk.CTkLabel(self.frame_inputs, text="[x0] (Complejo ej 1+2j):", text_color="gray").grid(row=2, column=0, padx=10, sticky="w")
        self.entrada_x0 = ctk.CTkEntry(self.frame_inputs, width=100)
        self.entrada_x0.grid(row=3, column=0, padx=10, pady=(0, 10))
        ctk.CTkLabel(self.frame_inputs, text="[x1]:", text_color="gray").grid(row=2, column=1, padx=10, sticky="w")
        self.entrada_x1 = ctk.CTkEntry(self.frame_inputs, width=100)
        self.entrada_x1.grid(row=3, column=1, padx=10, pady=(0, 10))
        ctk.CTkLabel(self.frame_inputs, text="[x2]:", text_color="gray").grid(row=2, column=2, padx=10, sticky="w")
        self.entrada_x2 = ctk.CTkEntry(self.frame_inputs, width=100)
        self.entrada_x2.grid(row=3, column=2, padx=10, pady=(0, 10))
        ctk.CTkLabel(self.frame_inputs, text="Tolerancia:", text_color="gray").grid(row=4, column=0, padx=10, sticky="w")
        self.entrada_tol = ctk.CTkEntry(self.frame_inputs, width=100)
        self.entrada_tol.grid(row=5, column=0, padx=10, pady=(0, 10))
        ctk.CTkLabel(self.frame_inputs, text="Max Iteraciones:", text_color="gray").grid(row=4, column=1, padx=10, sticky="w")
        self.entrada_iter = ctk.CTkEntry(self.frame_inputs, width=100)
        self.entrada_iter.insert(0, "100")
        self.entrada_iter.grid(row=5, column=1, padx=10, pady=(0, 10))
        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.pack(pady=5)
        self.btn_calc = ctk.CTkButton(self.frame_botones, text="Calcular", command=self.calcular, fg_color="#28a745", hover_color="#218838")
        self.btn_calc.pack(side="left", padx=10)
        self.btn_limpiar = ctk.CTkButton(self.frame_botones, text="Limpiar", command=self.limpiar, fg_color="#dc3545", hover_color="#c82333", width=80)
        self.btn_limpiar.pack(side="left", padx=10)
        self.tabla = TablaResultados(self, height=200)
        self.tabla.pack(fill="both", expand=True, padx=20, pady=10)

    def limpiar(self):
        self.entrada_f.delete(0, 'end'); self.entrada_x0.delete(0, 'end'); self.entrada_x1.delete(0, 'end')
        self.entrada_x2.delete(0, 'end'); self.entrada_tol.delete(0, 'end')
        self.entrada_iter.delete(0, 'end'); self.entrada_iter.insert(0, "100")
        self.tabla.actualizar_datos([], [], "")

    def calcular(self):
        try:
            x0, x1, x2 = complex(self.entrada_x0.get()), complex(self.entrada_x1.get()), complex(self.entrada_x2.get())
            cols, filas, msj = logica_ec.muller(self.entrada_f.get(), x0, x1, x2, float(self.entrada_tol.get()), int(self.entrada_iter.get()))
            if not cols: self.tabla.actualizar_datos([], [], msj, error=True)
            else: self.tabla.actualizar_datos(cols, filas, msj)
        except ValueError: self.tabla.actualizar_datos([], [], "Error de formato. Usa '1.5' o '1+2j'.", error=True)
        except Exception as e: self.tabla.actualizar_datos([], [], f"Error: {e}", error=True)

class FrameDeflacionNewton(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Deflación (Newton-Raphson)", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=(20, 10))
        self.frame_inputs = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inputs.pack(pady=5)
        ctk.CTkLabel(self.frame_inputs, text="Función f(x):", text_color="gray").grid(row=0, column=0, columnspan=2, padx=10, sticky="w")
        self.entrada_f = ctk.CTkEntry(self.frame_inputs, width=280)
        self.entrada_f.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="w")
        ctk.CTkLabel(self.frame_inputs, text="Punto inicial (x0):", text_color="gray").grid(row=2, column=0, padx=10, sticky="w")
        self.entrada_x0 = ctk.CTkEntry(self.frame_inputs, width=120)
        self.entrada_x0.grid(row=3, column=0, padx=10, pady=(0, 10))
        ctk.CTkLabel(self.frame_inputs, text="Cant. Raíces:", text_color="gray").grid(row=2, column=1, padx=10, sticky="w")
        self.entrada_raices = ctk.CTkEntry(self.frame_inputs, width=120)
        self.entrada_raices.insert(0, "2")
        self.entrada_raices.grid(row=3, column=1, padx=10, pady=(0, 10))
        ctk.CTkLabel(self.frame_inputs, text="Tolerancia:", text_color="gray").grid(row=4, column=0, padx=10, sticky="w")
        self.entrada_tol = ctk.CTkEntry(self.frame_inputs, width=120)
        self.entrada_tol.grid(row=5, column=0, padx=10, pady=(0, 10))
        ctk.CTkLabel(self.frame_inputs, text="Max Iteraciones:", text_color="gray").grid(row=4, column=1, padx=10, sticky="w")
        self.entrada_iter = ctk.CTkEntry(self.frame_inputs, width=120)
        self.entrada_iter.insert(0, "100")
        self.entrada_iter.grid(row=5, column=1, padx=10, pady=(0, 10))
        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.pack(pady=5)
        self.btn_calc = ctk.CTkButton(self.frame_botones, text="Calcular", command=self.calcular, fg_color="#28a745", hover_color="#218838")
        self.btn_calc.pack(side="left", padx=10)
        self.btn_limpiar = ctk.CTkButton(self.frame_botones, text="Limpiar", command=self.limpiar, fg_color="#dc3545", hover_color="#c82333", width=80)
        self.btn_limpiar.pack(side="left", padx=10)
        self.tabla = TablaResultados(self, height=200)
        self.tabla.pack(fill="both", expand=True, padx=20, pady=10)

    def limpiar(self):
        self.entrada_f.delete(0, 'end'); self.entrada_x0.delete(0, 'end'); self.entrada_raices.delete(0, 'end')
        self.entrada_raices.insert(0, "2"); self.entrada_tol.delete(0, 'end'); self.entrada_iter.delete(0, 'end')
        self.entrada_iter.insert(0, "100"); self.tabla.actualizar_datos([], [], "")

    def calcular(self):
        try:
            x0 = complex(self.entrada_x0.get())
            cols, filas, msj = logica_ec.deflacion_newton(self.entrada_f.get(), x0, float(self.entrada_tol.get()), int(self.entrada_iter.get()), int(self.entrada_raices.get()))
            if not cols: self.tabla.actualizar_datos([], [], msj, error=True)
            else: self.tabla.actualizar_datos(cols, filas, msj)
        except Exception as e: self.tabla.actualizar_datos([], [], f"Error: {e}", error=True)

class FrameDeflacionMuller(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Deflación (Muller)", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=(20, 10))
        self.frame_inputs = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inputs.pack(pady=5)
        ctk.CTkLabel(self.frame_inputs, text="Función f(x):", text_color="gray").grid(row=0, column=0, columnspan=3, padx=10, sticky="w")
        self.entrada_f = ctk.CTkEntry(self.frame_inputs, width=300)
        self.entrada_f.grid(row=1, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="w")
        ctk.CTkLabel(self.frame_inputs, text="[x0]:", text_color="gray").grid(row=2, column=0, padx=10, sticky="w")
        self.entrada_x0 = ctk.CTkEntry(self.frame_inputs, width=90)
        self.entrada_x0.grid(row=3, column=0, padx=10, pady=(0, 10))
        ctk.CTkLabel(self.frame_inputs, text="[x1]:", text_color="gray").grid(row=2, column=1, padx=10, sticky="w")
        self.entrada_x1 = ctk.CTkEntry(self.frame_inputs, width=90)
        self.entrada_x1.grid(row=3, column=1, padx=10, pady=(0, 10))
        ctk.CTkLabel(self.frame_inputs, text="[x2]:", text_color="gray").grid(row=2, column=2, padx=10, sticky="w")
        self.entrada_x2 = ctk.CTkEntry(self.frame_inputs, width=90)
        self.entrada_x2.grid(row=3, column=2, padx=10, pady=(0, 10))
        ctk.CTkLabel(self.frame_inputs, text="Cant. Raíces:", text_color="gray").grid(row=4, column=0, padx=10, sticky="w")
        self.entrada_raices = ctk.CTkEntry(self.frame_inputs, width=90)
        self.entrada_raices.insert(0, "3")
        self.entrada_raices.grid(row=5, column=0, padx=10, pady=(0, 10))
        ctk.CTkLabel(self.frame_inputs, text="Tolerancia:", text_color="gray").grid(row=4, column=1, padx=10, sticky="w")
        self.entrada_tol = ctk.CTkEntry(self.frame_inputs, width=90)
        self.entrada_tol.grid(row=5, column=1, padx=10, pady=(0, 10))
        ctk.CTkLabel(self.frame_inputs, text="Iteraciones:", text_color="gray").grid(row=4, column=2, padx=10, sticky="w")
        self.entrada_iter = ctk.CTkEntry(self.frame_inputs, width=90)
        self.entrada_iter.insert(0, "100")
        self.entrada_iter.grid(row=5, column=2, padx=10, pady=(0, 10))
        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.pack(pady=5)
        self.btn_calc = ctk.CTkButton(self.frame_botones, text="Calcular", command=self.calcular, fg_color="#28a745", hover_color="#218838")
        self.btn_calc.pack(side="left", padx=10)
        self.btn_limpiar = ctk.CTkButton(self.frame_botones, text="Limpiar", command=self.limpiar, fg_color="#dc3545", hover_color="#c82333", width=80)
        self.btn_limpiar.pack(side="left", padx=10)
        self.tabla = TablaResultados(self, height=200)
        self.tabla.pack(fill="both", expand=True, padx=20, pady=10)

    def limpiar(self):
        self.entrada_f.delete(0, 'end'); self.entrada_x0.delete(0, 'end'); self.entrada_x1.delete(0, 'end')
        self.entrada_x2.delete(0, 'end'); self.entrada_raices.delete(0, 'end'); self.entrada_raices.insert(0, "3")
        self.entrada_tol.delete(0, 'end'); self.entrada_iter.delete(0, 'end'); self.entrada_iter.insert(0, "100")
        self.tabla.actualizar_datos([], [], "")

    def calcular(self):
        try:
            x0, x1, x2 = complex(self.entrada_x0.get()), complex(self.entrada_x1.get()), complex(self.entrada_x2.get())
            cols, filas, msj = logica_ec.deflacion_muller(self.entrada_f.get(), x0, x1, x2, float(self.entrada_tol.get()), int(self.entrada_iter.get()), int(self.entrada_raices.get()))
            if not cols: self.tabla.actualizar_datos([], [], msj, error=True)
            else: self.tabla.actualizar_datos(cols, filas, msj)
        except Exception as e: self.tabla.actualizar_datos([], [], f"Error: {e}", error=True)


# --- INTERPOLACIONES ---
class FrameInterpolacion(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Métodos de Interpolación", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=(20, 10))
        
        frame_inputs = ctk.CTkFrame(self, fg_color="transparent")
        frame_inputs.pack(pady=5)

        self.menu_metodo = ctk.CTkOptionMenu(
            frame_inputs, 
            values=["Polinomio de Lagrange", "Método de Neville", "Diferencias Divididas"],
            width=250
        )
        self.menu_metodo.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        self.entrada_x = ctk.CTkEntry(frame_inputs, width=350, placeholder_text="Valores de X (ej: 1, 2, 3)")
        self.entrada_x.grid(row=1, column=0, padx=10, pady=5)

        self.frame_y_opciones = ctk.CTkFrame(frame_inputs, fg_color="transparent")
        self.frame_y_opciones.grid(row=2, column=0, padx=10, pady=5)
        
        self.usar_funcion_var = ctk.BooleanVar(value=False)
        self.switch_funcion = ctk.CTkSwitch(
            self.frame_y_opciones, 
            text="Usar función f(x)", 
            variable=self.usar_funcion_var,
            command=self.toggle_modo_y
        )
        self.switch_funcion.pack(side="left", padx=(0, 10))

        self.entrada_y = ctk.CTkEntry(self.frame_y_opciones, width=200, placeholder_text="Valores de Y (ej: 5, 8, 12)")
        self.entrada_y.pack(side="left")

        self.entrada_x_int = ctk.CTkEntry(frame_inputs, width=150, placeholder_text="X a interpolar")
        self.entrada_x_int.grid(row=1, column=1, padx=10, pady=5, rowspan=2)

        self.btn_calc = ctk.CTkButton(self, text="Calcular", command=self.calcular)
        self.btn_calc.pack(pady=10)

        self.lbl_resultado = ctk.CTkLabel(self, text="Resultado: ---", font=ctk.CTkFont(size=16, weight="bold"), text_color="#f39c12")
        self.lbl_resultado.pack(pady=(5, 10))

        self.tabla = TablaResultados(self, height=250)
        self.tabla.pack(fill="both", expand=True, padx=20, pady=10)

    def toggle_modo_y(self):
        self.entrada_y.delete(0, "end")
        if self.usar_funcion_var.get():
            self.entrada_y.configure(placeholder_text="Escribe f(x) (ej: sin(x) + x**2)")
        else:
            self.entrada_y.configure(placeholder_text="Valores de Y (ej: 5, 8, 12)")

    def calcular(self):
        self.lbl_resultado.configure(text="Resultado: ---") 
        try:
            str_x = self.entrada_x.get()
            str_y_input = self.entrada_y.get()
            
            if not str_x or not str_y_input:
                raise ValueError("Faltan datos en los vectores X o Y/f(x).")

            x_datos = [float(i.strip()) for i in str_x.split(',')]
            x_val = float(self.entrada_x_int.get())

            if self.usar_funcion_var.get():
                y_datos = interpolaciones.generar_y_desde_funcion(str_y_input, x_datos)
            else:
                y_datos = [float(i.strip()) for i in str_y_input.split(',')]

            if len(x_datos) != len(y_datos):
                self.tabla.actualizar_datos([], [], "Error: X e Y no tienen la misma cantidad de elementos.", error=True)
                return

            metodo = self.menu_metodo.get()

            if metodo == "Polinomio de Lagrange":
                resultado, filas, err = interpolaciones.interpolacion_lagrange(x_datos, y_datos, x_val)
                cols = ["i", "Xi", "Yi", "Li(x)", "Término"]
                msj = "Tabla de Lagrange calculada correctamente."

            elif metodo == "Método de Neville":
                resultado, filas = interpolaciones.interpolacion_neville(x_datos, y_datos, x_val)
                cols = ["X"] + [f"Nivel {i}" for i in range(len(x_datos))]
                msj = "Tabla de Neville generada con éxito."

            elif metodo == "Diferencias Divididas":
                coeficientes, filas = interpolaciones.diferencias_divididas(x_datos, y_datos)
                cols = ["X", "Y"] + [f"Diff {i}" for i in range(1, len(x_datos))]
                msj = f"Diferencias Divididas. El coeficiente b0 es {round(coeficientes[0], 4)}"
                resultado = interpolaciones.interpolacion_lagrange(x_datos, y_datos, x_val)[0]

            self.tabla.actualizar_datos(cols, filas, msj)
            
            if isinstance(resultado, (int, float)):
                self.lbl_resultado.configure(text=f"Resultado: f({x_val}) ≈ {round(resultado, 6)}")
                
                plt.figure("Gráfica de Interpolación")
                plt.clf()
                plt.title(f"Método: {metodo}")
                plt.plot(x_datos, y_datos, 'bo--', alpha=0.6, label='Puntos conocidos (Nodos)')
                plt.plot(x_val, resultado, 'r*', markersize=15, label=f'Punto interpolado\n({x_val}, {round(resultado, 4)})')
                plt.xlabel("Eje X")
                plt.ylabel("Eje Y")
                plt.grid(True, linestyle=':', alpha=0.7)
                plt.legend()
                plt.show() 
                
            else:
                self.lbl_resultado.configure(text=f"Resultado: {resultado}")

        except ValueError as e:
            self.tabla.actualizar_datos([], [], f"Error: {str(e)}", error=True)
        except Exception as e:
            self.tabla.actualizar_datos([], [], f"Ocurrió un error: {str(e)}", error=True)


# --- APROXIMACIONES ---
class FrameAproximaciones(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Aproximaciones Numéricas", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=(20, 10))

        self.menu_metodo = ctk.CTkOptionMenu(
            self, 
            values=["Serie de Taylor", "Mínimos Cuadrados (Cuadrático)", "Mínimos Cuadrados (Cúbico)", "Mínimos Cuadrados (Grado n)"],
            width=300,
            command=self.cambiar_entradas
        )
        self.menu_metodo.pack(pady=10)

        self.frame_inputs = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inputs.pack(pady=5)

        self.lbl_f = ctk.CTkLabel(self.frame_inputs, text="f(x):", text_color="gray")
        self.entrada_f = ctk.CTkEntry(self.frame_inputs, width=200, placeholder_text="ej: sin(x), exp(x)")
        self.lbl_a = ctk.CTkLabel(self.frame_inputs, text="Centro (a):", text_color="gray")
        self.entrada_a = ctk.CTkEntry(self.frame_inputs, width=80)
        self.lbl_x = ctk.CTkLabel(self.frame_inputs, text="Evaluar en (x):", text_color="gray")
        self.entrada_x_taylor = ctk.CTkEntry(self.frame_inputs, width=80)
        self.lbl_n_taylor = ctk.CTkLabel(self.frame_inputs, text="Grado (n):", text_color="gray")
        self.entrada_n = ctk.CTkEntry(self.frame_inputs, width=80)

        self.lbl_vec_x = ctk.CTkLabel(self.frame_inputs, text="Vector X:", text_color="gray")
        self.entrada_x_vec = ctk.CTkEntry(self.frame_inputs, width=250, placeholder_text="Valores X (ej: 1,2,3)")
        self.lbl_vec_y = ctk.CTkLabel(self.frame_inputs, text="Vector Y:", text_color="gray")
        self.entrada_y_vec = ctk.CTkEntry(self.frame_inputs, width=250, placeholder_text="Valores Y (ej: 4,5,6)")
        self.lbl_grado = ctk.CTkLabel(self.frame_inputs, text="Grado (n):", text_color="gray")
        self.entrada_grado_mc = ctk.CTkEntry(self.frame_inputs, width=80, placeholder_text="Grado")

        self.cambiar_entradas("Serie de Taylor") 

        self.btn_calc = ctk.CTkButton(self, text="Calcular", command=self.calcular)
        self.btn_calc.pack(pady=10)

        self.lbl_resultado = ctk.CTkLabel(self, text="Resultado: ---", font=ctk.CTkFont(size=16, weight="bold"), text_color="#f39c12")
        self.lbl_resultado.pack(pady=(5, 10))

        self.tabla = TablaResultados(self, height=200)
        self.tabla.pack(fill="both", expand=True, padx=20, pady=10)

    def cambiar_entradas(self, metodo_seleccionado):
        for widget in self.frame_inputs.winfo_children():
            widget.grid_forget()

        if "Taylor" in metodo_seleccionado:
            self.lbl_f.grid(row=0, column=0, padx=5, sticky="w")
            self.entrada_f.grid(row=1, column=0, padx=5, pady=(0, 10))
            self.lbl_a.grid(row=0, column=1, padx=5, sticky="w")
            self.entrada_a.grid(row=1, column=1, padx=5, pady=(0, 10))
            self.lbl_x.grid(row=0, column=2, padx=5, sticky="w")
            self.entrada_x_taylor.grid(row=1, column=2, padx=5, pady=(0, 10))
            self.lbl_n_taylor.grid(row=0, column=3, padx=5, sticky="w")
            self.entrada_n.grid(row=1, column=3, padx=5, pady=(0, 10))
        else:
            self.lbl_vec_x.grid(row=0, column=0, padx=5, sticky="w")
            self.entrada_x_vec.grid(row=1, column=0, padx=5, pady=(0, 10))
            self.lbl_vec_y.grid(row=0, column=1, padx=5, sticky="w")
            self.entrada_y_vec.grid(row=1, column=1, padx=5, pady=(0, 10))
            
            if "Grado n" in metodo_seleccionado:
                self.lbl_grado.grid(row=0, column=2, padx=5, sticky="w")
                self.entrada_grado_mc.grid(row=1, column=2, padx=5, pady=(0, 10))

    def calcular(self):
        self.lbl_resultado.configure(text="Resultado: ---")
        metodo = self.menu_metodo.get()
        try:
            if "Taylor" in metodo:
                f_str = self.entrada_f.get()
                a_val = float(self.entrada_a.get())
                x_val = float(self.entrada_x_taylor.get())
                n_val = int(self.entrada_n.get())
                
                resultado, error, filas = aproximaciones.taylor(f_str, a_val, x_val, n_val)
                cols = ["i", "Derivada", "f^(i)(a)", "Término", "Aproximación"]
                msj = f"Error verdadero (absoluto): {error:.8e}"
                
                self.tabla.actualizar_datos(cols, filas, msj)
                self.lbl_resultado.configure(text=f"Resultado f({x_val}) ≈ {round(resultado, 6)}")

            else:
                str_x = self.entrada_x_vec.get()
                str_y = self.entrada_y_vec.get()
                x_datos = [float(i.strip()) for i in str_x.split(',')]
                y_datos = [float(i.strip()) for i in str_y.split(',')]
                
                if "Cuadrático" in metodo: grado = 2
                elif "Cúbico" in metodo: grado = 3
                else: grado = int(self.entrada_grado_mc.get())

                ecuacion, sr, filas = aproximaciones.minimos_cuadrados(x_datos, y_datos, grado)
                cols = ["i", "X", "Y Real", "Y Calculado", "|Error|"]
                msj = f"Suma de Residuos al Cuadrado (Sr): {sr:.6f}"
                
                self.tabla.actualizar_datos(cols, filas, msj)
                self.lbl_resultado.configure(text=f"Ecuación: {ecuacion}")
                
                plt.figure("Mínimos Cuadrados")
                plt.clf()
                plt.plot(x_datos, y_datos, 'bo', label="Datos Reales")
                
                x_curva = np.linspace(min(x_datos), max(x_datos), 100)
                coefs = np.polyfit(x_datos, y_datos, grado)
                p = np.poly1d(coefs)
                plt.plot(x_curva, p(x_curva), 'r-', label=f"Ajuste (Grado {grado})")
                
                plt.title(f"Ajuste Polinomial - Mínimos Cuadrados")
                plt.legend()
                plt.grid(True, linestyle=':', alpha=0.7)
                plt.show()

        except Exception as e:
            self.tabla.actualizar_datos([], [], f"Error: {str(e)}", error=True)


# --- DERIVACIÓN NUMÉRICA ---
class FrameDerivacion(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Derivación Numérica", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=(20, 10))

        self.menu_metodo = ctk.CTkOptionMenu(
            self, 
            values=["1ra Derivada (2 puntos)", "1ra Derivada (3 puntos)", "1ra Derivada (4 puntos)", "1ra Derivada (5 puntos)",
                    "2da Derivada (3 puntos)", "2da Derivada (4 puntos)", "2da Derivada (5 puntos)"],
            width=250
        )
        self.menu_metodo.pack(pady=10)

        self.frame_inputs = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inputs.pack(pady=10)

        ctk.CTkLabel(self.frame_inputs, text="Función f(x):", text_color="gray").grid(row=0, column=0, padx=10, sticky="w")
        self.entrada_f = ctk.CTkEntry(self.frame_inputs, width=220, placeholder_text="ej: sin(x) + x**2")
        self.entrada_f.grid(row=1, column=0, padx=10, pady=(0, 10))

        ctk.CTkLabel(self.frame_inputs, text="Punto a evaluar (x):", text_color="gray").grid(row=0, column=1, padx=10, sticky="w")
        self.entrada_x = ctk.CTkEntry(self.frame_inputs, width=120)
        self.entrada_x.grid(row=1, column=1, padx=10, pady=(0, 10))

        ctk.CTkLabel(self.frame_inputs, text="Tamaño de paso (h):", text_color="gray").grid(row=0, column=2, padx=10, sticky="w")
        self.entrada_h = ctk.CTkEntry(self.frame_inputs, width=120, placeholder_text="ej: 0.1")
        self.entrada_h.grid(row=1, column=2, padx=10, pady=(0, 10))

        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.pack(pady=5)
        
        self.btn_calc = ctk.CTkButton(self.frame_botones, text="Calcular", command=self.calcular, fg_color="#28a745", hover_color="#218838")
        self.btn_calc.pack(side="left", padx=10)
        
        self.btn_limpiar = ctk.CTkButton(self.frame_botones, text="Limpiar", command=self.limpiar, fg_color="#dc3545", hover_color="#c82333", width=80)
        self.btn_limpiar.pack(side="left", padx=10)

        self.lbl_resultado = ctk.CTkLabel(self, text="Aproximación: ---", font=ctk.CTkFont(size=16, weight="bold"), text_color="#f39c12")
        self.lbl_resultado.pack(pady=(10, 5))
        
        self.lbl_exacta = ctk.CTkLabel(self, text="Valor Exacto: ---", text_color="gray")
        self.lbl_exacta.pack(pady=(0, 10))

        self.tabla = TablaResultados(self, height=180)
        self.tabla.pack(fill="both", expand=True, padx=20, pady=10)

    def limpiar(self):
        self.entrada_f.delete(0, 'end')
        self.entrada_x.delete(0, 'end')
        self.entrada_h.delete(0, 'end')
        self.tabla.actualizar_datos([], [], "")
        self.lbl_resultado.configure(text="Aproximación: ---")
        self.lbl_exacta.configure(text="Valor Exacto: ---")

    def calcular(self):
        metodo = self.menu_metodo.get()
        try:
            f_str = self.entrada_f.get()
            x_val = float(self.entrada_x.get())
            h_val = float(self.entrada_h.get())
            
            tipo_derivada = 1 if "1ra" in metodo else 2
            puntos = int(metodo.split("(")[1].split()[0])
            
            aprox, error, filas, formula, exacta = derivacion.calcular_derivada(f_str, x_val, h_val, tipo_derivada, puntos)
            
            cols = ["Término Evaluado", "Valor de x", "Resultado f(x)"]
            msj = f"Fórmula: {formula} | Error: {error:.8e}"
            
            self.tabla.actualizar_datos(cols, filas, msj)
            self.lbl_resultado.configure(text=f"Aproximación: {round(aprox, 8)}")
            self.lbl_exacta.configure(text=f"Valor Exacto (Analítico): {round(exacta, 8)}")

        except Exception as e:
            self.tabla.actualizar_datos([], [], f"Error: {str(e)}", error=True)


# --- INTEGRACIÓN NUMÉRICA ---
# --- INTEGRACIÓN NUMÉRICA ---
class FrameIntegracion(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Integración Numérica", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=(15, 5))

        self.menu_metodo = ctk.CTkOptionMenu(
            self, 
            values=[
                "Trapecio Simple", "Trapecio Compuesto",
                "Simpson 1/3 Simple", "Simpson 1/3 Compuesto",
                "Simpson 3/8 Simple", "Simpson 3/8 Compuesto",
                "Integración de Romberg", "Cuadratura Adaptativa",
                "Cuadratura Gaussiana"
            ],
            width=250,
            command=self.cambiar_entradas
        )
        self.menu_metodo.pack(pady=5)

        # --- SWITCHES DE MODO ---
        self.frame_switches = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_switches.pack(pady=5)
        
        self.multi_var = ctk.BooleanVar(value=False)
        self.switch_multi = ctk.CTkSwitch(self.frame_switches, text="Multivariable f(x, y)", variable=self.multi_var, command=self.toggle_modos)
        self.switch_multi.pack(side="left", padx=10)

        self.discreto_var = ctk.BooleanVar(value=False)
        self.switch_discreto = ctk.CTkSwitch(self.frame_switches, text="Puntos Discretos (Vectores)", variable=self.discreto_var, command=self.toggle_modos)
        self.switch_discreto.pack(side="left", padx=10)

        # --- INPUTS ---
        self.frame_inputs = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inputs.pack(pady=5)

        # Inputs Continuos (Ecuaciones)
        self.lbl_f = ctk.CTkLabel(self.frame_inputs, text="Función:", text_color="gray")
        self.entrada_f = ctk.CTkEntry(self.frame_inputs, width=180, placeholder_text="ej: exp(x**2)")
        self.lbl_a = ctk.CTkLabel(self.frame_inputs, text="Lím X [a]:", text_color="gray")
        self.entrada_a = ctk.CTkEntry(self.frame_inputs, width=65)
        self.lbl_b = ctk.CTkLabel(self.frame_inputs, text="Lím X [b]:", text_color="gray")
        self.entrada_b = ctk.CTkEntry(self.frame_inputs, width=65)
        self.lbl_c = ctk.CTkLabel(self.frame_inputs, text="Lím Y [c]:", text_color="gray")
        self.entrada_c = ctk.CTkEntry(self.frame_inputs, width=65)
        self.lbl_d = ctk.CTkLabel(self.frame_inputs, text="Lím Y [d]:", text_color="gray")
        self.entrada_d = ctk.CTkEntry(self.frame_inputs, width=65)
        self.lbl_param = ctk.CTkLabel(self.frame_inputs, text="Intervalos (n):", text_color="gray")
        self.entrada_param = ctk.CTkEntry(self.frame_inputs, width=100)

        # Inputs Discretos (Vectores)
        self.lbl_x_vec = ctk.CTkLabel(self.frame_inputs, text="Valores X:", text_color="gray")
        self.entrada_x_vec = ctk.CTkEntry(self.frame_inputs, width=250, placeholder_text="ej: 1, 2, 3")
        self.lbl_y_vec = ctk.CTkLabel(self.frame_inputs, text="Valores Y:", text_color="gray")
        self.entrada_y_vec = ctk.CTkEntry(self.frame_inputs, width=250, placeholder_text="ej: 5, 8, 12")

        self.toggle_modos()

        # --- BOTONES Y RESULTADOS ---
        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.pack(pady=5)
        self.btn_calc = ctk.CTkButton(self.frame_botones, text="Calcular", command=self.calcular, fg_color="#28a745", hover_color="#218838")
        self.btn_calc.pack(side="left", padx=10)
        self.btn_limpiar = ctk.CTkButton(self.frame_botones, text="Limpiar", command=self.limpiar, fg_color="#dc3545", hover_color="#c82333", width=80)
        self.btn_limpiar.pack(side="left", padx=10)

        self.lbl_resultado = ctk.CTkLabel(self, text="Resultado: ---", font=ctk.CTkFont(size=16, weight="bold"), text_color="#f39c12")
        self.lbl_resultado.pack(pady=(5, 2))
        self.lbl_exacta = ctk.CTkLabel(self, text="Valor Exacto: ---", text_color="gray")
        self.lbl_exacta.pack(pady=(0, 5))

        self.tabla = TablaResultados(self, height=180)
        self.tabla.pack(fill="both", expand=True, padx=20, pady=5)

    def toggle_modos(self):
        # Desactivar el otro switch si uno se activa para evitar conflictos lógicos
        if self.discreto_var.get() and self.multi_var.get():
            self.multi_var.set(False)

        # Limpiar grilla visual
        for widget in self.frame_inputs.winfo_children():
            widget.grid_remove()

        metodo = self.menu_metodo.get()

        if self.discreto_var.get():
            # MODO DISCRETO
            self.lbl_x_vec.grid(row=0, column=0, padx=5, sticky="w")
            self.entrada_x_vec.grid(row=1, column=0, padx=5, pady=(0, 10))
            self.lbl_y_vec.grid(row=0, column=1, padx=5, sticky="w")
            self.entrada_y_vec.grid(row=1, column=1, padx=5, pady=(0, 10))
        else:
            # MODO CONTINUO (Ecuación)
            self.lbl_f.grid(row=0, column=0, padx=5, sticky="w")
            self.entrada_f.grid(row=1, column=0, padx=5, pady=(0, 10))
            self.lbl_a.grid(row=0, column=1, padx=5, sticky="w")
            self.entrada_a.grid(row=1, column=1, padx=5, pady=(0, 10))
            self.lbl_b.grid(row=0, column=2, padx=5, sticky="w")
            self.entrada_b.grid(row=1, column=2, padx=5, pady=(0, 10))
            
            if self.multi_var.get():
                self.lbl_c.grid(row=0, column=3, padx=5, sticky="w")
                self.entrada_c.grid(row=1, column=3, padx=5, pady=(0, 10))
                self.lbl_d.grid(row=0, column=4, padx=5, sticky="w")
                self.entrada_d.grid(row=1, column=4, padx=5, pady=(0, 10))
                self.lbl_param.configure(text="Params (nx, ny):")
                self.entrada_param.configure(placeholder_text="ej: 2, 2")
                self.lbl_param.grid(row=0, column=5, padx=5, sticky="w")
                self.entrada_param.grid(row=1, column=5, padx=5, pady=(0, 10))
            else:
                self.cambiar_entradas(metodo)

    def cambiar_entradas(self, metodo_seleccionado):
        if self.discreto_var.get() or self.multi_var.get(): return

        if "Simple" in metodo_seleccionado and "Simpson" not in metodo_seleccionado:
            self.lbl_param.grid_remove()
            self.entrada_param.grid_remove()
        elif "Adaptativa" in metodo_seleccionado:
            self.lbl_param.configure(text="Tolerancia:"); self.entrada_param.configure(placeholder_text="ej: 0.0001")
            self.lbl_param.grid(row=0, column=5, padx=5, sticky="w"); self.entrada_param.grid(row=1, column=5, padx=5, pady=(0, 10))
        elif "Gaussiana" in metodo_seleccionado:
            self.lbl_param.configure(text="Puntos (n):"); self.entrada_param.configure(placeholder_text="ej: 2 o 3")
            self.lbl_param.grid(row=0, column=5, padx=5, sticky="w"); self.entrada_param.grid(row=1, column=5, padx=5, pady=(0, 10))
        else:
            self.lbl_param.configure(text="Intervalos (n):"); self.entrada_param.configure(placeholder_text="ej: 10")
            self.lbl_param.grid(row=0, column=5, padx=5, sticky="w"); self.entrada_param.grid(row=1, column=5, padx=5, pady=(0, 10))

    def limpiar(self):
        self.entrada_f.delete(0, 'end'); self.entrada_a.delete(0, 'end'); self.entrada_b.delete(0, 'end')
        self.entrada_c.delete(0, 'end'); self.entrada_d.delete(0, 'end'); self.entrada_param.delete(0, 'end')
        self.entrada_x_vec.delete(0, 'end'); self.entrada_y_vec.delete(0, 'end')
        self.tabla.actualizar_datos([], [], "")
        self.lbl_resultado.configure(text="Resultado: ---"); self.lbl_exacta.configure(text="Valor Exacto: ---")

    def calcular(self):
        metodo = self.menu_metodo.get()
        try:
            if self.discreto_var.get():
                # LÓGICA DATOS DISCRETOS
                x_datos = [float(i.strip()) for i in self.entrada_x_vec.get().split(',')]
                y_datos = [float(i.strip()) for i in self.entrada_y_vec.get().split(',')]
                
                aprox, error, filas, form, exacta = integracion.calcular_integracion_discreta(metodo, x_datos, y_datos)
                
                if "Trapecio" in metodo: cols = ["i", "x_i", "x_i+1", "y_i", "y_i+1", "h_i", "Área"]
                else: cols = ["i", "x_i", "y_i", "Coeficiente", "Término"]
                
            elif self.multi_var.get():
                # LÓGICA MULTIVARIABLE
                f_str = self.entrada_f.get()
                a_val, b_val = float(self.entrada_a.get()), float(self.entrada_b.get())
                c_val, d_val = float(self.entrada_c.get()), float(self.entrada_d.get())
                parametro = self.entrada_param.get()
                aprox, error, filas, form, exacta = integracion_multivariable.calcular_multivariable(metodo, f_str, a_val, b_val, c_val, d_val, parametro)
                cols = ["i", "j", "x_i", "y_j", "f(x_i, y_j)", "Coeficiente", "Término"]
                
            else:
                # LÓGICA CONTINUA NORMAL
                f_str = self.entrada_f.get()
                a_val, b_val = float(self.entrada_a.get()), float(self.entrada_b.get())
                parametro = 0 
                if "Compuesto" in metodo or "Romberg" in metodo or "Gaussiana" in metodo: parametro = int(self.entrada_param.get())
                elif "Adaptativa" in metodo: parametro = float(self.entrada_param.get())

                aprox, error, filas, form, exacta = integracion.calcular_integracion(metodo, f_str, a_val, b_val, parametro)
                
                if "Romberg" in metodo: cols = ["Precisión"] + [f"Nivel {i}" for i in range(int(self.entrada_param.get()))]
                elif "Adaptativa" in metodo: cols = ["Límite A", "Límite B", "Punto Medio", "Área Subtramo", "Error Local"]
                elif "Gaussiana" in metodo: cols = ["i", "t_i (Raíz)", "c_i (Peso)", "f(x(t_i))", "Término Eval"]
                else: cols = ["i", "x_i", "f(x_i)", "Coeficiente", "Término"]

            msj = f"{form} | Error: {error:.8e}" if isinstance(error, float) else f"{form} | Error Exacto: N/A"
            self.tabla.actualizar_datos(cols, filas, msj)
            self.lbl_resultado.configure(text=f"Resultado Aproximado: {round(aprox, 8)}")
            self.lbl_exacta.configure(text=f"Valor Exacto: {round(exacta, 8) if exacta is not None else 'No calculable'}")

        except Exception as e:
            self.tabla.actualizar_datos([], [], f"Error: {str(e)}", error=True)

# --- ECUACIONES DIFERENCIALES ORDINARIAS ---
class FrameEDOs(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Solución de EDOs (Primer Orden)", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=(15, 5))

        self.menu_metodo = ctk.CTkOptionMenu(
            self, 
            values=["Euler", "Taylor Orden Superior", "Heun", "Runge-Kutta 2", "Runge-Kutta 4", "Runge-Kutta-Fehlberg (RKF45)"],
            width=250,
            command=self.cambiar_entradas
        )
        self.menu_metodo.pack(pady=10)

        self.frame_inputs = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inputs.pack(pady=5)

        ctk.CTkLabel(self.frame_inputs, text="EDO y':", text_color="gray").grid(row=0, column=0, padx=5, sticky="w")
        self.entrada_f = ctk.CTkEntry(self.frame_inputs, width=150, placeholder_text="ej: x - y")
        self.entrada_f.grid(row=1, column=0, padx=5, pady=(0, 10))

        ctk.CTkLabel(self.frame_inputs, text="x0:", text_color="gray").grid(row=0, column=1, padx=5, sticky="w")
        self.entrada_x0 = ctk.CTkEntry(self.frame_inputs, width=60)
        self.entrada_x0.grid(row=1, column=1, padx=5, pady=(0, 10))

        ctk.CTkLabel(self.frame_inputs, text="y0:", text_color="gray").grid(row=0, column=2, padx=5, sticky="w")
        self.entrada_y0 = ctk.CTkEntry(self.frame_inputs, width=60)
        self.entrada_y0.grid(row=1, column=2, padx=5, pady=(0, 10))

        ctk.CTkLabel(self.frame_inputs, text="xf:", text_color="gray").grid(row=0, column=3, padx=5, sticky="w")
        self.entrada_xf = ctk.CTkEntry(self.frame_inputs, width=60)
        self.entrada_xf.grid(row=1, column=3, padx=5, pady=(0, 10))

        self.lbl_h = ctk.CTkLabel(self.frame_inputs, text="Paso (h):", text_color="gray")
        self.lbl_h.grid(row=0, column=4, padx=5, sticky="w")
        self.entrada_h = ctk.CTkEntry(self.frame_inputs, width=80)
        self.entrada_h.grid(row=1, column=4, padx=5, pady=(0, 10))

        self.lbl_extra = ctk.CTkLabel(self.frame_inputs, text="Grado Taylor:", text_color="gray")
        self.entrada_extra = ctk.CTkEntry(self.frame_inputs, width=80)

        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.pack(pady=5)
        self.btn_calc = ctk.CTkButton(self.frame_botones, text="Calcular y Graficar", command=self.calcular, fg_color="#28a745", hover_color="#218838")
        self.btn_calc.pack(side="left", padx=10)
        self.btn_limpiar = ctk.CTkButton(self.frame_botones, text="Limpiar", command=self.limpiar, fg_color="#dc3545", hover_color="#c82333", width=80)
        self.btn_limpiar.pack(side="left", padx=10)

        self.lbl_resultado = ctk.CTkLabel(self, text="Valor Final: ---", font=ctk.CTkFont(size=16, weight="bold"), text_color="#f39c12")
        self.lbl_resultado.pack(pady=(5, 5))

        self.tabla = TablaResultados(self, height=200)
        self.tabla.pack(fill="both", expand=True, padx=20, pady=5)

    def cambiar_entradas(self, metodo_seleccionado):
        self.lbl_extra.grid_remove()
        self.entrada_extra.grid_remove()
        self.lbl_h.configure(text="Paso (h):")
        
        if "Taylor" in metodo_seleccionado:
            self.lbl_extra.configure(text="Grado Taylor (n):")
            self.entrada_extra.configure(placeholder_text="ej: 3")
            self.lbl_extra.grid(row=0, column=5, padx=5, sticky="w")
            self.entrada_extra.grid(row=1, column=5, padx=5, pady=(0, 10))
        elif "RKF45" in metodo_seleccionado:
            self.lbl_h.configure(text="Paso inicial (h):")
            self.lbl_extra.configure(text="Tolerancia Max:")
            self.entrada_extra.configure(placeholder_text="ej: 0.0001")
            self.lbl_extra.grid(row=0, column=5, padx=5, sticky="w")
            self.entrada_extra.grid(row=1, column=5, padx=5, pady=(0, 10))

    def limpiar(self):
        self.entrada_f.delete(0, 'end'); self.entrada_x0.delete(0, 'end'); self.entrada_y0.delete(0, 'end')
        self.entrada_xf.delete(0, 'end'); self.entrada_h.delete(0, 'end'); self.entrada_extra.delete(0, 'end')
        self.tabla.actualizar_datos([], [], "")
        self.lbl_resultado.configure(text="Valor Final: ---")

    def calcular(self):
        metodo = self.menu_metodo.get()
        try:
            f_str, x0, y0, xf, h = self.entrada_f.get(), float(self.entrada_x0.get()), float(self.entrada_y0.get()), float(self.entrada_xf.get()), float(self.entrada_h.get())
            
            grado, tol = 2, 1e-5
            if "Taylor" in metodo: grado = int(self.entrada_extra.get())
            elif "RKF45" in metodo: tol = float(self.entrada_extra.get())

            x_vals, y_vals, filas = edos.resolver_edo(metodo, f_str, x0, y0, xf, h, grado, tol)

            if "RKF45" in metodo: cols = ["Iter", "x", "y", "h usado", "Error Trunc.", "Estado"]
            elif "Euler" in metodo: cols = ["i", "x_i", "y_i", "f(x_i, y_i)", "y_{i+1}"]
            elif "Heun" in metodo: cols = ["i", "x_i", "y_i", "y^0_pred", "f(x_i, y_i)", "f(x_{i+1}, y^0)", "y_{i+1}"]
            elif "Taylor" in metodo: cols = ["i", "x_i", "y_i"] + [f"Término {k+1}" for k in range(grado)] + ["y_{i+1}"]
            elif "Runge-Kutta 2" in metodo: cols = ["i", "x_i", "y_i", "k1", "k2", "y_{i+1}"]
            elif "Runge-Kutta 4" in metodo: cols = ["i", "x_i", "y_i", "k1", "k2", "k3", "k4", "y_{i+1}"]

            msj = f"Solución calculada exitosamente usando {metodo}"
            self.tabla.actualizar_datos(cols, filas, msj)
            self.lbl_resultado.configure(text=f"Valor Final: y({xf}) ≈ {round(y_vals[-1], 6)}")

            plt.figure(f"EDO: {metodo}")
            plt.clf()
            plt.plot(x_vals, y_vals, 'bo-' if "RKF45" not in metodo else 'rx--', linewidth=2, markersize=5, label=f"Aproximación {metodo}")
            plt.plot(x0, y0, 'go', markersize=8, label="Inicio")
            plt.plot(x_vals[-1], y_vals[-1], 'ro', markersize=8, label="Fin")
            plt.title(f"Solución EDO: y' = {f_str}")
            plt.xlabel("X"); plt.ylabel("Y"); plt.grid(True, linestyle=':', alpha=0.7); plt.legend()
            plt.show(block=False)

        except Exception as e:
            self.tabla.actualizar_datos([], [], f"Error: {str(e)}", error=True)

# --- ÁLGEBRA LINEAL ---
class FrameAlgebraLineal(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Sistemas de Ecuaciones Lineales", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=(15, 5))

        self.menu_metodo = ctk.CTkOptionMenu(
            self, 
            values=["Parcial de Columna", "Parcial Escalado", "Factorización LU"], 
            width=250
        )
        self.menu_metodo.pack(pady=5)

        # --- CONTROLES PARA GENERAR LA CUADRÍCULA ---
        self.frame_config = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_config.pack(pady=5)
        
        ctk.CTkLabel(self.frame_config, text="Tamaño del Sistema (n x n):", text_color="gray").pack(side="left", padx=5)
        self.entrada_n = ctk.CTkEntry(self.frame_config, width=60)
        self.entrada_n.insert(0, "3")
        self.entrada_n.pack(side="left", padx=5)
        
        self.btn_generar = ctk.CTkButton(self.frame_config, text="Generar Cuadrícula", command=self.generar_cuadricula)
        self.btn_generar.pack(side="left", padx=10)

        # --- FRAME DINÁMICO PARA LA MATRIZ ---
        self.frame_matriz = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_matriz.pack(pady=10)

        # Aquí guardaremos las referencias a cada cajita de texto
        self.entradas_A = [] 
        self.entradas_b = [] 

        self.btn_calc = ctk.CTkButton(self, text="Resolver Sistema", command=self.calcular, fg_color="#28a745", hover_color="#218838")
        self.btn_calc.pack(pady=5)

        self.tabla = TablaResultados(self, height=180)
        self.tabla.pack(fill="both", expand=True, padx=20, pady=5)
        
        # Generar una cuadrícula inicial de 3x3 por defecto al abrir la ventana
        self.generar_cuadricula()

    def generar_cuadricula(self):
        try:
            n = int(self.entrada_n.get())
            if n <= 1 or n > 10: # Límite razonable para no desbordar la pantalla
                raise ValueError("El tamaño debe ser entre 2 y 10.")
        except ValueError as e:
            self.tabla.actualizar_datos([], [], f"Tamaño inválido: {e}", error=True)
            return

        # 1. Limpiar cuadrícula anterior (destruye los widgets viejos)
        for widget in self.frame_matriz.winfo_children():
            widget.destroy()

        self.entradas_A = []
        self.entradas_b = []

        # 2. Encabezados Visuales
        ctk.CTkLabel(self.frame_matriz, text="Matriz de Coeficientes [A]", text_color="#17a2b8", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=n, pady=(0,5))
        ctk.CTkLabel(self.frame_matriz, text="Vector [b]", text_color="#f39c12", font=ctk.CTkFont(weight="bold")).grid(row=0, column=n+1, pady=(0,5))

        # 3. Dibujar la cuadrícula dinámica
        for i in range(n):
            fila_A = []
            for j in range(n):
                # Celdas de la Matriz A
                entry_a = ctk.CTkEntry(self.frame_matriz, width=50, justify="center")
                entry_a.grid(row=i+1, column=j, padx=2, pady=2)
                fila_A.append(entry_a)
            self.entradas_A.append(fila_A)

            # Separador visual "="
            ctk.CTkLabel(self.frame_matriz, text="=").grid(row=i+1, column=n, padx=10)

            # Celdas del Vector b
            entry_b = ctk.CTkEntry(self.frame_matriz, width=50, justify="center")
            entry_b.grid(row=i+1, column=n+1, padx=2, pady=2)
            self.entradas_b.append(entry_b)

    def calcular(self):
        try:
            metodo = self.menu_metodo.get()
            n = len(self.entradas_A)
            
            if n == 0:
                raise ValueError("Genera primero la cuadrícula.")

            # --- EXTRAER DATOS DE LA UI HACIA PYTHON ---
            A = []
            for i in range(n):
                fila_valores = []
                for j in range(n):
                    val = self.entradas_A[i][j].get()
                    if not val: raise ValueError(f"Falta un dato en la matriz A (Fila {i+1}, Columna {j+1})")
                    fila_valores.append(float(val))
                A.append(fila_valores)

            b = []
            for i in range(n):
                val = self.entradas_b[i].get()
                if not val: raise ValueError(f"Falta un dato en el vector b (Fila {i+1})")
                b.append(float(val))

            # --- ENVIAR AL BACKEND MATEMÁTICO ---
            if metodo == "Factorización LU":
                x_res, pasos, matriz_L, matriz_U = algebra_lineal.factorizacion_lu(A, b)
                msj_exito = "Factorización LU finalizada con éxito."
            else:
                x_res, pasos, Ab_final = algebra_lineal.eliminacion_gaussiana(A, b, metodo)
                msj_exito = f"Eliminación Gaussiana ({metodo}) finalizada."

            # --- MOSTRAR RESULTADOS ---
            cols = ["Paso / Fase", "Operación Realizada", "Detalle / Resultado"]
            self.tabla.actualizar_datos(cols, pasos, msj_exito)

            msj_resultados = "Raíces encontradas:\n"
            for i, raiz in enumerate(x_res):
                msj_resultados += f"x_{i+1} = {round(raiz, 6)}    "
            
            self.tabla.lbl_mensaje.configure(text=msj_resultados)

        except Exception as e:
            self.tabla.actualizar_datos([], [], f"Error: {str(e)}", error=True)


# --- SIMULADOR DE PÉNDULO ---
class FramePendulo(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.lbl_titulo = ctk.CTkLabel(self, text="Simulador Físico: Péndulo Simple", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=(20, 10))

        # Menú para conectar con los métodos de EDOs
        self.menu_metodo = ctk.CTkOptionMenu(
            self, 
            values=["Euler", "Heun", "Runge-Kutta 2", "Runge-Kutta 4"],
            width=250
        )
        self.menu_metodo.set("Runge-Kutta 4") # Default seguro
        self.menu_metodo.pack(pady=5)

        self.frame_inputs = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inputs.pack(pady=10)

        # Columna 1
        ctk.CTkLabel(self.frame_inputs, text="Longitud Cuerda L (m):", text_color="gray").grid(row=0, column=0, padx=10, sticky="w")
        self.entrada_L = ctk.CTkEntry(self.frame_inputs, width=120)
        self.entrada_L.insert(0, "1.0")
        self.entrada_L.grid(row=1, column=0, padx=10, pady=(0, 10))

        ctk.CTkLabel(self.frame_inputs, text="Ángulo Inicial (grados):", text_color="gray").grid(row=2, column=0, padx=10, sticky="w")
        self.entrada_theta = ctk.CTkEntry(self.frame_inputs, width=120)
        self.entrada_theta.insert(0, "45")
        self.entrada_theta.grid(row=3, column=0, padx=10, pady=(0, 10))

        ctk.CTkLabel(self.frame_inputs, text="Tiempo Total tf (s):", text_color="gray").grid(row=4, column=0, padx=10, sticky="w")
        self.entrada_tf = ctk.CTkEntry(self.frame_inputs, width=120)
        self.entrada_tf.insert(0, "10.0")
        self.entrada_tf.grid(row=5, column=0, padx=10, pady=(0, 10))

        # Columna 2
        ctk.CTkLabel(self.frame_inputs, text="Gravedad g (m/s²):", text_color="gray").grid(row=0, column=1, padx=10, sticky="w")
        self.entrada_g = ctk.CTkEntry(self.frame_inputs, width=120)
        self.entrada_g.insert(0, "9.81")
        self.entrada_g.grid(row=1, column=1, padx=10, pady=(0, 10))

        ctk.CTkLabel(self.frame_inputs, text="Vel. Angular w0 (rad/s):", text_color="gray").grid(row=2, column=1, padx=10, sticky="w")
        self.entrada_w0 = ctk.CTkEntry(self.frame_inputs, width=120)
        self.entrada_w0.insert(0, "0.0")
        self.entrada_w0.grid(row=3, column=1, padx=10, pady=(0, 10))

        ctk.CTkLabel(self.frame_inputs, text="Paso integración h (s):", text_color="gray").grid(row=4, column=1, padx=10, sticky="w")
        self.entrada_h = ctk.CTkEntry(self.frame_inputs, width=120)
        self.entrada_h.insert(0, "0.05")
        self.entrada_h.grid(row=5, column=1, padx=10, pady=(0, 10))

        self.btn_simular = ctk.CTkButton(self, text="Iniciar Simulación en Vivo", command=self.simular, fg_color="#17a2b8", hover_color="#138496", height=40)
        self.btn_simular.pack(pady=20)

        self.lbl_info = ctk.CTkLabel(self, text="Visualiza el error de cada algoritmo numérico en la física real.", text_color="gray")
        self.lbl_info.pack()

    def simular(self):
        try:
            metodo = self.menu_metodo.get()
            L = float(self.entrada_L.get())
            g = float(self.entrada_g.get())
            theta0 = float(self.entrada_theta.get())
            w0 = float(self.entrada_w0.get())
            tf = float(self.entrada_tf.get())
            h = float(self.entrada_h.get())

            if L <= 0 or tf <= 0 or h <= 0:
                self.lbl_info.configure(text="Error: L, tf y h deben ser positivos.", text_color="#dc3545")
                return

            self.lbl_info.configure(text=f"Simulando con {metodo}...", text_color="#28a745")

            # 1. Llamar al backend matemático con el método seleccionado
            t, theta, w = pendulo.simular_pendulo(metodo, L, g, theta0, w0, tf, h)

            # 2. Convertir coordenadas polares a cartesianas (x, y)
            x = L * np.sin(theta)
            y = -L * np.cos(theta)

            # 3. Configurar la ventana de animación
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.set_xlim(-L - 0.5, L + 0.5)
            ax.set_ylim(-L - 0.5, 0.5)
            ax.set_aspect('equal')
            ax.grid(True, linestyle=':', alpha=0.7)
            ax.set_title(f"Péndulo Dinámico (Método: {metodo})")
            
            ax.plot([0], [0], 'ks', markersize=8) 

            linea_cuerda, = ax.plot([], [], 'k-', lw=2, alpha=0.7)
            punto_masa, = ax.plot([], [], 'ro', markersize=15)

            def init():
                linea_cuerda.set_data([], [])
                punto_masa.set_data([], [])
                return linea_cuerda, punto_masa

            def update(i):
                linea_cuerda.set_data([0, x[i]], [0, y[i]])
                punto_masa.set_data([x[i]], [y[i]])
                return linea_cuerda, punto_masa

            intervalo_ms = h * 1000 
            
            self.ani = animation.FuncAnimation(
                fig, update, frames=len(t),
                init_func=init, blit=True, interval=intervalo_ms, repeat=True
            )
            
            plt.show()
            self.lbl_info.configure(text="Simulación finalizada.", text_color="gray")

        except Exception as e:
            self.lbl_info.configure(text=f"Error: {str(e)}", text_color="#dc3545")
        
if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    app = App()
    app.mainloop()