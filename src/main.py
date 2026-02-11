import customtkinter as ctk
from tkinter import filedialog
import os
import subprocess
import threading

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class LovaScalerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("LovaScaler v0.6.2")
        self.geometry("700x550") 

        self.ruta_entrada = ""
        self.ruta_salida = ""
        
        # Localización robusta del motor
        ruta_script = os.path.dirname(os.path.abspath(__file__))
        self.ruta_bin = os.path.join(os.path.dirname(ruta_script), "bin")
        self.exe_path = os.path.join(self.ruta_bin, "realesrgan-ncnn-vulkan.exe")

        self.titulo = ctk.CTkLabel(self, text="LovaScaler AI", font=("Roboto", 28, "bold"))
        self.titulo.pack(pady=20)

        self.btn_entrada = ctk.CTkButton(self, text="Seleccionar origen", command=self.seleccionar_entrada)
        self.btn_entrada.pack(pady=10)
        self.lbl_entrada = ctk.CTkLabel(self, text="Sin seleccion", text_color="gray")
        self.lbl_entrada.pack()

        self.btn_salida = ctk.CTkButton(self, text="Seleccionar destino", command=self.seleccionar_salida, fg_color="#2E8B57")
        self.btn_salida.pack(pady=10)
        self.lbl_salida = ctk.CTkLabel(self, text="Sin seleccion", text_color="gray")
        self.lbl_salida.pack()

        self.progreso = ctk.CTkProgressBar(self, width=400)
        self.progreso.set(0)
        self.progreso.pack(pady=20)

        self.btn_turbo = ctk.CTkButton(
            self, text="Iniciar escalado", command=self.iniciar_hilo, 
            state="disabled", fg_color="gray", height=50, font=("Roboto", 16, "bold")
        )
        self.btn_turbo.pack(pady=20)

    def seleccionar_entrada(self):
        carpeta = filedialog.askdirectory()
        if carpeta:
            self.ruta_entrada = carpeta
            self.lbl_entrada.configure(text=carpeta, text_color="white")
            self.verificar_listo()

    def seleccionar_salida(self):
        carpeta = filedialog.askdirectory()
        if carpeta:
            self.ruta_salida = carpeta
            self.lbl_salida.configure(text=carpeta, text_color="white")
            self.verificar_listo()

    def verificar_listo(self):
        if self.ruta_entrada and self.ruta_salida:
            self.btn_turbo.configure(state="normal", fg_color="#1f6aa5")

    def iniciar_hilo(self):
        if not os.path.exists(self.exe_path):
            self.titulo.configure(text="Error: Falta el motor en bin")
            return
        hilo = threading.Thread(target=self.procesar_lote)
        hilo.start()

    def procesar_lote(self):
        archivos = os.listdir(self.ruta_entrada)
        extensiones = ('.jpg', '.jpeg', '.png', '.webp')
        fotos = [f for f in archivos if f.lower().endswith(extensiones)]
        
        if not fotos:
            self.titulo.configure(text="No hay imagenes en la carpeta")
            return

        self.btn_turbo.configure(state="disabled")
        total = len(fotos)
        
        for i, nombre_foto in enumerate(fotos):
            self.titulo.configure(text=f"Procesando {i+1} de {total}")
            self.progreso.set((i + 1) / total)

            ruta_in = os.path.join(self.ruta_entrada, nombre_foto)
            # Aseguramos que el nombre de salida sea correcto y no cause conflictos
            nombre_limpio = os.path.splitext(nombre_foto)[0]
            ruta_out = os.path.join(self.ruta_salida, f"{nombre_limpio}_4k.png")

            # Ejecutamos el motor desde su propia carpeta (cwd) para que encuentre los modelos
            comando = [self.exe_path, "-i", ruta_in, "-o", ruta_out, "-n", "realesrgan-x4plus"]

            try:
                # Capturamos la salida para ver errores en la terminal de VS Code
                resultado = subprocess.run(
                    comando, 
                    check=True, 
                    cwd=self.ruta_bin, 
                    capture_output=True, 
                    text=True
                )
            except subprocess.CalledProcessError as e:
                print(f"Error en {nombre_foto}:")
                print(e.stderr) # Esto nos dirá por qué falló la IA exactamente

        self.titulo.configure(text="Proceso finalizado")
        self.btn_turbo.configure(state="normal")

if __name__ == "__main__":
    app = LovaScalerApp()
    app.mainloop()