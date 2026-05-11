import numpy as np
import sympy as sp
import math

def taylor(str_funcion, a, x_val, n):
    """
    Calcula el polinomio de Taylor de grado 'n' para una función f(x)
    centrada en 'a' y evaluada en 'x_val'.
    """
    x = sp.Symbol('x')
    try:
        # Convertimos el string a una expresión matemática de SymPy
        str_funcion = str_funcion.replace('^', '**')
        f = sp.sympify(str_funcion)
    except Exception as e:
        raise ValueError(f"Error en la sintaxis de f(x). Detalle: {e}")

    valor_aprox = 0
    filas_tabla = []
    
    for i in range(n + 1):
        # Derivada de orden i
        derivada = sp.diff(f, x, i)
        # Evaluamos la derivada en el punto 'a'
        derivada_en_a = float(derivada.subs(x, a))
        
        # Término de Taylor: (f^(i)(a) / i!) * (x - a)^i
        termino = (derivada_en_a / math.factorial(i)) * ((x_val - a)**i)
        valor_aprox += termino
        
        # Formatear derivada para mostrar en tabla
        str_der = str(derivada).replace('**', '^')
        filas_tabla.append([i, str_der, round(derivada_en_a, 6), round(termino, 6), round(valor_aprox, 6)])
        
    # Calculamos el error verdadero (Valor Real - Valor Aproximado)
    valor_real = float(f.subs(x, x_val))
    error_verdadero = abs(valor_real - valor_aprox)

    return valor_aprox, error_verdadero, filas_tabla

def minimos_cuadrados(x_datos, y_datos, grado):
    """
    Calcula la regresión por mínimos cuadrados polinomial.
    Funciona para cuadrático (2), cúbico (3) o cualquier grado (n).
    """
    # polyfit encuentra los coeficientes que minimizan el error cuadrático
    coeficientes = np.polyfit(x_datos, y_datos, grado)
    polinomio = np.poly1d(coeficientes)
    
    filas_tabla = []
    suma_errores_cuadrados = 0
    
    # Evaluar el polinomio en cada punto para ver el error
    for i in range(len(x_datos)):
        y_aprox = polinomio(x_datos[i])
        error_i = abs(y_datos[i] - y_aprox)
        suma_errores_cuadrados += error_i**2
        filas_tabla.append([i, x_datos[i], y_datos[i], round(y_aprox, 6), round(error_i, 6)])
        
    # Crear un string presentable del polinomio final
    str_ecuacion = "f(x) = "
    for i, coef in enumerate(coeficientes):
        potencia = grado - i
        if potencia > 1:
            str_ecuacion += f"{round(coef, 4)}x^{potencia} "
        elif potencia == 1:
            str_ecuacion += f"{round(coef, 4)}x "
        else:
            str_ecuacion += f"{round(coef, 4)}"
            
        if i < len(coeficientes) - 1 and coeficientes[i+1] >= 0:
            str_ecuacion += "+ "
            
    return str_ecuacion, suma_errores_cuadrados, filas_tabla