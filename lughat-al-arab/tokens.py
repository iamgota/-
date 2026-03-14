from dataclasses import dataclass
from enum import Enum, auto

class TokenKind(Enum):
    # Keywords
    KW_AZDA = "‫اذا"
    KW_WALLA = "‫واال"
    KW_WAZDA = "‫واذا"
    KW_BAYNAMA = "‫بينما"
    KW_LIKULL = "‫لكل"
    KW_KARRIR = "‫كرر"
    KW_TAWAQQAF = "‫توقف"
    KW_TABI = "‫تابع"
    
    KW_DALA = "‫دالة"
    KW_IRJAH = "‫ارجع"
    
    KW_SINF = "‫صنف"
    KW_HADHA = "‫هذا"
    KW_JADID = "‫جديد"
    KW_YARITH = "‫يرث"
    
    KW_MUTAGHAYYIR = "‫متغير"
    KW_THABIT = "‫ثابت"
    
    # Types
    KW_ADAD = "‫عدد"
    KW_NASS = "‫نص"
    KW_QAIMA = "‫قائمة"
    KW_QAMUS = "‫قاموس"
    
    # Booleans & Null
    KW_SAHH = "‫صح"
    KW_KHATA = "‫خطا"
    KW_FARIGH = "‫فارغ"
    
    # Built-ins / IO
    KW_ITBA = "‫اطبع"
    KW_IQRA = "‫اقرا"
    
    # Error Handling
    KW_HAWAL = "‫حاول"
    KW_ILTAQIT = "‫التقط"
    KW_AKHIRAN = "‫اخيرا"
    KW_ARMI = "‫ارمي"
    
    # Modules
    KW_ISTAWRED = "‫استورد"
    KW_SADDIR = "‫صدر"
    
    # AI (future)
    KW_NAMUTHAJ = "‫نموذج"
    KW_DARRIB = "‫درب"
    KW_TANABBA = "‫تنبا"
    
    # Logic
    KW_WA = "‫و"
    KW_AW = "‫او"
    KW_LAYSA = "‫ليس"
    KW_FI = "‫في"
    
    # Literals
    IDENTIFICADOR = "IDENTIFICADOR"
    NUMERO_ENTERO = "NUMERO_ENTERO"
    NUMERO_FLOTANTE = "NUMERO_FLOTANTE"
    CADENA = "CADENA"
    
    # Arithmetic & Logic Ops
    OP_MAS = "+"
    OP_MENOS = "-"
    OP_MULTI = "*"
    OP_DIV = "/"
    OP_MOD = "%"
    OP_POTENCIA = "**"
    
    OP_IGUAL_IGUAL = "=="
    OP_DISTINTO = "!="
    OP_MENOR = "<"
    OP_MENOR_IGUAL = "<="
    OP_MAYOR = ">"
    OP_MAYOR_IGUAL = ">="
    
    # Assignment
    OP_ASIGNACION = "="
    OP_ASIG_MAS = "+="
    OP_ASIG_MENOS = "-="
    OP_ASIG_MULTI = "*="
    OP_ASIG_DIV = "/="
    OP_FLECHA = "->"
    
    # Punctuation
    PUNT_PAREN_IZQ = "("
    PUNT_PAREN_DER = ")"
    PUNT_LLAVE_IZQ = "{"
    PUNT_LLAVE_DER = "}"
    PUNT_CORCHETE_IZQ = "["
    PUNT_CORCHETE_DER = "]"
    PUNT_COMA = "،"
    PUNT_PUNTO = "."
    PUNT_DOS_PUNTOS = ":"
    
    # Special
    NUEVA_LINEA = "NUEVA_LINEA"
    FIN_ARCHIVO = "FIN_ARCHIVO"

# Map of literal string keywords to their standard internal enum (NFC normalized, no hamza ideally)
KEYWORDS_MAP = {
    "اذا": TokenKind.KW_AZDA,
    "إذا": TokenKind.KW_AZDA,
    "واذا": TokenKind.KW_WAZDA,
    "وإذا": TokenKind.KW_WAZDA,
    "واال": TokenKind.KW_WALLA,
    "وإال": TokenKind.KW_WALLA,
    "بينما": TokenKind.KW_BAYNAMA,
    "لكل": TokenKind.KW_LIKULL,
    "كرر": TokenKind.KW_KARRIR,
    "توقف": TokenKind.KW_TAWAQQAF,
    "تابع": TokenKind.KW_TABI,
    "دالة": TokenKind.KW_DALA,
    "ارجع": TokenKind.KW_IRJAH,
    "أرجع": TokenKind.KW_IRJAH,
    "صنف": TokenKind.KW_SINF,
    "هذا": TokenKind.KW_HADHA,
    "جديد": TokenKind.KW_JADID,
    "يرث": TokenKind.KW_YARITH,
    "متغير": TokenKind.KW_MUTAGHAYYIR,
    "ثابت": TokenKind.KW_THABIT,
    "عدد": TokenKind.KW_ADAD,
    "نص": TokenKind.KW_NASS,
    "قائمة": TokenKind.KW_QAIMA,
    "قاموس": TokenKind.KW_QAMUS,
    "صح": TokenKind.KW_SAHH,
    "خطا": TokenKind.KW_KHATA,
    "فارغ": TokenKind.KW_FARIGH,
    "اطبع": TokenKind.KW_ITBA,
    "اقرا": TokenKind.KW_IQRA,
    "اقرأ": TokenKind.KW_IQRA,
    "حاول": TokenKind.KW_HAWAL,
    "التقط": TokenKind.KW_ILTAQIT,
    "اخيرا": TokenKind.KW_AKHIRAN,
    "أخيراً": TokenKind.KW_AKHIRAN,
    "ارمي": TokenKind.KW_ARMI,
    "ارم": TokenKind.KW_ARMI,
    "استورد": TokenKind.KW_ISTAWRED,
    "صدر": TokenKind.KW_SADDIR,
    "نموذج": TokenKind.KW_NAMUTHAJ,
    "درب": TokenKind.KW_DARRIB,
    "درّب": TokenKind.KW_DARRIB,
    "تنبا": TokenKind.KW_TANABBA,
    "تنبأ": TokenKind.KW_TANABBA,
    "و": TokenKind.KW_WA,
    "او": TokenKind.KW_AW,
    "أو": TokenKind.KW_AW,
    "ليس": TokenKind.KW_LAYSA,
    "في": TokenKind.KW_FI,
}

@dataclass
class Token:
    tipo: TokenKind
    valor: str
    linea: int
    columna: int
    valor_canonico: str
