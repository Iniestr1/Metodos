import numpy as np

def eliminacion_gaussiana(matriz_A, vector_b, tipo_pivoteo="Parcial de Columna"):
    """
    Resuelve el sistema Ax = b usando Eliminación Gaussiana con pivoteo.
    """
    try:
        A = np.array(matriz_A, dtype=float)
        b = np.array(vector_b, dtype=float).flatten()
        n = len(b)
        
        if A.shape[0] != n or A.shape[1] != n:
            raise ValueError("La matriz A debe ser cuadrada (n x n) y coincidir con b.")

        # Matriz aumentada [A | b]
        Ab = np.column_stack((A, b))
        
        filas_tabla = [] # Para documentar el proceso en la GUI
        
        # --- VECTOR DE ESCALAS (Para Pivoteo Escalado) ---
        escalas = np.max(np.abs(A), axis=1)
        if tipo_pivoteo == "Parcial Escalado" and any(escalas == 0):
            raise ValueError("El sistema tiene una fila de ceros, no tiene solución única.")

        # --- ELIMINACIÓN HACIA ADELANTE ---
        for k in range(n - 1):
            # 1. ESTRATEGIAS DE PIVOTEO
            if tipo_pivoteo == "Parcial de Columna":
                # Busca el mayor valor absoluto en la columna actual, de la diagonal hacia abajo
                fila_pivote = np.argmax(np.abs(Ab[k:n, k])) + k
            
            elif tipo_pivoteo == "Parcial Escalado":
                # Busca el mayor (valor absoluto / escala de su fila)
                cocientes = np.abs(Ab[k:n, k]) / escalas[k:n]
                fila_pivote = np.argmax(cocientes) + k

            # Intercambio de filas si el pivote no está en la diagonal actual
            if fila_pivote != k:
                Ab[[k, fila_pivote]] = Ab[[fila_pivote, k]]
                if tipo_pivoteo == "Parcial Escalado":
                    escalas[[k, fila_pivote]] = escalas[[fila_pivote, k]]
                filas_tabla.append([f"Paso {k+1}", f"F{k+1} <-> F{fila_pivote+1}", f"Pivote: {round(Ab[k,k], 4)}"])

            # Verificación de singularidad
            if abs(Ab[k, k]) < 1e-12:
                raise ValueError("El sistema es singular o cercano a singular.")

            # 2. ELIMINACIÓN
            for i in range(k + 1, n):
                factor = Ab[i, k] / Ab[k, k]
                Ab[i, k:] = Ab[i, k:] - factor * Ab[k, k:]
                filas_tabla.append([f"Paso {k+1}", f"F{i+1} = F{i+1} - ({round(factor,4)})*F{k+1}", "Eliminación"])

        # --- SUSTITUCIÓN HACIA ATRÁS ---
        x = np.zeros(n)
        for i in range(n - 1, -1, -1):
            if abs(Ab[i, i]) < 1e-12:
                raise ValueError("Sistema singular detectado en la sustitución.")
            suma = np.dot(Ab[i, i+1:n], x[i+1:n])
            x[i] = (Ab[i, -1] - suma) / Ab[i, i]

        return x, filas_tabla, Ab

    except Exception as e:
        raise ValueError(str(e))

def factorizacion_lu(matriz_A, vector_b):
    """
    Resuelve el sistema Ax = b utilizando Factorización LU (Método de Doolittle).
    Devuelve las raíces, los pasos documentados, y las matrices L y U.
    """
    try:
        A = np.array(matriz_A, dtype=float)
        b = np.array(vector_b, dtype=float).flatten()
        n = len(b)

        if A.shape[0] != n or A.shape[1] != n:
            raise ValueError("La matriz A debe ser cuadrada (n x n) y coincidir con b.")

        L = np.zeros((n, n))
        U = np.zeros((n, n))
        filas_tabla = []

        # --- FASE 1: DESCOMPOSICIÓN L y U ---
        for i in range(n):
            # La diagonal principal de L es 1 (Método Doolittle)
            L[i][i] = 1.0

            # Calcular la fila 'i' de U
            for j in range(i, n):
                suma = sum(L[i][k] * U[k][j] for k in range(i))
                U[i][j] = A[i][j] - suma

            # Calcular la columna 'i' de L
            for j in range(i + 1, n):
                if abs(U[i][i]) < 1e-12:
                    raise ValueError("Se detectó un 0 en la diagonal de U. Este sistema requiere pivoteo, el cual no está soportado en LU simple.")
                suma = sum(L[j][k] * U[k][i] for k in range(i))
                L[j][i] = (A[j][i] - suma) / U[i][i]

        filas_tabla.append(["Fase 1", "Descomposición", "Matrices L y U calculadas"])

        # --- FASE 2: RESOLVER Ly = b (Sustitución hacia adelante) ---
        y = np.zeros(n)
        for i in range(n):
            suma = np.dot(L[i, :i], y[:i])
            y[i] = b[i] - suma
        
        y_redondeado = [round(val, 4) for val in y]
        filas_tabla.append(["Fase 2", "Sustitución Hacia Adelante (Ly = b)", f"Vector y: {y_redondeado}"])

        # --- FASE 3: RESOLVER Ux = y (Sustitución hacia atrás) ---
        x = np.zeros(n)
        for i in range(n - 1, -1, -1):
            if abs(U[i][i]) < 1e-12:
                raise ValueError("Sistema singular detectado en la sustitución hacia atrás.")
            suma = np.dot(U[i, i+1:], x[i+1:])
            x[i] = (y[i] - suma) / U[i][i]

        x_redondeado = [round(val, 4) for val in x]
        filas_tabla.append(["Fase 3", "Sustitución Hacia Atrás (Ux = y)", f"Vector x: {x_redondeado}"])

        return x, filas_tabla, L, U

    except Exception as e:
        raise ValueError(str(e))