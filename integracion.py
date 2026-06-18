import numpy as np
import sympy as sp

def calcular_integracion(metodo, str_funcion, a, b, parametro):
    x = sp.Symbol('x')
    str_funcion = str_funcion.replace('^', '**')
    
    # Interpretar la función matemáticamente
    f_sympy = sp.sympify(str_funcion, locals={'e': sp.E, 'pi': sp.pi})
    
    # --- 1. VALOR EXACTO (RED DE SEGURIDAD) ---
    exacta = None
    try:
        integral_obj = sp.integrate(f_sympy, (x, a, b))
        evaluacion = integral_obj.evalf()
        if evaluacion.is_number:
            exacta = float(evaluacion)
    except Exception:
        exacta = None

    # --- 2. EVALUADOR NUMÉRICO BLINDADO ---
    # Traduce la fórmula a matemáticas rápidas y seguras de Python
    f_rapida = sp.lambdify(x, f_sympy, "math")

    def f(val):
        try:
            # Intento 1: Ultra rápido
            return float(f_rapida(float(val)))
        except Exception:
            try:
                # Intento 2: Paracaídas 100% seguro de SymPy
                res = f_sympy.subs(x, float(val)).evalf()
                return float(res)
            except Exception:
                raise ValueError(f"Sintaxis inválida o indefinida en x={val}")

    # --- 3. LÓGICA DE LOS MÉTODOS ---
    filas_tabla = []
    aprox = 0
    formula_usada = ""

    if "Trapecio" in metodo or "Simpson" in metodo:
        if "Simple" in metodo:
            if "Trapecio" in metodo: n = 1
            elif "1/3" in metodo: n = 2
            elif "3/8" in metodo: n = 3
        else:
            n = int(parametro) 
            if "1/3" in metodo and n % 2 != 0:
                raise ValueError("Para Simpson 1/3 Compuesto, 'n' debe ser par.")
            if "3/8" in metodo and n % 3 != 0:
                raise ValueError("Para Simpson 3/8 Compuesto, 'n' debe ser múltiplo de 3.")

        h = (b - a) / n
        x_vals = np.linspace(a, b, n + 1)
        y_vals = [f(xv) for xv in x_vals]
        suma = 0

        for i in range(n + 1):
            if "Trapecio" in metodo:
                coef = 1 if i == 0 or i == n else 2
                formula_usada = f"h = {round(h, 6)} | Trapecio"
            elif "1/3" in metodo:
                if i == 0 or i == n: coef = 1
                elif i % 2 != 0: coef = 4
                else: coef = 2
                formula_usada = f"h = {round(h, 6)} | Simpson 1/3"
            elif "3/8" in metodo:
                if i == 0 or i == n: coef = 1
                elif i % 3 == 0: coef = 2
                else: coef = 3
                formula_usada = f"h = {round(h, 6)} | Simpson 3/8"

            termino = coef * y_vals[i]
            suma += termino
            filas_tabla.append([i, round(x_vals[i], 6), round(y_vals[i], 6), coef, round(termino, 6)])

        if "Trapecio" in metodo: aprox = (h / 2) * suma
        elif "1/3" in metodo: aprox = (h / 3) * suma
        elif "3/8" in metodo: aprox = (3 * h / 8) * suma

    elif "Romberg" in metodo:
        niveles = int(parametro)
        R = np.zeros((niveles, niveles))
        
        for i in range(niveles):
            n = 2**i
            h = (b - a) / n
            x_vals = np.linspace(a, b, n + 1)
            y_vals = [f(xv) for xv in x_vals]
            R[i][0] = (h / 2) * (y_vals[0] + 2*sum(y_vals[1:-1]) + y_vals[-1])
            
        for j in range(1, niveles):
            for i in range(j, niveles):
                R[i][j] = R[i][j-1] + (R[i][j-1] - R[i-1][j-1]) / (4**j - 1)

        for i in range(niveles):
            fila = [f"O(h^{2*(i+1)})"]
            for j in range(niveles):
                if j <= i: fila.append(round(R[i][j], 8))
                else: fila.append("")
            filas_tabla.append(fila)

        aprox = R[niveles-1][niveles-1]
        formula_usada = f"Romberg ({niveles} niveles de Richardson)"

    elif "Adaptativa" in metodo:
        tol = parametro
        
        def simpson_tercio(a_val, b_val):
            h_s = (b_val - a_val) / 2
            return (h_s/3) * (f(a_val) + 4*f((a_val+b_val)/2) + f(b_val))
            
        def adaptativa_recursiva(a_r, b_r, tol_r, nivel):
            # Límite de seguridad
            if nivel > 15: return simpson_tercio(a_r, b_r)
                
            m = (a_r + b_r) / 2
            S = simpson_tercio(a_r, b_r)
            S_izq = simpson_tercio(a_r, m)
            S_der = simpson_tercio(m, b_r)
            
            error_est = abs(S - (S_izq + S_der))
            
            if error_est < 15 * tol_r:
                area_tramo = S_izq + S_der
                filas_tabla.append([round(a_r, 6), round(b_r, 6), round(m, 6), round(area_tramo, 8), round(error_est/15, 8)])
                return area_tramo
            else:
                return adaptativa_recursiva(a_r, m, tol_r/2, nivel+1) + adaptativa_recursiva(m, b_r, tol_r/2, nivel+1)

        aprox = adaptativa_recursiva(a, b, tol, 1)
        formula_usada = f"Adaptativa (Tolerancia: {tol})"
    elif "Gaussiana" in metodo:
        puntos = int(parametro)
        if puntos not in [2, 3]:
            raise ValueError("Por ahora solo se soporta Cuadratura Gaussiana de 2 o 3 puntos.")

        # Valores de raíces (t) y pesos (c) tabulados para Legendre
        if puntos == 2:
            t_vals = [-1/np.sqrt(3), 1/np.sqrt(3)]
            c_vals = [1.0, 1.0]
            formula_usada = "Cuadratura Gaussiana (2 puntos)"
        elif puntos == 3:
            t_vals = [-np.sqrt(3/5), 0.0, np.sqrt(3/5)]
            c_vals = [5/9, 8/9, 5/9]
            formula_usada = "Cuadratura Gaussiana (3 puntos)"

        suma = 0
        # Transformación de límites [a, b] al intervalo [-1, 1]
        factor_dx = (b - a) / 2
        termino_indep = (b + a) / 2

        for i in range(puntos):
            t_i = t_vals[i]
            c_i = c_vals[i]
            
            # Mapeo de t a x
            x_i = factor_dx * t_i + termino_indep
            fx_i = f(x_i)
            
            termino = c_i * fx_i
            suma += termino
            
            # Guardamos para la tabla: ["i", "t_i (Raíz)", "c_i (Peso)", "f(x(t_i))", "Término Evaluado"]
            filas_tabla.append([i+1, round(t_i, 6), round(c_i, 6), round(fx_i, 6), round(termino, 6)])

        aprox = factor_dx * suma
        
    error_verdadero = abs(exacta - aprox) if exacta is not None else "N/A"
    return aprox, error_verdadero, filas_tabla, formula_usada, exacta

