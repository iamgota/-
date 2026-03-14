class ErrorSemantico(Exception):
    def __init__(self, mensaje: str):
        super().__init__(f"‫خطا دلالي‬: {mensaje}")

class Scope:
    def __init__(self, padre=None):
        self.simbolos = {} # nombre -> {'valor': Any, 'es_constante': bool}
        self.padre = padre

    def declarar(self, nombre: str, valor, es_constante: bool = False):
        if nombre in self.simbolos:
            raise ErrorSemantico(f"'{nombre}' ‫مُعرَّف مسبقاً في هذا النطاق‬")
        self.simbolos[nombre] = {'valor': valor, 'es_constante': es_constante}

    def asignar(self, nombre: str, valor):
        if nombre in self.simbolos:
            if self.simbolos[nombre]['es_constante']:
                raise ErrorSemantico(f"‫لا يمكن تغيير قيمة الثابت‬ '{nombre}'")
            self.simbolos[nombre]['valor'] = valor
            return
        if self.padre:
            self.padre.asignar(nombre, valor)
            return
        raise ErrorSemantico(f"‫متغير غير معرّف‬ '{nombre}'")

    def buscar(self, nombre: str):
        if nombre in self.simbolos:
            return self.simbolos[nombre]['valor']
        if self.padre:
            return self.padre.buscar(nombre)
        raise ErrorSemantico(f"‫متغير غير معرّف‬ '{nombre}'")

class Entorno:
    def __init__(self, padre=None):
        self.scope_actual = Scope(padre)
        
    def _nuevo_scope(self):
        self.scope_actual = Scope(padre=self.scope_actual)
        
    def _cerrar_scope(self):
        if self.scope_actual.padre:
            self.scope_actual = self.scope_actual.padre

    def definir(self, nombre: str, valor, es_constante: bool = False):
        self.scope_actual.declarar(nombre, valor, es_constante)

    def asignar(self, nombre: str, valor):
        self.scope_actual.asignar(nombre, valor)

    def obtener(self, nombre: str):
        return self.scope_actual.buscar(nombre)
