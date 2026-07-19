import os
import sounddevice as sd
import soundfile as sf
import numpy as np
from .nvda_utils import speak

class ActiveStream:
    """Representa una reproducción de audio activa utilizando sounddevice."""
    def __init__(self, sound_name, data, fs, device=None, loops=0, volume=1.0, pan=0.0):
        self.sound_name = sound_name
        self.data = data
        self.fs = fs
        self.device = device
        self.loops = loops
        self.volume = volume
        self.pan = pan
        
        self.current_frame = 0
        self.fade_out_frames = 0
        self.fade_out_total_frames = 0
        self.is_fading = False
        self.active = True
        
        # Abrimos el stream de salida
        self.stream = sd.OutputStream(
            samplerate=self.fs,
            channels=2,
            callback=self.callback,
            finished_callback=self.finished,
            device=self.device
        )
        self.stream.start()

    def callback(self, outdata, frames, time, status):
        if not self.active:
            outdata.fill(0)
            return

        written = 0
        while written < frames:
            frames_left = len(self.data) - self.current_frame
            
            if frames_left <= 0:
                if self.loops == -1:
                    self.current_frame = 0
                    frames_left = len(self.data)
                else:
                    outdata[written:].fill(0)
                    raise sd.CallbackStop()
            
            to_write = min(frames - written, frames_left)
            chunk = self.data[self.current_frame : self.current_frame + to_write]
            
            # Aplicar volumen y panorama
            left_gain = min(1.0, 1.0 - self.pan)
            right_gain = min(1.0, 1.0 + self.pan)
            
            processed = chunk * self.volume
            processed[:, 0] *= left_gain
            processed[:, 1] *= right_gain
            
            if self.is_fading:
                # Desvanecimiento vectorial
                start_factor = self.fade_out_frames / self.fade_out_total_frames
                step = 1.0 / self.fade_out_total_frames
                factors = start_factor - np.arange(to_write) * step
                factors = np.maximum(0.0, factors)
                processed *= factors[:, np.newaxis]
                
                self.fade_out_frames -= to_write
                if self.fade_out_frames <= 0:
                    self.fade_out_frames = 0
                    outdata[written : written + to_write] = processed
                    outdata[written + to_write :].fill(0)
                    raise sd.CallbackStop()
            
            outdata[written : written + to_write] = processed
            self.current_frame += to_write
            written += to_write

    def finished(self):
        self.active = False

    def set_volume(self, volume):
        self.volume = volume

    def set_pan(self, pan):
        self.pan = pan

    def fade(self, duration_ms):
        total_fade_frames = int((duration_ms / 1000.0) * self.fs)
        self.fade_out_total_frames = total_fade_frames
        self.fade_out_frames = total_fade_frames
        self.is_fading = True

    def stop(self):
        self.active = False
        if self.stream.active:
            try:
                self.stream.stop()
            except Exception:
                pass
        try:
            self.stream.close()
        except Exception:
            pass


