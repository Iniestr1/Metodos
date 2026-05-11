import math
import cmath
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

# --- FUNCIÓN AUXILIAR DE FORMATEO COMPLEJO ---
def format_comp(num):
    if isinstance(num, complex):
        if abs(num.imag) < 1e-10: 
            return f"{num.real:.5f}"
        signo = "+" if num.imag >= 0 else "-"
        return f"{num.real:.5f}{signo}{abs(num.imag):.5f}j"
    return f"{num:.5f}"

# --- FUNCIÓN EVALUADORA SEGURA ---
def evaluar(expr, x_val):
    expr = expr.replace("^", "**")
    entorno = {"x": x_val, "e": math.e, "pi": math.pi}
    entorno.update({k: v for k, v in math.__dict__.items() if not k.startswith('_')})
    entorno["cbrt"] = np.cbrt  
    entorno["sign"] = np.sign  
    entorno["abs"] = abs       
    
    try:
        return eval(expr, {"__builtins__": None}, entorno)
    except ValueError:
        entorno.update({k: v for k, v in cmath.__dict__.items() if not k.startswith('_')})
        return eval(expr, {"__builtins__": None}, entorno)

# --- FUNCIÓN AUXILIAR PARA GRAFICAR F(X) GENÉRICA ---
def graficar_generico(f_str, x_hist, titulo, root_found=True):
    try:
        x_reales = [x.real for x in x_hist if not isinstance(x, complex) or abs(x.imag) < 1e-5]
        if not x_reales:
            return
            
        x_min, x_max = min(x_reales) - 1.5, max(x_reales) + 1.5
        x_vals = np.linspace(x_min, x_max, 400)
        
        y_vals = []
        for val in x_vals:
            try:
                res = evaluar(f_str, val)
                y_vals.append(res.real if isinstance(res, complex) else res)
            except Exception:
                y_vals.append(np.nan)

        plt.figure(figsize=(8, 5))
        plt.plot(x_vals, y_vals, label=f"f(x) = {f_str}", color='royalblue', linewidth=2)
        plt.axhline(0, color='black', linewidth=1)
        plt.axvline(0, color='black', linewidth=1)
        
        y_hist = []
        for x in x_reales:
            try:
                y_hist.append(evaluar(f_str, x).real)
            except:
                y_hist.append(0)
                
        plt.plot(x_reales, y_hist, 'ro-', alpha=0.5, label='Iteraciones', markersize=5)
        
        if root_found and x_reales:
            plt.plot(x_reales[-1], 0, 'go', markersize=10, label=f'Raíz: {x_reales[-1]:.4f}')
            
        plt.title(titulo)
        plt.xlabel("x")
        plt.ylabel("y")
        plt.legend()
        plt.grid(True, linestyle=':', alpha=0.7)
        plt.show(block=False)
    except Exception as e:
        print(f"No se pudo graficar: {e}")

# --- 1. BISECCIÓN ---
def biseccion(f_str, a, b, tol, max_iter):
    fa = evaluar(f_str, a)
    fb = evaluar(f_str, b)
    if isinstance(fa, complex): fa = fa.real
    if isinstance(fb, complex): fb = fb.real
    
    if fa * fb > 0:
        return [], [], "Error: La función debe tener signos opuestos en 'a' y 'b'."
    
    columnas = ["Iter", "a", "b", "c", "f(c)", "Error"]
    filas = []
    x_hist = [a, b]
    root_found = False
    mensaje_final = ""
    
    for i in range(1, max_iter + 1):
        c = (a + b) / 2
        fc = evaluar(f_str, c)
        if isinstance(fc, complex): fc = fc.real
            
        error = abs(b - a) / 2
        x_hist.append(c)
        filas.append([i, f"{a:.5f}", f"{b:.5f}", f"{c:.5f}", f"{fc:.5f}", f"{error:.5f}"])
        
        if error < tol or fc == 0:
            mensaje_final = f"Raíz encontrada en x = {c:.6f} con error {error:.6f}"
            root_found = True
            break
        if fa * fc < 0:
            b, fb = c, fc
        else:
            a, fa = c, fc
    else:
        mensaje_final = "Máximo de iteraciones alcanzado."
        
    graficar_generico(f_str, x_hist, "Método de Bisección", root_found)
    return columnas, filas, mensaje_final

