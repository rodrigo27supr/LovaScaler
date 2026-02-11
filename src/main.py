import customtkinter as ctk  
import os  


ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")

class LovaScalerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("LovaScaler - v0.1")
        self.geometry("600x400") 
      
        self.titulo = ctk.CTkLabel(
            self, 
            text="LovaScaler está listo.", 
            font=("Roboto", 24) 
        )
        self.titulo.pack(pady=20) 

        self.boton = ctk.CTkButton(
            self, 
            text="Probar Sistema", 
            command=self.saludar 
        )
        self.boton.pack(pady=20)

    def saludar(self):
        print("Todo funciona correctamente") 
        self.titulo.configure(text="Iniciado con éxito") 

if __name__ == "__main__":
    app = LovaScalerApp() 
    app.mainloop() 