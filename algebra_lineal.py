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