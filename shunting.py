####
# Constants
####
numbers = "0123456789"
operators = "+-*/^%"
whitespace = "\r\n\t "

####
# Tokenizer
####
class TokenizerError(Exception): pass

class Tokenizer:
	def __init__(self, text):
		self._text = text + " "
		self._tokens = list()
		self._buffer = ""
		self._state = "init"
	
	def nextToken(self):
		while len(self._tokens) == 0 and len(self._text) != 0:
			self.stepChar()
		if len(self._tokens) > 0:
			return self._tokens.pop(0)
		else:
			return None
	
	def __iter__(self):
		while True:
			t = self.nextToken()
			if t == None: break
			yield t

	def stepChar(self):
		c = self._text[0]
		self._text = self._text[1:]
		if   self._state == "init":
			if   c in numbers:
				self._buffer = c
				self._state = "number"
			elif c in operators:
				self._tokens.append(("operator", c))
			elif c == "(":
				self._tokens.append(("lparen",))
			elif c == ")":
				self._tokens.append(("rparen",))
			elif c in whitespace:
				pass
			else:
				raise TokenizerError("unexpected '%s'" % c)
		elif self._state == "number":
			if   c in numbers:
				self._buffer += c
			elif c in operators:
				self._tokens.append(("number", float(self._buffer)))
				self._tokens.append(("operator", c))
				self._state = "init"
			elif c == "(":
				self._tokens.append(("number", float(self._buffer)))
				self._tokens.append(("lparen",))
				self._state = "init"
			elif c == ")":
				self._tokens.append(("number", float(self._buffer)))
				self._tokens.append(("rparen",))
				self._state = "init"
			elif c in whitespace:
				self._tokens.append(("number", float(self._buffer)))
				self._state = "init"
			else:
				raise TokenizerError("unexpected '%s'" % c)

def tokenize(text):
	t = Tokenizer(text)
	return [tok for tok in t]

####
# Shunting yard algorithm
####
Assoc_Left  = 0
Assoc_Right = 1

opertable = {
	"+": (Assoc_Left,  1),
	"-": (Assoc_Right, 1),
	"*": (Assoc_Left,  2),
	"/": (Assoc_Left, 2),
	"^": (Assoc_Right, 4),
	"%": (Assoc_Left, 3),
}

def shunt(tokens):
	tokens = list(tokens)
	out = list()
	stack = list()
	for token in tokens:
		if token[0] == "operator":
			o1 = token[1]
			props = opertable[o1]
			while len(stack) > 0:
				o2 = stack[-1]
				if o2 == "(":
					stack.pop(-1)
					break
				else:
					p = opertable[o2]
					if (p[0] == Assoc_Left and p[1] >= props[1]) or (p[1] == Assoc_Right and p[1] > props[1]):
						stack.pop(-1)
						out.append(o2)
					else:
						break
			stack.append(o1)
		elif token[0] == "number":
			out.append(token[1])
		elif token[0] == "lparen":
			stack.append("(")
		elif token[0] == "rparen":
			while len(stack) > 0:
				if stack[-1] == "(":
					break
				else:
					out.append(stack.pop(-1))
	for oper in stack[::-1]:
		out.append(oper)
	return out

####
# Calculator
####
def stackop(ac):
	def decorator(f):
		def wrapper(stack):
			args = list()
			for i in range(ac):
				args.append(stack.pop(-1))
			stack.append(f(*args))
		return wrapper
	return decorator

operfuncs = dict([(k, stackop(2)(v)) for k, v in {
	"+": lambda x, y: x + y,
	"-": lambda x, y: x - y,
	"*": lambda x, y: x * y,
	"/": lambda x, y: x / y,
	"^": lambda x, y: x ** y,
	"%": lambda x, y: x % y,
}.items()])

def calc(toks):
	if len(toks) == 0: return 0
	stack = list()
	for t in toks:
		if   type(t) == float:
			stack.append(t)
		else:
			operfuncs[t](stack)
	return stack[0]

if __name__ == "__main__":
	while True:
		s = input("=> ")
		print(calc(shunt(tokenize(s))))
