import numpy as np
import math

def simular_pendulo(metodo, L, g, theta0_grados, w0, tf, h):
    """
    Resuelve el sistema del péndulo usando diferentes métodos numéricos.
    """
    theta0 = math.radians(theta0_grados)
    t_vals = np.arange(0, tf + h, h)
    n = len(t_vals)
    
    theta_vals = np.zeros(n)
    w_vals = np.zeros(n)
    theta_vals[0] = theta0
    w_vals[0] = w0
    
    # Funciones del sistema (d(theta)/dt = w, d(w)/dt = -g/L*sin(theta))
    def f_th(w_val): return w_val
    def f_w(th_val): return -(g / L) * math.sin(th_val)
    
    for i in range(n - 1):
        th = theta_vals[i]
        w = w_vals[i]
        
        if metodo == "Euler":
            theta_vals[i+1] = th + h * f_th(w)
            w_vals[i+1] = w + h * f_w(th)
            
        elif metodo == "Heun":
            th_pred = th + h * f_th(w)
            w_pred = w + h * f_w(th)
            theta_vals[i+1] = th + (h/2) * (f_th(w) + f_th(w_pred))
            w_vals[i+1] = w + (h/2) * (f_w(th) + f_w(th_pred))
            
        elif metodo == "Runge-Kutta 2":
            k1_th = f_th(w)
            k1_w = f_w(th)
            
            k2_th = f_th(w + h * k1_w)
            k2_w = f_w(th + h * k1_th)
            
            theta_vals[i+1] = th + (h/2) * (k1_th + k2_th)
            w_vals[i+1] = w + (h/2) * (k1_w + k2_w)
            
        elif metodo == "Runge-Kutta 4":
            k1_th = w
            k1_w = -(g / L) * math.sin(th)
            
            th_mid1 = th + 0.5 * h * k1_th
            k2_th = w + 0.5 * h * k1_w
            k2_w = -(g / L) * math.sin(th_mid1)
            
            th_mid2 = th + 0.5 * h * k2_th
            k3_th = w + 0.5 * h * k2_w
            k3_w = -(g / L) * math.sin(th_mid2)
            
            th_end = th + h * k3_th
            k4_th = w + h * k3_w
            k4_w = -(g / L) * math.sin(th_end)
            
            theta_vals[i+1] = th + (h / 6.0) * (k1_th + 2*k2_th + 2*k3_th + k4_th)
            w_vals[i+1] = w + (h / 6.0) * (k1_w + 2*k2_w + 2*k3_w + k4_w)
            
    return t_vals, theta_vals, w_vals