# --- 2. FALSA POSICIÓN ---
def falsa_posicion(f_str, a, b, tol, max_iter):
    fa = evaluar(f_str, a)
    fb = evaluar(f_str, b)
    if isinstance(fa, complex): fa = fa.real
    if isinstance(fb, complex): fb = fb.real
    
    if fa * fb > 0:
        return [], [], "Error: La función debe tener signos opuestos en 'a' y 'b'."
    
    columnas = ["Iter", "a", "b", "c", "f(c)", "Error"]
    filas = []
    c_old = a
    x_hist = [a, b]
    root_found = False
    mensaje_final = ""
    
    for i in range(1, max_iter + 1):
        if fa - fb == 0:
            return columnas, filas, "Error: División por cero (fa y fb son iguales)."
            
        c = b - (fb * (a - b)) / (fa - fb)
        fc = evaluar(f_str, c)
        if isinstance(fc, complex): fc = fc.real
            
        error = abs(c - c_old)
        x_hist.append(c)
        filas.append([i, f"{a:.5f}", f"{b:.5f}", f"{c:.5f}", f"{fc:.5f}", f"{error:.5f}"])
        
        if error < tol and i > 1 or fc == 0:
            mensaje_final = f"Raíz encontrada en x = {c:.6f} con error {error:.6f}"
            root_found = True
            break
        if fa * fc < 0:
            b, fb = c, fc
        else:
            a, fa = c, fc
        c_old = c
    else:
        mensaje_final = "Máximo de iteraciones alcanzado."
        
    graficar_generico(f_str, x_hist, "Método de Falsa Posición", root_found)
    return columnas, filas, mensaje_final

# --- 3. PUNTO FIJO ---
def punto_fijo(g_str, x0, tol, max_iter):
    columnas = ["Iter", "xi", "xi+1 (g(xi))", "Error"]
    filas = []
    x_hist = [x0]
    root_found = False
    mensaje_final = ""
    
    for i in range(1, max_iter + 1):
        x1 = evaluar(g_str, x0)
        if isinstance(x1, complex):
            return columnas, filas, f"Error: Valor complejo generado en x = {x1}"
            
        error = abs(x1 - x0)
        x_hist.append(x1)
        filas.append([i, f"{x0:.6f}", f"{x1:.6f}", f"{error:.6f}"])
        
        if error < tol:
            mensaje_final = f"Raíz encontrada en x = {x1:.6f}"
            root_found = True
            break
        x0 = x1
    else:
        mensaje_final = "Máximo de iteraciones alcanzado."
        
    try:
        x_min, x_max = min(x_hist) - 1, max(x_hist) + 1
        x_vals = np.linspace(x_min, x_max, 400)
        y_vals_g = [evaluar(g_str, v).real if isinstance(evaluar(g_str, v), complex) else evaluar(g_str, v) for v in x_vals]
        
        plt.figure(figsize=(8, 5))
        plt.plot(x_vals, y_vals_g, label=f"g(x) = {g_str}", color='royalblue', linewidth=2)
        plt.plot(x_vals, x_vals, label="y = x", color='darkorange', linestyle='--', linewidth=2)
        
        px, py = x_hist[0], 0
        for i in range(1, len(x_hist)):
            nx, ny = x_hist[i-1], x_hist[i]
            plt.plot([px, nx], [py, ny], 'r-', alpha=0.5) 
            px, py = nx, ny
            nx, ny = x_hist[i], x_hist[i]
            plt.plot([px, nx], [py, ny], 'r-', alpha=0.5) 
            px, py = nx, ny
            
        if root_found:
            plt.plot(x_hist[-1], x_hist[-1], 'go', markersize=8, label=f'Raíz: {x_hist[-1]:.4f}')
            
        plt.title("Método de Punto Fijo (Telaraña)")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.legend()
        plt.grid(True, linestyle=':', alpha=0.7)
        plt.show(block=False)
    except Exception as e:
        pass

    return columnas, filas, mensaje_final

