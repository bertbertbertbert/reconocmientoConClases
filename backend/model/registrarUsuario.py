import tkinter as tk
from tkinter import filedialog
from consultas_bbdd import consultas_bbdd

class registro_usuario:

    def __init__(self):
        self.db = consultas_bbdd()

    def _pedir_codigo(self):
        codigo = input("Introducir el código de usuario: ").strip()
        while not codigo:
            codigo = input("Error: El código no puede estar vacío: ").strip()
        return codigo

    def _seleccionar_archivo(self):
        print("Abriendo selector de archivos...")
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        ruta_fichero = filedialog.askopenfilename(
            title="Selecciona el fichero a procesar",
            filetypes=[
                ("Archivos de imagen", "*.jpg *.jpeg *.png *.webp *.bmp"),
                ("Todos los archivos", "*.*")
            ]
        )
        return ruta_fichero

    def solicitar_datos(self):
        codigo = self._pedir_codigo()
        ruta_fichero = self._seleccionar_archivo()

        if not ruta_fichero:
            print("Operación cancelada: No se seleccionó ningún archivo.")
            return

        resultado = self.db.registrar_usuario_nuevo(codigo, ruta_fichero)
        if resultado:
            print(f"El usuario {codigo} se ha actualizado correctamente")
        else:
            print(f"Error: No se han podido actualizar los datos del usuario {codigo}.")