# -*- coding: utf-8 -*- 
#!/usr/bin/python

class RegularExpresion:
	
	def __str__(self):
		raise NotImplementedError


class Lambda(RegularExpresion):

	def __str__(self):
		return "λ"

class Symbol(RegularExpresion):

	def __init__(self, symbol):
		self.symbol = symbol

	def __str__(self):
		return self.symbol

class Or(RegularExpresion):

	def __init__(self, regexp1, regexp2):
		self.regexp1 = regexp1
		self.regexp2 = regexp2

	def __str__(self):
		return "(%s|%s)" % (str(self.regexp1), str(self.regexp2))

class Concatenate(RegularExpresion):

	def __init__(self, regexp1, regexp2):
		self.regexp1 = regexp1
		self.regexp2 = regexp2

	def __str__(self):
		return "%s%s" % (str(self.regexp1), str(self.regexp2))

class Star(RegularExpresion):

	def __init__(self, regexp1):
		self.regexp1 = regexp1

	def __str__(self):
		return "(%s)*" % str(self.regexp1)

class Plus(RegularExpresion):

	def __init__(self, regexp1):
		self.regexp1 = regexp1

	def __str__(self):
		return "(%s)+" % str(self.regexp1)


# ab(0|(ab|c)1)*

ab = Concatenate(Symbol("a"), Symbol("b"))
c = Symbol("c")
abORc = Or(ab, c)
abORc1 = Concatenate(abORc, Symbol("1"))
zeroORabORc1 = Or(Symbol("0"), abORc1)

r = Concatenate(Symbol("a"), Concatenate(Symbol("b"), Star(zeroORabORc1)))
print r