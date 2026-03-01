import customtkinter as ctk
from tkinter import filedialog
import subprocess
import threading
import os
import sys
import json
import time
import queue
from pathlib import Path
from typing import Optional, List, Tuple, Callable
from PIL import Image

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ToolTip:
    def __init__(self, elemento_ui: ctk.CTkBaseClass, texto_informativo: str) -> None:
        self.elemento_ui = elemento_ui
        self.texto_informativo = texto_informativo
        self.ventana_flotante: Optional[ctk.CTkToplevel] = None
        self.elemento_ui.bind("<Enter>", self.mostrar_tooltip)
        self.elemento_ui.bind("<Leave>", self.ocultar_tooltip)

    def mostrar_tooltip(self, event=None) -> None:
        posicion_x = self.elemento_ui.winfo_rootx() + 30
        posicion_y = self.elemento_ui.winfo_rooty() + 20
        self.ventana_flotante = ctk.CTkToplevel(self.elemento_ui)
        self.ventana_flotante.wm_overrideredirect(True)
        self.ventana_flotante.wm_geometry(f"+{posicion_x}+{posicion_y}")
        self.ventana_flotante.attributes("-topmost", True)
        etiqueta_texto = ctk.CTkLabel(self.ventana_flotante, text=self.texto_informativo, justify="left", fg_color="#2b2b2b", text_color="white", corner_radius=6, padx=10, pady=5)
        etiqueta_texto.pack()

    def ocultar_tooltip(self, event=None) -> None:
        if self.ventana_flotante:
            self.ventana_flotante.destroy()
            self.ventana_flotante = None

class MotorRealESRGAN:
    def __init__(self) -> None:
        if getattr(sys, 'frozen', False):
            self.directorio_base = Path(sys.executable).parent
        else:
            self.directorio_base = Path(__file__).resolve().parent.parent

        self.directorio_binarios = self.directorio_base / "bin"
        self.ruta_ejecutable = self.directorio_binarios / "realesrgan-ncnn-vulkan.exe"
        self.proceso_subyacente: Optional[subprocess.Popen] = None

    def verificar_existencia_ejecutable(self) -> bool:
        return self.ruta_ejecutable.exists()

    def procesar_archivo(self, ruta_origen: Path, ruta_destino: Path, tipo_procesamiento: str, callback_actualizacion: Callable[[float], None]) -> Tuple[bool, str]:
        identificador_modelo = "realesrgan-x4plus-anime" if "Anime" in tipo_procesamiento else "realesrgan-x4plus"
        argumentos_comando: List[str] = [str(self.ruta_ejecutable), "-i", str(ruta_origen), "-o", str(ruta_destino), "-n", identificador_modelo, "-s", "4", "-t", "256"]
        
        try:
            banderas_creacion = 0x08000000 if os.name == 'nt' else 0
            self.proceso_subyacente = subprocess.Popen(
                argumentos_comando, cwd=str(self.directorio_binarios),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                creationflags=banderas_creacion, bufsize=1, universal_newlines=True
            )
            
            if self.proceso_subyacente.stderr:
                for linea_salida in self.proceso_subyacente.stderr:
                    linea_limpia = linea_salida.strip()
                    if "%" in linea_limpia:
                        try:
                            valor_porcentaje = float(linea_limpia.replace("%", "").strip()) / 100.0
                            callback_actualizacion(valor_porcentaje)
                        except ValueError:
                            pass

            self.proceso_subyacente.wait() 
            if self.proceso_subyacente.returncode != 0:
                return False, "Proceso interrumpido o finalizado con errores."
            return True, "Operacion exitosa."
        except Exception as excepcion_capturada:
            return False, str(excepcion_capturada)
        finally:
            self.proceso_subyacente = None

    def detener_proceso(self) -> None:
        if self.proceso_subyacente:
            try:
                self.proceso_subyacente.terminate()
            except Exception:
                pass

