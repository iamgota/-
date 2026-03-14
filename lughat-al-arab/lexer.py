import unicodedata
from typing import List, Optional
from tokens import Token, TokenKind, KEYWORDS_MAP

class LexerError(Exception):
    def __init__(self, mensaje: str, linea: int, columna: int):
        self.mensaje = f"‫خطا معجمي‬: {mensaje} (L{linea}:C{columna})"
        super().__init__(self.mensaje)

class Lexer:
    def __init__(self, codigo: str):
        self.codigo = unicodedata.normalize("NFC", codigo)
        self.pos = 0
        self.linea = 1
        self.columna = 1
        self.tokens: List[Token] = []

    def tokenizar(self) -> List[Token]:
        while self.pos < len(self.codigo):
            self._saltar_espacios()
            if self.pos >= len(self.codigo):
                break
            
            token = self._siguiente_token()
            if token:
                self.tokens.append(token)
                
        self.tokens.append(Token(TokenKind.FIN_ARCHIVO, "", self.linea, self.columna, ""))
        return self.tokens

    def _saltar_espacios(self):
        while self.pos < len(self.codigo):
            c = self.codigo[self.pos]
            if c == '\n':
                # ASI placeholder logic or just ignore
                self.linea += 1
                self.columna = 1
                self._avanzar()
            elif c in (' ', '\t', '\r'):
                self._avanzar()
            else:
                break

    def _siguiente_token(self) -> Optional[Token]:
        c = self.codigo[self.pos]
        
        # Comments
        if c == '/':
            if self._peek() == '/':
                return self._leer_comentario_linea()
            elif self._peek() == '*':
                return self._leer_comentario_bloque()

        if c.isdigit():
            return self._leer_numero()
            
        if c == '"':
            return self._leer_cadena()
            
        if self._es_inicio_identificador(c):
            return self._leer_identificador()
            
        return self._leer_operador_o_puntuacion()

    def _avanzar(self) -> str:
        if self.pos >= len(self.codigo):
            return ""
        c = self.codigo[self.pos]
        self.pos += 1
        self.columna += 1
        return c

    def _peek(self, offset=1) -> str:
        if self.pos + offset >= len(self.codigo):
            return ""
        return self.codigo[self.pos + offset]

    def _es_inicio_identificador(self, c: str) -> bool:
        cp = ord(c)
        return (0x0600 <= cp <= 0x06FF or  # Arabic basic
                0xFB50 <= cp <= 0xFDFF or  # Arabic extended A
                c == "_" or c.isalpha())

    def _leer_identificador(self) -> Token:
        inicio = self.pos
        col_inicio = self.columna
        
        while self.pos < len(self.codigo):
            c = self.codigo[self.pos]
            if not (self._es_inicio_identificador(c) or c.isdigit() or c == "_"):
                break
            self._avanzar()
            
        texto = self.codigo[inicio:self.pos]
        
        tipo = KEYWORDS_MAP.get(texto, TokenKind.IDENTIFICADOR)
        # In a full implementation, canonizar handles hamza removal
        canonico = texto 
        
        return Token(tipo, texto, self.linea, col_inicio, canonico)

    def _leer_numero(self) -> Token:
        inicio = self.pos
        col_inicio = self.columna
        es_flotante = False
        
        while self.pos < len(self.codigo):
            c = self.codigo[self.pos]
            if c.isdigit():
                self._avanzar()
            elif c == '.' and not es_flotante and self._peek().isdigit():
                es_flotante = True
                self._avanzar()
            else:
                break
                
        texto = self.codigo[inicio:self.pos]
        tipo = TokenKind.NUMERO_FLOTANTE if es_flotante else TokenKind.NUMERO_ENTERO
        return Token(tipo, texto, self.linea, col_inicio, texto)

    def _leer_cadena(self) -> Token:
        col_inicio = self.columna
        self._avanzar() # Skip initial quote
        inicio = self.pos
        texto_interno = ""
        
        while self.pos < len(self.codigo):
            c = self.codigo[self.pos]
            if c == '"':
                break
            elif c == '\\':
                self._avanzar()
                if self.pos < len(self.codigo):
                    esc = self.codigo[self.pos]
                    if esc == 'n': texto_interno += '\n'
                    elif esc == 't': texto_interno += '\t'
                    elif esc == '"': texto_interno += '"'
                    elif esc == '\\': texto_interno += '\\'
                    else: texto_interno += esc
                    self._avanzar()
            else:
                texto_interno += c
                if c == '\n':
                    self.linea += 1
                    self.columna = 1
                self._avanzar()
                
        if self.pos >= len(self.codigo):
            raise LexerError("Cadena no cerrada", self.linea, col_inicio)
            
        self._avanzar() # Skip final quote
        return Token(TokenKind.CADENA, texto_interno, self.linea, col_inicio, texto_interno)

    def _leer_comentario_linea(self) -> None:
        while self.pos < len(self.codigo) and self.codigo[self.pos] != '\n':
            self._avanzar()
        return None

    def _leer_comentario_bloque(self) -> None:
        linea_inicio = self.linea
        col_inicio = self.columna
        self._avanzar() # /
        self._avanzar() # *
        
        while self.pos < len(self.codigo):
            if self.codigo[self.pos] == '*' and self._peek() == '/':
                self._avanzar()
                self._avanzar()
                return None
            if self.codigo[self.pos] == '\n':
                self.linea += 1
                self.columna = 1
            self._avanzar()
            
        raise LexerError("Comentario de bloque no cerrado", linea_inicio, col_inicio)

    def _leer_operador_o_puntuacion(self) -> Token:
        c = self.codigo[self.pos]
        col_inicio = self.columna
        siguiente = self._peek()
        
        # Operadores compuestos de 2 caracteres
        if c == '=' and siguiente == '=':
            self._avanzar(); self._avanzar()
            return Token(TokenKind.OP_IGUAL_IGUAL, "==", self.linea, col_inicio, "==")
        if c == '!' and siguiente == '=':
            self._avanzar(); self._avanzar()
            return Token(TokenKind.OP_DISTINTO, "!=", self.linea, col_inicio, "!=")
        if c == '<' and siguiente == '=':
            self._avanzar(); self._avanzar()
            return Token(TokenKind.OP_MENOR_IGUAL, "<=", self.linea, col_inicio, "<=")
        if c == '>' and siguiente == '=':
            self._avanzar(); self._avanzar()
            return Token(TokenKind.OP_MAYOR_IGUAL, ">=", self.linea, col_inicio, ">=")
        if c == '+' and siguiente == '=':
            self._avanzar(); self._avanzar()
            return Token(TokenKind.OP_ASIG_MAS, "+=", self.linea, col_inicio, "+=")
        if c == '-' and siguiente == '=':
            self._avanzar(); self._avanzar()
            return Token(TokenKind.OP_ASIG_MENOS, "-=", self.linea, col_inicio, "-=")
        if c == '*' and siguiente == '=':
            self._avanzar(); self._avanzar()
            return Token(TokenKind.OP_ASIG_MULTI, "*=", self.linea, col_inicio, "*=")
        if c == '/' and siguiente == '=':
            self._avanzar(); self._avanzar()
            return Token(TokenKind.OP_ASIG_DIV, "/=", self.linea, col_inicio, "/=")
        if c == '*' and siguiente == '*':
            self._avanzar(); self._avanzar()
            return Token(TokenKind.OP_POTENCIA, "**", self.linea, col_inicio, "**")
        if c == '-' and siguiente == '>':
            self._avanzar(); self._avanzar()
            return Token(TokenKind.OP_FLECHA, "->", self.linea, col_inicio, "->")

        # 1 caracter
        self._avanzar()
        if c == '=': tipo = TokenKind.OP_ASIGNACION
        elif c == '+': tipo = TokenKind.OP_MAS
        elif c == '-': tipo = TokenKind.OP_MENOS
        elif c == '*': tipo = TokenKind.OP_MULTI
        elif c == '/': tipo = TokenKind.OP_DIV
        elif c == '%': tipo = TokenKind.OP_MOD
        elif c == '<': tipo = TokenKind.OP_MENOR
        elif c == '>': tipo = TokenKind.OP_MAYOR
        elif c == '(': tipo = TokenKind.PUNT_PAREN_IZQ
        elif c == ')': tipo = TokenKind.PUNT_PAREN_DER
        elif c == '{': tipo = TokenKind.PUNT_LLAVE_IZQ
        elif c == '}': tipo = TokenKind.PUNT_LLAVE_DER
        elif c == '[': tipo = TokenKind.PUNT_CORCHETE_IZQ
        elif c == ']': tipo = TokenKind.PUNT_CORCHETE_DER
        elif c == '،' or c == ',': tipo = TokenKind.PUNT_COMA  # Soporta coma árabe y occidente
        elif c == '.': tipo = TokenKind.PUNT_PUNTO
        elif c == ':': tipo = TokenKind.PUNT_DOS_PUNTOS
        else:
            raise LexerError(f"Carácter inesperado: '{c}'", self.linea, col_inicio)
            
        return Token(tipo, c, self.linea, col_inicio, c)
