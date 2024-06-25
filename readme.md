# FX

Por [Gera Kessler](http://gera.ar))

Este pequeño programa fue pensado para cubrir una necesidad concreta, y sus funciones están basadas en ello.
La idea es poder disparar sonidos (fondos musicales o efectos) en obras de teatro o eventos que requieran de sonidos en simultáneo.
A través de unos pocos atajos de teclado se puede seleccionar el dispositivo de audio de reproducción, reproducir música de fondo, disparar efectos, modificar el volumen, modificar el canal izquierdo o derecho de los efectos, reproducir fondos en loop, y algunas cositas más.

## Uso

Lo más importante antes de iniciar el programa, es pegar dentro de las correspondientes carpetas los archivos de audio a utilizar. Los formatos soportados son:

* mp3
* flac
* ogg
* wav

El programa tiene tan solo 2 listas entre las cuales podemos movernos con tabulador.
En ellas se encuentra la lista de los archivos de cada directorio, los cuales pueden recorrerse con flechas arriba y abajo.

### Atajos de teclado

* Barra espaciadora; inicia la reproducción del archivo seleccionado en la lista
* p; inicia y detiene la previsualización del archivo seleccionado (reproduce a través del dispositivo por defecto en Windows)
* 1; inicia la reproducción del archivo en loop (solo lista fondos)
* q; aumenta el volumen del fondo
* z; disminuye el volumen del fondo
* a; detiene la reproducción del fondo con fadeout corto
* s; detiene la reproducción del fondo con fadeout largo
* r; verbaliza el tiempo restante del fondo (Solo NVDA)
* flecha derecha; reproduce los efectos solo por el canal derecho
* flecha izquierda; reproduce los efectos solo por el canal izquierdo
* c; reproduce los efectos por ambos canales

## Configuración de sonido

Generalmente es necesario contar con 2 dispositivos diferentes en la pc para poder dividir el sonido del sistema junto al lector de pantallas, y el sonido de reproducción del programa para evitar accidentes.
De esta manera al previsualizar un archivo lo hará a través de la configuración por defecto del sistema, y no por la salida del programa.

### Configurar salida del sistema

En Windows podemos seleccionar la salida fácilmente abriendo el menú ejecutar con Windows + r, y escribiendo

    mmsys.cpl

Al pulsar intro tendremos la lista de dispositivos de salida. Al pulsar alt + p sobre el deseado, este quedará marcado como predeterminado.

### Configurar salida de NVDA

En las nuevas versiones del lector de pantallas, el atajo por defecto NVDA + control + u permite seleccionar la salida.

### Configuración de salida principal del programa

Al pulsar la letra o, se abre una interfaz con la lista de dispositivos disponibles.
Seleccionamos la deseada en la lista y pulsamos en aceptar. O cancelar para salir sin guardar cambios.

Nota:  
Si con el programa abierto se realizan modificaciones en las carpetas fondos y efectos, estos no se verán reflejados automáticamente. Para ello puede pulsarse f5, que refresca las listas.

Para salir del programa; alt + f4.