class AudioManager:
    """Gestiona toda la lógica de reproducción y control de audio."""
    def __init__(self, audio_folder='audios'):
        self.audio_folder = audio_folder
        self.sounds = {}
        self.audio_files = {}
        self.channels = []
        self.playing = []
        self.handle = None
        
        # Mapeo de dispositivos de salida de sounddevice
        self.device_map = {}
        self.devices = []
        self.current_device_name = None
        self.current_device_id = None
        self.refresh_devices()

        self.volumes = {
            0.0: 'silencio', 0.1: '10 porciento', 0.2: '20 porciento',
            0.3: '30 porciento', 0.4: '40 porciento', 0.5: '50 porciento',
            0.6: '60 porciento', 0.7: '70 porciento', 0.8: '80 porciento',
            0.9: '90 porciento', 1.0: 'máximo'
        }
        
        # Registros de volumen y panorama por sonido
        self.vols = {}
        self.pans = {}
        
        self.load_audio_files()

    def refresh_devices(self):
        """Refresca la lista de dispositivos de audio de salida de sounddevice."""
        self.device_map.clear()
        self.devices.clear()
        try:
            for idx, d in enumerate(sd.query_devices()):
                if d['max_output_channels'] > 0:
                    host_name = sd.query_hostapis(d['hostapi'])['name']
                    desc = f"{d['name']} ({host_name})"
                    self.device_map[desc] = idx
            self.devices = list(self.device_map.keys())
        except Exception as e:
            print(f"Error querying devices: {e}")
            self.devices = []

    def load_audio_files(self):
        """Carga o recarga los archivos de audio desde la carpeta especificada."""
        if not os.path.exists(self.audio_folder):
            os.makedirs(self.audio_folder, exist_ok=True)

        self.sounds.clear()
        self.audio_files.clear()

        audio_file_names = []
        for filename in sorted(os.listdir(self.audio_folder)):
            if filename.lower().endswith(('.mp3', '.wav', '.flac', '.ogg')):
                name, _ = os.path.splitext(filename)
                filepath = os.path.join(self.audio_folder, filename)
                self.audio_files[name] = filepath
                
                try:
                    data, fs = sf.read(filepath, dtype='float32')
                    if data.ndim == 1:
                        data = np.column_stack((data, data))
                    elif data.ndim > 2:
                        data = data[:, :2]
                    self.sounds[name] = (data, fs)
                    audio_file_names.append(name)
                    
                    # Inicializar volumen y panorama por defecto
                    if name not in self.vols:
                        self.vols[name] = 1.0
                    if name not in self.pans:
                        self.pans[name] = 0.0
                except Exception as e:
                    print(f"Error loading sound {filepath}: {e}")
                    
        return audio_file_names

    def get_sound_obj(self, name):
        """Obtiene la tupla de datos de sonido (para compatibilidad)."""
        return self.sounds.get(name)

    def clean_inactive_channels(self):
        """Limpia los canales que han terminado de reproducir."""
        inactive_streams = []
        for stream_obj in self.channels:
            if not stream_obj.active:
                try:
                    stream_obj.stream.close()
                except Exception:
                    pass
                
                # Resetear panorama al centro al finalizar el audio
                self.pans[stream_obj.sound_name] = 0.0
                
                if stream_obj.sound_name in self.playing:
                    self.playing.remove(stream_obj.sound_name)
                inactive_streams.append(stream_obj)
                
        for stream_obj in inactive_streams:
            self.channels.remove(stream_obj)

        # También limpiar la preview (handle) si terminó
        if self.handle and not self.handle.active:
            try:
                self.handle.stream.close()
            except Exception:
                pass
            self.handle = None

    def play_stop(self, sound_name, flag):
        """Inicia o detiene la reproducción de un sonido."""
        sound_data = self.sounds.get(sound_name)
        if not sound_data:
            return

        data, fs = sound_data
        stream_obj = next((st for st in self.channels if st.sound_name == sound_name), None)

        if stream_obj and stream_obj.active:
            stream_obj.stop()
            self.pans[sound_name] = 0.0
            if sound_name in self.playing:
                self.playing.remove(sound_name)
            self.channels.remove(stream_obj)
            speak('Audio detenido')
        else:
            volume = self.vols.setdefault(sound_name, 1.0)
            pan = self.pans.setdefault(sound_name, 0.0)

            try:
                new_stream = ActiveStream(
                    sound_name=sound_name,
                    data=data,
                    fs=fs,
                    device=self.current_device_id,
                    loops=flag,
                    volume=volume,
                    pan=pan
                )
                self.channels.append(new_stream)
                if sound_name not in self.playing:
                    self.playing.append(sound_name)
                speak("Reproducción en loop" if flag == -1 else "Reproduciendo")
            except Exception as e:
                speak("Error al iniciar reproducción")
                print(f"Error starting stream: {e}")

    def fade(self, sound_name, key):
        """Aplica un desvanecimiento al sonido."""
        durations = {49: 2000, 50: 4000, 51: 8000, 52: 12000}
        stream_obj = next((st for st in self.channels if st.sound_name == sound_name), None)
        if stream_obj and stream_obj.active:
            stream_obj.fade(durations[key])
            speak('Desvanecimiento')

    def status(self, sound_name):
        """Informa el estado de un sonido, incluyendo volumen y panorama."""
        stream_obj = next((st for st in self.channels if st.sound_name == sound_name), None)
        if stream_obj and stream_obj.active:
            current = round(stream_obj.volume, 1)
            vol_str = self.volumes.get(current, "desconocido")
            
            pan_val = self.pans.get(sound_name, 0.0)
            if pan_val == 0.0:
                pan_str = "centro"
            elif pan_val < 0.0:
                pan_str = f"{round(abs(pan_val) * 100)} porciento izquierda"
            else:
                pan_str = f"{round(abs(pan_val) * 100)} porciento derecha"
                
            msg = f'En reproducción, volúmen {vol_str}, panorama {pan_str}'
            speak(msg)
        else:
            speak("Sin reproducción")

    def volume_up(self, sound_name):
        """Sube el volumen de un sonido."""
        stream_obj = next((st for st in self.channels if st.sound_name == sound_name), None)
        if stream_obj and stream_obj.active:
            if stream_obj.volume < 1.0:
                volume = round(stream_obj.volume + 0.1, 1)
                stream_obj.set_volume(volume)
                self.vols[sound_name] = volume
                speak(self.volumes[volume])
            else:
                speak("Volúmen máximo")
        else:
            speak("Sin reproducción")

    def volume_down(self, sound_name):
        """Baja el volumen de un sonido."""
        stream_obj = next((st for st in self.channels if st.sound_name == sound_name), None)
        if stream_obj and stream_obj.active:
            if stream_obj.volume > 0.1:
                volume = round(stream_obj.volume - 0.1, 1)
                stream_obj.set_volume(volume)
                self.vols[sound_name] = volume
                speak(self.volumes[volume])
            else:
                speak("Volúmen mínimo")
        else:
            speak("Sin reproducción")

    def pan_left(self, sound_name):
        """Mueve el panorama del sonido a la izquierda."""
        stream_obj = next((st for st in self.channels if st.sound_name == sound_name), None)
        if stream_obj and stream_obj.active:
            self.pans[sound_name] = round(max(-1.0, self.pans[sound_name] - 0.1), 1)
            stream_obj.set_pan(self.pans[sound_name])
            
            val = self.pans[sound_name]
            if val == 0.0:
                speak("centro")
            else:
                pct = round(abs(val) * 100)
                speak(f"{pct} porciento izquierda")
        else:
            speak("Sin reproducción")

    def pan_right(self, sound_name):
        """Mueve el panorama del sonido a la derecha."""
        stream_obj = next((st for st in self.channels if st.sound_name == sound_name), None)
        if stream_obj and stream_obj.active:
            self.pans[sound_name] = round(min(1.0, self.pans[sound_name] + 0.1), 1)
            stream_obj.set_pan(self.pans[sound_name])
            
            val = self.pans[sound_name]
            if val == 0.0:
                speak("centro")
            else:
                pct = round(abs(val) * 100)
                speak(f"{pct} porciento derecha")
        else:
            speak("Sin reproducción")

    def pan_center(self, sound_name):
        """Centra el panorama del sonido."""
        stream_obj = next((st for st in self.channels if st.sound_name == sound_name), None)
        if stream_obj and stream_obj.active:
            self.pans[sound_name] = 0.0
            stream_obj.set_pan(0.0)
            speak("centro")
        else:
            speak("Sin reproducción")

    def preview(self, sound_name):
        """Activa o desactiva el modo de previsualización."""
        sound_data = self.sounds.get(sound_name)
        if not sound_data:
            return

        data, fs = sound_data

        if not self.handle:
            try:
                self.handle = ActiveStream(
                    sound_name=sound_name,
                    data=data,
                    fs=fs,
                    device=self.current_device_id,
                    loops=0,
                    volume=1.0,
                    pan=0.0
                )
                speak('Preview activada')
            except Exception as e:
                speak("Error al iniciar preview")
                print(f"Error starting preview: {e}")
        else:
            self.handle.stop()
            self.handle = None
            speak('Preview desactivada')
            
    def get_playing_sounds(self):
        """Devuelve una cadena con los sonidos en reproducción."""
        return ", ".join(self.playing) if self.playing else 'Sin reproducciones activas'

    def set_device(self, device_name):
        """Establece el dispositivo de audio de salida."""
        self.current_device_name = device_name
        self.current_device_id = self.device_map.get(device_name)
        speak(f'Dispositivo configurado: {device_name}')

    def quit(self):
        """Detiene el motor de audio."""
        if self.handle:
            self.handle.stop()
            self.handle = None
        for stream_obj in self.channels:
            stream_obj.stop()
        self.channels.clear()
