from ast_nodes import *
from environment import Entorno, ErrorSemantico
from stdlib import crear_stdlib, ModuloNativo
import sys
import os

class ErrorEjecucion(Exception):
    def __init__(self, mensaje: str, nodo: NodoAST = None):
        pos = f" (L{nodo.linea}:C{nodo.columna})" if nodo else ""
        super().__init__(f"‫خطا في التنفيذ‬: {mensaje}{pos}")

class ErrorUsuarioLanzado(Exception):
    def __init__(self, valor):
        self.valor = valor

class SeñalRetornar(Exception):
    def __init__(self, valor):
        self.valor = valor

class FuncionNativa:
    def __init__(self, func, aridad):
        self.func = func
        self.aridad = aridad
        
    def __call__(self, *args):
        if len(args) != self.aridad and self.aridad != -1:
            raise ErrorEjecucion(f"‫توقع {self.aridad} معامالت لكن أعطيت {len(args)}‬")
        return self.func(*args)

class FuncionDefinidaUsuario:
    def __init__(self, nodo: NodoDeclFuncion, entorno_cierre: Entorno):
        self.nodo = nodo
        self.entorno_cierre = entorno_cierre
        
class MetodoVinculado:
    def __init__(self, nodo: NodoDeclFuncion, entorno_cierre: Entorno, instancia):
        self.nodo = nodo
        self.entorno_cierre = entorno_cierre
        self.instancia = instancia

class ClaseDefinidaUsuario:
    def __init__(self, nodo: NodoDeclClase, entorno_cierre: Entorno):
        self.nodo = nodo
        self.entorno_cierre = entorno_cierre
        self.padre_clase = None

class ObjetoInstancia:
    def __init__(self, clase: ClaseDefinidaUsuario):
        self.clase = clase
        self.campos = {}

    def obtener_metodo(self, nombre_metodo: str):
        clase_actual = self.clase
        while clase_actual is not None:
            for miembro in clase_actual.nodo.miembros:
                if isinstance(miembro, NodoDeclFuncion) and miembro.nombre == nombre_metodo:
                    return MetodoVinculado(miembro, clase_actual.entorno_cierre, self)
            clase_actual = clase_actual.padre_clase
        return None

