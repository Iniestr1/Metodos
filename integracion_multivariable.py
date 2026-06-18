import numpy as np
import sympy as sp

def calcular_multivariable(metodo, str_funcion, a, b, c, d, parametro):
    """
    Calcula la integral doble de una función f(x, y).
    a, b: Límites para la variable x
    c, d: Límites para la variable y
    parametro: String con el formato "nx, ny" (ej: "2, 2")
    """
    # --- 1. PROCESAR PARÁMETROS (nx, ny) ---
    try:
        partes = parametro.split(',')
        nx = int(partes[0].strip())
        ny = int(partes[1].strip())
    except:
        raise ValueError("El parámetro debe tener el formato 'nx, ny' (ejemplo: 2, 2 o 3, 3)")

    if nx <= 0 or ny <= 0:
        raise ValueError("Los valores nx y ny deben ser mayores a 0.")

    # --- 2. CONFIGURACIÓN MATEMÁTICA ---
    x, y = sp.symbols('x y')
    str_funcion = str_funcion.replace('^', '**')
    f_sympy = sp.sympify(str_funcion, locals={'e': sp.E, 'pi': sp.pi})

    # Intentar calcular el valor exacto analítico usando integración doble
    exacta = None
    try:
        integral_obj = sp.integrate(sp.integrate(f_sympy, (x, a, b)), (y, c, d))
        evaluacion = integral_obj.evalf()
        if evaluacion.is_number:
            exacta = float(evaluacion)
    except Exception:
        exacta = None

    # Función evaluadora segura
    f_rapida = sp.lambdify((x, y), f_sympy, "math")

    def f(val_x, val_y):
        try:
            return float(f_rapida(float(val_x), float(val_y)))
        except Exception:
            try:
                res = f_sympy.subs({x: float(val_x), y: float(val_y)}).evalf()
                return float(res)
            except Exception:
                raise ValueError(f"Indefinición matemática al evaluar en x={val_x}, y={val_y}")

    suma_total = 0
    filas_tabla = []

    # --- 3. LÓGICA DE CUADRATURA GAUSSIANA 2D ---
    if "Gaussiana" in metodo:
        if nx not in [2, 3] or ny not in [2, 3]:
            raise ValueError("Para Gaussiana Multivariable, los puntos 'nx, ny' deben ser 2 o 3 (ej: '2, 2' o '3, 2').")
            
        def obtener_gauss(n):
            if n == 2: return [-1/np.sqrt(3), 1/np.sqrt(3)], [1.0, 1.0]
            elif n == 3: return [-np.sqrt(3/5), 0.0, np.sqrt(3/5)], [5/9, 8/9, 5/9]

        tx_vals, cx_vals = obtener_gauss(nx) # Raíces y pesos en X
        ty_vals, cy_vals = obtener_gauss(ny) # Raíces y pesos en Y

        # Factores de transformación para pasar de [-1, 1] a los límites reales
        factor_x = (b - a) / 2
        factor_y = (d - c) / 2
        termino_indep_x = (b + a) / 2
        termino_indep_y = (d + c) / 2
        
        for j in range(ny):
            for i in range(nx):
                # Mapeo de coordenadas
                x_val = factor_x * tx_vals[i] + termino_indep_x
                y_val = factor_y * ty_vals[j] + termino_indep_y
                
                # Multiplicación de pesos: w_i * w_j
                coef_peso = cx_vals[i] * cy_vals[j]
                
                f_xy = f(x_val, y_val)
                termino = coef_peso * f_xy
                suma_total += termino
                
                filas_tabla.append([
                    i+1, 
                    j+1, 
                    round(x_val, 6), 
                    round(y_val, 6), 
                    round(f_xy, 6), 
                    round(coef_peso, 6), 
                    round(termino, 6)
                ])
        
        # El área final se multiplica por el Jacobiano (factor_x * factor_y)
        aprox = factor_x * factor_y * suma_total
        formula_usada = f"Gaussiana 2D ({nx} pts X, {ny} pts Y)"

    # --- 4. LÓGICA DE TRAPECIO Y SIMPSON MULTIVARIABLE ---
    else:
        if "Simpson" in metodo and (nx % 2 != 0 or ny % 2 != 0):
            raise ValueError("Para Simpson 1/3 Multivariable, los intervalos 'nx' y 'ny' DEBEN ser números pares.")

        def pesos_trapecio(n):
            w = np.full(n + 1, 2.0)
            w[0] = 1.0; w[n] = 1.0
            return w

        def pesos_simpson(n):
            w = np.ones(n + 1)
            w[1:n:2] = 4.0 
            w[2:n-1:2] = 2.0 
            return w

        hx = (b - a) / nx
        hy = (d - c) / ny

        if "Trapecio" in metodo:
            wx, wy = pesos_trapecio(nx), pesos_trapecio(ny)
            factor_metodo = (hx * hy) / 4.0
            formula_usada = f"Trapecio Múltiple (nx={nx}, ny={ny})"
        elif "Simpson" in metodo:
            wx, wy = pesos_simpson(nx), pesos_simpson(ny)
            factor_metodo = (hx * hy) / 9.0
            formula_usada = f"Simpson 1/3 Múltiple (nx={nx}, ny={ny})"

        x_vals = np.linspace(a, b, nx + 1)
        y_vals = np.linspace(c, d, ny + 1)

        for j in range(ny + 1):
            for i in range(nx + 1):
                coeficiente_ij = wx[i] * wy[j] 
                f_xy = f(x_vals[i], y_vals[j])
                termino = coeficiente_ij * f_xy
                suma_total += termino
                
                coef_limpio = int(coeficiente_ij) if coeficiente_ij.is_integer() else round(coeficiente_ij, 4)
                
                filas_tabla.append([i, j, round(x_vals[i], 6), round(y_vals[j], 6), round(f_xy, 6), coef_limpio, round(termino, 6)])

        aprox = factor_metodo * suma_total

    # --- 5. RESULTADOS FINALES ---
    error_verdadero = abs(exacta - aprox) if exacta is not None else "N/A"

    return aprox, error_verdadero, filas_tabla, formula_usada, exacta