# --- 4. NEWTON-RAPHSON ---
def newton_raphson(f_str, x0, tol, max_iter):
    x_sym = sp.Symbol('x')
    f_str_sym = f_str.replace('cbrt(x)', 'x**(1/3)').replace('^', '**')
    try:
        f_sym = sp.sympify(f_str_sym)
        df_sym = sp.diff(f_sym, x_sym)
        df_str = str(df_sym).replace('**', '^') 
    except Exception:
        return [], [], "Error: La función no es válida para la derivación automática."

    def calc_df(x_val):
        entorno_df = {"x": x_val, "e": math.e, "pi": math.pi}
        entorno_df.update({k: v for k, v in math.__dict__.items() if not k.startswith('_')})
        try:
            return eval(str(df_sym), {"__builtins__": None}, entorno_df)
        except:
            return float(df_sym.subs(x_sym, x_val))

    columnas = ["Iter", "xi", "f(xi)", "f'(xi)", "Error"]
    filas = []
    x_hist = [x0]
    root_found = False
    mensaje_final = f"Derivada: f'(x) = {df_str}  |  "
    
    for i in range(1, max_iter + 1):
        fx = evaluar(f_str, x0)
        dfx = calc_df(x0)
        
        if dfx == 0:
            return columnas, filas, mensaje_final + "Error: Derivada igual a cero."
            
        x1 = x0 - (fx / dfx)
        error = abs(x1 - x0)
        x_hist.append(x1)
        
        filas.append([i, f"{x0:.5f}", f"{fx:.5f}", f"{dfx:.5f}", f"{error:.5f}"])
        
        if error < tol:
            mensaje_final += f"Raíz encontrada en x = {x1:.6f}"
            root_found = True
            break
        x0 = x1
    else:
        mensaje_final += "Máximo de iteraciones alcanzado."

    try:
        x_min, x_max = min(x_hist) - 1.5, max(x_hist) + 1.5
        x_vals = np.linspace(x_min, x_max, 400)
        y_vals_f = [evaluar(f_str, x) for x in x_vals]
        y_vals_df = [calc_df(x) for x in x_vals]

        plt.figure(figsize=(8, 5))
        plt.plot(x_vals, y_vals_f, label=f"f(x) = {f_str}", color='royalblue', linewidth=2)
        plt.plot(x_vals, y_vals_df, label=f"f'(x) = {df_str}", color='darkorange', linestyle='--', linewidth=2)
        plt.axhline(0, color='black', linewidth=1)
        
        y_hist = [evaluar(f_str, xi) for xi in x_hist]
        plt.plot(x_hist, y_hist, 'ro-', alpha=0.5, markersize=5)
        if root_found:
            plt.plot(x_hist[-1], 0, 'go', markersize=10, label=f'Raíz: {x_hist[-1]:.4f}')

        plt.title("Método de Newton-Raphson")
        plt.grid(True, linestyle=':', alpha=0.7)
        plt.legend()
        plt.show(block=False) 
    except Exception:
        pass

    return columnas, filas, mensaje_final

# --- 5. SECANTE ---
def secante(f_str, x0, x1, tol, max_iter):
    columnas = ["Iter", "x_i-1", "x_i", "f(x_i)", "Error"]
    filas = []
    x_hist = [x0, x1]
    root_found = False
    mensaje_final = ""
    
    for i in range(1, max_iter + 1):
        f0 = evaluar(f_str, x0)
        f1 = evaluar(f_str, x1)
        
        if f1 - f0 == 0:
            return columnas, filas, "Error: División por cero."
            
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        error = abs(x2 - x1)
        x_hist.append(x2)
        filas.append([i, f"{x0:.5f}", f"{x1:.5f}", f"{f1:.5f}", f"{error:.5f}"])
        
        if error < tol:
            mensaje_final = f"Raíz encontrada en x = {x2:.6f}"
            root_found = True
            break
        x0, x1 = x1, x2
    else:
        mensaje_final = "Máximo de iteraciones alcanzado."
        
    graficar_generico(f_str, x_hist, "Método de la Secante", root_found)
    return columnas, filas, mensaje_final

