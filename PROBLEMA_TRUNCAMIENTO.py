import struct

def calcular_ieee754(numero, bits=32):
    """
    Convierte un número decimal a su representación IEEE 754.
    Soporta 32 bits (precisión simple) y 64 bits (precisión doble).
    """
    try:
        if bits == 32:
            empaquetado = struct.pack('>f', numero)
            sesgo = 127
            bits_caracteristica = 8
        elif bits == 64:
            empaquetado = struct.pack('>d', numero)
            sesgo = 1023
            bits_caracteristica = 11
        else:
            return None, "Solo se soportan 32 o 64 bits estándar."

        # Convertir los bytes a una cadena binaria de ceros y unos
        binario = ''.join(f'{b:08b}' for b in empaquetado)
        
        # Desglosar según el estándar
        signo = binario[0]
        caracteristica = binario[1:1+bits_caracteristica]
        mantisa = binario[1+bits_caracteristica:]
        
        # Calcular los valores reales matemáticos
        valor_caracteristica = int(caracteristica, 2)
        exponente_real = valor_caracteristica - sesgo
        significado_signo = "Negativo (-)" if signo == "1" else "Positivo (+)"
        
        # Empaquetar todo en un diccionario para mandarlo a la interfaz
        datos = {
            "signo": signo,
            "sig_signo": significado_signo,
            "caracteristica": caracteristica,
            "val_caracteristica": valor_caracteristica,
            "sesgo": sesgo,
            "exponente_real": exponente_real,
            "mantisa": mantisa,
            "binario_completo": binario,
            "hexadecimal": hex(int(binario, 2)).upper().replace("0X", "0x")
        }
        return datos, "Cálculo exitoso"
        
    except OverflowError:
        return None, "El número es demasiado grande para esta precisión."
    except Exception as e:
        return None, f"Error inesperado: {str(e)}"