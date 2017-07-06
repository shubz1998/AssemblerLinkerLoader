import sys

reg = {}
reg['A'] = 0
reg['B'] = 0
reg['C'] = 0
reg['D'] = 0
reg['E'] = 0
reg['F'] = 0
reg['G'] = 0
reg['H'] = 0
reg['PC'] = 0
reg['SP'] = 0

PC = 0
stack = []
oplen = {}
dbloc = []

memory = {}
MainMemoryValues = {}

# check if string passed is an integer
def isint(string):
    try:
        int(string)
        return True
    except:
        return False

def calculatelen():
	inputFile = open('opcodes.txt',"r")
	code = inputFile.read()
	lines = code.split('\n')
	for line in lines :
		line = line.lstrip().rstrip()
		if line != '' :
			oplen[line.split(' ')[0]] = int(line.split(' ')[1])

def load(filename, offset):
	inputFile = open(filename,"r")
	code = inputFile.read()
	lines = code.split('\n')
	mem = offset
	for line in lines :
		memory[mem] = line
		op = line.split(' ')[0].lstrip().rstrip()
		if op in oplen: # Main opcode
			mem += oplen[op]
		elif op[0] == "=": # for literals
			mem += 1
		else: # adding variables to variables table
			op = line.split(' ')[1].lstrip().rstrip()
			dbloc.append(mem)
			size = line.split(' ')[2]
			mem += int(oplen[op])*int(size)
	
def simulator(pc = 0):
	inst = memory[pc]
	opcode = inst.split(' ')[0]
	
	# for DS/DC type of statements
	try :
		if opcode not in oplen and inst.split(' ')[1].lstrip().rstrip() in oplen:
			opcode = inst.split(' ')[1].lstrip().rstrip()
	except :
		if opcode not in oplen:
			opcode = "LITTERAL"

	global stack
	memlocs = ''
	for db in dbloc:
		memlocs += (str(db) + ' : ' + str(memory[db].split(' ')[2]) + '\n')

	if opcode == 'HLT':
		return
	elif opcode == 'JMP':
		nextinst = int(inst.split(' ')[1])
		PC = nextinst
	elif opcode == 'MVI':
		regvar = inst.split(' ')[1].split(',')[0].lstrip().rstrip()  # First Operand
		secOperand = inst.split(' ')[2].lstrip().rstrip() # Second operand
		try:
			if isint(secOperand.split('\'')[1].lstrip().rstrip('\'')) :
				secOperand = secOperand.split('\'')[1].lstrip().rstrip('\'')
		except:
			pass
		reg[regvar] = int(secOperand)  
		PC = pc + int(oplen[opcode])
	elif opcode == 'ADI':
		reg['A'] = int(reg['A']) + int(inst.split(' ')[1])
		PC = pc + int(oplen[opcode])
	elif opcode == 'STA':
		memloc = int(inst.split(' ')[1])
		# memory[memloc] = int(reg['A'])
		MainMemoryValues[str(memloc)] = int(reg['A'])
		PC = pc + int(oplen[opcode])
	elif opcode == 'LDA':
		memloc = int(inst.split(' ')[1])
		# reg['A'] = int(memory[memloc])
		reg ['A'] = int(MainMemoryValues[str(memloc)])
		PC = pc + int(oplen[opcode])
	elif opcode == 'MOV':
		dest = inst.split(' ')[1].split(',')[0].lstrip().rstrip()
		src = inst.split(' ')[1].split(',')[1].lstrip().rstrip()
		# Register to memory
		if isint(dest):
			MainMemoryValues[dest] = reg[src]
		# Memory to Register
		elif isint(src):
			reg[dest] = MainMemoryValues[src]
		# Register to Register
		else:
			reg[dest] = reg[src]
		PC = pc + int(oplen[opcode])
	elif opcode == 'ADD':
		srcreg = inst.split(' ')[1]
		reg['A'] = int(reg['A']) + int(reg[srcreg])
		PC = pc + int(oplen[opcode])
	elif opcode == 'SUI':
		reg['A'] = int(reg['A']) - int(inst.split(' ')[1])
		PC = pc + int(oplen[opcode])
	elif opcode == 'SUB':
		srcreg = inst.split(' ')[1]
		reg['A'] = int(reg['A']) - int(reg[srcreg])
		PC = pc + int(oplen[opcode])
	elif opcode == 'ANI':
		reg['A'] = int(reg['A']) & int(inst.split(' ')[1])
		PC = pc + int(oplen[opcode])
	elif opcode == 'ANA':
		srcreg = inst.split(' ')[1]
		reg['A'] = int(reg['A']) & int(reg[srcreg])
		PC = pc + int(oplen[opcode])
	elif opcode == 'ORI':
		reg['A'] = int(reg['A']) | int(inst.split(' ')[1])
		PC = pc + int(oplen[opcode])
	elif opcode == 'ORA':
		srcreg = inst.split(' ')[1]
		reg['A'] = int(reg['A']) | int(reg[srcreg])
		PC = pc + int(oplen[opcode])
	elif opcode == 'PUSH':
		srcreg = inst.split(' ')[1]
		stack.append(int(reg[srcreg]))
		PC = pc + int(oplen[opcode])
	elif opcode == 'POP':
		srcreg = inst.split(' ')[1]
		reg[srcreg] = stack.pop()
		PC = pc + int(oplen[opcode])
	elif opcode == 'JNZ':
		nextinst = int(inst.split(' ')[1])
		if int(reg['A']) != 0:
			PC = nextinst
		else:
			PC = pc + int(oplen[opcode])
	elif opcode == 'JZ':
		nextinst = int(inst.split(' ')[1])
		if int(reg['A']) == 0:
			PC = nextinst
		else:
			PC = pc + int(oplen[opcode])
	elif opcode == 'JP':
		nextinst = int(inst.split(' ')[1])
		if int(reg['A']) > 0:
			PC = nextinst
		else:
			PC = pc + int(oplen[opcode])
	elif opcode == 'JM':
		nextinst = int(inst.split(' ')[1])
		if int(reg['A']) < 0:
			PC = nextinst
		else:
			PC = pc + int(oplen[opcode])
	elif opcode == "END":
		PC = pc + int(oplen[opcode])
	elif opcode == "DS":
		size = inst.split(' ')[2]
		PC = pc + int(oplen[opcode])*int(size)
	elif opcode == "CALL":
		reg['SP'] = pc
		functionAddress = inst.split(' ')[1].lstrip().rstrip()
		PC = functionAddress
	elif opcode == "RET":
		PC = reg['SP'] + oplen['CALL']
		reg['SP'] = 0
	elif opcode == "LITTERAL":
		PC = pc + 1
	reg['PC'] = PC

def callbackf():
	simulator(int(reg['PC']))

# Reset all the memory registers
def resetAll():
	global reg
	global PC
	global stack
	global dbloc
	global memory
	global MainMemoryValues

	reg['A'] = 0
	reg['B'] = 0
	reg['C'] = 0
	reg['D'] = 0
	reg['E'] = 0
	reg['F'] = 0
	reg['G'] = 0
	reg['H'] = 0
	reg['PC'] = 0
	reg['SP'] = 0

	PC = 0
	stack = []
	dbloc = []

	memory = {}
	MainMemoryValues = {}

calculatelen()