class AplicacionLovaScaler(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("LovaScaler Pro")
        self.geometry("680x850")

        self.motor_ia = MotorRealESRGAN()
        self.directorio_origen: Optional[Path] = None
        self.directorio_destino: Optional[Path] = None
        self.operacion_cancelada: bool = False
        
        self.cola_eventos = queue.Queue()
        
        if getattr(sys, 'frozen', False):
            self.directorio_raiz = Path(sys.executable).parent
        else:
            self.directorio_raiz = Path(__file__).resolve().parent.parent
            
        self.ruta_archivo_configuracion = self.directorio_raiz / "config.json"

        self.etiqueta_titulo = ctk.CTkLabel(self, text="LovaScaler AI", font=("Roboto", 24, "bold"))
        self.etiqueta_titulo.pack(pady=(20, 10))

        self.contenedor_origen = ctk.CTkFrame(self)
        self.contenedor_origen.pack(pady=5, padx=20, fill="x")
        self.boton_seleccionar_origen = ctk.CTkButton(self.contenedor_origen, text="Carpeta origen", width=120, command=self.asignar_directorio_origen)
        self.boton_seleccionar_origen.pack(side="left", padx=10, pady=10)
        self.etiqueta_ruta_origen = ctk.CTkLabel(self.contenedor_origen, text="No seleccionado", text_color="gray")
        self.etiqueta_ruta_origen.pack(side="left", padx=10)
        self.boton_ayuda_origen = ctk.CTkButton(self.contenedor_origen, text="?", width=28, fg_color="#555555", hover_color="#777777")
        self.boton_ayuda_origen.pack(side="right", padx=10)
        ToolTip(self.boton_ayuda_origen, "Selecciona el directorio que contiene las imagenes a procesar.")

        self.contenedor_destino = ctk.CTkFrame(self)
        self.contenedor_destino.pack(pady=5, padx=20, fill="x")
        self.boton_seleccionar_destino = ctk.CTkButton(self.contenedor_destino, text="Carpeta destino", width=120, command=self.asignar_directorio_destino, fg_color="#2E8B57")
        self.boton_seleccionar_destino.pack(side="left", padx=10, pady=10)
        self.etiqueta_ruta_destino = ctk.CTkLabel(self.contenedor_destino, text="No seleccionado", text_color="gray")
        self.etiqueta_ruta_destino.pack(side="left", padx=10)
        self.boton_ayuda_destino = ctk.CTkButton(self.contenedor_destino, text="?", width=28, fg_color="#555555", hover_color="#777777")
        self.boton_ayuda_destino.pack(side="right", padx=10)
        ToolTip(self.boton_ayuda_destino, "Selecciona el directorio donde se guardaran los resultados.")

        self.contenedor_opciones = ctk.CTkFrame(self)
        self.contenedor_opciones.pack(pady=10, padx=20, fill="x")
        self.etiqueta_modelo = ctk.CTkLabel(self.contenedor_opciones, text="Tipo de imagen:", font=("Roboto", 12))
        self.etiqueta_modelo.pack(side="left", padx=(10, 5), pady=10)
        self.variable_seleccion_modelo = ctk.StringVar(value="Foto (General)")
        self.menu_desplegable_modelo = ctk.CTkOptionMenu(self.contenedor_opciones, values=["Foto (General)", "Anime / Ilustración"], variable=self.variable_seleccion_modelo, width=150, command=self.persistir_configuracion)
        self.menu_desplegable_modelo.pack(side="left", padx=5)
        self.boton_ayuda_modelo = ctk.CTkButton(self.contenedor_opciones, text="?", width=28, fg_color="#555555", hover_color="#777777")
        self.boton_ayuda_modelo.pack(side="left", padx=(10, 15))
        ToolTip(self.boton_ayuda_modelo, "ESCALADO NATIVO x4\n- Foto: Realismo y texturas.\n- Anime: Ilustraciones y dibujos 2D.")

        self.panel_previsualizacion = ctk.CTkLabel(self, text="Sin vista previa", fg_color="#2b2b2b", width=200, height=200, corner_radius=8)
        self.panel_previsualizacion.pack(pady=(10, 5))

        self.etiqueta_estado_operacion = ctk.CTkLabel(self, text="Sistema en espera", font=("Roboto", 14))
        self.etiqueta_estado_operacion.pack(pady=(5, 5))
        self.barra_progreso_general = ctk.CTkProgressBar(self, width=500)
        self.barra_progreso_general.set(0)
        self.barra_progreso_general.pack(pady=5)
        self.etiqueta_tiempo_estimado = ctk.CTkLabel(self, text="", text_color="gray", font=("Roboto", 12))
        self.etiqueta_tiempo_estimado.pack(pady=(0, 5))

        self.contenedor_controles = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor_controles.pack(pady=10)
        self.boton_iniciar_proceso = ctk.CTkButton(self.contenedor_controles, text="Iniciar proceso", command=self.desencadenar_procesamiento, state="disabled", fg_color="#1f6aa5", height=45, font=("Roboto", 16, "bold"))
        self.boton_iniciar_proceso.pack(side="left", padx=10)
        self.boton_accion_alternativa = ctk.CTkButton(self.contenedor_controles, text="Cancelar", command=self.ejecutar_accion_alternativa, state="disabled", fg_color="#cc0000", hover_color="#990000", height=45, font=("Roboto", 16, "bold"))
        self.boton_accion_alternativa.pack(side="left", padx=10)

        self.panel_registro_eventos = ctk.CTkTextbox(self, height=120, state="disabled", font=("Consolas", 12), fg_color="#1e1e1e")
        self.panel_registro_eventos.pack(pady=(10, 20), padx=20, fill="both", expand=True)
        
        self.recuperar_configuracion()
        self.registrar_evento("Sistema inicializado. Preferencias de usuario cargadas.")
        
        self.procesar_cola_eventos()

    def procesar_cola_eventos(self):
        try:
            while True:
                paquete_datos = self.cola_eventos.get_nowait()
                categoria_evento = paquete_datos.get("tipo")
                contenido_evento = paquete_datos.get("datos")

                if categoria_evento == "log":
                    self.panel_registro_eventos.configure(state="normal")
                    self.panel_registro_eventos.insert("end", contenido_evento + "\n")
                    self.panel_registro_eventos.see("end")
                    self.panel_registro_eventos.configure(state="disabled")
                elif categoria_evento == "progreso":
                    texto_estado, valor_progreso = contenido_evento
                    self.etiqueta_estado_operacion.configure(text=texto_estado)
                    self.barra_progreso_general.set(valor_progreso)
                elif categoria_evento == "eta":
                    self.etiqueta_tiempo_estimado.configure(text=contenido_evento)
                elif categoria_evento == "imagen":
                    imagen_renderizada = ctk.CTkImage(light_image=contenido_evento, dark_image=contenido_evento, size=contenido_evento.size)
                    self.panel_previsualizacion.configure(image=imagen_renderizada, text="")
                elif categoria_evento == "ui":
                    if contenido_evento == "completado":
                        self.boton_accion_alternativa.configure(state="normal", text="Abrir directorio", fg_color="#2E8B57", hover_color="#1f5e3d")
                    elif contenido_evento == "cancelado":
                        self.boton_accion_alternativa.configure(state="disabled")
                    self.boton_iniciar_proceso.configure(state="normal")
        except queue.Empty:
            pass
        finally:
            self.after(50, self.procesar_cola_eventos)

    def registrar_evento(self, mensaje_registro: str) -> None:
        self.cola_eventos.put({"tipo": "log", "datos": mensaje_registro})
        
    def emitir_actualizacion_progreso(self, mensaje_estado: str, indice_progreso: float) -> None:
        self.cola_eventos.put({"tipo": "progreso", "datos": (mensaje_estado, indice_progreso)})

    def recuperar_configuracion(self) -> None:
        if self.ruta_archivo_configuracion.exists():
            try:
                with open(self.ruta_archivo_configuracion, "r", encoding="utf-8") as archivo_json:
                    parametros_guardados = json.load(archivo_json)
                if "entrada" in parametros_guardados and os.path.exists(parametros_guardados["entrada"]):
                    self.directorio_origen = Path(parametros_guardados["entrada"])
                    self.etiqueta_ruta_origen.configure(text=self.directorio_origen.name, text_color="white")
                if "salida" in parametros_guardados and os.path.exists(parametros_guardados["salida"]):
                    self.directorio_destino = Path(parametros_guardados["salida"])
                    self.etiqueta_ruta_destino.configure(text=self.directorio_destino.name, text_color="white")
                if "modelo" in parametros_guardados:
                    self.variable_seleccion_modelo.set(parametros_guardados["modelo"])
                self.evaluar_estado_preparacion()
            except Exception as excepcion_lectura:
                self.registrar_evento(f"Error durante la lectura del archivo de configuracion: {excepcion_lectura}")

    def persistir_configuracion(self, *args) -> None:
        estructura_datos = {
            "entrada": str(self.directorio_origen) if self.directorio_origen else "",
            "salida": str(self.directorio_destino) if self.directorio_destino else "",
            "modelo": self.variable_seleccion_modelo.get()
        }
        try:
            with open(self.ruta_archivo_configuracion, "w", encoding="utf-8") as archivo_json:
                json.dump(estructura_datos, archivo_json, indent=4)
        except Exception:
            pass

    def resolver_colision_archivos(self, ruta_objetivo: Path) -> Path:
        if not ruta_objetivo.exists(): return ruta_objetivo
        indice_sufijo = 1
        while True:
            ruta_alternativa = ruta_objetivo.with_name(f"{ruta_objetivo.stem}_{indice_sufijo}{ruta_objetivo.suffix}")
            if not ruta_alternativa.exists(): return ruta_alternativa
            indice_sufijo += 1

    def asignar_directorio_origen(self) -> None:
        seleccion_directorio = filedialog.askdirectory()
        if seleccion_directorio:
            self.directorio_origen = Path(seleccion_directorio)
            self.etiqueta_ruta_origen.configure(text=self.directorio_origen.name, text_color="white")
            self.persistir_configuracion()
            self.evaluar_estado_preparacion()

    def asignar_directorio_destino(self) -> None:
        seleccion_directorio = filedialog.askdirectory()
        if seleccion_directorio:
            self.directorio_destino = Path(seleccion_directorio)
            self.etiqueta_ruta_destino.configure(text=self.directorio_destino.name, text_color="white")
            self.persistir_configuracion()
            self.evaluar_estado_preparacion()

    def evaluar_estado_preparacion(self) -> None:
        if self.directorio_origen and self.directorio_destino:
            self.boton_iniciar_proceso.configure(state="normal")
            
    def ejecutar_accion_alternativa(self) -> None:
        etiqueta_boton_actual = self.boton_accion_alternativa.cget("text")
        if etiqueta_boton_actual == "Cancelar":
            self.operacion_cancelada = True
            self.emitir_actualizacion_progreso("Interrumpiendo operacion, por favor espere...", self.barra_progreso_general.get())
            self.cola_eventos.put({"tipo": "eta", "datos": ""})
            self.boton_accion_alternativa.configure(state="disabled")
            self.registrar_evento("Senal de interrupcion enviada. Terminando subprocesos.")
            self.motor_ia.detener_proceso()
        elif etiqueta_boton_actual == "Abrir directorio":
            if self.directorio_destino and self.directorio_destino.exists():
                os.startfile(self.directorio_destino)

    def desencadenar_procesamiento(self) -> None:
        if not self.motor_ia.verificar_existencia_ejecutable():
            self.emitir_actualizacion_progreso("Error critico: Motor no detectado.", 0)
            self.registrar_evento("Error de dependencias: Archivo ejecutable no localizado en el directorio bin.")
            return
            
        self.operacion_cancelada = False
        self.cola_eventos.put({"tipo": "eta", "datos": "Calculando metricas iniciales..."})
        self.boton_iniciar_proceso.configure(state="disabled")
        self.boton_accion_alternativa.configure(state="normal", text="Cancelar", fg_color="#cc0000", hover_color="#990000")
        self.registrar_evento("Iniciando secuencia de escalado por lotes.")
        threading.Thread(target=self.ejecutar_lote_trabajo, daemon=True).start()

    def estructurar_cadena_tiempo(self, total_segundos: float) -> str:
        minutos = int(total_segundos // 60)
        segundos = int(total_segundos % 60)
        return f"{minutos}m {segundos}s" if minutos > 0 else f"{segundos}s"

    def ejecutar_lote_trabajo(self) -> None:
        if not self.directorio_origen or not self.directorio_destino: return
        formatos_soportados = {'.jpg', '.jpeg', '.png', '.webp'}
        coleccion_archivos = [archivo for archivo in self.directorio_origen.iterdir() if archivo.is_file() and archivo.suffix.lower() in formatos_soportados]
        
        if not coleccion_archivos:
            self.emitir_actualizacion_progreso("Directorio vacio o formatos no soportados.", 0)
            self.registrar_evento("Advertencia: No se detectaron imagenes procesables en la ubicacion de origen.")
            self.cola_eventos.put({"tipo": "ui", "datos": "cancelado"})
            self.cola_eventos.put({"tipo": "eta", "datos": ""})
            return

        cantidad_total = len(coleccion_archivos)
        configuracion_modelo = self.variable_seleccion_modelo.get() 
        promedio_tiempo_ejecucion = 0 
        
        for indice, ruta_archivo_actual in enumerate(coleccion_archivos):
            if self.operacion_cancelada: break
            
            marca_tiempo_inicio = time.time() 
            cadena_estado_proceso = f"Procesando elemento {indice+1}/{cantidad_total}: {ruta_archivo_actual.name}"
            self.registrar_evento(f"Aplicando filtro x4: {ruta_archivo_actual.name}")

            try:
                with Image.open(ruta_archivo_actual) as imagen_fuente:
                    imagen_memoria = imagen_fuente.copy()
                    imagen_memoria.thumbnail((200, 200)) 
                    self.cola_eventos.put({"tipo": "imagen", "datos": imagen_memoria})
            except Exception as error_renderizado:
                self.registrar_evento(f"Fallo al generar miniatura de interfaz: {error_renderizado}")

            ruta_salida_proyectada = self.directorio_destino / f"{ruta_archivo_actual.stem}_x4.png"
            ruta_salida_definitiva = self.resolver_colision_archivos(ruta_salida_proyectada)
            
            if ruta_salida_definitiva != ruta_salida_proyectada:
                self.registrar_evento(f"Resolucion de conflicto: Guardando como {ruta_salida_definitiva.name}")

            def notificar_fraccion_progreso(porcentaje_relativo: float):
                progreso_absoluto = (indice + porcentaje_relativo) / cantidad_total
                self.emitir_actualizacion_progreso(cadena_estado_proceso, progreso_absoluto)

            resultado_operacion, detalle_error = self.motor_ia.procesar_archivo(ruta_archivo_actual, ruta_salida_definitiva, configuracion_modelo, notificar_fraccion_progreso)

            if self.operacion_cancelada: break
            if not resultado_operacion:
                self.registrar_evento(f"Error de procesamiento en {ruta_archivo_actual.name}: {detalle_error[:50]}... Omitiendo archivo.")
                continue 
            else:
                self.registrar_evento(f"Completado exitosamente: {ruta_archivo_actual.name}")

            marca_tiempo_fin = time.time()
            duracion_ciclo = marca_tiempo_fin - marca_tiempo_inicio
            promedio_tiempo_ejecucion = duracion_ciclo if promedio_tiempo_ejecucion == 0 else (promedio_tiempo_ejecucion + duracion_ciclo) / 2
            elementos_pendientes = cantidad_total - (indice + 1)
            proyeccion_tiempo_restante = promedio_tiempo_ejecucion * elementos_pendientes
            
            if elementos_pendientes > 0:
                self.cola_eventos.put({"tipo": "eta", "datos": f"Tiempo estimado restante: {self.estructurar_cadena_tiempo(proyeccion_tiempo_restante)}"})

        if self.operacion_cancelada:
            self.emitir_actualizacion_progreso("Procesamiento abortado por el usuario.", 0)
            self.registrar_evento("Secuencia finalizada prematuramente.")
            self.cola_eventos.put({"tipo": "eta", "datos": ""})
            self.cola_eventos.put({"tipo": "ui", "datos": "cancelado"})
            self.cola_eventos.put({"tipo": "imagen", "datos": Image.new("RGB", (200, 200), (43, 43, 43))})
        else:
            self.emitir_actualizacion_progreso("Lote completado exitosamente.", 1.0)
            self.registrar_evento("Todas las operaciones han concluido sin errores fatales.")
            self.cola_eventos.put({"tipo": "eta", "datos": "Operacion concluida."})
            self.cola_eventos.put({"tipo": "ui", "datos": "completado"})

if __name__ == "__main__":
    aplicacion = AplicacionLovaScaler()
    aplicacion.mainloop()