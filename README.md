# LovaScaler Pro v2.0

LovaScaler Pro es un programa para Windows que utiliza inteligencia artificial (Real-ESRGAN) para ampliar tus imágenes hasta 4 veces su tamaño original sin que se vean pixeladas ni pierdan nitidez.

## Lo nuevo en esta versión

Hemos mejorado el programa para que sea más estable y cómodo de usar:

* **Sin bloqueos**: El motor de la IA ahora trabaja de forma independiente a la ventana, por lo que puedes mover la aplicación o interactuar con ella mientras trabaja sin que se quede congelada.
* **Vista previa en vivo**: El programa muestra una miniatura de la imagen que está procesando en cada momento para que sepas exactamente por dónde va el trabajo.
* **Barra de progreso**: Se ha añadido una barra que avanza en tiempo real según se completan las tareas de la lista.
* **Memoria de carpetas**: La aplicación recuerda las últimas rutas que utilizaste, evitándote tener que buscarlas cada vez que abras el programa.

## Qué puedes hacer con el programa

* **Interfaz sencilla**: Un diseño moderno en modo oscuro que facilita el uso de la herramienta.
* **Procesamiento automático**: Selecciona una carpeta completa y el programa escalará todas las imágenes que encuentre de forma seguida.
* **Seguridad de archivos**: Si en el destino ya existe una foto con el mismo nombre, el programa le añade un número al final automáticamente para no borrar tus fotos por error.
* **Modos de IA**: Incluye un modo específico para fotos reales y otro optimizado para dibujos o anime.

## Cómo usarlo

### Si usas el ejecutable (.exe)
Para que el programa funcione, la carpeta de descarga debe mantener este orden:
* `LovaScaler.exe`: El programa que debes ejecutar.
* `bin/`: Carpeta que contiene el motor de la IA y los modelos necesarios.

### Si eres desarrollador
Para lanzarlo desde el código fuente, necesitas:
* **Python 3.10** o superior.
* Instalar las librerías `customtkinter` y `Pillow`.
* Tener los archivos de Real-ESRGAN dentro de la carpeta `bin`.

## Organización del proyecto

* `src/`: Contiene el código fuente principal.
* `logo/`: Iconos y recursos visuales de la aplicación.
* `logoScaler.ico`: Icono oficial del programa.
