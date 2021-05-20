from kivy.graphics import *
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.base import runTouchApp
from kivy.core.window import Window as win
from kivy.properties import *
from kivy.clock import Clock
from kivy.animation import Animation

from copy import deepcopy as dc

class RotateableLine(Line,):
	'''A Line segment that can be rotated about its first point, self.points[:2] that is.
	Note: Must have only 2 points [x1,y1, x2,y2]'''
	_angle = 0
	def __init__(self, **kws):
		super().__init__(**kws)
		o = self.points[:2]
		p = self.points[2:]
		dy = (p[1]-o[1])
		dx = (p[0]-o[0])
		self.coordAngTransform = deg(atan(dy/dx))
	@property
	def angle(self):
		return self._angle
	@angle.setter
	def angle(self, ang):
		self._angle = ang
		self.points = self.rotate(ang, transform=self.coordAngTransform)
		
	def rotate(self, ang, transform=0):
		p = self.points
		o = p[:2]
		end = p[2:]
		facx = o[0]
		facy = o[1]
		np =[0,0, end[0]-facx, end[1]-facy]
		r = dist(o,end)
		ny = r*sin(rad(ang+transform))
		nx = r*cos(rad(ang+transform))
		np = [*o, nx+facx, ny+facy]
		return np
		
def group(iterable, l=2):
	k=0
	new = []
	temp = []
	for i in range(len(iterable)):
		temp.append(iterable[i])
		k+=1
		if k==l:
			new.append(dc(temp))
			temp.clear()
			k=0
	return new
		
class Circle(Ellipse):
	@property
	def center(self):
		x,y = self.pos
		w,h = self.size
		return x+w/2, y+h/2
	@center.setter
	def center(self, val):
		x,y = val
		w,h = self.size
		self.pos = x-w/2, y-h/2
	@property
	def bottom(self):
		return self.center[0], self.center[1]-self.size[1]/2

#Note: To set the bottom of the stickman, that is, where it’s feet touches, set stickmaninstance.hcenter = x, (max(headsize)/10)*52 + y
'''
Example:::
	sm = StickMan((0,0), headsize=[30,30])
	sm.hcenter = 20, 52*3
'''
class StickMan(Widget):
	hsrc = ObjectProperty(None)
	legsrc =[[None, None], [None, None]]
	armsrc = ListProperty([[None, None], [None, None]])
	axsrc = ObjectProperty(None)
	#bottom = NumericProperty(0)

	def __init__(self, headcenter, color=[.9,.4, .4], headsize=[50,50], eyecolor=[255,50,50], **kws):
		self.hc = headcenter
		super().__init__(**kws)
		self.color = color
		headsize[1]=headsize[0]
		self.headsize=headsize
		self.eyecolor = eyecolor
		self._bottom = 0
		#with self.canvas:
