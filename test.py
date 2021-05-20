from stickman import StickMan, Circle, Widget
#from stickman2 import StickMan as StickMan2
#StickMan = StickMan2
from parser.animationloader import Animloader #This one’s for .anim files
from parser.xmlanimparser import Animloader as XAnimloader #And this is for xml files

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Rectangle, Color, Line, Point

#Window.clearcolor = .2, .5, .6,1
Window.rotation = 0 #set to -90 if you need to rotate the screen to the left by 90 deg
wid = Widget(size=[Window.width, 40])
with wid.canvas.before:
	Color(.3, .3, .6, 1)
	bg = Rectangle(size=wid.size)
Window.add_widget(wid)

sm = StickMan([200,200])


######----------#######---#######
#Note: To set the initial bottom (y ordinate) of the stickman, that is, where it’s feet touches, set hcenter[1] to (max(headsize)/10)*54 + y
sm.headsize = 34,34
sm.bottom = 40

k,h = sm.leg11.points[:2]
l, i = sm.leg12.points[2:]

alx = XAnimloader(sm)
class TestApp(App):
	def build(self):
		alx.run('''
		<StickMan>
			<arm1j1 angle='-50'/>
			<Loop n="4">
				<arm1j2 angle="-50"/>
				<arm1j2 angle="0"/>
			</Loop>
		</StickMan>
		''')
		def walk(e):
			alx.run_file('animations/walk_full.xml')
		def highkick(e):
			alx.run_file('animations/onelegkick.xml')
			alx.oncomplete = walk

		alx.oncomplete = highkick
		return sm
	
TestApp().run()