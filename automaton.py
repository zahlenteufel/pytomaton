# -*- coding: utf-8 -*- 
#!/usr/bin/python

from itertools import product # cartesian product
from collections import deque

class FA:

	def accepts(self, s, currentState=None):
		raise NotImplementedError

class DFA(FA):

	def __init__(self, nodes, transition, initial, finals):
		assert(initial in nodes and	all(n in nodes for n in transition.keys()) and 
			all(n in nodes for k in transition.keys() for n in transition[k].values()) and
			all(n in nodes for n in finals))
		self.nodes = nodes
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

	def getReachables(self):
		# Consider only the states reachable from the start (BFS):
		reachables = set()
		reachables.add(self.initial)
		queue = deque([self.initial])
		while queue:
			currentState = queue.popleft()
			for symbol in self.transition[currentState]:
				neighbour = self.transition[currentState][symbol]
				if neighbour not in reachables:
					queue.append(neighbour)
					reachables.add(neighbour)
		return list(reachables)

	def getIndistinguishablePartition(self, reachables):
		alphabet = set([symbol for state in reachables for symbol in self.transition[state]])
		
		distinct = [[False]*len(reachables) for _ in xrange(len(reachables))]
		index = {}
		for r in xrange(len(reachables)):
			index[reachables[r]] = r

		for i in xrange(len(reachables)):
			for j in xrange(i+1, len(reachables)):
				distinct[i][j] = self.isFinal(i) != self.isFinal(j)
		changed = True

		while changed:
			changed = False
			for i in xrange(len(reachables)):
				for j in xrange(i+1, len(reachables)):
					if not distinct[i][j]:
						for symbol in alphabet:
							trI = self.transition[reachables[i]].get(symbol, -1)
							trJ = self.transition[reachables[j]].get(symbol, -1)
							if trI == -1 or trJ == -1:
								if trI != trJ: # if only one of them is undefined on transition with symbol
									distinct[i][j] = True
									changed = True
							elif distinct[index[trI]][index[trJ]]:
								distinct[i][j] = True
								changed = True
		
		return partitionFromDistinctTable(reachables, distinct)

	def minimize(self):
		reachables = self.getReachables()

		P = self.getIndistinguishablePartition(reachables)

		# Translate the transitions, initial and finals to the new indexes

		newIndex = dict()
		for index in xrange(len(P)):
			for state in P[index]:
				newIndex[state] = index
		newFinals = list(set([newIndex[state] for state in reachables if self.isFinal(state)]))
		newInitial = newIndex[self.initial]
		newTransition = dict((newIndex[state], dict()) for state in reachables)
		for state in reachables:
			for symbol in self.transition[state]:
				newTransition[newIndex[state]][symbol] = newIndex[self.transition[state][symbol]]

		return DFA(newTransition.keys(), newTransition, newInitial, newFinals)

def partitionFromDistinctTable(reachables, distinct):
	parent = [i for i in xrange(len(reachables))]
	for i in xrange(len(reachables)):
		for j in xrange(i+1, len(reachables)):
			if not distinct[i][j]:
				# merge class i and class j
				classI = parent[i]
				classJ = parent[j]
				newClass = min(classI, classJ)
				for k in xrange(len(reachables)):
					if parent[k] in (classI, classJ):
						parent[k] = newClass
	P = []
	for i in xrange(len(reachables)):
		if i == parent[i]:
			indistinguishableClass = [reachables[i]]
			for j in xrange(i+1, len(reachables)):
				if parent[j] == i:
					indistinguishableClass.append(reachables[j])
			P += [indistinguishableClass]
	return P


def flatten(listoflist):
	return [item for sublist in listoflist for item in sublist]

def union(c):
	return set(flatten(c))

class NFA(FA):

	def __init__(self, nodes, transition, initial, finals):
		assert(initial in nodes and
			all(n in nodes for n in transition.keys()) and
			all(n in nodes for k in transition.keys() for c in transition[k].values() for n in c) and
			all(n in nodes for n in finals)
			)
		self.nodes = nodes
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
				for symbol in T:
					if symbol not in next:
						next[symbol] = set()
					next[symbol] |= set(T[symbol])
			for symbol in next:
				nextState = tuple(next[symbol])
				d[currentStates][symbol] = nextState
				if nextState not in seen:
					queue.append(nextState)
					seen.add(nextState)
		finals = []
		for states in d:
			if self.anyFinal(states):
				finals.append(states)
		return DFA(d.keys(), d, initial, finals)

class NFAlambda(FA):

	def __init__(self, nodes, transition, initial, finals):
		assert(initial in nodes and
			all(n in nodes for n in transition.keys()) and
			all(n in nodes for k in transition.keys() for c in transition[k].values() for n in c) and
			all(n in nodes for n in finals)
			)
		self.nodes = nodes
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
				for symbol in self.transition[extstate]:
					if symbol != "λ":
						if symbol not in reached:
							reached[symbol] = []
						reached[symbol] += self.transition[extstate][symbol]
			for symbol in reached:
				reached[symbol] = self.lambdaClosureOfSet(reached[symbol])
			d[state] = reached

		finals = self.finals[:]

		if self.anyFinal(self.lambdaClosure(self.initial)):
			finals.append(self.initial)

		return NFA(d.keys(), d, self.initial, finals)

d = {
	0: {'0' : [0], 'λ': [1]},
	1: {'1' : [1], 'λ': [2]},
	2: {'2' : [2]}
}

a = NFAlambda(d.keys(), d, 0, [2]) # 0*1*2*

b = a.toNFA().toDFA().minimize()

alphabet = "01"

MAX_LENGTH = 10
print "Accepted strings up to length %d:" % MAX_LENGTH
for length in xrange(MAX_LENGTH+1):
	for string in product(alphabet, repeat=length):
		s = ''.join(string)
		assert(a.accepts(s) == b.accepts(s))
		if a.accepts(s):
			print s if len(s) > 0 else "λ"