# --- 6. MULLER ---
def muller(f_str, x0, x1, x2, tol, max_iter):
    columnas = ["Iter", "x2 (actual)", "x3 (nuevo)", "Error"]
    filas = []
    x_hist = [x0, x1, x2]
    root_found = False
    mensaje_final = ""
    
    for i in range(1, max_iter + 1):
        f0 = evaluar(f_str, x0)
        f1 = evaluar(f_str, x1)
        f2 = evaluar(f_str, x2)
        
        h0, h1 = x1 - x0, x2 - x1
        if h0 == 0 or h1 == 0:
            return columnas, filas, "Error: Puntos repetidos (división por cero)."
            
        d0, d1 = (f1 - f0) / h0, (f2 - f1) / h1
        a = (d1 - d0) / (h1 + h0)
        b = a * h1 + d1
        c = f2
        
        disc = cmath.sqrt(b**2 - 4*a*c)
        den = b + disc if abs(b + disc) > abs(b - disc) else b - disc
            
        if den == 0:
            return columnas, filas, "Error: Denominador igual a cero."
            
        dx = -2 * c / den
        x3 = x2 + dx
        error = abs(dx) 
        x_hist.append(x3)
        
        filas.append([i, format_comp(x2), format_comp(x3), f"{error:.5f}"])
        
        if error < tol:
            mensaje_final = f"Raíz encontrada en x = {format_comp(x3)}"
            root_found = True
            break
        x0, x1, x2 = x1, x2, x3
    else:
        mensaje_final = "Máximo de iteraciones alcanzado."
        
    graficar_generico(f_str, x_hist, "Método de Muller", root_found)
    return columnas, filas, mensaje_final

# --- 7. DEFLACIÓN CON NEWTON-RAPHSON ---
def deflacion_newton(f_str, x0, tol, max_iter, num_raices):
    x_sym = sp.Symbol('x')
    f_str_sym = f_str.replace('cbrt(x)', 'x**(1/3)').replace('^', '**')
    try:
        f_sym = sp.sympify(f_str_sym)
        df_sym = sp.diff(f_sym, x_sym)
        df_str = str(df_sym).replace('**', '^')
    except Exception:
        return [], [], "Error: La función no es válida para la derivación automática."

    def calc_df(x_val):
        entorno_df = {"x": x_val, "e": math.e, "pi": math.pi}
        entorno_df.update({k: v for k, v in cmath.__dict__.items() if not k.startswith('_')})
        try:
            return eval(str(df_sym), {"__builtins__": None}, entorno_df)
        except:
            return complex(df_sym.subs(x_sym, x_val))

    columnas = ["Raíz Obj.", "Iter", "xi", "Error"]
    filas = []
    raices = []
    mensaje_final = f"Derivada: {df_str} | Raíces: "

    for r in range(num_raices):
        xi = x0
        root_found = False
        
        for i in range(1, max_iter + 1):
            fx = evaluar(f_str, xi)
            dfx = calc_df(xi)
            
            suma_deflacion = 0
            for raiz in raices:
                denom = (xi - raiz)
                if abs(denom) < 1e-12: denom = 1e-12 + 1e-12j
                suma_deflacion += 1 / denom
                
            denominador_newton = dfx - fx * suma_deflacion
            
            if abs(denominador_newton) == 0:
                filas.append([f"Raíz {r+1}", i, "Error", "Denominador Cero"])
                break
                
            x_next = xi - (fx / denominador_newton)
            error = abs(x_next - xi)
            
            filas.append([f"Raíz {r+1}", i, format_comp(xi), f"{error:.5f}"])
            
            if error < tol:
                raices.append(x_next)
                mensaje_final += f"[{format_comp(x_next)}]  "
                root_found = True
                break
            xi = x_next
            
        if not root_found:
            mensaje_final += f"[Raíz {r+1}: Fallo] "

    try:
        x_reales = [r.real for r in raices if not isinstance(r, complex) or abs(r.imag) < 1e-5]
        if x_reales:
            x_min, x_max = min(x_reales) - 2, max(x_reales) + 2
            x_vals = np.linspace(x_min, x_max, 400)
            y_vals = [evaluar(f_str, v) for v in x_vals]
            y_vals = [y.real if isinstance(y, complex) else y for y in y_vals]
            
            plt.figure(figsize=(8, 5))
            plt.plot(x_vals, y_vals, label=f"f(x) = {f_str}", color='royalblue')
            plt.axhline(0, color='black', linewidth=1)
            for real_root in x_reales:
                plt.plot(real_root, 0, 'go', markersize=8)
            plt.title(f"Deflación Newton-Raphson: {len(x_reales)} raíces reales encontradas")
            plt.grid(True, linestyle=':', alpha=0.7)
            plt.legend()
            plt.show(block=False)
    except Exception:
        pass

    return columnas, filas, mensaje_final