def calcular_integracion_discreta(metodo, x_datos, y_datos):
    """
    Calcula la integral numérica utilizando una serie de puntos discretos (vectores X e Y).
    """
    n = len(x_datos) - 1
    if n < 1: 
        raise ValueError("Se necesitan al menos 2 puntos para integrar.")
    if len(x_datos) != len(y_datos): 
        raise ValueError("Los vectores X e Y deben tener la misma cantidad de elementos.")

    filas_tabla = []
    suma = 0

    if "Trapecio" in metodo:
        # El método del trapecio soporta espacios (h) variables entre puntos
        for i in range(n):
            h_i = x_datos[i+1] - x_datos[i]
            area_i = (h_i / 2) * (y_datos[i] + y_datos[i+1])
            suma += area_i
            filas_tabla.append([i, round(x_datos[i], 6), round(x_datos[i+1], 6), round(y_datos[i], 6), round(y_datos[i+1], 6), round(h_i, 6), round(area_i, 6)])
        formula = "Trapecio Discreto (áreas por subtramo)"
        return suma, "N/A", filas_tabla, formula, None

    elif "Simpson 1/3" in metodo:
        if n % 2 != 0: 
            raise ValueError("Simpson 1/3 requiere un número par de intervalos (impar de puntos).")
        h = x_datos[1] - x_datos[0] # Asume h constante
        suma = y_datos[0] + y_datos[-1]
        
        for i in range(1, n):
            coef = 4 if i % 2 != 0 else 2
            termino = coef * y_datos[i]
            suma += termino
            filas_tabla.append([i, round(x_datos[i], 6), round(y_datos[i], 6), coef, round(termino, 6)])
            
        aprox = (h / 3) * suma
        return aprox, "N/A", filas_tabla, f"Simpson 1/3 Discreto (h={round(h, 4)})", None

    elif "Simpson 3/8" in metodo:
        if n % 3 != 0: 
            raise ValueError("Simpson 3/8 requiere un número de intervalos múltiplo de 3.")
        h = x_datos[1] - x_datos[0]
        suma = y_datos[0] + y_datos[-1]
        
        for i in range(1, n):
            coef = 2 if i % 3 == 0 else 3
            termino = coef * y_datos[i]
            suma += termino
            filas_tabla.append([i, round(x_datos[i], 6), round(y_datos[i], 6), coef, round(termino, 6)])
            
        aprox = (3 * h / 8) * suma
        return aprox, "N/A", filas_tabla, f"Simpson 3/8 Discreto (h={round(h, 4)})", None

    else:
        raise ValueError(f"El método '{metodo}' requiere una función f(x), no puntos discretos.")