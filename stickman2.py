'''This code here is still a very big work in progress and contains lots of confusing code even to I who wrote it *haha*. It is meant to replace the other stickman (see stickman.py) or act as a substitute. This is because of some issues with Rotate and Translate calls which apply changes to the canvas coordinates rather than to the coordinates (position) of the individual stickman parts.
In other words, if the end point of an arm is (100, 200) before rotation/translation, the end points still remain the same and unaffected even after the transformations applied. This is undesirable especially if the StickMan is intended to be used in a game and it is necessary to track the individual coordinates of any of the parts.'''

from kivy.graphics import *
from kivy.uix.widget import Widget
from kivy.base import runTouchApp
from kivy.properties import *
from kivy.event import EventDispatcher
from kivy.vector import Vector

from math import *
from copy import deepcopy as dc
from helpers import List

rad = radians
deg = degrees
#:::===========:::#
#:=============:#
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
	
#:::====================::#
#:::====================::#
class RotateableLine(Line,):
	'''A Line that can be rotated about its first point, self.points[:2] that is.
	Note: Must have only 2 points [x1,y1, x2,y2]'''
	_angle = 0
	def __init__(self, **kws):
		super().__init__(**kws)
		self._angle = self.getCoordAngTransform()
		self.initial_offset = self.getCoordAngTransform()
		o = self.points[:2]
		p = self.points[2:]
		self.refp = [p[0]-o[0], p[1]-o[1]]
		
	def getCoordAngTransform(self):
		o = self.points[:2]
		p = self.points[2:]
		np = Vector([p[0]-o[0], p[1]-o[1]])
		ang = np.angle((90,0))
		return ang if ang>0 else 360-abs(ang)
		
	@property
	def angle(self):
		return self._angle-self.initial_offset
		
	@angle.setter
	def angle(self, ang):
		self._angle = ang+self.initial_offset
		#self.points = rotateP(self.points[:2], self.points[2:], ang)
		o = self.points[:2]
		rot = Vector(self.refp).rotate(ang)
		rot[0]+=o[0]
		rot[1]+=o[1]
		self.points =[*o, *rot]
	@property
	def x1(self):
		return self.points[0]
	@property
	def x2(self):
		return self.points[2]
	@x1.setter
	def x1(self, x):
		p = self.points
		p[0] = x
		self.points = p
	@x2.setter
	def x2(self, x):
		p = self.points
		p[2] = x
		self.points = p
	@property
	def y1(self):
		p = self.points
		return p[1]
	@property
	def y2(self):
		p = self.points
		return p[3]
	@y1.setter
	def y1(self, y):
		p = self.points
		p[1] = y
		self.points = p
	@y2.setter
	def y2(self, y):
		p = self.points
		p[3] = y
		self.points = p
		
#:==================:#
def rotateP(about:list, point:list, ang:(float or int))->[float,float, float,float]:
	o = about
	facx = o[0]
	facy = o[1]
	np =[0,0, point[0]-facx, point[1]-facy]
	v = Vector(np[2:])
	_np = v.rotate(ang)
	np[:2] = o
	np[2:] = [_np[0]+facx, _np[1]+facy]
	return np
#:============%========:#
def _(pos, orig):
	return [pos[0]-orig[0], pos[1]-orig[1]]
def _convertTo360(ang):
	'''Simple function to convert a negative angle to its equivalent positive angle'''
	return ang if ang>0 else 360+ang
#:=====================:#
class BodyPart(EventDispatcher):
	angle = NumericProperty(0)
	#attached_line: The actual line the instance of this class is updates its coordinates.
	attached_line = ObjectProperty(None)
	#other_line: The other line whose origin point is the endpoint of the attached_line
	other_line = ObjectProperty(None)
	def __init__(self, **kws):
		super().__init__(**kws)
		
	def on_attached_line(self, inst, line):
		self.p = dc(self.attached_line.points)
	def on_other_line(self, inst, line):
		self.q = dc(self.other_line.points)
		
	def on_angle(self, inst, val):
		#p = dc(self.attached_line.points)
		#q = dc(self.other_line.points)
		far_end = self.q[2:]
		orig = self.p[:2]
		tr = far_end[0]-orig[0], far_end[1]-orig[1]
		self.ref_vec_point = list(tr)
		#far_end = q[2:]
		#orig = p[:2]
		#trans = far_end[1]-orig[1], far_end[0]-orig[0]
		self.attached_line.angle = val
		_vec = Vector(self.ref_vec_point)
		np = _vec.rotate(val)
		np[0]+=orig[0]
		np[1]+=orig[1]
		self.other_line.points =[*self.attached_line.points[2:], *np]
		#Done
