from typing import List, Optional
from tokens import Token, TokenKind
from ast_nodes import *

class ErrorSintaxis(Exception):
    def __init__(self, mensaje: str, token: Token):
        super().__init__(f"‫خطا في التركيب‬: {mensaje} (L{token.linea}:C{token.columna})")
        self.token = token

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    @property
    def token_actual(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1] # EOF

    def _consumir(self, tipo_esperado: TokenKind) -> Token:
        if self.token_actual.tipo != tipo_esperado:
            raise ErrorSintaxis(f"‫متوقع‬ {tipo_esperado.value} ‫لكن وجدت‬ '{self.token_actual.valor}'", self.token_actual)
        token = self.token_actual
        self.pos += 1
        return token

    def _coincide(self, *tipos: TokenKind) -> bool:
        if self.token_actual.tipo in tipos:
            return True
        return False

    def _avanzar(self):
        self.pos += 1

    def parsear_programa(self) -> NodoPrograma:
        declaraciones = []
        while not self._coincide(TokenKind.FIN_ARCHIVO):
            declaraciones.append(self.parsear_declaracion())
        return NodoPrograma(cuerpo=declaraciones)

    def parsear_declaracion(self) -> NodoAST:
        # According to PRD grammar rules
        if self._coincide(TokenKind.KW_MUTAGHAYYIR, TokenKind.KW_THABIT):
            return self.parsear_decl_variable()
        if self._coincide(TokenKind.KW_DALA):
            return self.parsear_decl_funcion()
        if self._coincide(TokenKind.KW_SINF):
            return self.parsear_decl_clase()
            
        return self.parsear_sentencia()

    def parsear_sentencia(self) -> NodoAST:
        if self._coincide(TokenKind.KW_AZDA):
            return self.parsear_sent_si()
        if self._coincide(TokenKind.KW_BAYNAMA):
            return self.parsear_sent_mientras()
        if self._coincide(TokenKind.KW_LIKULL):
            return self.parsear_sent_para_cada()
        if self._coincide(TokenKind.KW_KARRIR):
            return self.parsear_sent_repetir()
        if self._coincide(TokenKind.KW_IRJAH):
            return self.parsear_sent_retornar()
        if self._coincide(TokenKind.PUNT_LLAVE_IZQ):
            return self.parsear_bloque()
            
        expr = self.parsear_expresion()
        return NodoExpresionSentencia(valor=expr)

    def parsear_decl_variable(self) -> NodoAST:
        es_constante = self._coincide(TokenKind.KW_THABIT)
        self._avanzar() # Consumir el kw

        id_token = self._consumir(TokenKind.IDENTIFICADOR)
        tipo = None
        
        if self._coincide(TokenKind.PUNT_DOS_PUNTOS):
            self._avanzar()
            tipo = self._consumir(TokenKind.IDENTIFICADOR).valor
            
        self._consumir(TokenKind.OP_ASIGNACION)
        valor = self.parsear_expresion()
        
        return NodoDeclVariable(
            linea=id_token.linea, 
            columna=id_token.columna,
            nombre=id_token.valor, 
            valor=valor, 
            tipo_anotado=tipo, 
            es_constante=es_constante
        )

    def parsear_decl_funcion(self) -> NodoDeclFuncion:
        t = self._consumir(TokenKind.KW_DALA)
        nombre = self._consumir(TokenKind.IDENTIFICADOR).valor
        
        self._consumir(TokenKind.PUNT_PAREN_IZQ)
        parametros = []
        if not self._coincide(TokenKind.PUNT_PAREN_DER):
            parametros.append(self.parsear_parametro())
            while self._coincide(TokenKind.PUNT_COMA):
                self._avanzar()
                parametros.append(self.parsear_parametro())
        self._consumir(TokenKind.PUNT_PAREN_DER)
        
        tipo_retorno = None
        if self._coincide(TokenKind.OP_FLECHA):
            self._avanzar()
            tipo_retorno = self._consumir(TokenKind.IDENTIFICADOR).valor
            
        cuerpo = self.parsear_bloque()
        return NodoDeclFuncion(linea=t.linea, columna=t.columna, nombre=nombre, parametros=parametros, cuerpo=cuerpo, tipo_retorno=tipo_retorno)

    def parsear_parametro(self) -> NodoParametro:
        t = self._consumir(TokenKind.IDENTIFICADOR)
        tipo = None
        valor_defecto = None
        if self._coincide(TokenKind.PUNT_DOS_PUNTOS):
            self._avanzar()
            tipo = self._consumir(TokenKind.IDENTIFICADOR).valor
        if self._coincide(TokenKind.OP_ASIGNACION):
            self._avanzar()
            valor_defecto = self.parsear_expresion()
            
        return NodoParametro(linea=t.linea, columna=t.columna, nombre=t.valor, tipo=tipo, valor_defecto=valor_defecto)

    def parsear_decl_clase(self) -> NodoDeclClase:
        t = self._consumir(TokenKind.KW_SINF)
        nombre = self._consumir(TokenKind.IDENTIFICADOR).valor
        padre = None
        if self._coincide(TokenKind.KW_YARITH):
            self._avanzar()
            padre = self._consumir(TokenKind.IDENTIFICADOR).valor
            
        self._consumir(TokenKind.PUNT_LLAVE_IZQ)
        miembros = []
        while not self._coincide(TokenKind.PUNT_LLAVE_DER) and not self._coincide(TokenKind.FIN_ARCHIVO):
            if self._coincide(TokenKind.KW_MUTAGHAYYIR, TokenKind.KW_THABIT):
                miembros.append(self.parsear_decl_variable())
            elif self._coincide(TokenKind.KW_DALA):
                miembros.append(self.parsear_decl_funcion())
            else:
                raise ErrorSintaxis("Solo se permiten variables y funciones en una clase", self.token_actual)
        self._consumir(TokenKind.PUNT_LLAVE_DER)
        
        return NodoDeclClase(linea=t.linea, columna=t.columna, nombre=nombre, padre=padre, miembros=miembros)

    def parsear_bloque(self) -> NodoBloque:
        t = self._consumir(TokenKind.PUNT_LLAVE_IZQ)
        sentencias = []
        while not self._coincide(TokenKind.PUNT_LLAVE_DER) and not self._coincide(TokenKind.FIN_ARCHIVO):
            sentencias.append(self.parsear_declaracion())
        self._consumir(TokenKind.PUNT_LLAVE_DER)
        return NodoBloque(linea=t.linea, columna=t.columna, sentencias=sentencias)

    def parsear_sent_si(self) -> NodoSi:
        t = self._consumir(TokenKind.KW_AZDA)
        self._consumir(TokenKind.PUNT_PAREN_IZQ)
        cond = self.parsear_expresion()
        self._consumir(TokenKind.PUNT_PAREN_DER)
        entonces = self.parsear_bloque()
        
        ramas_elif = []
        while self._coincide(TokenKind.KW_WAZDA):
            self._avanzar()
            self._consumir(TokenKind.PUNT_PAREN_IZQ)
            cond_elif = self.parsear_expresion()
            self._consumir(TokenKind.PUNT_PAREN_DER)
            bloq_elif = self.parsear_bloque()
            ramas_elif.append((cond_elif, bloq_elif))
            
        sino = None
        if self._coincide(TokenKind.KW_WALLA):
            self._avanzar()
            sino = self.parsear_bloque()
            
        return NodoSi(linea=t.linea, columna=t.columna, condicion=cond, entonces=entonces, ramas_elif=ramas_elif, sino=sino)

    def parsear_sent_mientras(self) -> NodoBucle_Mientras:
        t = self._consumir(TokenKind.KW_BAYNAMA)
        self._consumir(TokenKind.PUNT_PAREN_IZQ)
        cond = self.parsear_expresion()
        self._consumir(TokenKind.PUNT_PAREN_DER)
        cuerpo = self.parsear_bloque()
        return NodoBucle_Mientras(linea=t.linea, columna=t.columna, condicion=cond, cuerpo=cuerpo)
        
    def parsear_sent_para_cada(self) -> NodoBucle_ParaCada:
        t = self._consumir(TokenKind.KW_LIKULL)
        var_id = self._consumir(TokenKind.IDENTIFICADOR).valor
        self._consumir(TokenKind.KW_FI)
        iterable = self.parsear_expresion()
        cuerpo = self.parsear_bloque()
        return NodoBucle_ParaCada(linea=t.linea, columna=t.columna, variable=var_id, iterable=iterable, cuerpo=cuerpo)
        
    def parsear_sent_repetir(self) -> NodoBucle_Repetir:
        # كرر من 0 حتى ن { }
        t = self._consumir(TokenKind.KW_KARRIR)
        ident_min = self._consumir(TokenKind.IDENTIFICADOR) # should be "من"
        inicio = self.parsear_expresion()
        ident_hatta = self._consumir(TokenKind.IDENTIFICADOR) # should be "حتى"
        fin = self.parsear_expresion()
        cuerpo = self.parsear_bloque()
        return NodoBucle_Repetir(linea=t.linea, columna=t.columna, variable="ر", inicio=inicio, fin=fin, cuerpo=cuerpo)

    def parsear_sent_retornar(self) -> NodoRetornar:
        t = self._consumir(TokenKind.KW_IRJAH)
        valor = None
        if not self._coincide(TokenKind.PUNT_LLAVE_DER, TokenKind.FIN_ARCHIVO):
            valor = self.parsear_expresion()
        return NodoRetornar(linea=t.linea, columna=t.columna, valor=valor)

    # --- Expresiones ---
    # Precedence: (lowest) Asignacion -> OR -> AND -> Igualdad -> Comparacion -> Adicion -> Mult -> Unario -> Postfijo -> Primario (highest)
    def parsear_expresion(self) -> NodoAST:
        return self.parsear_asignacion()

    def parsear_asignacion(self) -> NodoAST:
        expr = self.parsear_logica_o()
        
        ops_asig = [TokenKind.OP_ASIGNACION, TokenKind.OP_ASIG_MAS, TokenKind.OP_ASIG_MENOS, TokenKind.OP_ASIG_MULTI, TokenKind.OP_ASIG_DIV]
        if self._coincide(*ops_asig):
            t = self.token_actual
            self._avanzar()
            valor = self.parsear_asignacion() # Right associative
            return NodoAsignacion(linea=t.linea, columna=t.columna, objetivo=expr, valor=valor, operador=t.valor)
            
        return expr

    def parsear_logica_o(self) -> NodoAST:
        expr = self.parsear_logica_y()
        while self._coincide(TokenKind.KW_AW):
            t = self.token_actual
            self._avanzar()
            derecha = self.parsear_logica_y()
            expr = NodoOpBinaria(linea=t.linea, columna=t.columna, izquierda=expr, operador=t.valor, derecha=derecha)
        return expr

    def parsear_logica_y(self) -> NodoAST:
        expr = self.parsear_igualdad()
        while self._coincide(TokenKind.KW_WA):
            t = self.token_actual
            self._avanzar()
            derecha = self.parsear_igualdad()
            expr = NodoOpBinaria(linea=t.linea, columna=t.columna, izquierda=expr, operador=t.valor, derecha=derecha)
        return expr

    def parsear_igualdad(self) -> NodoAST:
        expr = self.parsear_comparacion()
        while self._coincide(TokenKind.OP_IGUAL_IGUAL, TokenKind.OP_DISTINTO):
            t = self.token_actual
            self._avanzar()
            derecha = self.parsear_comparacion()
            expr = NodoOpBinaria(linea=t.linea, columna=t.columna, izquierda=expr, operador=t.valor, derecha=derecha)
        return expr

    def parsear_comparacion(self) -> NodoAST:
        expr = self.parsear_adicion()
        ops = [TokenKind.OP_MENOR, TokenKind.OP_MENOR_IGUAL, TokenKind.OP_MAYOR, TokenKind.OP_MAYOR_IGUAL]
        while self._coincide(*ops):
            t = self.token_actual
            self._avanzar()
            derecha = self.parsear_adicion()
            expr = NodoOpBinaria(linea=t.linea, columna=t.columna, izquierda=expr, operador=t.valor, derecha=derecha)
        return expr

    def parsear_adicion(self) -> NodoAST:
        expr = self.parsear_multiplicacion()
        while self._coincide(TokenKind.OP_MAS, TokenKind.OP_MENOS):
            t = self.token_actual
            self._avanzar()
            derecha = self.parsear_multiplicacion()
            expr = NodoOpBinaria(linea=t.linea, columna=t.columna, izquierda=expr, operador=t.valor, derecha=derecha)
        return expr

    def parsear_multiplicacion(self) -> NodoAST:
        expr = self.parsear_unario()
        while self._coincide(TokenKind.OP_MULTI, TokenKind.OP_DIV, TokenKind.OP_MOD):
            t = self.token_actual
            self._avanzar()
            derecha = self.parsear_unario()
            expr = NodoOpBinaria(linea=t.linea, columna=t.columna, izquierda=expr, operador=t.valor, derecha=derecha)
        return expr

    def parsear_unario(self) -> NodoAST:
        if self._coincide(TokenKind.OP_MENOS, TokenKind.KW_LAYSA):
            t = self.token_actual
            self._avanzar()
            derecha = self.parsear_unario()
            return NodoOpUnaria(linea=t.linea, columna=t.columna, operador=t.valor, operando=derecha)
        return self.parsear_postfijo()

    def parsear_postfijo(self) -> NodoAST:
        expr = self.parsear_primario()
        
        while True:
            t = self.token_actual
            if self._coincide(TokenKind.PUNT_PUNTO):
                self._avanzar()
                nombre = self._consumir(TokenKind.IDENTIFICADOR).valor
                expr = NodoAcceso(linea=t.linea, columna=t.columna, objeto=expr, campo=nombre)
            elif self._coincide(TokenKind.PUNT_PAREN_IZQ):
                self._avanzar() # '('
                argumentos = []
                if not self._coincide(TokenKind.PUNT_PAREN_DER):
                    argumentos.append(self.parsear_expresion())
                    while self._coincide(TokenKind.PUNT_COMA):
                        self._avanzar()
                        argumentos.append(self.parsear_expresion())
                self._consumir(TokenKind.PUNT_PAREN_DER)
                expr = NodoLlamada(linea=t.linea, columna=t.columna, funcion=expr, argumentos=argumentos)
            elif self._coincide(TokenKind.PUNT_CORCHETE_IZQ):
                self._avanzar() # '['
                indice = self.parsear_expresion()
                self._consumir(TokenKind.PUNT_CORCHETE_DER)
                expr = NodoIndice(linea=t.linea, columna=t.columna, objeto=expr, indice=indice)
            else:
                break
                
        return expr

    def parsear_primario(self) -> NodoAST:
        t = self.token_actual
        if self._coincide(TokenKind.NUMERO_ENTERO):
            self._avanzar()
            return NodoLiteralNumero(linea=t.linea, columna=t.columna, valor=int(t.valor))
        if self._coincide(TokenKind.NUMERO_FLOTANTE):
            self._avanzar()
            return NodoLiteralNumero(linea=t.linea, columna=t.columna, valor=float(t.valor))
        if self._coincide(TokenKind.CADENA):
            self._avanzar()
            return NodoLiteralCadena(linea=t.linea, columna=t.columna, valor=t.valor)
        if self._coincide(TokenKind.KW_SAHH):
            self._avanzar()
            return NodoLiteralBool(linea=t.linea, columna=t.columna, valor=True)
        if self._coincide(TokenKind.KW_KHATA):
            self._avanzar()
            return NodoLiteralBool(linea=t.linea, columna=t.columna, valor=False)
        if self._coincide(TokenKind.KW_FARIGH):
            self._avanzar()
            return NodoLiteralNulo(linea=t.linea, columna=t.columna)
        if self._coincide(TokenKind.IDENTIFICADOR):
            self._avanzar()
            return NodoIdentificador(linea=t.linea, columna=t.columna, nombre=t.valor)
        if self._coincide(TokenKind.KW_ITBA):
            self._avanzar()
            return NodoIdentificador(linea=t.linea, columna=t.columna, nombre="اطبع") # Treat as built-in identifier for parsing
        if self._coincide(TokenKind.KW_HADHA):
            self._avanzar()
            return NodoIdentificador(linea=t.linea, columna=t.columna, nombre="هذا")
        if self._coincide(TokenKind.KW_JADID):
            self._avanzar()
            clase = self._consumir(TokenKind.IDENTIFICADOR).valor
            self._consumir(TokenKind.PUNT_PAREN_IZQ)
            argumentos = []
            if not self._coincide(TokenKind.PUNT_PAREN_DER):
                argumentos.append(self.parsear_expresion())
                while self._coincide(TokenKind.PUNT_COMA):
                    self._avanzar()
                    argumentos.append(self.parsear_expresion())
            self._consumir(TokenKind.PUNT_PAREN_DER)
            return NodoNuevo(linea=t.linea, columna=t.columna, clase=clase, argumentos=argumentos)
            
        if self._coincide(TokenKind.PUNT_PAREN_IZQ):
            self._avanzar()
            expr = self.parsear_expresion()
            self._consumir(TokenKind.PUNT_PAREN_DER)
            return expr
            
        if self._coincide(TokenKind.PUNT_CORCHETE_IZQ):
            self._avanzar()
            elementos = []
            if not self._coincide(TokenKind.PUNT_CORCHETE_DER):
                elementos.append(self.parsear_expresion())
                while self._coincide(TokenKind.PUNT_COMA):
                    self._avanzar()
                    elementos.append(self.parsear_expresion())
            self._consumir(TokenKind.PUNT_CORCHETE_DER)
            return NodoLiteralLista(linea=t.linea, columna=t.columna, elementos=elementos)
            
        raise ErrorSintaxis("Expresión inválida", t)
