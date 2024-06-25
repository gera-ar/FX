import ctypes
from pygame import mixer
import pygame._sdl2.audio as sdl2_audio
import os
import wx
from time import sleep
import subprocess
import threading

mixer.init()
devices= sdl2_audio.get_audio_device_names()

# constantes
nvda= ctypes.WinDLL('_internal/nvda64.dll')
app_name= 'FX'
supported_files= ['.aiff', '.wav', '.ogg', '.mp3', '.flac']
ffplay= '_internal/ffplay.exe'

def speak(string):
	wstr= ctypes.c_wchar_p(string)
	nvda.nvdaController_speakText(wstr)

class MyFrame(wx.Frame):
	def __init__(self):
		super().__init__(parent=None, title=app_name)
		self.ch= mixer.Channel(4)
		self.duration= None
		self.pan= (1.0, 1.0)
		
		self.fondos_files= []
		self.efectos_files= []
		
		self.process = None
		self.is_playing = False
		
		panel= wx.Panel(self)
		
		main_sizer= wx.BoxSizer(wx.VERTICAL)
		fondos_sizer = wx.BoxSizer(wx.HORIZONTAL)
		efectos_sizer = wx.BoxSizer(wx.HORIZONTAL)
		
		wx.StaticText(panel, -1, 'Fondos')
		self.fondos_listbox = wx.ListBox(panel, -1, size=(200, 200), name='fondos')
		fondos_sizer.Add(self.fondos_listbox, 0, wx.EXPAND | wx.ALL, 5)
		
		wx.StaticText(panel, -1, 'Efectos')
		self.efectos_listbox = wx.ListBox(panel, -1, size=(200, 200), name='efectos')
		efectos_sizer.Add(self.efectos_listbox, 0, wx.EXPAND | wx.ALL, 5)
		
		main_sizer.Add(fondos_sizer, 1, wx.EXPAND | wx.ALL, 10)
		main_sizer.Add(efectos_sizer, 1, wx.EXPAND | wx.ALL, 10)
		
		panel.SetSizer(main_sizer)
		
		self.SetSize((600, 400))
		self.SetMinSize((600, 400))
		
		self.load()
		
		self.fondos_listbox.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
		self.efectos_listbox.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)

	def load(self):
		if not os.path.exists('fondos'):
			os.makedirs('fondos', exist_ok= True)
		self.fondos_files.clear()
		self.fondos_listbox.Clear()
		for filename in os.listdir('fondos'):
			if os.path.isfile(os.path.join('fondos', filename)):
				name, ext= os.path.splitext(filename)[0], os.path.splitext(filename)[1]
				if ext in supported_files:
					self.fondos_listbox.Append(name)
					self.fondos_files.append(filename)
		
		if not os.path.exists('efectos'):
			os.makedirs('efectos', exist_ok= True)
		self.efectos_files.clear()
		self.efectos_listbox.Clear()
		for filename in os.listdir('efectos'):
			if os.path.isfile(os.path.join('efectos', filename)):
				name, ext= os.path.splitext(filename)[0], os.path.splitext(filename)[1]
				if ext in supported_files:
					self.efectos_listbox.Append(name)
					self.efectos_files.append(filename)
		if len(self.fondos_files) > 0:
			self.fondos_listbox.SetSelection(0)
		if len(self.efectos_files) > 0:
			self.efectos_listbox.SetSelection(0)

	def onKeyPress(self, event):
		widget= event.GetEventObject().GetName()
		key= event.GetKeyCode()
		if event.GetKeyCode() == wx.WXK_SPACE:
			select= self.fondos_listbox.GetSelection() if widget == 'fondos' else self.efectos_listbox.GetSelection()
			self.play(widget, select)
		elif event.GetKeyCode() == wx.WXK_LEFT:
			self.panorama('left')
		elif event.GetKeyCode() == wx.WXK_RIGHT:
			self.panorama('right')
		elif key == 344:
			speak('Actualizando las listas')
			self.load()
		elif key == 67:
			self.panorama('center')
		elif key == 49:
			select= self.fondos_listbox.GetSelection() 
			if widget == 'fondos' and select != wx.NOT_FOUND:
				speak('Reproducción en loop')
				self.loop(select)
		elif key == 65 or key == 83:
			self.stop(key)
		elif key == 81:
			self.up()
		elif key == 90:
			self.down()
		elif key == 82:
			self.time()
		elif key == 79:
			AudioDevice().Show()
		elif key == 80:
			self.preview(widget)
		else:
			event.Skip()

	def preview(self, widget):
		if not self.is_playing:
			if widget == 'fondos':
				file= f'fondos/{self.fondos_files[self.fondos_listbox.GetSelection()]}'
			elif widget == 'efectos':
				file= f'efectos/{self.efectos_files[self.efectos_listbox.GetSelection()]}'
			self.process= subprocess.Popen([ffplay, '-nodisp', file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)
			self.is_playing = True
			speak('Preview activada')
		else:
			self.process.terminate()
			self.process.wait()
			self.is_playing = False
			speak('Preview desactivada')


	def play(self, widget, select):
		if widget == 'fondos' and select != wx.NOT_FOUND:
			if not os.path.exists(f'fondos/{self.fondos_files[select]}'):
				speak('El archivo no existe')
				self.load()
			if mixer.music.get_busy():
				mixer.music.fadeout(100)
			mixer.music.load(f'fondos/{self.fondos_files[select]}')
			mixer.music.play()
			self.duration= int(mixer.Sound(f'fondos/{self.fondos_files[select]}').get_length())
		elif widget == 'efectos' and select != wx.NOT_FOUND:
			if not os.path.exists(f'efectos/{self.efectos_files[select]}'):
				speak('El archivo ya no existe')
				self.load()
			if self.ch.get_busy():
				self.ch.stop()
			efect= mixer.Sound(f'efectos/{self.efectos_files[select]}')
			self.ch.set_volume(self.pan[0], self.pan[1])
			self.ch.play(efect)
		else:
			speak('Sin selección')

	def stop(self, key):
		if key == 65:
			mixer.music.fadeout(1000)
		else:
			mixer.music.fadeout(5000)

	def up(self):
		current= mixer.music.get_volume()
		if current < 1.0:
			mixer.music.set_volume(current+0.1)

	def down(self):
		current= mixer.music.get_volume()
		if current > 0.0:
			mixer.music.set_volume(current-0.1)

	def loop(self, select):
		if mixer.music.get_busy():
			mixer.music.fadeout(100)
		mixer.music.load(f'fondos/{self.fondos_files[select]}')
		mixer.music.play(loops=-1, fade_ms=1000)

	def panorama(self, channel):
		if channel == 'left':
			self.pan= (1.0, 0.1)
			self.ch.set_volume(self.pan[0], self.pan[1])
			speak('Izquierda')
		elif channel == 'right':
			self.pan= (0.1, 1.0)
			self.ch.set_volume(self.pan[0], self.pan[1])
			speak('Derecha')
		elif channel == 'center':
			self.pan= 1.0, 1.0
			self.ch.set_volume(self.pan[0], self.pan[1])
			speak('Centro')

	def time(self):
		if not self.duration: return
		current = mixer.music.get_pos() / 1000
		remaining_minutes = int(self.duration - current) // 60
		remaining_seconds = int(self.duration - current) % 60
		msg = f'Quedan {remaining_minutes} minutos, {remaining_seconds} segundos'
		speak(msg)


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
	app = wx.App()
	frame = MyFrame()
	frame.Show()	
	app.MainLoop()