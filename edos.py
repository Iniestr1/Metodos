import numpy as np
import sympy as sp
import math

def resolver_edo(metodo, str_funcion, x0, y0, xf, h, grado_taylor=2, tol=1e-5):
    x_sym, y_sym = sp.symbols('x y')
    str_funcion = str_funcion.replace('^', '**')
    
    try:
        f_expr = sp.sympify(str_funcion, locals={'e': sp.E, 'pi': sp.pi})
    except Exception as e:
        raise ValueError(f"Error en sintaxis: {e}")

    f_num = sp.lambdify((x_sym, y_sym), f_expr, "math")
    def f(val_x, val_y):
        try: return float(f_num(float(val_x), float(val_y)))
        except: return float(f_expr.subs({x_sym: val_x, y_sym: val_y}).evalf())

    x_vals, y_vals = [x0], [y0]
    filas_tabla = []
    
    # --- LÓGICA PASO ADAPTABLE (RKF45) ---
    if "RKF45" in metodo:
        xi, yi = x0, y0
        i = 0
        while xi < xf:
            # Prevenir pasarse del límite superior
            if xi + h > xf: 
                h = xf - xi

            # Coeficientes de Butcher para RKF45
            k1 = h * f(xi, yi)
            k2 = h * f(xi + h/4, yi + k1/4)
            k3 = h * f(xi + 3*h/8, yi + 3*k1/32 + 9*k2/32)
            k4 = h * f(xi + 12*h/13, yi + 1932*k1/2197 - 7200*k2/2197 + 7296*k3/2197)
            k5 = h * f(xi + h, yi + 439*k1/216 - 8*k2 + 3680*k3/513 - 845*k4/4104)
            k6 = h * f(xi + h/2, yi - 8*k1/27 + 2*k2 - 3544*k3/2565 + 1859*k4/4104 - 11*k5/40)

            # Aproximación de orden 4 y orden 5
            y_next_4 = yi + 25*k1/216 + 1408*k3/2565 + 2197*k4/4104 - k5/5
            y_next_5 = yi + 16*k1/135 + 6656*k3/12825 + 28561*k4/56430 - 9*k5/50 + 2*k6/55

            # Error de truncamiento
            error = abs(y_next_5 - y_next_4)
            error_ajustado = error if error > 0 else 1e-20 # Evitar división por cero

            # Factor de corrección para el nuevo h
            q = 0.84 * (tol / error_ajustado)**0.25

            if error <= tol:
                # Paso Aceptado
                xi = xi + h
                yi = y_next_4 # Normalmente se avanza con la de orden 4 en RKF45 original
                x_vals.append(xi)
                y_vals.append(yi)
                filas_tabla.append([i, round(xi, 6), round(yi, 6), round(h, 6), round(error, 8), "Aceptado"])
                i += 1
            
            # Ajustar h para la siguiente iteración (o reintentar si fue rechazado)
            h = h * q
            # Límites de seguridad para h
            if h > 4.0: h = 4.0
            if h < 1e-6: raise ValueError("El paso 'h' se hizo demasiado pequeño para alcanzar la tolerancia.")

        return x_vals, y_vals, filas_tabla

    # --- LÓGICA PASO FIJO (Métodos Anteriores) ---
    n_pasos = int(round((xf - x0) / h))
    
    derivadas_lambdas = []
    if "Taylor" in metodo:
        derivadas_expr = [f_expr]
        for _ in range(1, grado_taylor):
            D = sp.diff(derivadas_expr[-1], x_sym) + sp.diff(derivadas_expr[-1], y_sym) * f_expr
            derivadas_expr.append(sp.simplify(D))
        for expr in derivadas_expr:
            derivadas_lambdas.append(sp.lambdify((x_sym, y_sym), expr, "math"))

    for i in range(n_pasos):
        xi, yi = x_vals[-1], y_vals[-1]
        
        if "Euler" in metodo:
            y_next = yi + h * f(xi, yi)
            filas_tabla.append([i, round(xi, 6), round(yi, 6), round(f(xi, yi), 6), round(y_next, 6)])
            
        elif "Heun" in metodo:
            f_xy = f(xi, yi)
            y_pred = yi + h * f_xy
            f_next = f(xi + h, y_pred)
            y_next = yi + (h / 2) * (f_xy + f_next)
            filas_tabla.append([i, round(xi, 6), round(yi, 6), round(y_pred, 6), round(f_xy, 6), round(f_next, 6), round(y_next, 6)])
            
        elif "Taylor" in metodo:
            y_next = yi
            terminos = []
            for k in range(grado_taylor):
                try: val_derivada = float(derivadas_lambdas[k](float(xi), float(yi)))
                except: val_derivada = float(derivadas_expr[k].subs({x_sym: xi, y_sym: yi}).evalf())
                termino = (val_derivada / math.factorial(k + 1)) * (h ** (k + 1))
                y_next += termino
                terminos.append(round(termino, 6))
            filas_tabla.append([i, round(xi, 6), round(yi, 6)] + terminos + [round(y_next, 6)])
            
        elif "Runge-Kutta 2" in metodo:
            k1 = f(xi, yi)
            k2 = f(xi + h, yi + h * k1)
            y_next = yi + (h / 2) * (k1 + k2)
            filas_tabla.append([i, round(xi, 6), round(yi, 6), round(k1, 6), round(k2, 6), round(y_next, 6)])
            
        elif "Runge-Kutta 4" in metodo:
            k1 = f(xi, yi)
            k2 = f(xi + 0.5 * h, yi + 0.5 * h * k1)
            k3 = f(xi + 0.5 * h, yi + 0.5 * h * k2)
            k4 = f(xi + h, yi + h * k3)
            y_next = yi + (h / 6) * (k1 + 2*k2 + 2*k3 + k4)
            filas_tabla.append([i, round(xi, 6), round(yi, 6), round(k1, 6), round(k2, 6), round(k3, 6), round(k4, 6), round(y_next, 6)])
            
        x_vals.append(xi + h)
        y_vals.append(y_next)

    return x_vals, y_vals, filas_tabla