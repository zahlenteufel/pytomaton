# -*- coding: utf-8 -*- 
#!/usr/bin/python

from itertools import product # cartesian product
from collections import deque

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

def union(c):
	return set(flatten(c))

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
			newStates = union([self.transition[state].get(a, []) for state in currentStates])
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

		stateLambdaClosure = union([self.lambdaClosure(state) for state in currentStates])

		if s == "":
			return self.isFinal(stateLambdaClosure)
		else:
			a, w = s[0], s[1:] # s = aw
			newStates = union([self.transition[state].get(a, []) for state in stateLambdaClosure])
			newStates = self.lambdaClosureOfSet(newStates)
			return self.accepts(w, newStates)

	def lambdaClosureOfSet(self, set_states):
		return union([self.lambdaClosure(state) for state in set_states])

	def lambdaClosure(self, state):
		# BFS
		connectedComponent = set()
		connectedComponent.add(state)
		queue = deque([state])
		while queue:
			currentState = queue.popleft()
			for adjacent in self.transition[currentState].get("λ", []):
				if adjacent not in connectedComponent:
					queue.append(adjacent)
					connectedComponent.add(adjacent)
		return connectedComponent

	def toNFA(self):
		raise NotImplemented

d = {
	0: {'0' : [0], 'λ': [1]},
	1: {'1' : [1], 'λ': [2]},
	2: {'2' : [2]}
}

a = NFAlambda(d, 0, [2]) #0*1*2*

alphabet = "012"

MAX_LENGTH = 4
print "Accepted strings up to length %d:" % MAX_LENGTH
if a.accepts(""):
 	print "λ"
for length in xrange(1, 5):
	for string in product(alphabet, repeat=length):
		s = ''.join(string)
		if a.accepts(s):
			print s



