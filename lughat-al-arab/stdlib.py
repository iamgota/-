import math
import random
import time
import os

try:
    import numpy as np
    NUMPY_DISPONIBLE = True
except ImportError:
    NUMPY_DISPONIBLE = False

try:
    import torch
    TORCH_DISPONIBLE = True
except ImportError:
    TORCH_DISPONIBLE = False

class ModuloNativo:
    def __init__(self, nombre: str, funciones: dict):
        self.nombre = nombre
        self.funciones = funciones
        
    def obtener_miembro(self, nombre: str):
        if nombre in self.funciones:
            return self.funciones[nombre]
        raise KeyError(f"‫العضو '{nombre}' غير موجود في الوحدة '{self.nombre}'‬")

def crear_stdlib() -> dict:
    modulos = {}
    
    # 1. رياضيات (math)
    mat_funcs = {
        "جذر": math.sqrt,
        "اسس": math.pow,
        "لوغاريتم": math.log,
        "جيب": math.sin,
        "جيب_تمام": math.cos,
        "قيمة_مطلقة": abs,
        "دور": round,
        "اقصى": max,
        "ادنى": min,
        "مجموع": sum,
        "pi": math.pi,
        "e": math.e
    }
    modulos["رياضيات"] = ModuloNativo("رياضيات", mat_funcs)
    
    # 2. نصوص (strings)
    def_num_parser = lambda s: float(s) if '.' in s else int(s)
    texto_funcs = {
        "طول": len,
        "قطع": lambda text, inicio, fin: text[inicio:fin],
        "دمج": lambda lista, separator="": separator.join(lista),
        "ابحث": lambda text, sub: text.find(sub),
        "استبدل": lambda text, old, new: text.replace(old, new),
        "مقسم": lambda text, sep: text.split(sep),
        "يبدأ_بـ": lambda text, pref: text.startswith(pref),
        "ينتهي_بـ": lambda text, suf: text.endswith(suf),
        "حروف_كبيرة": lambda text: text.upper(),
        "حروف_صغيرة": lambda text: text.lower(),
        "قص_المسافات": lambda text: text.strip(),
        "تحويل_نص": str,
        "تحويل_عدد": def_num_parser,
        "مقارن": lambda t1, t2: t1 == t2
    }
    modulos["نصوص"] = ModuloNativo("نصوص", texto_funcs)
    
    # 3. قوائم (lists)
    def shuffle_inplace(lst):
        random.shuffle(lst)
        return lst
        
    listas_funcs = {
        "اضف": lambda lst, item: lst.append(item) or lst,
        "احذف": lambda lst, idx: lst.pop(idx),
        "رتب": lambda lst: sorted(lst),
        "عكس": lambda lst: list(reversed(lst)),
        "ابحث": lambda lst, item: lst.index(item) if item in lst else -1,
        "طول": len,
        "مرشح": lambda func, lst: list(filter(func, lst)),
        "حول": lambda func, lst: list(map(func, lst))
    }
    modulos["قوائم"] = ModuloNativo("قوائم", listas_funcs)
    
    # 4. ملفات (files)
    def leer_archivo(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return f.read()
            
    def escribir_archivo(ruta, cont):
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(cont)
            
    archivos_funcs = {
        "اقرا_ملف": leer_archivo,
        "اكتب_ملف": escribir_archivo,
        "وجود_ملف": os.path.exists
    }
    modulos["ملفات"] = ModuloNativo("ملفات", archivos_funcs)
    
    # 5. عشوائي (random)
    rand_funcs = {
        "عدد_عشوائي": random.randint,
        "اختر": random.choice,
        "خلط": shuffle_inplace
    }
    modulos["عشوائي"] = ModuloNativo("عشوائي", rand_funcs)
    
    # 6. وقت (time)
    tiempo_funcs = {
        "الان": time.time,
        "نم": time.sleep
    }
    modulos["وقت"] = ModuloNativo("وقت", tiempo_funcs)
    
    # 7. ذكاء (inteligencia artificial)
    def ia_matriz(datos):
        if NUMPY_DISPONIBLE: return np.array(datos)
        return datos

    def ia_forma(arr):
        if NUMPY_DISPONIBLE and isinstance(arr, np.ndarray):
            return list(arr.shape)
        if isinstance(arr, list):
            filas = len(arr)
            cols = len(arr[0]) if filas > 0 and isinstance(arr[0], list) else 0
            if cols > 0: return [filas, cols]
            return [filas]
        return []

    def ia_sumar_matriz(a, b):
        if NUMPY_DISPONIBLE and (isinstance(a, np.ndarray) or isinstance(b, np.ndarray)):
            return a + b
        # Fallback Python
        if isinstance(a, list) and isinstance(b, list):
            # simple 1D or 2D sum
            if isinstance(a[0], list):
                return [[a[i][j] + b[i][j] for j in range(len(a[i]))] for i in range(len(a))]
            return [a[i] + b[i] for i in range(len(a))]
        return a + b

    def ia_multiplicar_matriz(a, b):
        if NUMPY_DISPONIBLE and (isinstance(a, np.ndarray) or isinstance(b, np.ndarray)):
            return np.dot(a, b)
        # Fallback Python simple lists (2D * 2D)
        if isinstance(a, list) and isinstance(b, list):
            filas_a, cols_a = len(a), len(a[0])
            filas_b, cols_b = len(b), len(b[0])
            res = [[0] * cols_b for _ in range(filas_a)]
            for i in range(filas_a):
                for j in range(cols_b):
                    for k in range(cols_a):
                        res[i][j] += a[i][k] * b[k][j]
            return res
        return a * b

    def ia_normalizar(lista):
        if NUMPY_DISPONIBLE and isinstance(lista, np.ndarray):
            min_val = np.min(lista)
            max_val = np.max(lista)
            return ((lista - min_val) / (max_val - min_val)).tolist()
        min_v = min(lista)
        max_v = max(lista)
        if max_v - min_v == 0: return [0.0]*len(lista)
        return [(x - min_v) / (max_v - min_v) for x in lista]

    def ia_media(lista):
        if NUMPY_DISPONIBLE and isinstance(lista, np.ndarray):
            return np.mean(lista).item()
        return sum(lista) / len(lista)

    def ia_desviacion(lista):
        if NUMPY_DISPONIBLE and isinstance(lista, np.ndarray):
            return np.std(lista).item()
        mean = sum(lista) / len(lista)
        variance = sum((x - mean) ** 2 for x in lista) / len(lista)
        return math.sqrt(variance)

    def ia_train_simple(X, y, iteraciones=100, tasa=0.01):
        # Fallback lineal simple y = mx + b para X(1D) y y(1D)
        # Gradient descent
        m = 0.0
        b = 0.0
        n = len(X)
        for _ in range(int(iteraciones)):
            dm = 0.0
            db = 0.0
            for i in range(n):
                pred = m * X[i] + b
                error = pred - y[i]
                dm += (2/n) * X[i] * error
                db += (2/n) * error
            m -= tasa * dm
            b -= tasa * db
        return [m, b]

    def ia_pred_simple(X, pesos, sesgo):
        m = pesos
        if isinstance(pesos, list) and len(pesos) > 0:
            m = pesos[0]
        # Soporta X array o unico
        if isinstance(X, list):
            return [m * x + sesgo for x in X]
        return m * X + sesgo

    ia_funcs = {
        "مصفوفة": ia_matriz,
        "شكل": ia_forma,
        "جمع_مصفوفة": ia_sumar_matriz,
        "ضرب_مصفوفة": ia_multiplicar_matriz,
        "تحويل_ارقام": ia_normalizar,
        "متوسط": ia_media,
        "انحراف": ia_desviacion,
        "درب_بسيط": ia_train_simple,
        "تنبا_بسيط": ia_pred_simple
    }
    modulos["ذكاء"] = ModuloNativo("ذكاء", ia_funcs)

    return modulos
