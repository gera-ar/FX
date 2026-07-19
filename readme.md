# FX

Por [Gera Kessler](http://gera.ar)  
Refactorización del código (Gemini)

Este es un programa sencillo y liviano, diseñado para reproducir canciones y efectos de sonido en hasta 8 canales diferentes, con controles de volumen, paneo y desvanecimiento.  

Los archivos de audio deben colocarse en la carpeta **audios**.  
Los formatos compatibles son: **mp3, wav, flac y ogg**.

---

## Recomendaciones de uso

La forma más práctica de utilizar el programa es configurando la salida de sonido de Windows (incluyendo NVDA) por un lado, y la salida de este programa por otro.  
De esta manera, el usuario recibe la previsualización de los audios y las verbalizaciones de NVDA, mientras que la salida del programa se dirige al dispositivo externo.  

Se recomienda renombrar los archivos de audio en el orden de preferencia para facilitar su uso en la interfaz.

---

## Atajos de teclado

### Comandos que afectan solo al archivo de audio con el foco en la lista de la interfaz:

- **Barra espaciadora**: Inicia o detiene la reproducción.  
- **L**: Inicia la reproducción en bucle.  
- **E**: NVDA verbaliza el estado de reproducción, panorama y volumen actual.  
- **B**: Disminuye el volumen en un 10% (solo durante la reproducción).  
- **S**: Aumenta el volumen en un 10% (solo durante la reproducción).  
- **A**: Mueve el panorama a la izquierda en un 10% (solo durante la reproducción).  
- **D**: Mueve el panorama a la derecha en un 10% (solo durante la reproducción).  
- **C**: Mueve el panorama al centro (solo durante la reproducción).  
- **P**: Inicia o detiene la previsualización a través del dispositivo de audio predeterminado del sistema.
- **Números 1 a 4**: Realizan un desvanecimiento con distinta duración:  
  - 1 → 2 segundos  
  - 2 → 4 segundos  
  - 3 → 8 segundos  
  - 4 → 16 segundos  

### Atajos generales:

- **Flechas arriba/abajo**: Mueven el foco por la lista de archivos.  
- **R**: NVDA verbaliza el nombre de los archivos en reproducción activa.  
- **F5**: Recarga la lista de archivos desde la carpeta **audios**.  
- **Q**: Cierra el programa.

---

## Configuración de sonido

Al pulsar la tecla **O** en la interfaz, se abre un cuadro de diálogo con la lista de dispositivos de salida disponibles.  
Solo es necesario seleccionar el dispositivo deseado y pulsar **Aceptar**.  

Se recomienda asignar un dispositivo exclusivo para este programa, evitando que otros programas o el sistema operativo interfieran con la salida de audio.
