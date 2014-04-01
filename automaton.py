# -*- coding: utf-8 -*- 
#!/usr/bin/python

from itertools import product # cartesian product
from collections import deque

class FA:
	pass

def getSublistNumber(listoflists):
	d = dict()
	for i in xrange(len(listoflists)):
		for elem in listoflists[i]:
			d[elem] = i
	return d


class DFA(FA):

	def __init__(self, transition, initial, finals):
		#TODO: check correctness of the the input
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

	def split(self, X, indexOf, a):
		# print X, indexOf, a
		preimg = {}
		# print indexOf
		for state in X:
			# print state, "-",a,"->", self.transition[state].get(a, None)
			index = indexOf.get(self.transition[state].get(a, None), None)
			if index not in preimg:
				preimg[index] = set()
			preimg[index].add(state)
		# print preimg
		return preimg.values()

	def minimize(self):
		# Consider only the states reachable from the start (BFS):
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
		
		alphabet = set([letter for state in reachables for letter in self.transition[state]])
		
		# Refine the partition

		F = [state for state in reachables if self.isFinal(state)]
		notF = [state for state in reachables if state not in F]
		P = [notF, F]

		anySplit = True
		while anySplit:
			indexOf = getSublistNumber(P)
			P2 = []
			anySplit = False
			while P:
				X = P.pop()
				if len(X) <= 1:
					P2.append(X)
					continue
				for letter in alphabet:
					Xs = self.split(X, indexOf, letter)
					if len(Xs) > 1:
						anySplit = True
						P2 += Xs
						break
				else:
					P2.append(X)
			P = P2

		# Translate the transitions, initial and finals to the new indexes

		newIndex = dict()
		for index in xrange(len(P)):
			for state in P[index]:
				newIndex[state] = index
		newFinals = list(set([newIndex[state] for state in F]))
		newInitial = newIndex[self.initial]
		newTransition = dict((newIndex[state], dict()) for state in reachables)
		for state in reachables:
			for letter in self.transition[state]:
				newTransition[newIndex[state]][letter] = newIndex[self.transition[state][letter]]

		return DFA(newTransition, newInitial, newFinals)

def flatten(listoflist):
	return [item for sublist in listoflist for item in sublist]

def union(c):
	return set(flatten(c))

class NFA(FA):

	def __init__(self, transition, initial, finals):
		#TODO: check correctness of the the input
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
		#TODO: check correctness of the the input
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
	0: {'0': 3, '1': 1},
	1: {'0': 2},
	2: {},
	3: {'0': 4},
	4: {}
}

a = DFA(d, 0, [2, 4]) # (1|0)0

b = a.minimize()


alphabet = "01"

MAX_LENGTH = 5
print "Accepted strings up to length %d:" % MAX_LENGTH
for length in xrange(MAX_LENGTH+1):
	for string in product(alphabet, repeat=length):
		s = ''.join(string)
		assert(a.accepts(s) == b.accepts(s))
		if a.accepts(s):
			print s if len(s) > 0 else "λ"



