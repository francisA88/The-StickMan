from kivy.animation import Animation
from copy import deepcopy
from itertools import cycle

class ParserError(SyntaxError): pass

def isnumber(string):
	try:
		float(string)
	except ValueError:
		return False
	return True
	
def repeat_elems(indices, li, n):
	from copy import deepcopy as copy
	a,b = indices
	fp = copy(li)[0:a]
	mp = copy(li)[a:b+1]
	ep = copy(li)[b+1:]
	del li[a:]
	li.extend(mp*n)
	li.extend(ep)

class Parser:
	_tokens =[]
	keywords = {
		"sync": "",
		"endsync": "",
		"loop": int,
		"endloop": "",
		"speed":int,
		"endspeed":"",
		"reset": ""
	}
	def __init__(self, string):
		self.content = string
		
	def get_tokens(self):
		for i in range(len(self.content.splitlines())):
			line = self.content.splitlines()[i]
			line = line[:line.index("#")] if "#" in line else line
			print(line)
			#if self.iscomment(line): continue
			self.parse_line(line, i+1)
			if ":" in line: #This makes it a keyword usage
				l = line.replace(" ","").replace("\t","")
				_temp = l.split(":")
				keyw = _temp[0]
				value = _temp[1]
				keyw_val =self.keywords[keyw]
				if keyw_val ==int:
					if not isnumber(value):
						raise TypeError("On line {}, expected an integer instead got another type".format(i+1))
				else:
					if value != keyw_val:
						raise TypeError("On line {0}, expected {1} instead got {2}".format(i, "nothing after ':'" if keyw_val=="" else keyw_val, value))
				self._tokens.append(_temp)
			else:
				_temp = line.split(" ")
				#If an empty line,...
				if not _temp[0]: continue
				if len(_temp)==1:
					raise SyntaxError("Expected both an attribute and a group of values but instead got only one of them on line %s"%(i+1))
				_temp = [s.replace(" ","").replace("\t","") for s in _temp if s.replace(" ","").replace("\t","")]
				real_temp = [_temp[0]]
				real_temp.extend([eval(i) for i in _temp[1:]])
				self._tokens.append(real_temp)
		return deepcopy(self._tokens)
		
	def iscomment(self, line):
		return line.lstrip().startswith("#")
	def parse_line(self, line, lineno):
		for i in range(len(line)):
			if line[i] == "#":break
			if line[i] not in "+-_/*.:" and not line[i].isalnum() and not line[i].isspace():
				raise ParserError("Unexpected character '{0}' on line {1}".format(line[i], lineno))
				
#Animation Loader class. Handles all instructions from the animation file/string
class Animloader:
	def __init__(self, sm, speed=1):
		self.anim_sync = False #
		self.default_speed = speed #Default speed
		self.speed = speed #Current animation speed
		self.sm = sm #StickMan instance
		self.attr_setter_type = "increment" #or "as-is"
	def run(self, string):
		self.anim_queue = []
		parser = Parser(string)
		self.parts = parser.get_tokens()
		self.kws = parser.keywords.keys()
		self.evaluate()
		parser._tokens.clear()
		
	def evaluate(self, n=0):
		evaluate = self.evaluate
		if n>len(self.parts)-1:return
		first = self.parts[n][0]
		if self.iskeyword(first):
			if first in ["sync","endsync"]:
				self.anim_sync = not self.anim_sync
				evaluate(n+1)
			elif first =="loop":
				value = int(self.parts[n][1])
				for i in range(n,len(self.parts)):
					if self.parts[i][0]=="endloop":
						b = i
						break
				else: raise Exception(f"Missing an 'endloop' keyword to match earlier 'loop' keyword")
				#repeat_elems((n+1,b-1), self.parts, value)
				for i in range(value):
					for j in range(n+1, b):
						print(self.parts[j])
						evaluate(j)
				#evaluate(n+1)
				evaluate(b+1)
			elif first=="speed":
				value = float(self.parts[n][1])
				self.speed = value
				evaluate(n+1)
			elif first=="endspeed":
				self.speed = self.default_speed
				evaluate(n+1)
			elif first== "reset": self.sm.reset_all()
		else:
			i = first.index(".")
			attr = getattr(self.sm, first[:i])
			property = first[i+1:]
			temp = self.parts[n][1:]
			value = temp if len(temp)>1 else temp[0]
			#If the type of a property is an integer, then the new value of that property
			#should be added to the old value instead of replacing that old value
			old_value = getattr(attr,property)
			if isinstance(old_value, (int,float)):
				if self.attr_setter_type == "increment":
					old_value+=value
				elif self.attr_setter_type == "as-is":
					old_value = value
				else: raise ValueError(f"Invalid value for attr_setter_type '{self.attr_setter_type}' . Must be one of ['increment','as-is']")
				value=old_value
			pair = {property:value}
			anim = Animation(**pair, duration=1/self.speed, t="out_expo")
			self.anim_queue.append(anim)
			def call_next(*args):
				evaluate(n+1)
			if not self.anim_sync:
				anim.bind(on_complete=call_next)
			else:
				anim.bind(on_start=call_next)
			anim.start(attr)
		print("Parts: ",len(self.parts))
		if n==0:
			self.anim_queue[-1].bind(on_complete=self.on_completion)
	def run_file(self, filepath):
		self.run(open(filepath).read())
		
	def iskeyword(self, word):
		return word in self.kws
		
	def on_completion(self, *args):
		pass
		