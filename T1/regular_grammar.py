import non_deterministic_automaton
from globals import *

'''
	for regular grammars only
'''

class Grammar:
	def __init__(self, productions, name = None, add = False):
		if len(productions) is 0:
			return None
		self.productions = self.validate_productions(productions)
		if name is None:
			self.name = 'G' + str(Globals.grammar_count)
			if add:
				Globals.grammar_count += 1
		else:
			self.name = name
		if self not in Globals.grammars and add:
			Globals.grammars.append(self)

	def validate_productions(self, productions):
		prods = []
		hasEpsilon = False
		for p in productions:
			if len(p.rightSide) > 2 or len(p.rightSide) < 1 or len(p.leftSide) != 1 or\
				(p.rightSide[0] is '&' and p.leftSide != productions[0].leftSide) or\
				p.rightSide[0].isupper() or (len(p.rightSide) is 2 and not p.rightSide[-1].isupper()) or\
				not p.leftSide.isupper() or not (p.rightSide[0].islower() or p.rightSide[0].isdigit() or\
				p.rightSide[0] is '&'):
				continue
			else:
				if p.rightSide[0] is '&':
					hasEpsilon = True
				prods.append(p)
		if hasEpsilon:
			prods2 = []
			for p in prods:
				if len(p.rightSide) is 2 and p.rightSide[-1] is productions[0].leftSide[0]:
					continue
				else:
					prods2.append(p)
			prods = prods2
		return prods


	def __hash__(self):
		hashable = self.name
		sigma = 0
		i = 1
		for c in hashable:
			sigma += ord(c) * i
			i += 1
		return sigma

	def __eq__(self, other):
		return self.__hash__() == other.__hash__()

	'''
		this function outputs all the sentences generated by this grammar with
		size less than or equal to the argument "size"
	'''
	def produce(self, size, comment = False):
		if len(self.productions) == 0:
			return []
		sentences = []
		if size is 0:
			for p in self.productions:
				if p.rightSide is '&' and p.leftSide is self.productions[0].leftSide:
					return ['&']
		sForms = [self.productions[0].leftSide]
		old_curr = sForms[0]
		while len(sForms) != 0:
			curr_sym = sForms[0][-1]
			for prods in self.productions:
				if curr_sym == prods.leftSide[-1]:
					curr_form = ''.join(sForms[0].rsplit(sForms[0][-1]))
					curr_form = curr_form + prods.rightSide
					if comment:
						print(sForms[0] + " -> " + curr_form)
					if len(curr_form) <= size:
						if all(s.isdigit() or s.islower() for s in curr_form):
							if curr_form not in sentences:
								sentences.append(curr_form)
						else:
							sForms.append(curr_form)
			sForms.pop(0)
		return sentences

	def getAlphabet(self):
		Σ = set()
		for prod in self.productions:
			Σ.add(prod.rightSide[0])
		return list(Σ)

	def has_empty_sentence(self):
		for p in self.productions:
			if p.leftSide == 'S' and p.rightSide == '&':
				return True
		return False

	def __str__(self):
		if len(self.productions) == 0:
			return ""
		stringerson = ""
		leftSides = set()
		first = True
		for prods in self.productions:
			if prods.leftSide != self.productions[0].leftSide:
				leftSides.add(prods.leftSide)
		leftSides = [self.productions[0].leftSide] + sorted(leftSides)
		for lefts in leftSides:
			for prods in self.productions:
				if first and lefts is prods.leftSide:
					stringerson = stringerson + lefts + " -> " + prods.rightSide
					first = False
				elif lefts is prods.leftSide:
					stringerson = stringerson + " | " + prods.rightSide
			stringerson = stringerson + "\n"
			first = True
		return stringerson

	def get_non_terminals(self):
		ret = []
		for p in self.productions:
			if not p.leftSide == 'S':
				ret.append(p.leftSide)

		return ['S'] + sorted(list(set(ret)), key=str.lower)

	'''
		this function outputs the productions of a given non-terminal
		e.g if the non_terminal has the following productions:  B -> bS | aC | a,
		the function is supposed to output [bS, aC, a]
	'''
	def get_productions_from(self, non_terminal):
		ret = []
		for p in self.productions:
			if p.leftSide == non_terminal:
				ret.append(p.rightSide)
		return ret

	'''
		this functions outputs the productions in lexical order
		e.g: if the non_terminal has the following productions: B -> bS | aC | a,
		the functions is supposed to output [a, aC, bS]
	'''
	def get_ord_productions_from(self, non_terminal):
		ret = []
		for p in self.productions:
			if p.leftSide == non_terminal:
				ret.append(p.rightSide)
		return sorted(ret, key=str.lower)

	'''
		this functions works the same way as the function above, but it outputs
		the productions in lists. E.g: if the non_terminal has the following productions: B -> bS | aC | a,
		the functions is supposed to output [[a, aC], [bS]]
	'''
	def _get_ord_productions_from(self, non_terminal):
		sorted = self.get_ord_productions_from(non_terminal)
		lastSymbol = sorted[0][0]
		add = []
		ret = []
		t = 0
		for p in sorted:
			if p[0] == lastSymbol:
				add.append(p)
			else:
				ret.append(add)
				lastSymbol = p[0]
				add = []
				add.append(p)
		ret.append(add)
		return ret

	def convert_to_automaton(self):
		alphabet = list(set(self.getAlphabet()) - {'&'})
		sfinal = False
		if self.has_empty_sentence():
			sfinal = True
		print(alphabet)
		states = {s:non_deterministic_automaton.NDState(s) for s in self.get_non_terminals()}
		states_str = {s for s in self.get_non_terminals()} #alguém me mata
		# state that accepts the input
		λ = non_deterministic_automaton.NDState('λ', True)
		λ.isAccptance = True
		φ = non_deterministic_automaton.NDState('φ')
		for s in alphabet:
			λ.add_transition(non_deterministic_automaton.NDTransition(s, [φ]))
			φ.add_transition(non_deterministic_automaton.NDTransition(s, [φ]))
		for s in states:
			prods = self._get_ord_productions_from(s.__str__())
			for prod in prods:
				sset = []
				for i in prod:
					symbol = i[0] #terminal symbol
					if len(i) == 1:
						sset.append(λ)
					else:
						nt = i[1]
						next_state = states[nt]
						sset.append(next_state)
				t = non_deterministic_automaton.NDTransition(symbol, sset)
				sset = []
				states[s].add_transition(t)

		states['λ'] = λ
		states['φ'] = φ

		for sstr in states_str:
			for symbol in alphabet:
				add = True
				for t in states[sstr].ndtransitions:
					if t.symbol == symbol:
						add = False
						break
				if add:
					states[sstr].add_transition( non_deterministic_automaton.NDTransition(symbol, [φ]))
		initialState = states[self.productions[0].leftSide]
		finalStates = [λ]
		if self.has_empty_sentence() or sfinal:
			finalStates.append(initialState)
			initialState.isAccptance = True
		print("sentences = ", end="")
		print(non_deterministic_automaton.NDAutomaton(states.values(), finalStates, initialState, alphabet).\
			n_first_sentences_accepted(4))
		return non_deterministic_automaton.NDAutomaton(states.values(), finalStates, initialState, alphabet)

	def add_production(self, prod):
		self.productions.append(prod)

class Production:
	def __init__(self, leftSide, rightSide):
		self.leftSide = leftSide
		self.rightSide = rightSide

	def __str__(self):
		return self.leftSide + " -> " + self.rightSide

	def __repr__(self):
		return str(self)

	def isTerminalProduction(self):
		return len(self.rightSide) == 1

	def __hash__(self):
		hashable = self.leftSide + self.rightSide
		sigma = 0
		i = 1
		for c in hashable:
			sigma += ord(c) * i
			i += 1
		return sigma

	def __eq__(self, other):
		return self.__hash__() == other.__hash__()