class Interprete:
    def __init__(self):
        self.entorno_global = Entorno()
        self.entorno_actual = self.entorno_global
        self.modulos = crear_stdlib()
        self._registrar_stdlib()

    def _registrar_stdlib(self):
        self.entorno_global.definir("اطبع", FuncionNativa(print, -1))
        self.entorno_global.definir("طول", FuncionNativa(len, 1))
        def input_arabe(prompt=""):
            return input(prompt)
        self.entorno_global.definir("اقرا", FuncionNativa(input_arabe, 1))
        
        # In a complete implementation, lists are 'قائمة()'
        def lista_vacia(): return []
        self.entorno_global.definir("قائمة", FuncionNativa(lista_vacia, 0))
        
        def tipo_de(x):
            if isinstance(x, bool): return "صح_خطا"
            if isinstance(x, int) or isinstance(x, float): return "عدد"
            if isinstance(x, str): return "نص"
            if isinstance(x, list): return "قائمة"
            if x is None: return "فارغ"
            return "مجهول"
            
        self.entorno_global.definir("نوع", FuncionNativa(tipo_de, 1))
        self.entorno_global.definir("عدد_صحيح", FuncionNativa(int, 1))
        self.entorno_global.definir("عدد_عشري", FuncionNativa(float, 1))
        self.entorno_global.definir("نص", FuncionNativa(str, 1))
        self.entorno_global.definir("مدى", FuncionNativa(lambda start, end: list(range(start, end)), 2))
        self.entorno_global.definir("تعداد", FuncionNativa(lambda lst: [list(item) for item in enumerate(lst)], 1))
        self.entorno_global.definir("مضغوط", FuncionNativa(lambda l1, l2: [list(item) for item in zip(l1, l2)], 2))

    def ejecutar(self, nodo: NodoAST):
        if nodo is None: return None
        metodo = f"ejecutar_{type(nodo).__name__}"
        if hasattr(self, metodo):
            return getattr(self, metodo)(nodo)
        raise ErrorEjecucion(f"‫عقدة غير معروفة‬: {type(nodo).__name__}", nodo)

    def ejecutar_NodoPrograma(self, nodo: NodoPrograma):
        resultado = None
        for declaracion in nodo.cuerpo:
            resultado = self.ejecutar(declaracion)
        return resultado

    def ejecutar_NodoBloque(self, nodo: NodoBloque):
        self.entorno_actual._nuevo_scope()
        try:
            for declaracion in nodo.sentencias:
                self.ejecutar(declaracion)
        finally:
            self.entorno_actual._cerrar_scope()
        return None

    def ejecutar_NodoDeclVariable(self, nodo: NodoDeclVariable):
        valor = self.ejecutar(nodo.valor) if nodo.valor else None
        self.entorno_actual.definir(nodo.nombre, valor, nodo.es_constante)
        return None

    def ejecutar_NodoDeclFuncion(self, nodo: NodoDeclFuncion):
        funcion = FuncionDefinidaUsuario(nodo, self.entorno_actual)
        self.entorno_actual.definir(nodo.nombre, funcion)
        return None
        
    def ejecutar_NodoDeclClase(self, nodo: NodoDeclClase):
        padre_clase = None
        if nodo.padre:
            try:
                padre_clase = self.entorno_actual.obtener(nodo.padre)
                if not isinstance(padre_clase, ClaseDefinidaUsuario):
                    raise ErrorEjecucion(f"‫الصنف الأب يجب أن يكون صنفاً‬: {nodo.padre}", nodo)
            except ErrorSemantico:
                raise ErrorEjecucion(f"‫الصنف الأب غير موجود‬: {nodo.padre}", nodo)
                
        clase = ClaseDefinidaUsuario(nodo, self.entorno_actual)
        clase.padre_clase = padre_clase
        self.entorno_actual.definir(nodo.nombre, clase)
        return None
        
    def ejecutar_NodoImportar(self, nodo: NodoImportar):
        modulo_nombre = nodo.modulo
        mod = None
        
        if modulo_nombre in self.modulos:
            mod = self.modulos[modulo_nombre]
        else:
            rutas_posibles = [f"{modulo_nombre}.ه", f"{modulo_nombre}.عرب"]
            ruta_encontrada = None
            for ruta in rutas_posibles:
                if os.path.exists(ruta):
                    ruta_encontrada = ruta
                    break
                    
            if not ruta_encontrada:
                raise ErrorEjecucion(f"‫وحدة غير موجودة‬: {modulo_nombre}", nodo)
                
            with open(ruta_encontrada, "r", encoding="utf-8") as f:
                codigo = f.read()
                
            from lexer import Lexer
            from parser import Parser
            lexer = Lexer(codigo)
            tokens = lexer.tokenizar()
            parser = Parser(tokens)
            ast = parser.parsear_programa()
            
            interprete_mod = Interprete()
            interprete_mod.ejecutar(ast)
            
            miembros = {}
            for nombre, datos in interprete_mod.entorno_global.scope_actual.simbolos.items():
                miembros[nombre] = datos['valor']
                
            mod = ModuloNativo(modulo_nombre, miembros)
            self.modulos[modulo_nombre] = mod
            
        if not nodo.objetivos or nodo.objetivos == [modulo_nombre]:
            self.entorno_actual.definir(modulo_nombre, mod)
        else:
            for obj in nodo.objetivos:
                self.entorno_actual.definir(obj, mod.obtener_miembro(obj))
        return None

    def ejecutar_NodoSi(self, nodo: NodoSi):
        condicion = self.ejecutar(nodo.condicion)
        if condicion:
            self.ejecutar(nodo.entonces)
            return
            
        for cond_elif, bloq_elif in nodo.ramas_elif:
            if self.ejecutar(cond_elif):
                self.ejecutar(bloq_elif)
                return
                
        if nodo.sino:
            self.ejecutar(nodo.sino)

    def ejecutar_NodoBucle_Mientras(self, nodo: NodoBucle_Mientras):
        while self.ejecutar(nodo.condicion):
            self.ejecutar(nodo.cuerpo)
            
    def ejecutar_NodoBucle_Repetir(self, nodo: NodoBucle_Repetir):
        inicio = self.ejecutar(nodo.inicio)
        fin = self.ejecutar(nodo.fin)
        if not isinstance(inicio, int) or not isinstance(fin, int):
            raise ErrorEjecucion("‫يجب أن تكون حدود التكرار أعداد صحيحة‬", nodo)
            
        for val in range(inicio, fin):
            self.entorno_actual._nuevo_scope()
            self.entorno_actual.definir(nodo.variable, val)
            try:
                for declaracion in nodo.cuerpo.sentencias:
                    self.ejecutar(declaracion)
            finally:
                self.entorno_actual._cerrar_scope()

    def ejecutar_NodoRetornar(self, nodo: NodoRetornar):
        valor = self.ejecutar(nodo.valor) if nodo.valor else None
        raise SeñalRetornar(valor)

    def ejecutar_NodoIntentar(self, nodo: NodoIntentar):
        try:
            self.ejecutar(nodo.cuerpo)
        except SeñalRetornar:
            raise
        except Exception as e:
            if isinstance(e, ErrorUsuarioLanzado):
                valor_excepcion = e.valor
            else:
                # Wrap native python exceptions
                class NativeErr:
                    def __init__(self, msg):
                        self.mensaje = msg
                    def __str__(self): return self.mensaje
                valor_excepcion = NativeErr(str(e))
                
            for nombre, tipo, bloq_cap in nodo.capturas:
                self.entorno_actual._nuevo_scope()
                self.entorno_actual.definir(nombre, valor_excepcion)
                try:
                    self.ejecutar(bloq_cap)
                finally:
                    self.entorno_actual._cerrar_scope()
                break # Solo evaluamos el primer catch generico en el MVP
        finally:
            if nodo.finalmente:
                self.ejecutar(nodo.finalmente)
                
    def ejecutar_NodoLanzar(self, nodo: NodoLanzar):
        expr = self.ejecutar(nodo.excepcion)
        raise ErrorUsuarioLanzado(expr)

    def ejecutar_NodoExpresionSentencia(self, nodo: NodoExpresionSentencia):
        return self.ejecutar(nodo.valor)

    def ejecutar_NodoAsignacion(self, nodo: NodoAsignacion):
        if isinstance(nodo.objetivo, NodoIdentificador):
            valor = self.ejecutar(nodo.valor)
            if nodo.operador == "=":
                self.entorno_actual.asignar(nodo.objetivo.nombre, valor)
            else:
                actual = self.entorno_actual.obtener(nodo.objetivo.nombre)
                if nodo.operador == "+=": valor = actual + valor
                elif nodo.operador == "-=": valor = actual - valor
                elif nodo.operador == "*=": valor = actual * valor
                elif nodo.operador == "/=": valor = actual / valor
                self.entorno_actual.asignar(nodo.objetivo.nombre, valor)
            return valor
            
        elif isinstance(nodo.objetivo, NodoIndice):
            # Assignment to list index
            obj = self.ejecutar(nodo.objetivo.objeto)
            idx = self.ejecutar(nodo.objetivo.indice)
            valor = self.ejecutar(nodo.valor)
            if isinstance(obj, list) and isinstance(idx, int):
                if nodo.operador == "=":
                    obj[idx] = valor
                elif nodo.operador == "+=": obj[idx] += valor
                elif nodo.operador == "-=": obj[idx] -= valor
                elif nodo.operador == "*=": obj[idx] *= valor
                elif nodo.operador == "/=": obj[idx] /= valor
                return valor
        elif isinstance(nodo.objetivo, NodoAcceso):
            obj = self.ejecutar(nodo.objetivo.objeto)
            valor = self.ejecutar(nodo.valor)
            if isinstance(obj, ObjetoInstancia):
                if nodo.operador == "=":
                    obj.campos[nodo.objetivo.campo] = valor
                elif nodo.operador == "+=": obj.campos[nodo.objetivo.campo] += valor
                elif nodo.operador == "-=": obj.campos[nodo.objetivo.campo] -= valor
                elif nodo.operador == "*=": obj.campos[nodo.objetivo.campo] *= valor
                elif nodo.operador == "/=": obj.campos[nodo.objetivo.campo] /= valor
                return valor
            raise ErrorEjecucion("‫تعيين السمة غير صالح‬", nodo)
            
        raise ErrorEjecucion("‫ال يمكن تعيين القيمة إلى هذا الهدف‬", nodo.objetivo)

    def ejecutar_NodoOpBinaria(self, nodo: NodoOpBinaria):
        izq = self.ejecutar(nodo.izquierda)
        der = self.ejecutar(nodo.derecha)
        op = nodo.operador
        
        # PRD Note on '+' specifically
        if op == "+":
            if isinstance(izq, str) or isinstance(der, str):
                return str(izq) + str(der)
            return izq + der
            
        if op == "-": return izq - der
        if op == "*": return izq * der
        if op == "/":
            if der == 0: raise ErrorEjecucion("‫القسمة على صفر غير مسموح بها‬", nodo)
            return izq / der
        if op == "%": return izq % der
        if op == "**": return izq ** der
        if op == "==": return izq == der
        if op == "!=": return izq != der
        if op == "<": return izq < der
        if op == "<=": return izq <= der
        if op == ">": return izq > der
        if op == ">=": return izq >= der
        # Logicals uses short-circuit physically, but in naive evaluation, handle them as so:
        if op == "‫و": return izq and der
        if op == "‫او": return izq or der
        
        raise ErrorEjecucion(f"‫مُعامل ثنائي غير مدعوم‬: {op}", nodo)

    def ejecutar_NodoOpUnaria(self, nodo: NodoOpUnaria):
        operando = self.ejecutar(nodo.operando)
        if nodo.operador == "-":
            return -operando
        if nodo.operador == "‫ليس":
            return not operando
        raise ErrorEjecucion(f"‫مُعامل أحادي غير مدعوم‬: {nodo.operador}", nodo)

    def ejecutar_NodoLlamada(self, nodo: NodoLlamada):
        funcion = self.ejecutar(nodo.funcion)
        args = [self.ejecutar(a) for a in nodo.argumentos]
        
        if isinstance(funcion, FuncionNativa):
            return funcion(*args)
            
        if isinstance(funcion, FuncionDefinidaUsuario):
            if len(args) != len(funcion.nodo.parametros):
                raise ErrorEjecucion(f"‫الدالة '{funcion.nodo.nombre}' تحتاج {len(funcion.nodo.parametros)} معامالت لكن أعطيت {len(args)}‬", nodo)
                
            entorno_funcion = Entorno(padre=funcion.entorno_cierre.scope_actual)
            for param, valor in zip(funcion.nodo.parametros, args):
                entorno_funcion.definir(param.nombre, valor)
                
            entorno_previo = self.entorno_actual
            self.entorno_actual = entorno_funcion
            try:
                self.ejecutar_NodoBloque(funcion.nodo.cuerpo)
            except SeñalRetornar as ret:
                return ret.valor
            finally:
                self.entorno_actual = entorno_previo
            return None
            
        if isinstance(funcion, MetodoVinculado):
            if len(args) != len(funcion.nodo.parametros):
                raise ErrorEjecucion(f"‫التابع تحتاج {len(funcion.nodo.parametros)} معامالت لكن أعطيت {len(args)}‬", nodo)
                
            entorno_funcion = Entorno(padre=funcion.entorno_cierre.scope_actual)
            # Bind this / هذا
            entorno_funcion.definir("هذا", funcion.instancia)
            for param, valor in zip(funcion.nodo.parametros, args):
                entorno_funcion.definir(param.nombre, valor)
                
            entorno_previo = self.entorno_actual
            self.entorno_actual = entorno_funcion
            try:
                self.ejecutar_NodoBloque(funcion.nodo.cuerpo)
            except SeñalRetornar as ret:
                return ret.valor
            finally:
                self.entorno_actual = entorno_previo
            return None
            
        # Support python functions returned by standard library dicts
        if callable(funcion):
            return funcion(*args)
            
        raise ErrorEjecucion(f"‫هذا ليس دالة‬: {funcion}", nodo)
        
    def ejecutar_NodoNuevo(self, nodo: NodoNuevo):
        try:
            clase = self.entorno_actual.obtener(nodo.clase)
        except ErrorSemantico:
            raise ErrorEjecucion(f"‫صنف غير موجود‬: {nodo.clase}", nodo)
            
        if not isinstance(clase, ClaseDefinidaUsuario):
            if callable(clase):
                # allow calling python exceptions mapped into the env
                args = [self.ejecutar(a) for a in nodo.argumentos]
                return clase(*args)
            raise ErrorEjecucion(f"‫ال يمكن إنشاء نسخة من‬: {nodo.clase}", nodo)
            
        inst = ObjetoInstancia(clase)
        metodo_init = inst.obtener_metodo("انشاء")
        
        args = [self.ejecutar(a) for a in nodo.argumentos]
        if metodo_init:
            # We call the init method by wrapping it into a temporary NodoLlamada to reuse argument linking logic
            entorno_funcion = Entorno(padre=metodo_init.entorno_cierre.scope_actual)
            entorno_funcion.definir("هذا", inst)
            for param, valor in zip(metodo_init.nodo.parametros, args):
                entorno_funcion.definir(param.nombre, valor)
                
            entorno_previo = self.entorno_actual
            self.entorno_actual = entorno_funcion
            try:
                self.ejecutar_NodoBloque(metodo_init.nodo.cuerpo)
            except SeñalRetornar as ret:
                pass
            finally:
                self.entorno_actual = entorno_previo
                
        return inst
        
    def ejecutar_NodoAcceso(self, nodo: NodoAcceso):
        obj = self.ejecutar(nodo.objeto)
        if isinstance(obj, ObjetoInstancia):
            if nodo.campo in obj.campos:
                return obj.campos[nodo.campo]
            metodo = obj.obtener_metodo(nodo.campo)
            if metodo:
                return metodo
            raise ErrorEjecucion(f"‫السمة أو التابع '{nodo.campo}' غير موجود‬", nodo)
            
        if isinstance(obj, ModuloNativo):
            return obj.obtener_miembro(nodo.campo)
            
        raise ErrorEjecucion(f"‫ال يمكن الوصول إلى الحقل '{nodo.campo}' على هذا النوع‬", nodo)

    def ejecutar_NodoIndice(self, nodo: NodoIndice):
        objeto = self.ejecutar(nodo.objeto)
        indice = self.ejecutar(nodo.indice)
        try:
            return objeto[indice]
        except (KeyError, IndexError):
            raise ErrorEjecucion(f"‫الفهرس غير موجود‬: {indice}", nodo)

    def ejecutar_NodoLiteralNumero(self, nodo: NodoLiteralNumero):
        return nodo.valor

    def ejecutar_NodoLiteralCadena(self, nodo: NodoLiteralCadena):
        return nodo.valor

    def ejecutar_NodoLiteralBool(self, nodo: NodoLiteralBool):
        return nodo.valor

    def ejecutar_NodoLiteralNulo(self, nodo: NodoLiteralNulo):
        return None

    def ejecutar_NodoLiteralLista(self, nodo: NodoLiteralLista):
        return [self.ejecutar(e) for e in nodo.elementos]

    def ejecutar_NodoIdentificador(self, nodo: NodoIdentificador):
        try:
            return self.entorno_actual.obtener(nodo.nombre)
        except ErrorSemantico as e:
            raise ErrorEjecucion(str(e), nodo)