# --- 8. DEFLACIÓN CON MULLER ---
def deflacion_muller(f_str, x0, x1, x2, tol, max_iter, num_raices):
    def evaluar_deflactada(x_val, raices_encontradas):
        val = evaluar(f_str, x_val)
        for r in raices_encontradas:
            denom = x_val - r
            if abs(denom) < 1e-12: denom = 1e-12 + 1e-12j
            val = val / denom
        return val

    columnas = ["Raíz Obj.", "Iter", "x3 (nuevo)", "Error"]
    filas = []
    raices = []
    mensaje_final = "Raíces encontradas: "

    for r_idx in range(num_raices):
        curr_x0, curr_x1, curr_x2 = x0, x1, x2
        root_found = False
        
        for i in range(1, max_iter + 1):
            f0 = evaluar_deflactada(curr_x0, raices)
            f1 = evaluar_deflactada(curr_x1, raices)
            f2 = evaluar_deflactada(curr_x2, raices)
            
            h0, h1 = curr_x1 - curr_x0, curr_x2 - curr_x1
            if h0 == 0 or h1 == 0:
                filas.append([f"Raíz {r_idx+1}", i, "Error", "Puntos Repetidos"])
                break
                
            d0, d1 = (f1 - f0) / h0, (f2 - f1) / h1
            a = (d1 - d0) / (h1 + h0)
            b = a * h1 + d1
            c = f2
            
            disc = cmath.sqrt(b**2 - 4*a*c)
            den = b + disc if abs(b + disc) > abs(b - disc) else b - disc
            
            if den == 0:
                filas.append([f"Raíz {r_idx+1}", i, "Error", "Denominador Cero"])
                break
                
            dx = -2 * c / den
            x3 = curr_x2 + dx
            error = abs(dx)
            
            filas.append([f"Raíz {r_idx+1}", i, format_comp(x3), f"{error:.5f}"])
            
            if error < tol:
                raices.append(x3)
                mensaje_final += f"[{format_comp(x3)}]  "
                root_found = True
                break
                
            curr_x0, curr_x1, curr_x2 = curr_x1, curr_x2, x3
            
        if not root_found:
            mensaje_final += f"[Raíz {r_idx+1}: Fallo] "

    try:
        x_reales = [r.real for r in raices if not isinstance(r, complex) or abs(r.imag) < 1e-5]
        if x_reales:
            x_min, x_max = min(x_reales) - 2, max(x_reales) + 2
            x_vals = np.linspace(x_min, x_max, 400)
            y_vals = [evaluar(f_str, v) for v in x_vals]
            y_vals = [y.real if isinstance(y, complex) else y for y in y_vals]
            
            plt.figure(figsize=(8, 5))
            plt.plot(x_vals, y_vals, label=f"f(x) = {f_str}", color='darkorange')
            plt.axhline(0, color='black', linewidth=1)
            for real_root in x_reales:
                plt.plot(real_root, 0, 'go', markersize=8)
            plt.title(f"Deflación Muller: {len(x_reales)} raíces reales encontradas")
            plt.grid(True, linestyle=':', alpha=0.7)
            plt.legend()
            plt.show(block=False)
    except Exception:
        pass

    return columnas, filas, mensaje_final