# FX

Por [Gera Kessler](http://gera.ar))

Este es un sencillo y pequeño programa desarrollado para disparar canciones y efectos de sonido hasta en 8 canales diferentes, con sus respectivos controles de volumen y desvanecimiento.
Los archivos de audio a utilizar se deben pegar en la carpeta audios, y los formatos soportados son: mp3, wav, flac y ogg.
La forma de uso recomendada es configurando la salida de sonido de Windows (incluyendo a NVDA) por un lado, y la salida de este programa por otro. De esta manera se obtiene una previsualización de los audios y las verbalizaciones del NVDA solo para el usuario, y la salida del programa hacia el dispositivo externo.

## Atajos de teclado

* Flechas arriba y abajo: Mueve el foco por la lista de canciones.
* Barra espaciadora: Inicia y detiene la reproducción de la canción con el foco.
* Letra l: Inicia la reproducción en loop de la canción con el foco.
* Letra e: Verbaliza a través de NVDA el estado de reproducción y el volumen.
* Letra b: Disminuye el volumen de la canción con el foco (solo en reproducción).
* Letra s: Aumenta el volumen de la canción con el foco (solo en reproducción).
* Números alfanuméricos del 1 al 4: Realizan un desvanecimiento del volumen con diferente duración: 1, 2 segundos; 2, 4 segundos; 3, 8 segundos; 4, 16 segundos.
* Letra p: Inicia y detiene la previsualización de la canción con el foco a través del dispositivo de audio predeterminado del sistema.
* Letra r: Verbaliza el nombre de las canciones que están en reproducción.
* F5: Recarga la lista de canciones obtenidas de la carpeta audios.
* Letra q: Cierra el programa.

## Configuración de sonido

Al pulsar la letra o en la interfaz, se activa un diálogo con una lista de dispositivos de salida a seleccionar. Solo hay que enfocar el deseado y pulsar en el botón Aceptar.
