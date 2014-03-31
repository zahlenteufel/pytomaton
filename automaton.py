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

	def split(self, B, S, a):
		B1 = [state for state in B if self.transition[state].get(a, None) in S]
		return B1, B-B1

	def minimize(self):
		# first consider only the states reachable from the start (BFS):
		reachables = set()
		reachables.add(self.initial)
		queue = deque([self.initial])
		while queue:
			currentState = queue.popleft()
			for letter in self.transition[currentState]:
				neighbour = self.transition[currentState][letter]
				if neighbour not in reachables:
					queue.append(neighbour)
					reachables.add(neighbour)
		
		# groupIndex = dict((state, int(self.isFinal(state)) for state in reachables)
		F = set(state in reachables if self.isFinal(state))
		notF = reachables - F
		if len(F) < len(notF): # |F| < |Q-F|
			P = [notF, F]
		else:
			P = [F, notF]
		L = P[1]

		alphabet = [letter for self.transition[state] for state in reachables]
		
		while len(L) > 0:
			S = L.pop()
			for a in alphabet:
				for B in P:
					B1, B2 = self.split(B, S, a)
					P.remove(B)
					P.append(B1)
					P.append(B2)
					if len(B1) < len(B2):
						L.append(B1)
					else:
						L.append(B2)

		# P has the partition (new elements), we have to translate 
		# the new indexes, the transitions, initial and finals


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

	def anyFinal(self, states):
		return any(state in self.finals for state in states)

	def accepts(self, s, currentStates=None):
		if currentStates is None:
			currentStates = set([self.initial])

		if len(currentStates) == 0:
			return False
		if s == "":
			return self.anyFinal(currentStates)
		else:
			a, w = s[0], s[1:] # s = aw
			newStates = union([self.transition[state].get(a, []) for state in currentStates])
			return self.accepts(w, newStates)

	def toDFA(self):
		d = {}
		# for each transition: add those in the lambda closure..
		# do like a BFS (avoid potentially unreachable states)
		initial = (self.initial,)
		seen = set([initial])
		queue = deque([initial])
		while queue:
			currentStates = queue.popleft()
			d[currentStates] = {}
			next = {}
			for state in currentStates:
				T = self.transition[state]
				for letter in T:
					if letter not in next:
						next[letter] = set()
					next[letter] |= set(T[letter])
			for letter in next:
				nextState = tuple(next[letter])
				d[currentStates][letter] = nextState
				if nextState not in seen:
					queue.append(nextState)
					seen.add(nextState)
		finals = []
		for states in d:
			if self.anyFinal(states):
				finals.append(states)
		return DFA(d, initial, finals)

class NFAlambda(FA):

	def __init__(self, transition, initial, finals):
		self.nodes = transition.keys()
		self.transition = transition
		self.initial = initial
		self.finals = finals

	def anyFinal(self, states):
		return any(state in self.finals for state in states)

	def accepts(self, s, currentStates=None):
		if currentStates is None:
			currentStates = set([self.initial])

		if len(currentStates) == 0:
			return False

		stateLambdaClosure = union([self.lambdaClosure(state) for state in currentStates])

		if s == "":
			return self.anyFinal(stateLambdaClosure)
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
		d = {}
		# for each transition: add those in the lambda closure..
		for state in self.nodes:
			stateLambdaClosure = self.lambdaClosure(state)
			reached = {}
			for extstate in stateLambdaClosure:
				for letter in self.transition[extstate]:
					if letter != "λ":
						if letter not in reached:
							reached[letter] = []
						reached[letter] += self.transition[extstate][letter]
			for letter in reached:
				reached[letter] = self.lambdaClosureOfSet(reached[letter])
			d[state] = reached

		finals = self.finals[:]

		if self.anyFinal(self.lambdaClosure(self.initial)):
			finals.append(self.initial)

		return NFA(d, self.initial, finals)

d = {
	0: {'0' : [0, 1], '1': [0, 2]},
	1: {'0' : [3]},
	2: {'1' : [3]},
	3: {'0' : [3], '1' : [3]}
}

a = NFA(d, 0, [3]) # (0|1)*(00|11)(0|1)*, i.e. string with 00 or 11
b = a.toDFA();

alphabet = "01"

MAX_LENGTH = 5
print "Accepted strings up to length %d:" % MAX_LENGTH
for length in xrange(MAX_LENGTH+1):
	for string in product(alphabet, repeat=length):
		s = ''.join(string)
		assert(a.accepts(s) == b.accepts(s))
		if b.accepts(s):
			print s if len(s) > 0 else "λ"



