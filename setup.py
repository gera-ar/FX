import wx
from pygame import mixer
import os

# Inicializar Pygame
mixer.init()

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
        for filename in os.listdir(folder):
            if filename.endswith('.mp3') or filename.endswith('.wav'):
                name, _ = os.path.splitext(filename)
                self.listbox.Append(name)
                self.audio_files.append(os.path.join(folder, filename))
                self.sounds.append(mixer.Sound(os.path.join(folder, filename)))

    def keyPress(self, event):
        sound_obj = self.sounds[self.listbox.GetSelection()]
        if event.GetKeyCode() == wx.WXK_SPACE:
            self.playStop(sound_obj)
        if event.GetKeyCode() in (wx.WXK_F1, wx.WXK_F2, wx.WXK_F3, wx.WXK_F4):
            self.fade(event.GetKeyCode(), sound_obj)
        else:
            event.Skip()  # Permite que la tecla continúe su acción
    
    def playStop(self, sound_obj):
        channel_obj = next((ch for ch in self.channels if ch.get_sound() == sound_obj), None)
        if not self.channels or not channel_obj:
            channel = mixer.find_channel()
            channel.play(sound_obj)
            channel.set_volume(1.0)
            self.channels.append(channel)
        elif channel_obj.get_busy():
            channel_obj.stop()
            self.channels.remove(channel_obj)

    def fade(self, key, sound_obj):
        durations = {340: 2000, 341: 4000, 342: 8000, 343: 12000}
        channel_obj = next((ch for ch in self.channels if ch.get_sound() == sound_obj), None)
        if channel_obj and channel_obj.get_busy():
            channel_obj.fadeout(durations[key])
            self.channels.remove(channel_obj)

    def close(self, event=None):
        mixer.quit()
        self.Destroy()

if __name__ == '__main__':
    app = MyApp()
    app.MainLoop()