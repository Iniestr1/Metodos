import numpy as np
import sympy as sp

def primera_derivada_neville(str_funcion, x_val, h_inicial, iteraciones):
    """
    Calcula la primera derivada usando Extrapolación de Richardson (tipo Neville).
    Retorna la matriz escalonada, la aproximación y el error.
    """
    f_sympy = sp.sympify(str_funcion.replace('^', '**'))
    x = sp.Symbol('x')
    
    # Derivada exacta para comparar
    derivada_exacta = float(sp.diff(f_sympy, x).subs(x, x_val))
    
    def f(val):
        return float(f_sympy.subs(x, val))
        
    n = iteraciones
    D = np.zeros((n, n))
    
    # Primera columna: Diferencias centrales
    for i in range(n):
        h = h_inicial / (2**i)
        D[i][0] = (f(x_val + h) - f(x_val - h)) / (2 * h)
        
    # Construcción de la tabla (Neville/Richardson)
    for j in range(1, n):
        for i in range(j, n):
            # Fórmula de Richardson
            D[i][j] = D[i][j-1] + (D[i][j-1] - D[i-1][j-1]) / (4**j - 1)
            
    # Preparar datos para la UI
    tabla_visual = []
    for i in range(n):
        fila = [f"h/{2**i}"]
        for j in range(n):
            if j <= i:
                fila.append(round(D[i][j], 8))
            else:
                fila.append("")
        tabla_visual.append(fila)
        
    aprox_final = D[n-1][n-1]
    error = abs(derivada_exacta - aprox_final)
    
    return aprox_final, error, tabla_visual, derivada_exacta

def segunda_derivada_taylor(str_funcion, x_val, h, num_puntos):
    """
    Calcula la segunda derivada usando diferencias finitas (Taylor).
    Soporta 3, 4 y 5 puntos.
    """
    f_sympy = sp.sympify(str_funcion.replace('^', '**'))
    x = sp.Symbol('x')
    
    # Derivada exacta
    derivada_exacta = float(sp.diff(f_sympy, x, 2).subs(x, x_val))
    
    def f(val):
        return float(f_sympy.subs(x, val))
        
    fx = f(x_val)
    fx_mas_h = f(x_val + h)
    fx_menos_h = f(x_val - h)
    
    tabla_evaluaciones = [
        ["f(x)", x_val, fx],
        ["f(x+h)", round(x_val+h, 4), fx_mas_h],
        ["f(x-h)", round(x_val-h, 4), fx_menos_h]
    ]

    if num_puntos == 3:
        # Centrada O(h^2)
        aprox = (fx_menos_h - 2*fx + fx_mas_h) / (h**2)
        formula = "Centrada 3pts: [f(x-h) - 2f(x) + f(x+h)] / h^2"
        
    elif num_puntos == 4:
        # Hacia adelante O(h^2)
        fx_mas_2h = f(x_val + 2*h)
        fx_mas_3h = f(x_val + 3*h)
        tabla_evaluaciones.extend([
            ["f(x+2h)", round(x_val+2*h, 4), fx_mas_2h],
            ["f(x+3h)", round(x_val+3*h, 4), fx_mas_3h]
        ])
        aprox = (2*fx - 5*fx_mas_h + 4*fx_mas_2h - fx_mas_3h) / (h**2)
        formula = "Adelante 4pts: [2f(x) - 5f(x+h) + 4f(x+2h) - f(x+3h)] / h^2"
        
    elif num_puntos == 5:
        # Centrada O(h^4)
        fx_mas_2h = f(x_val + 2*h)
        fx_menos_2h = f(x_val - 2*h)
        tabla_evaluaciones.extend([
            ["f(x+2h)", round(x_val+2*h, 4), fx_mas_2h],
            ["f(x-2h)", round(x_val-2*h, 4), fx_menos_2h]
        ])
        aprox = (-fx_mas_2h + 16*fx_mas_h - 30*fx + 16*fx_menos_h - fx_menos_2h) / (12 * h**2)
        formula = "Centrada 5pts: [-f(x+2h)+16f(x+h)-30f(x)+16f(x-h)-f(x-2h)] / 12h^2"
    
    error = abs(derivada_exacta - aprox)
    return aprox, error, tabla_evaluaciones, formula, derivada_exacta