from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.uix.button import Button
from kivy.base import runTouchApp

__all__ = ("MyAnimation", "SequentialAnim", "ParallelAnim")

class MyAnimation: pass
class MyAnimation(Animation):
	def __init__(self, prop, **kws):
		super().__init__(**kws)
		self.prop = prop
		self.is_paused = False
		self.me = "ams"
	def __gt__(self, other:MyAnimation):
		self.on_complete = lambda *args: other.start()
		self.start()
	
	def start(self):
		super().start(self.prop)
		
	def pause(self):
		anim_props = self.animated_properties
		self.stop(self.prop)
		self.is_paused = True
#		for p in anim_props:
#			attr = getattr(self.prop, p)
	def resume(self):
		if self.is_paused:
			anim_props = self.animated_properties
			print(anim_props)
			new = self.__class__(self.prop, **anim_props)
			new.start()
			new.on_complete = self.on_complete
			self.is_paused = False
		
class SequentialAnim:
	'''Runs various animation classes in sequel'''
	def __init__(self, *anims):
		self.anims = list(anims)
		
	def queue(self, other:MyAnimation):
		self.anims.append(other)
		
	@staticmethod
	def then(current, nextone):
		if isinstance(current, MyAnimation):
			current.on_complete = lambda *arg: nextone.start()
		elif isinstance(current, (SequentialAnim, ParallelAnim)):
			current.oncomplete = lambda *arg: nextone.start()
		
	def start(self):
		#if not self.anims:return self.oncomplete()
		for i in range(len(self.anims)-1):
			SequentialAnim.then(self.anims[i], self.anims[i+1])
		self.anims[0].start()
		if isinstance(self.anims[-1], MyAnimation):
			self.anims[-1].on_complete = self.oncomplete
		elif isinstance(self.anims[-1], (self.__class__, ParallelAnim)):
			self.anims[-1].oncomplete = self.oncomplete
	def oncomplete(self, *args):
		pass

class ParallelAnim:
	def __init__(self, *anims):
		self.anims = list(anims)
	def queue(self, anim):
		self.anims.append(anim)
		
	def start(self):
		#if not self.anims: return self.oncomplete()
		longestanim = max(self.anims, key=lambda a: a.duration)
		longestanim.on_complete = self.oncomplete
		for anim in self.anims:
			anim.start()
			
	def oncomplete(self, *args):
		pass
		
if __name__ == '__main__':
	from kivy.clock import Clock
	btn1 = Button(text="1")
	
	btn2 = Button(text="2", pos=[110,0])
	widget = Widget()
	widget.add_widget(btn1)
	widget.add_widget(btn2)
	anim1 = Animation(y=200)
	anim2 = Animation(x=200)
	
	manim1 = MyAnimation(btn1, y=300)
	manim2 = MyAnimation(btn2, duration=2, x=200)
	manim3 = MyAnimation(btn1, y=0, t="out_quad")
	manim3.me = "mink"
	btn1.on_press = lambda *arg: manim1.resume()
	def f(*args):
		if btn1.y>=200:
			manim1.pause()
			Clock.schedule_once(lambda dt: manim1.resume(), 2)
	manim1.on_progress = f
	manim1.start()
	runTouchApp(widget)