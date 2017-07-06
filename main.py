import assembler, linker, loader, simulation

x = []

# Run Assembler Pass1
def runass():
	assembler.pass1(x)

# Run Linker
def runlin():
	linker.link(x)

# Run Loader
def runload(offset=0):
	loader.convert(x, offset)
	simulation.reg['PC'] = offset

# Get symbols table
def getSymTable():
	return assembler.symtab

# Get literals table
def getLitTable():
	return assembler.littab2

# Get Global table
def getGlobTable():
	return assembler.globtab

# Get Extern table
def getExtTable():
	return {}
	return assembler.extTable

# Get If table
def getifTable():
	return assembler.iftable

# Run Loader
def runloader(file, offset=0):
	simulation.load(file, offset)

# Simulation
def runSimulator():
	simulation.callbackf()

# Get register values
def getRegisters():
	return simulation.reg

# get Stack of simulator
def getStack():
	return simulation.stack

# get memory locations of simulator
def getMemlocs():
	return simulation.memory

# Get the stored values of variables in the memory
def getMemData():
	return simulation.MainMemoryValues

def resetAll():
	simulation.resetAll()
