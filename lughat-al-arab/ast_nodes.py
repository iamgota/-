from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class NodoAST:
    linea: int = 0
    columna: int = 0

# --- Nodos de Declaracion ---
@dataclass
class NodoPrograma(NodoAST):
    cuerpo: List[NodoAST] = field(default_factory=list)

@dataclass
class NodoDeclVariable(NodoAST):
    nombre: str = ""
    valor: Optional[NodoAST] = None
    tipo_anotado: Optional[str] = None
    es_constante: bool = False

@dataclass
class NodoDeclFuncion(NodoAST):
    nombre: str = ""
    parametros: List["NodoParametro"] = field(default_factory=list)
    cuerpo: "NodoBloque" = None
    tipo_retorno: Optional[str] = None

@dataclass
class NodoParametro(NodoAST):
    nombre: str = ""
    tipo: Optional[str] = None
    valor_defecto: Optional[NodoAST] = None

@dataclass
class NodoDeclClase(NodoAST):
    nombre: str = ""
    padre: Optional[str] = None
    miembros: List[NodoAST] = field(default_factory=list)

# --- Nodos de Sentencia ---
@dataclass
class NodoBloque(NodoAST):
    sentencias: List[NodoAST] = field(default_factory=list)

@dataclass
class NodoSi(NodoAST):
    condicion: NodoAST = None
    entonces: NodoBloque = None
    ramas_elif: List[tuple] = field(default_factory=list) # [(condicion, bloque)]
    sino: Optional[NodoBloque] = None

@dataclass
class NodoBucle_Mientras(NodoAST):
    condicion: NodoAST = None
    cuerpo: NodoBloque = None

@dataclass
class NodoBucle_ParaCada(NodoAST):
    variable: str = ""
    iterable: NodoAST = None
    cuerpo: NodoBloque = None

@dataclass
class NodoBucle_Repetir(NodoAST):
    # كرر من 0 حتى 10 { }
    variable: str = ""
    inicio: NodoAST = None
    fin: NodoAST = None
    cuerpo: NodoBloque = None

@dataclass
class NodoRetornar(NodoAST):
    valor: Optional[NodoAST] = None

@dataclass
class NodoExpresionSentencia(NodoAST):
    valor: NodoAST = None

# --- Nodos de Expresion ---
@dataclass
class NodoAsignacion(NodoAST):
    objetivo: NodoAST = None
    valor: NodoAST = None
    operador: str = "=" 

@dataclass
class NodoOpBinaria(NodoAST):
    izquierda: NodoAST = None
    operador: str = ""
    derecha: NodoAST = None

@dataclass
class NodoOpUnaria(NodoAST):
    operador: str = ""
    operando: NodoAST = None

@dataclass
class NodoLlamada(NodoAST):
    funcion: NodoAST = None
    argumentos: List[NodoAST] = field(default_factory=list)

@dataclass
class NodoAcceso(NodoAST):
    objeto: NodoAST = None
    campo: str = ""

@dataclass
class NodoIndice(NodoAST):
    objeto: NodoAST = None
    indice: NodoAST = None

@dataclass
class NodoNuevo(NodoAST):
    clase: str = ""
    argumentos: List[NodoAST] = field(default_factory=list)

# --- Literales ---
@dataclass
class NodoLiteralNumero(NodoAST):
    valor: float = 0.0

@dataclass
class NodoLiteralCadena(NodoAST):
    valor: str = ""

@dataclass
class NodoLiteralBool(NodoAST):
    valor: bool = False

@dataclass
class NodoLiteralNulo(NodoAST):
    pass

@dataclass
class NodoLiteralLista(NodoAST):
    elementos: List[NodoAST] = field(default_factory=list)

@dataclass
class NodoLiteralDict(NodoAST):
    pares: List[tuple] = field(default_factory=list) # [(clave, valor)]

@dataclass
class NodoIdentificador(NodoAST):
    nombre: str = ""
