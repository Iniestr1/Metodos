import struct

def obtener_configuracion_bits(total_bits):
    """
    Define cuántos bits usar para el exponente y la mantisa
    basado en estándares comunes o aproximaciones.
    """
    if total_bits == 8:
        # Minifloat (Común en gráficos/AI)
        # 1 signo, 4 exponente, 3 mantisa
        return 4, 3
    elif total_bits == 16:
        # Half Precision (IEEE 754-2008)
        # 1 signo, 5 exponente, 10 mantisa
        return 5, 10
    elif total_bits == 32:
        # Single Precision
        # 1 signo, 8 exponente, 23 mantisa
        return 8, 23
    elif total_bits == 64:
        # Double Precision
        # 1 signo, 11 exponente, 52 mantisa
        return 11, 52
    else:
        # Configuración personalizada genérica para bits raros (ej: 12 bits)
        # Regla de dedo: Exponente toma aprox 1/3 o 1/4 del espacio disponible
        exp = max(3, total_bits // 3) 
        mant = total_bits - 1 - exp
        return exp, mant

def float_a_binario_custom(numero, total_bits):
    bits_exp, bits_mant = obtener_configuracion_bits(total_bits)
    bias = (2**(bits_exp - 1)) - 1  # El sesgo para el exponente

    if numero == 0:
        return '0' * total_bits

    # 1. Signo
    signo = '1' if numero < 0 else '0'
    numero = abs(numero)

    # 2. Normalización (Convertir a formato 1.xxxxx * 2^E)
    # Convertimos la parte entera y fraccionaria a binario crudo primero
    parte_entera = int(numero)
    parte_fraccionaria = numero - parte_entera
    
    bin_entero = bin(parte_entera)[2:]
    
    # Convertir fracción a binario (con precisión extra para redondeo)
    bin_fraccion = []
    temp_frac = parte_fraccionaria
    while len(bin_fraccion) < (bits_mant + bits_exp + 10) and temp_frac != 0:
        temp_frac *= 2
        bit = int(temp_frac)
        bin_fraccion.append(str(bit))
        temp_frac -= bit
    bin_fraccion = "".join(bin_fraccion)

    # Calcular exponente y mantisa según la posición del primer '1'
    if parte_entera > 0:
        # El punto se mueve a la izquierda
        exponente_real = len(bin_entero) - 1
        mantisa_full = bin_entero[1:] + bin_fraccion
    else:
        # El punto se mueve a la derecha (buscamos el primer 1 en la fracción)
        primero_uno = bin_fraccion.find('1')
        if primero_uno == -1: # Caso 0.0 (ya manejado arriba, pero por seguridad)
            return signo + '0'*bits_exp + '0'*bits_mant
        exponente_real = -(primero_uno + 1)
        mantisa_full = bin_fraccion[primero_uno + 1:]

    # 3. Aplicar Bias al exponente
    exponente_guardado = exponente_real + bias
    
    # Validar desbordamiento (Infinito)
    max_exp = (2**bits_exp) - 1
    if exponente_guardado >= max_exp:
        return f"Infinito ({signo} inf) - El número es muy grande para {total_bits} bits"
    if exponente_guardado <= 0:
        # Manejo simplificado de subnormales (opcional: devolver 0)
        return f"Underflow (Muy cercano a 0 para {total_bits} bits)"

    bin_exponente = bin(exponente_guardado)[2:].zfill(bits_exp)

    # 4. Recortar o rellenar mantisa
    if len(mantisa_full) < bits_mant:
        bin_mantisa = mantisa_full.ljust(bits_mant, '0')
    else:
        bin_mantisa = mantisa_full[:bits_mant] # Truncado simple

    return f"{signo} {bin_exponente} {bin_mantisa}"

def binario_a_float_custom(cadena_binaria, total_bits):
    # Limpiar espacios
    cadena_binaria = cadena_binaria.replace(" ", "")
    
    if len(cadena_binaria) != total_bits:
        return f"Error: Se esperaban {total_bits} bits, recibiste {len(cadena_binaria)}"

    bits_exp, bits_mant = obtener_configuracion_bits(total_bits)
    bias = (2**(bits_exp - 1)) - 1

    # Separar partes
    signo_bit = cadena_binaria[0]
    exp_bits = cadena_binaria[1:1+bits_exp]
    mant_bits = cadena_binaria[1+bits_exp:]

    # Convertir
    signo = -1 if signo_bit == '1' else 1
    exponente_decimal = int(exp_bits, 2)
    
    # Calcular mantisa (sumando potencias negativas: 2^-1, 2^-2...)
    mantisa_decimal = 1.0 # El '1.' implícito
    for i, bit in enumerate(mant_bits):
        if bit == '1':
            mantisa_decimal += 2**(-(i + 1))

    # Manejo de exponente 0 (casos especiales simplificados)
    if exponente_decimal == 0:
        return 0.0

    valor_real = signo * mantisa_decimal * (2**(exponente_decimal - bias))
    return valor_real

def menu():
    print("--- CONVERTIDOR DECIMAL FLOTANTE (IEEE 754 APROX) ---")
    while True:
        try:
            print("\nBits totales (Ej: 8, 16, 32, 64):")
            bits = int(input("> "))
            
            exp, mant = obtener_configuracion_bits(bits)
            print(f"[Configuración] Signo: 1 | Exponente: {exp} | Mantisa: {mant}")

            print("1. Decimal a Binario (Ej: -9.456)")
            print("2. Binario a Decimal")
            print("3. Salir")
            opcion = input("Elige: ")

            if opcion == '1':
                num = float(input("Ingresa número decimal: "))
                res = float_a_binario_custom(num, bits)
                print(f"Resultado binario: {res}")
            
            elif opcion == '2':
                b_str = input(f"Ingresa {bits} bits: ")
                res = binario_a_float_custom(b_str, bits)
                print(f"Resultado decimal: {res}")
            
            elif opcion == '3':
                break
        except ValueError:
            print("Entrada inválida.")

if __name__ == "__main__":
    menu()