class AngleListener(EventDispatcher):
	angle = NumericProperty(0)
	former_angle = NumericProperty(0)
	
class LinearListener(EventDispatcher):
	x = NumericProperty(0)
	y = NumericProperty(0)
#:=====================:#
class StickMan(Widget):
	hc = ListProperty([100,100])
	color = ListProperty([.9, .4, .4, 1])
	headradius = NumericProperty(25)
	eyecolor = ListProperty([1, 50/255, 50/255])
	def __init__(self, **kws):
		self.canv_cache =[]
		super().__init__(**kws)
		#self.hsize = self.headsize[]
		###some variables needed for a hack fix for rotation of some body part(s)
		self._former_angle = 0
		###
		self.draw()
		
	@property
	def flipped(self):
		return self.scale.x != 1
	@flipped.setter
	def flipped(self, value):
		self.scale.x = -1 if value else 1
		
	def redraw(self):
		self.clear()
		self.draw()
		
	def on_hc(self, inst, value):
		self.redraw()
	def on_color(self, inst, col):
		self.redraw()
	def on_headradius(self, inst, value):
		self.redraw()
	def on_eyecolor(self, inst, col):
		self.redraw()
	
	def clear(self):
		try:
			for obj in self.canv_cache:
				self.canvas.remove(obj)
		except: pass
		del self.canv_cache[:]
	def draw(self):
		rc = RenderContext(use_parent_projection=True,
			use_parent_modelview=True)
		width = self.headradius*2/7
		with rc:
			Color(*self.color)
			PushMatrix()
			self.scale = Scale(1,1,1)
			self.oposition = LinearListener()
			PushMatrix()
			self.headrot = Rotate(1,1,0)
			self.head = Circle(size=[self.headradius*2]*2)
			self.head.center = self.hc
			self.headrot.origin = self.head.center
			PopMatrix()
			hc = self.hc
			###Axis###
			self.axis = RotateableLine(points=[
				*self.head.bottom, hc[0], self.head.bottom[1]-1.05*self.head.size[1]], width=width)
			self.axis1 = RotateableLine(points=[
				*self.axis.points[2:], hc[0], self.axis.points[3]-1.01*self.head.size[1]], width=width)
			self.uax_rot = AngleListener()
			self.uax_rot.bind(angle = lambda inst, ang: self.rotate_upperUp(ang))
			self.ax_rot = AngleListener()
			self.ax_rot.bind(angle= lambda inst,ang: self.rotate_upper(ang))
			###End-axis##
			p = self.head.bottom
			h = self.head
			###Arms###
			self.arm11 = RotateableLine(
				points=[(p[0], p[1]-h.size[1]*.2),
			   (p[0]-h.size[0]*.75, p[1]-h.size[1]*0.7)], width=width)
			self.arm1j1 = BodyPart()
			self.arm1j1.attached_line = self.arm11
			self.arm1j2 = RotateableLine(points=[self.arm11.points[-2:],
		   	(p[0]-h.size[0]*1.4,p[1]-h.size[1]*1.55)],
			   width=width)
			self.arm1j1.other_line = self.arm1j2
			###₦₦₦₦####
			self.arm21 = RotateableLine(points=[
			   (p[0], p[1]-h.size[1]*.2),
			   (p[0]+h.size[0]*.75, p[1]-h.size[1]*0.7)], width=width)
			self.arm2j2 = RotateableLine(points=[
				self.arm21.points[-2:],
			   (p[0]+h.size[0]*1.4,p[1]-h.size[1]*1.55)],
			   width=width)
			self.arm2j1 = BodyPart()
			self.arm2j1.attached_line = self.arm21
			self.arm2j1.other_line = self.arm2j2
			##End arms##
			q = self.axis1.points[-1]
			##Legs###
			self.lrot = AngleListener()
			self.leg11 = RotateableLine(points=[
			   (p[0], q),
			   (p[0]-h.size[0]*.6, p[1]-h.size[1]*3.6)], width=width,)
			self.leg1j2 = RotateableLine(points=[
				self.leg11.points[-2:],(p[0]-h.size[0]*.9, p[1]-h.size[1]*4.7)], width=width)
			self.leg1j1 = BodyPart()
			self.leg1j1.attached_line = self.leg11
			self.leg1j1.other_line = self.leg1j2
			#####
			#####
			self.leg21 =RotateableLine(points=[
			   (p[0], q),
			   (p[0]+h.size[0]*.6, p[1]-h.size[1]*3.6)],width=width)
			self.leg2j2 = RotateableLine(points=(self.leg21.points[-2:],(p[0]+h.size[0]*.9, p[1]-h.size[1]*4.7)), width=width)
			self.leg2j1 = BodyPart()
			self.leg2j1.attached_line = self.leg21
			self.leg2j1.other_line = self.leg2j2
			self.cur_legs_ang = []
			def rotateBothLegs(inst, ang):
				self.cur_legs_ang.append([
					self.leg11.getCoordAngTransform(),
					self.leg21.getCoordAngTransform()])
				self.leg2j1.angle = 360-self.leg21.initial_offset+self.cur_legs_ang[0][1]+ang#+self.leg21.getCoordAngTransform()
				self.leg1j1.angle = 360-self.leg11.initial_offset+self.cur_legs_ang[0][0]+ang#+self.leg11.getCoordAngTransform()
				try:
					del self.cur_legs_ang[1:]
				except IndexError:
					pass
			self.lrot.bind(angle=rotateBothLegs)
			##End leg##
			PopMatrix()
		self.canvas.add(rc)
		eyerc = RenderContext(use_parent_projection=True,
			use_parent_modelview=True)
		with eyerc:
			Color(*self.eyecolor)
			ep = [h.center[0]+self.headradius/3.5,h.center[1]+self.headradius/4, 
				h.center[0]+self.headradius-3, h.center[1]+self.headradius/3,
				h.center[0]+self.headradius-3, h.center[1]-self.headradius/3]
			PushMatrix()
			self.eyerot = Rotate(1,1,0)
			self.eye = Triangle(points=ep)
			PopMatrix()
		self.canvas.add(eyerc)
		self.canv_cache.append(rc)
		self.canv_cache.append(eyerc)
	
	def rotate_upper(self, to=0):
		ang = -to #Makes sure that negative angles rotate to the left
		ang = ang - self._former_angle #hoping this fixes some stuff
		orig = self.axis1.points[2:]
		far_end1 = self.arm1j2.points[2:]
		elb1 = self.arm11.points[2:] #self.arm1j2.points[:2] #(elbow)
		shd1 = self.arm11.points[:2] #shoulder
		###
		far_end2 = self.arm2j2.points[2:]
		elb2 = self.arm21.points[2:]
		shd2 = self.arm21.points[:2] #or =shd1
		neck_j = self.axis.points[:2]
		waist_j = self.axis.points[2:] #a joint around the waist area
		_r = lambda p: _(p, orig)
		to360 = _convertTo360
		ang_deviation = Vector(_r(waist_j)).angle((0,90))
		#print("Dev: ",ang_deviation)
		ang = ang - ang_deviation
		###Vectors####
		lvec1 = Vector(_r(far_end1))
		lvec2 = Vector(_r(elb1))
		lvec3 = Vector(_r(shd1))
		cvec =  Vector(_r(neck_j))
		cvec1 =Vector(_r(waist_j))
		rvec3 = Vector(_r(shd2))
		rvec2 = Vector(_r(elb2))
		rvec1 = Vector(_r(far_end2))
		##
		_ret = lambda o, p: [p[0]+o[0], p[1]+o[1]]
		l1, l2, l3 =[
			_ret(orig, lvec1.rotate(ang)[:]),
			_ret(orig, lvec2.rotate(ang)[:]),
			_ret(orig, lvec3.rotate(ang)[:])
		]
		c = _ret(orig, cvec.rotate(ang)[:])
		c1 = _ret(orig, cvec1.rotate(ang)[:])
		r1, r2, r3 =[
			_ret(orig, rvec1.rotate(ang)[:]),
			_ret(orig, rvec2.rotate(ang)[:]),
			_ret(orig, rvec3.rotate(ang)[:])
		]
		self.arm11.points = l3+l2
		self.arm1j2.points = l2+l1
		self.arm21.points = r3+r2
		self.arm2j2.points = r2+r1
		self.axis.points = c+c1
		self.axis1.points = c1+orig
		p = self.axis.points[:2]
		r_ang = Vector(_r(p)).angle((90,0))
		r_ang = 90-r_ang
		self.head.center = p[0]+self.headradius*sin(rad(r_ang)), p[1]+self.headradius*cos(rad(r_ang))
		self.eyerot.origin = self.axis1.points[2:]
		self.eyerot.angle = -r_ang
		
		
	def rotate_upperUp(self, to=0):
		ang = -to #Makes sure that negative angles rotate to the left
		orig = self.axis.points[2:]
		far_end1 = self.arm1j2.points[2:]
		elb1 = self.arm11.points[2:] #self.arm1j2.points[:2] #(elbow)
		shd1 = self.arm11.points[:2] #shoulder
		###
		far_end2 = self.arm2j2.points[2:]
		elb2 = self.arm21.points[2:]
		shd2 = self.arm21.points[:2] #or =shd1
		neck_j = self.axis.points[:2]
		_r = lambda p: _(p, orig)
		to360 = _convertTo360
		ang_deviation = Vector(_r(neck_j)).angle(_(self.axis1.points[:2], self.axis.points[2:]))
		#print("Dev: ",ang_deviation)
		ang = ang - ang_deviation
		###Vectors####
		lvec1 = Vector(_r(far_end1))
		lvec2 = Vector(_r(elb1))
		lvec3 = Vector(_r(shd1))
		cvec = Vector(_r(neck_j))
		rvec3 = Vector(_r(shd2))
		rvec2 = Vector(_r(elb2))
		rvec1 = Vector(_r(far_end2))
		##
		_ret = lambda o, p: [p[0]+o[0], p[1]+o[1]]
		l1, l2, l3 =[
			_ret(orig, lvec1.rotate(ang)[:]),
			_ret(orig, lvec2.rotate(ang)[:]),
			_ret(orig, lvec3.rotate(ang)[:])
		]
		c = _ret(orig, cvec.rotate(ang)[:])
		r1, r2, r3 =[
			_ret(orig, rvec1.rotate(ang)[:]),
			_ret(orig, rvec2.rotate(ang)[:]),
			_ret(orig, rvec3.rotate(ang)[:])
		]
		self.arm11.points = l3+l2
		self.arm1j2.points = l2+l1
		self.arm21.points = r3+r2
		self.arm2j2.points = r2+r1
		self.axis.points = c+orig
		p = self.axis.points[:2]
		r_ang = Vector(_r(p)).angle(_(self.axis1.points[:2], self.axis.points[2:]))#angle((90,0))
		r_ang = 90-r_ang
		self.head.center = p[0]+self.headradius*sin(rad(r_ang)), p[1]+self.headradius*cos(rad(r_ang))
		self.eyerot.origin = self.axis.points[2:]
		self.eyerot.angle = -r_ang
		
	def translate_whole(self, x=0, y=0):
		parts =[
			'arm11', 'arm1j2',
			'arm21', 'arm2j2',
			'leg11', 'leg1j2',
			'leg21', 'leg2j2',
			'axis', 'axis1']
		for part in parts:
			bp = getattr(self, part)
			bp.x1 +=x
			bp.x2 += x
			bp.y1 +=y
			bp.y2 += y
		self.head.center = self.head.center[0]+x, self.head.center[1]+y
		
	def clear_lrot_cache(self):
		'''::NOTE: Make sure to call this method after a session of rotating the lower part of StickMan by setting lrot.angle.
		#A case when you are to use this function could be just after animating the lrot.angle or after setting the lrot.angle directly without any animation (kivy.animation.Animation class).
		#Having said that, if an Animation is used, expected call to this method is just after animation is complete. That can be done by binding Animation.on_complete .'''
		self.cur_legs_ang.clear()
		
if __name__ == '__main__':
	from kivy.clock import Clock
	from kivy.animation import Animation
	from time import sleep
	sm = StickMan()
	sm.hc = 200,300
	sm.headradius = 25
	sm.eyecolor = .96, .4, .36
	sm.color = 0, 90/255, 80/255
	anim=Animation(angle=50, duration=2)
	with sm.canvas:
		Color(*sm.color)
		line = RotateableLine(points=[50,50, 100,300], width=1.5)
	def lrot(*a):
		print(sm.leg11.initial_offset)
		Animation(angle=30, t="out_cubic").start(sm.uax_rot)
		Animation(angle=30, t="out_cubic").start(sm.ax_rot)
		Animation(angle=-100).start(line)
		#Animation(points=[50,50, 150,360]).start(line)
		#sm.translate_whole(44,99)
		#sm.uax_rot.angle = 120
		#sm.leg1j1.angle = sm.leg11.initial_offset
		print("After: ",sm.leg11.getCoordAngTransform())
	anim.on_complete = lrot
	print(sm.leg11.getCoordAngTransform())
	anim.start(sm.leg1j1)
	runTouchApp(sm)