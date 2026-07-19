import ctypes

try:
    # Intenta cargar la DLL de NVDA.
    nvda = ctypes.WinDLL('_internal/nvda64.dll')
except (OSError, AttributeError):
    # Si la DLL no se encuentra o no estamos en Windows, usa un 'mock' que imprime en la consola.
    class MockNvda:
        def nvdaController_speakText(self, wstr):
            """Función de reemplazo que imprime el texto en lugar de hablarlo."""
            print(f"NVDA Speak: {wstr.value}")
    nvda = MockNvda()

def speak(string: str):
    """
    Llama a la DLL de NVDA para verbalizar el texto proporcionado.
    Si la DLL no está disponible, imprimirá el texto en la consola.
    """
    wstr = ctypes.c_wchar_p(string)
    nvda.nvdaController_speakText(wstr)
