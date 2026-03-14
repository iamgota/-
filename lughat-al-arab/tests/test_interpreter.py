import unittest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lexer import Lexer
from parser import Parser
from interpreter import Interprete

class TestInterpreter(unittest.TestCase):
    def ejecutar(self, codigo):
        lexer = Lexer(codigo)
        parser = Parser(lexer.tokenizar())
        ast = parser.parsear_programa()
        interp = Interprete()
        self.salida = []
        # Override print to capture output
        interp.entorno_global.asignar("اطبع", lambda *args: self.salida.append(" ".join(map(str, args))))
        interp.ejecutar(ast)
        return self.salida

    def test_aritmetica(self):
        salida = self.ejecutar('اطبع(5 + 3 * 2)')
        self.assertEqual(salida[0], '11')

    def test_variables(self):
        salida = self.ejecutar('متغير ن = 10\nاطبع(ن)')
        self.assertEqual(salida[0], '10')

    def test_bucle(self):
        codigo = '''
        متغير مجموع = 0
        كرر من 1 حتى 4 { مجموع = مجموع + ر }
        اطبع(مجموع)
        '''
        salida = self.ejecutar(codigo)
        self.assertEqual(salida[0], '6') # 1+2+3 = 6

if __name__ == '__main__':
    unittest.main()
