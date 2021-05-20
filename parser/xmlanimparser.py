from xml.etree.ElementTree import XML
from copy import deepcopy as copy

from .specialanimation import *

from kivy.animation import Animation

def rep(s): return s.replace(" ","")

class InvalidRootTag(Exception): pass
class UnknownTag(BaseException): pass

class Animloader:
	'''Parser class for handling Stickman xml animation files'''
	'''
	nesting tags = ["sync","loop","speed"] #Nestable tags
	keyws = nestables+["reset", "flip"] #All keywords
	assoc_options = {"sync":None, "speed":"speed", "loop":"n", "flip":None}
	'''
	def __init__(self, sm):
		self.sm = sm
		self.speeds = [1]
		#animation specific variables
		self.is_sync = False
		self.speed = 1
		'''
		 :::if anim_setter_type is set to "as-is", the current value of the body part will be used as it is, else if it is "increment", it will be added to the former value.'''
		self.attr_setter_type = "as-is" #or increment
		
	def run_file(self, filename):
		return self.run(open(filename).read())
		
	def run(self, string):
		self.root = XML(string)
		if self.root.tag.lower() != "stickman":
			raise InvalidRootTag(self.root.tag)
		self.results = {}
		self.walk_children(self.root)
	def walk_children(self, elem, n=0):
		if n>=len(elem): return elem
		tagname = elem[n].tag.lower()
		if tagname == "speed":
			return self._handle_speed(elem, n)
		elif tagname == "sync":
			return self._handle_sync(elem, n)
		elif tagname == "loop":
			return self._handle_loop(elem, n)
		elif tagname == "flip":
			self.sm.flipped = not self.sm.flipped
			if n==len(self.root)-1: self.oncomplete(1)
			return self.walk_children(elem, n+1)
		else:
			opt, value= elem[n].items()[0]
			value = float(rep(value))
			part = getattr(self.sm, tagname)
			old_value = getattr(part, opt)
			if self.attr_setter_type == "increment":
				value += old_value
			opts = {opt:value}
			anim = Animation(**opts, duration=1/self.speed, t="in_quad")
			anim.start(part)
			if elem == self.root and n==len(elem)-1:
				anim.on_complete = self.oncomplete
			else:
				anim.on_complete = lambda *arg: self.walk_children(elem, n+1)
			
	def _handle_loop(self, elem, i):
		n = int(elem[i].attrib["n"])
		'''Repeatedly add the same elements in the loop tag n times'''
		l = len(elem[i])
		if not l: return self.walk_children(elem, i+1)
		for k in range(n-1):
			for j in range(l):
				elem[i].append(copy(elem[i][j]))
		sqanim = SequentialAnim()
		#When done, move to the next tag under the root tag.
		sqanim.oncomplete = lambda *arg: self.walk_children(elem, i+1)
		#Checks if this current tag is the last tag under root. Calls self.oncomplete if it is when done.
		if i == len(self.root)-1:
			sqanim.oncomplete = self.oncomplete
		for l in range(len(elem[i])):
			ch = elem[i][l]
			if ch.tag.lower() == "sync":
				par = ParallelAnim()
				for child in ch:
					tagname = child.tag.lower()
					opt, val = child.items()[0]
					try:
						part = getattr(self.sm, tagname)
					except AttributeError:
						raise AttributeError(f"Unknown tag {tagname} in parent tag {elem[n]}")
					old_val = getattr(part, opt)
					val = float(val)
					if self.attr_setter_type == "increment":
						val += old_val
					opts = {opt: val}
					anim = MyAnimation(part, **opts, duration=1/self.speed, t="in_quad")
					par.queue(anim)
				#Queue the parallel animation in the overall sequence
				sqanim.queue(par)
			else:
				tagname = ch.tag.lower()
				opt,val= ch.items()[0]
				part = getattr(self.sm, tagname)
				old_value = getattr(part, opt)
				val = float(val)
				if self.attr_setter_type == "increment":
					val+=old_value
				opts = {opt:val}
				anim = MyAnimation(part, **opts, duration=1/self.speed, t="out_quad")
				sqanim.queue(anim)
		#Start all the animations under Loop tag after queueing them.
		sqanim.start()
				
	def _handle_speed(self, elem, n):
		val = rep(elem[n].attrib["speed"])
		if val == "prev": self.speed = self.speeds[-2]
		else: self.speed = float(val)
		self.speeds.append(self.speed)
		#If the speed tag is not a container (has no children), continue to the next root descendant
		if not len(elem[n]):
			self.walk_children(elem, n+1)
		#Not sure how this’ll behave here so its better for now that a speed tag be a non-parent tag.
		#Example: <speed speed="3"/>
		else:
			self.walk_children(elem[n], 0)
		##
	def _handle_sync(self, elem, n):
		'''Special function to handle a sync tag if the sync tag is directly a descendant (child) of root.'''
		'''A sync tag runs animation instructions in parallel and is meant to have only stickman animation specific tags'''
		if not len(elem[n]):
			return self.walk_children(elem, n+1)
		for ch in elem[n]:
			tagname = ch.tag.lower()
			opt, val = ch.items()[0]
			try:
				part = getattr(self.sm, tagname)
			except AttributeError:
				raise AttributeError(f"Unknown tag {tagname} in parent tag {elem[n]}")
			old_val = getattr(part, opt)
			val = float(val)
			if self.attr_setter_type == "increment":
				val += old_val
			opts = {opt: val}
			anim = MyAnimation(part, **opts, duration=1/self.speed, t="out_quad")
			anim.start()
		#Given that the parent element {elem} is the root tag StickMan, and this Sync tag is the last tag under it, self.oncomplete is bound to anim.on_complete
		if elem == self.root and n == len(self.root) -1:
			anim.on_complete = self.oncomplete
		else:
			anim.on_complete = lambda *args: self.walk_children(elem, n+1)
	#You can override this method
	def oncomplete(self, *args):
		'''Called when all animation instructions are complete'''
		print("Done! ")
