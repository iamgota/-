import unittest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lexer import Lexer
from tokens import TokenKind

class TestLexer(unittest.TestCase):
    def test_palabras_clave(self):
        codigo = "اذا واال بينما لكل كرر من حتى توقف تابع دالة ارجع صنف هذا جديد يرث متغير ثابت"
        lexer = Lexer(codigo)
        tokens = lexer.tokenizar()
        esperados = [
            TokenKind.KW_AZDA, TokenKind.KW_WALLA, TokenKind.KW_BAYNAMA, 
            TokenKind.KW_LIKULL, TokenKind.KW_KARRIR, TokenKind.KW_MIN, 
            TokenKind.KW_HATTA, TokenKind.KW_TAWAQQAF, TokenKind.KW_TABI, 
            TokenKind.KW_DALA, TokenKind.KW_IRJAH, TokenKind.KW_SINF, 
            TokenKind.KW_HADHA, TokenKind.KW_JADID, TokenKind.KW_YARITH, 
            TokenKind.KW_MUTAGHAYYIR, TokenKind.KW_THABIT, TokenKind.FIN_ARCHIVO
        ]
        self.assertEqual([t.tipo for t in tokens], esperados)

    def test_numeros(self):
        lexer = Lexer("123 45.67")
        tokens = lexer.tokenizar()
        self.assertEqual(tokens[0].tipo, TokenKind.NUMERO_ENTERO)
        self.assertEqual(tokens[0].valor, "123")
        self.assertEqual(tokens[1].tipo, TokenKind.NUMERO_FLOTANTE)
        self.assertEqual(tokens[1].valor, "45.67")

    def test_cadenas(self):
        lexer = Lexer('"مرحبا"')
        tokens = lexer.tokenizar()
        self.assertEqual(tokens[0].tipo, TokenKind.CADENA)
        self.assertEqual(tokens[0].valor, "مرحبا")

    def test_identificadores(self):
        lexer = Lexer("المتغير_1")
        tokens = lexer.tokenizar()
        self.assertEqual(tokens[0].tipo, TokenKind.IDENTIFICADOR)

if __name__ == '__main__':
    unittest.main()
