import wx
from pygame import mixer
import pygame._sdl2.audio as sdl2_audio
import os
import ctypes
from threading import Thread
import sound_lib
from sound_lib import output
from sound_lib import stream

# constantes
nvda = ctypes.WinDLL('_internal/nvda64.dll')
o = output.Output()

def speak(string):
	wstr= ctypes.c_wchar_p(string)
	nvda.nvdaController_speakText(wstr)

# Inicializar Pygame
mixer.init()
devices= sdl2_audio.get_audio_device_names()

class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame()
        self.frame.Show()
        return True

class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Lista de Reproducción')
        self.panel = wx.Panel(self)
        
        # Crear ListBox
        self.listbox = wx.ListBox(self.panel)
        
        self.channels = []
        self.audio_files = []
        self.sounds = []
        self.playing = []
        self.handle = None
        self.volumes = {
            0.0: 'silencio',
            0.1: '10 porciento',
            0.2: '20 porciento',
            0.3: '30 porciento',
            0.4: '40 porciento',
            0.5: '50 porciento',
            0.6: '60 porciento',
            0.7: '70 porciento',
            0.8: '80 porciento',
            0.9: '90 porciento',
            1.0: 'máximo'
        }
        self.load_audio_files('audios')
        
        # Añadir ListBox a la ventana
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.listbox, 1, wx.EXPAND | wx.ALL, 10)
        self.panel.SetSizer(sizer)
        
        # Establecer foco en el primer elemento
        if self.listbox.GetCount() > 0:
            self.listbox.SetSelection(0)
        
        # Bind de teclas
        self.listbox.Bind(wx.EVT_KEY_DOWN, self.keyPress)
        
        # Bind de cierre
        self.Bind(wx.EVT_CLOSE, self.close)

    def load_audio_files(self, folder):
        if not os.path.exists('audios'):
            os.makedirs('audios', exist_ok= True)
        
        self.listbox.Clear()
        self.sounds.clear()
        self.audio_files.clear()
        
        for filename in os.listdir(folder):
            if filename.endswith('.mp3') or filename.endswith('.wav'):
                name, _ = os.path.splitext(filename)
                self.listbox.Append(name)
                self.audio_files.append(os.path.join(folder, filename))
                self.sounds.append(mixer.Sound(os.path.join(folder, filename)))

    def keyPress(self, event):
        sound_obj = self.sounds[self.listbox.GetSelection()]
        if event.GetKeyCode() == wx.WXK_SPACE or event.GetKeyCode() == 76:
            flag = -1 if event.GetKeyCode() == 76 else 0
            self.playStop(sound_obj, self.listbox.GetStringSelection(), flag)
        if event.GetKeyCode() in (49, 50, 51, 52):
            self.fade(event.GetKeyCode(), sound_obj)
        elif event.GetKeyCode() == wx.WXK_F5:
            speak('Refrescando el contenido')
            self.load_audio_files('audios')
        elif event.GetKeyCode() == 69:    # letra e
            self.status(sound_obj)
        elif event.GetKeyCode() == 66:    # letra b
            self.volumeDown(sound_obj)
        elif event.GetKeyCode() == 83:    # letra s
            self.volumeUp(sound_obj)
        elif event.GetKeyCode() == 79:    # letra o
            AudioDevice().Show()
        elif event.GetKeyCode() == 80:    # letra p
            self.preview(self.listbox.GetSelection())
        elif event.GetKeyCode() == 81:    # letra q
            self.close()
        elif event.GetKeyCode() == 82:    # letra r
            string = ", ".join(self.playing) if self.playing else 'Sin reproducciones activas'
            speak(string)
        else:
            event.Skip()
    
    def thread(self, channel, file_name):
        self.playing.append(file_name)
        while True:
            if not channel.get_busy():
                try:
                    self.playing.remove(file_name)
                    self.channels.remove(channel)
                except ValueError:
                    pass
                break
    
    def playStop(self, sound_obj, file_name, flag):
        channel_obj = next((ch for ch in self.channels if ch.get_sound() == sound_obj), None)
        if not self.channels or not channel_obj:
            channel = mixer.find_channel()
            channel.play(sound_obj, loops=flag)
            if flag == -1:
                speak("Reproducción en loop")
            else:
                speak('Reproduciendo')
            channel.set_volume(1.0)
            self.channels.append(channel)
            Thread(target=self.thread, args=(channel, file_name), daemon=True).start()
        elif channel_obj.get_busy():
            channel_obj.stop()
            speak('Audio detenido')

    def fade(self, key, sound_obj):
        durations = {49: 2000, 50: 4000, 51: 8000, 52: 12000}
        durations = {49: 2000, 50: 4000, 51: 8000, 52: 12000}
        channel_obj = next((ch for ch in self.channels if ch.get_sound() == sound_obj), None)
        if channel_obj and channel_obj.get_busy():
            channel_obj.fadeout(durations[key])
            self.channels.remove(channel_obj)
            speak('Desvanecimiento')
    
    def status(self, sound_obj):
        channel_obj = next((ch for ch in self.channels if ch.get_sound() == sound_obj), None)
        if channel_obj:
            current = round(channel_obj.get_volume(), 1)
            msg = f'En reproducción, volúmen {self.volumes[current]}'
            speak(msg)
        else:
            speak("Sin reproducción")
    
    def volumeUp(self, sound_obj):
        channel_obj = next((ch for ch in self.channels if ch.get_sound() == sound_obj), None)
        if channel_obj and channel_obj.get_volume():
            if channel_obj.get_volume() < 1.0:
                volume = round(channel_obj.get_volume() + 0.1, 1)
                channel_obj.set_volume(volume)
                speak(self.volumes[volume])
            else:
                speak("Volúmen máximo")
        else:
            speak("Sin reproducción")
    
    def volumeDown(self, sound_obj):
        channel_obj = next((ch for ch in self.channels if ch.get_sound() == sound_obj), None)
        if channel_obj and channel_obj.get_volume():
            if channel_obj.get_volume() > 0.1:
                volume = round(channel_obj.get_volume() - 0.1, 1)
                channel_obj.set_volume(volume)
                speak(self.volumes[volume])
            else:
                speak("Volúmen mínimo")
        else:
            speak("Sin reproducción")
    
    def preview(self, selection):
        if not self.handle:
            self.handle = stream.FileStream(file=self.audio_files[selection])
            self.handle.play()
            speak('Preview activada')
        else:
            self.handle.stop()
            self.handle = None
            speak('Preview desactivada')
    
    def close(self, event=None):
        dialog = wx.MessageDialog(self, "¿Seguro que quieres salir?", "¡Atención!", wx.YES_NO | wx.ICON_QUESTION)
        result = dialog.ShowModal()
        if result == wx.ID_YES:
            mixer.quit()
            self.Destroy()
        dialog.Destroy()

class AudioDevice(wx.Dialog):
    def __init__(self):
        super().__init__(parent=None, title='Configuración de audio')
        panel = wx.Panel(self)
        
        static_text = wx.StaticText(panel, label="Selecciona el dispositivo de audio:")
        static_text.Wrap(-1)
        
        self.listbox = wx.ListBox(panel, choices=devices, style=wx.LB_SINGLE)
        
        save_button = wx.Button(panel, label='&Aceptar')
        save_button.Bind(wx.EVT_BUTTON, self.onSave)
        cancel_button = wx.Button(panel, label='&Cancelar')
        cancel_button.Bind(wx.EVT_BUTTON, self.onClose)
    
    def onSave(self, event):
        selected_device= self.listbox.GetStringSelection()
        mixer.quit()
        mixer.init(devicename=selected_device)
        speak('Dispositivo configurado: {}'.format(selected_device))
        self.Destroy()
    
    def onClose(self, event):
        self.Destroy()

if __name__ == '__main__':
    app = MyApp()
    app.MainLoop()