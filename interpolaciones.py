import numpy as np
import math


def generar_y_desde_funcion(str_funcion, x_datos):
    """
    Toma una cadena de texto f(x) y una lista de valores X, 
    y retorna la lista de valores Y evaluados.
    """
    y_datos = []
    
    entorno_matematico = {
        'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
        'exp': np.exp, 'log': np.log, 'log10': np.log10,
        'sqrt': np.sqrt, 'pi': np.pi, 'e': np.e,
        'x': 0 
    }
    
    # Limpieza automática: cambiamos el gorrito de potencia por la sintaxis de Python
    str_funcion = str_funcion.replace('^', '**')
    
    for val in x_datos:
        entorno_matematico['x'] = float(val)
        try:
            y_val = eval(str_funcion, {"__builtins__": None}, entorno_matematico)
            y_datos.append(float(y_val))
        except SyntaxError:
            # Capturamos el error exacto que te salió y damos una instrucción clara
            raise ValueError("Revisa la sintaxis. Recuerda usar '*' para multiplicar (ej. 2*x en lugar de 2x) y usa '.' para decimales (ej. 1.5).")
        except Exception as e:
            raise ValueError(f"Error al evaluar f(x) en x={val}.\nDetalle: {e}")
            
    return y_datos


def interpolacion_lagrange(x_datos, y_datos, x_interpolar, m_derivada_n_mas_1=None):
    """
    Calcula la interpolación de Lagrange y prepara los datos para tabular.
    
    Parámetros:
    - x_datos, y_datos: Listas o arreglos con los puntos conocidos.
    - x_interpolar: El valor de X que queremos evaluar.
    - m_derivada_n_mas_1: (Opcional) El valor máximo de la derivada (n+1) en el intervalo 
                          para calcular el error máximo teórico.
                          
    Retorna:
    - resultado: El valor interpolado Y.
    - tabla_pasos: Lista de listas con [i, x_i, y_i, L_i, Termino_i] para la interfaz.
    - error_maximo: El valor del error (si se proporcionó la derivada).
    """
    n = len(x_datos)
    resultado = 0
    tabla_pasos = []
    
    # Construcción de los polinomios de Lagrange L_i(x)
    for i in range(n):
        L_i = 1
        for j in range(n):
            if i != j:
                L_i *= (x_interpolar - x_datos[j]) / (x_datos[i] - x_datos[j])
        
        termino = L_i * y_datos[i]
        resultado += termino
        
        # Guardamos la fila para la tabla visual (redondeando a 6 decimales para estética)
        tabla_pasos.append([i, x_datos[i], y_datos[i], round(L_i, 6), round(termino, 6)])

    # Cálculo del Error Máximo de Interpolación
    error_maximo = None
    if m_derivada_n_mas_1 is not None:
        # Fórmula del error: E = |(f^(n+1)(xi) / (n+1)!) * Productoria(x - xi)|
        productoria = 1
        for x in x_datos:
            productoria *= (x_interpolar - x)
        
        error_maximo = abs((m_derivada_n_mas_1 / math.factorial(n)) * productoria)

    return resultado, tabla_pasos, error_maximo


def interpolacion_neville(x_datos, y_datos, x_interpolar):
    """
    Construye la matriz del método de Neville iterativamente.
    
    Retorna:
    - matriz_neville: Una lista de listas que representa la tabla escalonada. 
                      Ideal para iterar y mostrar en el Treeview.
    - resultado: El valor final interpolado en la punta de la pirámide.
    """
    n = len(x_datos)
    # Inicializamos una matriz NxN con ceros
    Q = np.zeros((n, n))
    
    # La primera columna son los valores de Y
    for i in range(n):
        Q[i][0] = y_datos[i]
        
    # Construimos la tabla iterando por columnas y luego por filas
    for j in range(1, n):
        for i in range(j, n):
            # Fórmula de Neville
            Q[i][j] = ((x_interpolar - x_datos[i-j]) * Q[i][j-1] - (x_interpolar - x_datos[i]) * Q[i-1][j-1]) / (x_datos[i] - x_datos[i-j])
            
    # Formateamos la matriz para retornar una lista de listas amigable para la interfaz
    # Llenamos con cadenas vacías "" los espacios no calculados para que la tabla en UI se vea como un triángulo
    tabla_visual = []
    for i in range(n):
        fila = [x_datos[i]] # La primera columna de la tabla visual será la X
        for j in range(n):
            if j <= i:
                fila.append(round(Q[i][j], 6))
            else:
                fila.append("") # Espacio vacío en la matriz escalonada
        tabla_visual.append(fila)

    resultado = Q[n-1][n-1]
    return resultado, tabla_visual


def diferencias_divididas(x_datos, y_datos):
    """
    Calcula la tabla de diferencias divididas de Newton.
    
    Retorna:
    - coeficientes: Los valores b0, b1, b2... bn (la diagonal principal).
    - tabla_diferencias: Matriz formateada para el Treeview.
    """
    n = len(x_datos)
    # Matriz inicial llena de ceros
    F = np.zeros((n, n))
    
    # La primera columna son los valores de Y
    for i in range(n):
        F[i][0] = y_datos[i]

# Calculamos las diferencias divididas
    for j in range(1, n):
        for i in range(n - j):
            F[i][j] = (F[i+1][j-1] - F[i][j-1]) / (x_datos[i+j] - x_datos[i])
            
    # Extraemos los coeficientes (la primera fila de la matriz F)
    coeficientes = F[0, :].tolist()
    
    # Preparamos la tabla visual
    tabla_visual = []
    for i in range(n):
        fila = [x_datos[i], y_datos[i]]
        for j in range(1, n):
            if j < n - i:
                fila.append(round(F[i][j], 6))
            else:
                fila.append("") # Espacios vacíos de la matriz triangular
        tabla_visual.append(fila)
        
    return coeficientes, tabla_visual