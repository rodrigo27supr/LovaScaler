# LovaScaler

LovaScaler es una aplicación de escritorio para Windows dedicada al escalado de imágenes mediante inteligencia artificial utilizando el motor Real-ESRGAN. 
El proyecto se encuentra en fase de desarrollo.

## Estado actual del proyecto

La aplicación ha alcanzado su versión funcional. Actualmente es capaz de procesar muchas imágenes de forma automatizada sin bloquear la interfaz de usuario.

### Funcionalidades implementadas:
- Interfaz gráfica construida con CustomTkinter.
- Sistema de procesamiento en segundo plano mediante hilos para mantener la fluidez.
- Procesamiento por lotes, detección y escalado automático de todas las imágenes en una carpeta destino.
- Barra de progreso en tiempo real para el seguimiento de tareas.
- Integración directa con el motor Real-ESRGAN.

## Requisitos técnicos

Para que el programa funcione correctamente en un entorno local, es necesario contar con:
- Python 3.10 o superior.
- Librerías: customtkinter, pillow.
- El ejecutable `realesrgan-ncnn-vulkan.exe` y su carpeta de modelos deben estar presentes en el directorio `bin`.

## Estructura de archivos

- `src/main.py`: Código fuente principal de la aplicación.
- `bin/`: Directorio para los archivos pesados.



