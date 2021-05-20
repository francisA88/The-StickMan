class List(list):
	def forEach(self, function):
		for i in range(len(self)):
			function(self[i])
	
if __name__ == '__main__':
	li = List([6,7,8,9])