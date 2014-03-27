# -*- coding: utf-8 -*- 
#!/usr/bin/python

from itertools import product # cartesian product

class FA:
	pass

class DFA(FA):

	def __init__(self, transition, initial, finals):
		self.nodes = transition.keys()
		self.transition = transition
		self.initial = initial
		self.finals = finals

	def isFinal(self, state):
		return state in self.finals

	def accepts(self, s, currentState=None):
		if currentState is None:
			currentState = self.initial
		if s == "":
			return self.isFinal(currentState)
		else:
			a, w = s[0], s[1:] # s = aw
			return a in self.transition[currentState] and self.accepts(w, self.transition[currentState][a])		

	def minimize(self):
		raise NotImplemented

def flatten(listoflist):
	return [item for sublist in listoflist for item in sublist]

class NFA(FA):

	def __init__(self, transition, initial, finals):
		self.nodes = transition.keys()
		self.transition = transition
		self.initial = initial
		self.finals = finals

	def isFinal(self, states):
		return any(state in self.finals for state in states)

	def accepts(self, s, currentStates=None):
		if currentStates is None:
			currentStates = set([self.initial])

		if len(currentStates) == 0:
			return False
		if s == "":
			return self.isFinal(currentStates)
		else:
			a, w = s[0], s[1:] # s = aw
			newStates = set(flatten([self.transition[state].get(a, []) for state in currentStates]))
			return self.accepts(w, newStates)

	def determinize(self):
		raise NotImplemented

class NFAlambda(FA):

	def __init__(self, transition, initial, finals):
		self.nodes = transition.keys()
		self.transition = transition
		self.initial = initial
		self.finals = finals

	def isFinal(self, states):
		return any(state in self.finals for state in states)

	def accepts(self, s, currentStates=None):
		if currentStates is None:
			currentStates = set([self.initial])

		if len(currentStates) == 0:
			return False
		if s == "":
			return self.isFinal(currentStates)
		else:
			a, w = s[0], s[1:] # s = aw
			newStates = set(flatten([self.transition[state].get(a, []) for state in currentStates]))
			return self.accepts(w, newStates)

d = {
	0: {'0' : [0, 1], '1': [0, 2]},
	1: {'0' : [3]},
	2: {'1' : [3]},
	3: {'0' : [3], '1' : [3]}
}

a = NFA(d, 0, [3])

alphabet = "01"

MAX_LENGTH = 5
print "Accepted strings up to length %d:" % MAX_LENGTH
if a.accepts(""):
 	print "λ"
for length in xrange(1, 5):
	for string in product(alphabet, repeat=length):
		s = ''.join(string)
		if a.accepts(s):
			print s



