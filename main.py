import wx
from core.gui import MyFrame

class FxApp(wx.App):
    """Clase principal de la aplicación wxPython."""
    def OnInit(self):
        """Inicializa la aplicación creando la ventana principal."""
        self.frame = MyFrame()
        self.frame.Show()
        return True

if __name__ == '__main__':
    # Crea e inicia la aplicación.
    app = FxApp()
    app.MainLoop()
