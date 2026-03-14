from ast_nodes import *
from environment import Entorno, ErrorSemantico

class ErrorEjecucion(Exception):
    def __init__(self, mensaje: str, nodo: NodoAST = None):
        pos = f" (L{nodo.linea}:C{nodo.columna})" if nodo else ""
        super().__init__(f"‫خطا في التنفيذ‬: {mensaje}{pos}")

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

class Interprete:
    def __init__(self):
        self.entorno_global = Entorno()
        self.entorno_actual = self.entorno_global
        self._registrar_stdlib()

    def _registrar_stdlib(self):
        self.entorno_global.definir("اطبع", FuncionNativa(print, -1))
        self.entorno_global.definir("طول", FuncionNativa(len, 1))
        # Add 'اقرا' and others later
        def input_arabe(prompt):
            return input(prompt)
        self.entorno_global.definir("اقرا", FuncionNativa(input_arabe, 1))

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
            raise ErrorEjecucion("‫تعيين فهرس غير صالح‬", nodo)
            
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
            
        raise ErrorEjecucion(f"‫هذا ليس دالة‬: {funcion}", nodo)

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
