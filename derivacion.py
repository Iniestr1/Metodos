import sympy as sp

def calcular_derivada(str_funcion, x_val, h, tipo_derivada, puntos):
    """
    Calcula la 1ra o 2da derivada usando fórmulas de 2, 3 o 4 puntos.
    tipo_derivada: 1 (primera) o 2 (segunda)
    puntos: 2, 3, o 4
    """
    f_sympy = sp.sympify(str_funcion.replace('^', '**'))
    x = sp.Symbol('x')
    
    # Función auxiliar para evaluar
    def f(val):
        return float(f_sympy.subs(x, val))
        
    fx = f(x_val)
    fx_mas_h = f(x_val + h)
    fx_menos_h = f(x_val - h)
    
    # Iniciamos la tabla de evaluaciones que se mostrará en la interfaz
    tabla_evaluaciones = [["f(x)", round(x_val, 6), round(fx, 8)]]
    
    if tipo_derivada == 1:
        derivada_exacta = float(sp.diff(f_sympy, x).subs(x, x_val))
        
        if puntos == 2:
            aprox = (fx_mas_h - fx) / h
            formula = "Hacia adelante (2 pts): [f(x+h) - f(x)] / h"
            tabla_evaluaciones.append(["f(x+h)", round(x_val+h, 6), round(fx_mas_h, 8)])
            
        elif puntos == 3:
            aprox = (fx_mas_h - fx_menos_h) / (2 * h)
            formula = "Centrada (3 pts): [f(x+h) - f(x-h)] / 2h"
            tabla_evaluaciones.extend([
                ["f(x+h)", round(x_val+h, 6), round(fx_mas_h, 8)],
                ["f(x-h)", round(x_val-h, 6), round(fx_menos_h, 8)]
            ])
            
        elif puntos == 4:
            # Fórmula centrada de alta precisión
            fx_mas_2h = f(x_val + 2*h)
            fx_menos_2h = f(x_val - 2*h)
            aprox = (fx_menos_2h - 8*fx_menos_h + 8*fx_mas_h - fx_mas_2h) / (12 * h)
            formula = "Centrada (4 pts útiles): [f(x-2h) - 8f(x-h) + 8f(x+h) - f(x+2h)] / 12h"
            tabla_evaluaciones.extend([
                ["f(x+h)", round(x_val+h, 6), round(fx_mas_h, 8)],
                ["f(x-h)", round(x_val-h, 6), round(fx_menos_h, 8)],
                ["f(x+2h)", round(x_val+2*h, 6), round(fx_mas_2h, 8)],
                ["f(x-2h)", round(x_val-2*h, 6), round(fx_menos_2h, 8)]
            ])

    elif tipo_derivada == 2:
        derivada_exacta = float(sp.diff(f_sympy, x, 2).subs(x, x_val))
        
        if puntos == 2:
            raise ValueError("Matemáticamente, se requieren mínimo 3 puntos para la segunda derivada.")
            
        elif puntos == 3:
            aprox = (fx_mas_h - 2*fx + fx_menos_h) / (h**2)
            formula = "Centrada (3 pts): [f(x+h) - 2f(x) + f(x-h)] / h^2"
            tabla_evaluaciones.extend([
                ["f(x+h)", round(x_val+h, 6), round(fx_mas_h, 8)],
                ["f(x-h)", round(x_val-h, 6), round(fx_menos_h, 8)]
            ])
            
        elif puntos == 4:
            # Diferencia hacia adelante para 4 puntos
            fx_mas_2h = f(x_val + 2*h)
            fx_mas_3h = f(x_val + 3*h)
            aprox = (2*fx - 5*fx_mas_h + 4*fx_mas_2h - fx_mas_3h) / (h**2)
            formula = "Adelante (4 pts): [2f(x) - 5f(x+h) + 4f(x+2h) - f(x+3h)] / h^2"
            tabla_evaluaciones.extend([
                ["f(x+h)", round(x_val+h, 6), round(fx_mas_h, 8)],
                ["f(x+2h)", round(x_val+2*h, 6), round(fx_mas_2h, 8)],
                ["f(x+3h)", round(x_val+3*h, 6), round(fx_mas_3h, 8)]
            ])

    error = abs(derivada_exacta - aprox)
    return aprox, error, tabla_evaluaciones, formula, derivada_exacta