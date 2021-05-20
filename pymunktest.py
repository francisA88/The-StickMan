from kivy.base import runTouchApp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import *
from kivy.uix.button import Button
from kivy.core.audio import SoundLoader
from math import *
import pymunk
import os

Window.clearcolor = (.6,)*4

space = pymunk.Space()
space.gravity = 0, -1600
btninfo = Button(text="", size_hint=[None,None], size=[200,100])
btninfo.top = Window.height
btninfo.x = 200
Window.add_widget(btninfo)

sound = SoundLoader.load("/sdcard/projects/guidetheball_1/res/impact.wav")
				
###Defining a different Circle class just for a quick hack.#####
class Circle(pymunk.Circle):
	def __init__(self, *args, **kws):
		super().__init__(*args, **kws)
		self.hasJustPreviouslyCollided = False
	#previousAmplitude = 0 #Needed for doing stuff with collisions.
#######

def handle_collision(arb, sp, data):
	if not arb.shapes[0].hasJustPreviouslyCollided:
		sound.volume = 1
		sound.play()
		return
	return
	sv = list(arb.surface_velocity)
	imp = list(arb.total_impulse)
	rimp = (imp[0]**2+imp[1]**2)**.5
	sound.volume = rimp/600 if rimp<=600 else 1
	sound.pitch = .3
	sound.play()
	ke = arb.total_ke
	btninfo.text = str(round(imp[0], 2))+"\n"+str(round(imp[1],2))+"\n"+str(round(ke,2))+"\n"+str(round(sv[0]))
	return True
	
#space.add_collision_handler(1,2).post_solve = handle_collision

balls =[]
radius = 30
def updateBalls(ball, body, rot):
	ball.pos = body.position[0]-radius, body.position[1]-radius
	rot.origin = ball.pos[0]+ball.size[0]/2, ball.pos[1]+ball.size[1]/2
	rot.angle = body.angle *57.293 #(1 radian ≈ 57.29°)
	bp = body.position
	if bp[0]>Window.width or bp[0]<0\
		or bp[1] <0:
		space.remove(body)
		Window.canvas.remove(ball)
		balls.remove(ball)
		return False
		
def addBall():
	mass = 10
	moment = pymunk.moment_for_circle(mass, radius, 0)
	body = pymunk.Body(mass, 1666)
	#body.velocity= 0,-100
	body.position = 200, 660
	#body.velocity_func = vel_func
	body.apply_force_at_world_point((200,0), ([*body.position]))
	shape = Circle(body, radius)
	shape.elasticity = .8
	shape.friction = 1
	shape.collision_type = 1
	space.add(body, shape)
	with Window.canvas:
		PushMatrix()
		rot = Rotate(0,0,1)
		ball = Ellipse(size=[radius*2,]*2, source="/sdcard/pictures/12668.jpg")
		balls.append(ball)
		ball.pos = body.position[0]-radius, body.position[1]-radius
		PopMatrix()
	Clock.schedule_interval(lambda dt: updateBalls(ball, body, rot), .01)
	#objects.append([body, ball, rot])

btn4 = Button(text="FPS: "+str(Clock.get_fps()), size_hint=[None, None], size=[150,80])
btn4.top = Window.height
btn4.x = 30

def update(dt):
	ellipses = filter(lambda s: isinstance(s, Ellipse), Window.canvas.children)
	circles = tuple(filter(lambda s: isinstance(s, Circle), space.shapes))
	for ell in ellipses:
		c = ell.pos[0]+ell.size[0]/2, ell.pos[1]+ell.size[1]/2
		query = space.point_query(c, (ell.size[0]/2)+2, circles[0].filter)
		sp_query = filter(lambda q: isinstance(q.shape, pymunk.Segment), query)
		
		if list(sp_query):
			#if it just finished a collision, then it must be rolling along a surface and i definitely do not want the "impact" sound playing when it's rolling but only on impact
			if not query[0].shape.hasJustPreviouslyCollided:
				sound.volume = 1
				sound.play()
			if isinstance(query[0].shape, Circle):
				query[0].shape.hasJustPreviouslyCollided = True
				break
		else:
			query[0].shape.hasJustPreviouslyCollided = False
			
	space.step(.01)
	btn4.text = str(Clock.get_fps())
	
Clock.schedule_interval(update, .01)

sp = [150, 500, 400,400]
staticline = pymunk.Segment(space.static_body, sp[:2], sp[2:], 1)
staticline.friction = 1
staticline.elasticity = .6
#space.add(staticline)

#----

with Window.canvas:
	d_line = Line(width=2, points=[])
	#print(dir(d_line))
	
last_touch = None
lines = [d_line]
lines_dict = {d_line: []}
def drawline(touch):
	#print("here")
	if d_line not in lines: lines.append(d_line)
	if d_line not in lines_dict:
		lines_dict.update({d_line:[]})
	global last_touch
	if last_touch:
		d_line.points = d_line.points+list(touch.pos)
		if (len(d_line.points)>=4):
			p = d_line.points
			seg = pymunk.Segment(space.static_body, p[-4:-2], p[-2:], 0.5)
			seg.friction = .9
			seg.elasticity = .5
			seg.collision_type = 2
			space.add(seg)
			lines_dict[d_line].append(seg)
	
	last_touch = touch.pos
	
def recreate_line(touch):
	last_touch = None
	global d_line
	with Window.canvas:
		d_line = Line(width=2, points=[])
	
#print(dir(Window))
Window.on_touch_move=drawline
Window.on_touch_up = recreate_line
with Window.canvas:
	Color(.7, .4, .5)
	line = Line(points=sp, width=2)
	
btn1 = Button(text="clear_prev\nline", size_hint=[None, None])
def clear_prev_line():
	if lines:
		Window.canvas.remove(lines[-1])
		for seg in lines_dict[lines[-1]]:
			space.remove(seg)
		del lines[-1]
		
btn1.on_press = clear_prev_line

if __name__ == "__main__":
	#btn1.on_press = rotateL
	btn2 = Button(text="rotate\nright",size_hint=[None, None])
	btn3 = Button(text = "Add Ball", size_hint=[None, None])
	btn3.on_press = lambda :addBall()
	btn3.center_x = Window.center[0]
	btn2.right = Window.width
	
	Window.add_widget(btn1)
	Window.add_widget(btn2)
	Window.add_widget(btn3)
	Window.add_widget(btn4)
	runTouchApp()