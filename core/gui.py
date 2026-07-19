import wx
from .audio import AudioManager
from .nvda_utils import speak

class MyFrame(wx.Frame):
    """Ventana principal de la aplicación."""
    def __init__(self):
        super().__init__(parent=None, title='Lista de Reproducción')
        self.audio_manager = AudioManager()
        
        self.panel = wx.Panel(self)
        self.listbox = wx.ListBox(self.panel, choices=self.audio_manager.load_audio_files())
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.listbox, 1, wx.EXPAND | wx.ALL, 10)
        self.panel.SetSizer(sizer)
        
        if self.listbox.GetCount() > 0:
            self.listbox.SetSelection(0)
        
        self.listbox.Bind(wx.EVT_KEY_DOWN, self.on_key_press)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(500)

    def on_timer(self, event):
        """Evento de temporizador para limpiar canales de audio inactivos."""
        self.audio_manager.clean_inactive_channels()

    def refresh_audio_list(self):
        """Refresca la lista de archivos de audio en la interfaz."""
        speak('Refrescando el contenido')
        audio_files = self.audio_manager.load_audio_files()
        self.listbox.Set(audio_files)
        if self.listbox.GetCount() > 0:
            self.listbox.SetSelection(0)

    def on_key_press(self, event):
        """Maneja los eventos de teclado en la lista de audios."""
        selection = self.listbox.GetSelection()
        if selection == wx.NOT_FOUND:
            event.Skip()
            return
            
        sound_name = self.listbox.GetStringSelection()
        keycode = event.GetKeyCode()

        key_actions = {
            wx.WXK_SPACE: lambda: self.audio_manager.play_stop(sound_name, 0),
            76: lambda: self.audio_manager.play_stop(sound_name, -1),  # L
            49: lambda: self.audio_manager.fade(sound_name, keycode),  # 1
            50: lambda: self.audio_manager.fade(sound_name, keycode),  # 2
            51: lambda: self.audio_manager.fade(sound_name, keycode),  # 3
            52: lambda: self.audio_manager.fade(sound_name, keycode),  # 4
            wx.WXK_F5: self.refresh_audio_list,
            69: lambda: self.audio_manager.status(sound_name),      # E
            66: lambda: self.audio_manager.volume_down(sound_name),  # B
            83: lambda: self.audio_manager.volume_up(sound_name),    # S
            65: lambda: self.audio_manager.pan_left(sound_name),     # A
            68: lambda: self.audio_manager.pan_right(sound_name),    # D
            67: lambda: self.audio_manager.pan_center(sound_name),   # C
            79: self.show_audio_device_dialog,                      # O
            80: lambda: self.audio_manager.preview(sound_name),      # P
            81: self.Close,                                          # Q
            82: lambda: speak(self.audio_manager.get_playing_sounds()) # R
        }

        action = key_actions.get(keycode)
        if action:
            action()
        else:
            event.Skip()

    def show_audio_device_dialog(self):
        """Muestra el diálogo para cambiar el dispositivo de audio."""
        with AudioDevice(self, self.audio_manager) as dialog:
            dialog.ShowModal()

    def on_close(self, event):
        """Maneja el evento de cierre de la ventana."""
        with wx.MessageDialog(self, "¿Seguro que quieres salir?", "¡Atención!", wx.YES_NO | wx.ICON_QUESTION) as dialog:
            if dialog.ShowModal() == wx.ID_YES:
                self.audio_manager.quit()
                self.timer.Stop()
                self.Destroy()

class AudioDevice(wx.Dialog):
    """Diálogo para seleccionar el dispositivo de audio."""
    def __init__(self, parent, audio_manager):
        super().__init__(parent=parent, title='Configuración de audio')
        self.audio_manager = audio_manager
        
        panel = wx.Panel(self)
        
        static_text = wx.StaticText(panel, label="Selecciona el dispositivo de audio:")
        self.listbox = wx.ListBox(panel, choices=self.audio_manager.devices, style=wx.LB_SINGLE)
        
        save_button = wx.Button(panel, label='&Aceptar', id=wx.ID_OK)
        save_button.Bind(wx.EVT_BUTTON, self.on_save)
        cancel_button = wx.Button(panel, label='&Cancelar', id=wx.ID_CANCEL)
        
        save_button.SetDefault()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(static_text, 0, wx.ALL, 10)
        sizer.Add(self.listbox, 1, wx.EXPAND | wx.ALL, 10)
        
        btn_sizer = wx.StdDialogButtonSizer()
        btn_sizer.AddButton(save_button)
        btn_sizer.AddButton(cancel_button)
        btn_sizer.Realize()
        
        sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)
        
        panel.SetSizerAndFit(sizer)
        self.SetClientSize(panel.GetSize())

    def on_save(self, event):
        """Guarda el dispositivo seleccionado y cierra el diálogo."""
        selected_device = self.listbox.GetStringSelection()
        if selected_device:
            self.audio_manager.set_device(selected_device)
        self.EndModal(wx.ID_OK)
