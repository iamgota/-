import sys
from lexer import Lexer, LexerError
from parser import Parser, ErrorSintaxis
from interpreter import Interprete, ErrorEjecucion

def ejecutar_script(ruta: str):
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            codigo = f.read()
            
        lexer = Lexer(codigo)
        tokens = lexer.tokenizar()
        
        parser = Parser(tokens)
        ast = parser.parsear_programa()
        
        interprete = Interprete()
        interprete.ejecutar(ast)
        
    except (LexerError, ErrorSintaxis, ErrorEjecucion) as e:
        print(f"\n{e}")
    except FileNotFoundError:
        print(f"‫خطا‬: ‫لم يتم العثور على الملف‬ '{ruta}'")
    except Exception as e:
        print(f"‫خطا غير متوقع‬: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("‫االستخدام‬: python3 main.py <archivo.عرب>")
        sys.exit(1)
        
    ejecutar_script(sys.argv[1])