#			Color(*self.color)
#		self.canvas.clear()
		self.draw()
	@property
	def hcenter(self):
		return self.hc
	@hcenter.setter
	def hcenter(self, value):
		self.hc = value
		self.draw()
		#self.canvas
	@property
	def flipped(self):
		return self.scale.x != 1
	@flipped.setter
	def flipped(self, value):
		self.scale.x = -1 if value else 1
		
	def draw(self):
		self.canvas.clear()
		self.headsize = [max(self.headsize)]*2
		width = self.headsize[0]/5
		with self.canvas:
			Color(*self.color)
			PushMatrix() #For rotation whole body
			self.orotation = Rotate(1, 1, 0)
			PushMatrix() #For whole body translate
			self.scale = Scale(1,1,1)
			self.oposition = Translate(0,0,0) #Overall position
			#self.ocolor=Color(*self.color)
			PushMatrix() #For rotation of upper half
			self.ax_rot = Rotate(1,1,0) #Rotation for only the upper half. Used PushMatrix to ensure that.
			PushMatrix() #For rotation of part of the upper half
			self.uax_rot = Rotate(1,1,0)
			PushMatrix() #for translation of only upper half. Please do not use this part yet.
			self.uposition = Translate(0,0,0) #upper half position
			#ax_rot.angle = 90
			self.head = Circle(size=self.headsize, source=self.hsrc)
			lw = (self.headsize[0]/2)%7
			h=self.head
			#Color(*self.eyecolor)
			#Put eye here
			#Circle(size=self.headsize).center = h.center[0]+100, h.center[1]
			#Color(*self.color)
			hc = self.hc
			self.head.center = self.hc
			self.scale.origin = (self.head.center[0]+self.oposition.x, self.head.center[1]+self.oposition.y)
			#Center line
			self.axis = Line(width=width, points=[*h.bottom, hc[0],h.bottom[1]-1.05*h.size[1]], source=self.axsrc)
			self.uax_rot.origin = self.axis.points[-2:]
			p = self.axis.points[1]
			q = self.axis.points[3]
			#m = max(p,q); n=min(p,q)
			#self.orotation.origin = self.axis.points[0],(m-n)/2
			self.headjoint = self.axis.points[0],self.axis.points[1]
			#Arms
			p = self.headjoint
			PushMatrix() #For arm1, whole.
			self.arm1j1 = Rotate(1,1,0)
			self.arm11 = Line(points=[
			   (p[0], p[1]-h.size[1]*.2),
			   (p[0]-h.size[0]*.75, p[1]-h.size[1]*0.7)], width=width, source=self.armsrc[0][0])
			self.arm1j1.origin = self.arm11.points[:2]
			
			PushMatrix() #For arm1 lower part
			self.arm1j2 = Rotate(1,1,0)
			self.arm12 = Line(points=[self.arm11.points[-2:],
		   	(p[0]-h.size[0]*1.4,p[1]-h.size[1]*1.55)],
			   width=width, source=self.armsrc[0][1])
			self.arm1j2.origin = self.arm12.points[:2]
			PopMatrix() #End for arm1, lower part
			PopMatrix() #End for arm1, whole.
			PushMatrix() #for arm2, whole.
			self.arm2j1 = Rotate(1,1,0)
			self.arm21 = Line(points=[
			   (p[0], p[1]-h.size[1]*.2),
			   (p[0]+h.size[0]*.75, p[1]-h.size[1]*0.7)], width=width)
			self.arm2j1.origin = self.arm21.points[:2]
			PushMatrix() #For arm2, lower.
			self.arm2j2 = Rotate(1,1,0)
			self.arm22 = Line(points=[
				self.arm21.points[-2:],
			   (p[0]+h.size[0]*1.4,p[1]-h.size[1]*1.55)],
			   width=width, source=self.armsrc[1][1])
			self.arm2j2.origin = self.arm22.points[:2]
			PopMatrix() #End for arm2, lower.
			PopMatrix() #End for arm2, whole.
			PopMatrix() #End upper half translation
			PopMatrix() #End for rotation of part of upper half
			self.axis1 = Line(points=[self.axis.points[2], q, 
			      self.axis.points[2], h.bottom[1]-2.1*h.size[1]], width=width)
			q = self.axis1.points[3]
			self.ax_rot.origin = self.axis1.points[2:]
			PopMatrix() #End upper half rotation
			#Legs
			PushMatrix() #For rotation of lower half alone (both legs at a time)
			self.lrot = Rotate(1,1,0)
			self.lrot.origin = self.ax_rot.origin
			PushMatrix() #For whole of leg1
			self.leg1j1 = Rotate(1,1,0)
			self.leg11 = Line(points=[
			   (p[0], q),
			   (p[0]-h.size[0]*.6, p[1]-h.size[1]*3.6)], width=width, source=self.legsrc[0][0])
			self.leg1j1.origin = self.leg11.points[:2]
			PushMatrix() #For leg1, lower part
			self.leg1j2 = Rotate(1,1,0)
			self.leg12 = Line(points=[
				self.leg11.points[-2:],(p[0]-h.size[0]*.9, p[1]-h.size[1]*4.7)], width=width, source=self.legsrc[0][1])
			self.leg1j2.origin = self.leg12.points[:2]
			PopMatrix() #end For leg1, lower
			PopMatrix() #end For leg1 whole
			PushMatrix() #For leg2 whole
			self.leg2j1 = Rotate(1,1,0)
			self.leg21 =Line(points=[
			   (p[0], q),
			   (p[0]+h.size[0]*.6, p[1]-h.size[1]*3.6)],width=width, source=self.legsrc[1][0])
			self.leg2j1.origin = self.leg21.points[:2]
			PushMatrix() #For leg2 lower half
			self.leg2j2 = Rotate(1,1,0)
			self.leg22 = Line(points=(self.leg21.points[-2:],(p[0]+h.size[0]*.9, p[1]-h.size[1]*4.7)), width=width)#self.legsrc[1][1])
			self.leg2j2.origin = self.leg22.points[:2]
			self.orotation.origin = self.leg11.points[:2]
			PopMatrix() #end for leg2 lower
			PopMatrix() #end for leg2 whole
			PopMatrix() #end for lower rotation
			PopMatrix() #end translate for whole body
			PopMatrix() #End whole body rotation
		#Clock.schedule_interval(self._sync_leg_with_axis, 1/60)
			
	def _sync_leg_with_axis(self, dt):
		#This function should do something but is doing something else which it should not be doing.
		x,y = self.uposition.xy
		ax, ay = self.axis.points[2:]
		self.leg11.points[0]=ay+y#[self.leg11.points[2]+x, self.leg11.points[-1]+y]
		self.leg21.points[0]=self.leg11 .points[3]#[self.leg21.points[2]+x, self.leg21.points[-1]+y]
		
		
	def reset_all(self):
		for part in dir(self):
			p = getattr(self, part)
			if hasattr(p, "angle"):
				Animation(angle=0, duration=1/3).start(p)
		self.flipped = False
		anm = Animation(xy=(0,0), duration=1/3)
		anm.on_complete = self.on_reset_done 
		anm.start(self.oposition)
		#self.oposition.xy = 0,0
	def on_reset_done(self, e):
		pass
	
	@property
	def bottom(self):
		return self._bottom
	@bottom.setter
	def bottom(self, value):
		self.hcenter = self.hcenter[0], 54*max(self.headsize)/10 +  value
		self._bottom = value
		