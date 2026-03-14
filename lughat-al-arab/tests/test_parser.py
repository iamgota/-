import unittest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lexer import Lexer
from parser import Parser
from ast_nodes import *

class TestParser(unittest.TestCase):
    def test_declaracion_variable(self):
        codigo = "متغير ن = 10"
        lexer = Lexer(codigo)
        parser = Parser(lexer.tokenizar())
        ast = parser.parsear_programa()
        self.assertEqual(len(ast.cuerpo), 1)
        self.assertIsInstance(ast.cuerpo[0], NodoDeclVariable)
        self.assertEqual(ast.cuerpo[0].nombre, "ن")

    def test_operaciones_binarias(self):
        codigo = "1 + 2 * 3"
        lexer = Lexer(codigo)
        parser = Parser(lexer.tokenizar())
        ast = parser.parsear_programa()
        expr = ast.cuerpo[0].valor
        self.assertIsInstance(expr, NodoOpBinaria)
        self.assertEqual(expr.operador, "+")
        self.assertIsInstance(expr.derecha, NodoOpBinaria)
        self.assertEqual(expr.derecha.operador, "*")

    def test_bucle_repetir(self):
        codigo = "كرر من 1 حتى 5 {}"
        lexer = Lexer(codigo)
        parser = Parser(lexer.tokenizar())
        ast = parser.parsear_programa()
        self.assertIsInstance(ast.cuerpo[0], NodoBucle_Repetir)
        self.assertEqual(ast.cuerpo[0].variable, "ر")

if __name__ == '__main__':
    unittest.main()
