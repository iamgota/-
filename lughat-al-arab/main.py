import sys
from lexer import Lexer, LexerError
from parser import Parser, ErrorSintaxis
from interpreter import Interprete, ErrorEjecucion

def ejecutar_script(ruta: str):
    if not (ruta.endswith(".ه") or ruta.endswith(".عرب")):
        print("‫خطا‬: ‫يجب أن يكون امتداد الملف .ه أو .عرب‬")
        sys.exit(1)
        
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

def iniciar_repl():
    print("لغة العرب v0.2 — اكتب \"خروج\" للخروج")
    interprete = Interprete()
    
    while True:
        try:
            linea = input(">>> ")
            if linea.strip() == "خروج":
                break
            if not linea.strip():
                continue
                
            lexer = Lexer(linea)
            tokens = lexer.tokenizar()
            
            parser = Parser(tokens)
            ast = parser.parsear_programa()
            
            resultado = interprete.ejecutar(ast)
            if resultado is not None:
                print(resultado)
                
        except (LexerError, ErrorSintaxis, ErrorEjecucion) as e:
            print(e)
        except KeyboardInterrupt:
            print("\n")
            break
        except EOFError:
            print("\n")
            break
        except Exception as e:
            print(f"‫خطا غير متوقع‬: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "--repl":
        iniciar_repl()
    elif len(sys.argv) == 2:
        if sys.argv[1] in ["-h", "--help"]:
            print("‫االستخدام‬: python3 main.py <archivo.ه> أو python3 main.py --repl")
        else:
            ejecutar_script(sys.argv[1])
    else:
        print("‫االستخدام‬: python3 main.py <archivo.ه>")
        sys.exit(1)
