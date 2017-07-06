'''
AUTHOR :-   Roopansh Bansal     150101053
			Shivam Gupta        150101068
			Shubham Singhal     150101072
'''

import re

filelentab = {}
optab = {}
symtab = {}
funtab = {}
arraytab = {}
littab = {}
littab2 = {}
pooltab = []
globtab = {}
iftable = {}
error = "False"
pass1code = ''
vartab = {}
fcalls = {}
loops = 0

# read the opcodes file and store in optab along with opcode length
def findoptab():
	with open("opcodes.txt", "r") as file:
		opcodes = file.read().split("\n")
		file.close()
	for opcode in opcodes:
		opcode = opcode.lstrip().rstrip()
		if opcode != '':
			optab[opcode.split()[0]] = int(opcode.split()[1])

# check if string passed is an integer
def isint(string):
	try:
		int(string)
		return True
	except:
		return False


def pass1(fileNames):
	# to inform python that we are gonna update global vars and not the local ones
	global error
	global optab
	global symtab
	global funtab
	global globtab
	global arraytab
	global littab
	global littab2
	global pooltab
	global filelentab
	global location_counter
	global pooltab_counter
	global function_counter
	global pass1code
	global iftable
	global fcalls  
	global loops
	findoptab()

	'''
	REGULAR EXPRESSIONS
	'''

	# Variable declartions
	revar = re.compile("var\s+(\w+)\s*=\s*(\w+)\s*")
	reglo = re.compile("global\s+(\w+)\s*=\s*(\w+)\s*")
	reext = re.compile("extern\s+(\w+)\s*")

	# Arithmatic
	replus = re.compile("\s*(\w+)\s*=\s*(\w+)\s*\+\s*(\w+)\s*")
	reminus = re.compile("\s*(\w+)\s*=\s*(\w+)\s*-\s*(\w+)\s*")
	remul = re.compile("\s*(\w+)\s*=\s*(\w+)\s*\*\s*(\w+)\s*")
	rediv = re.compile("\s*(\w+)\s*=\s*(\w+)\s*\/\s*(\w+)\s*")
	
	# If Blocks
	reifgt = re.compile("\s*if\s+(\w+)\s*>\s*(\w+)\s*")
	reifeq = re.compile("\s*if\s+(\w+)\s*=\s*(\w+)\s*")
	reiflt = re.compile("\s*if\s+(\w+)\s*<\s*(\w+)\s*")
	reendif = re.compile("\s*endif\s*")

	# Bitwise AND/OR
	reand = re.compile("\s*(\w+)\s*=\s*(\w+)\s*&\s*(\w+)\s*")
	reor = re.compile("\s*(\w+)\s*=\s*(\w+)\s*\|\s*(\w+)\s*")

	# Array
	rearray = re.compile("\s*var\s+(\w+)\[(\w+)\]\s*")
	reassarr = re.compile("\s*(\w+)\[(\w+)\]\s*=\s*(\w+)\s*")

	# Loops
	reloop = re.compile("\s*loop\s+(\w+)\s*")
	reendloop = re.compile("\s*endloop\s*")

	# Functions
	refunction = re.compile("\s*function\s+(\w+)\s*")
	renfun = re.compile("\s*endfunction\s*")
	recall = re.compile("\s*(\w+)\(\)")
	reextf = re.compile("\s*extern\s+function\s+(\w+)\(\)\s*")

	# Min/Max
	# a = min(b,c,5,7,e)
	remin = re.compile("\s*(\w+)\s*=\s*min\s*\((.*)\)\s*")
	# a = max(b,c,5,7,e)
	remax = re.compile("\s*(\w+)\s*=\s*max\s*\((.*)\)\s*")

	# to implement goto statements
	# jump for jump statement and tag to define that address
	rejump = re.compile("\s*JUMP\s+(\w+)\s*")
	retag = re.compile("\s*(\w+)[:]\s*")

	remacro = re.compile("\s*macro\s*")
	remend = re.compile("\s*mend\s*")


	for filenam in fileNames:
		with open(filenam, 'r') as file:
			code = file.read()
			lines = code.split('\n')
			file.close()

		# get the filename
		filename = filenam.split('.')[0]

		pooltab_counter = 0
		location_counter = 0
		function_counter = 0

		# update location counter in start statment.
		ifs = 0

		assemblycode = []
		symtab[filename] = {}
		funtab[filename] = {}
		arraytab[filename] = {}
		littab[filename] = []
		littab2[filename] = {}
		globtab[filename] = {}
		vartab[filename] = []
		fcalls = {}
		macro = {}

		macro_define=0
		codelines=[]

		for line in lines:
			line = line.lstrip().rstrip()

			if remacro.match(line):
				macro_define=1
				continue
			
			elif remend.match(line):
				macro_define=0
				continue

			elif (macro_define !=0 ):
				if(macro_define ==1):
					macro_name=line.split(' ',1)[0].lstrip().rstrip()

					if(len(line.split(' ',1)) != 1):
						macro_vars=line.split(' ',1)[1].replace(" ","")
						macro_varscount=len(macro_vars.split(','))
						macro_variables=[]
						for i in range(macro_varscount):
							temp_var=macro_vars.split(',')[i]
							temp_value=""
							if "&" in temp_var and "=" in temp_var:
								temp_type=2
								temp_value=temp_var.split("=")[1]
								temp_name=temp_var.split('&')[1].split("=")[0]

							elif "&" in temp_var:
								# might add some error handling later for case when it is of this type 
								# but while using macro is not in current order
								temp_type=1
								temp_name=temp_var.split('&')[1]
							
							else:
								temp_type=3
								temp_name=temp_var
							macro_variables.append([temp_name,temp_value,temp_type])
							# might have to add temp_defaultvalue as seperate then varvalue
					else:
						macro_variables=[]

					macro_define=2
					macro[macro_name] = {}
					macro[macro_name]["code"] = []
					macro[macro_name]["variable"]=macro_variables

				else:
					macro[macro_name]["code"].append(line)

				continue


			elif (line.split(' ')[0].lstrip().rstrip() in macro):
				m_name=line.split(' ',1)[0].lstrip().rstrip()
				code=macro[m_name]["code"]
				variables=macro[m_name]["variable"]

				if(len(line.split(' ',1)) !=1):
					params = line.split(' ', 1)[1].split(',')
				else:
					params=[]
				count=0
				for p in params:
					param = p.lstrip().rstrip().split("=")

					if "=" in p:
						parameter = param[0]
						flag=0
						for i,v in enumerate(variables):
							if (parameter == v[0]):
								variables[i][1]=param[1]
								flag=1
								break
								
						if flag is 0:
							error = "Error in macor parameters"
							return error
						# macro_variables=[temp_varname,temp_varvalue,temp_vartype]
					
					else:
						variables[count][1]=param[0]
						count=count+1

				for i,l in enumerate(code):
					for v in variables:
						code[i]=code[i].replace(v[0],v[1])
				
				codelines= codelines+code
				# lines. 
			else:
				codelines.append(line)

		for line in codelines:
			
			if reglo.match(line):
				var1 = reglo.match(line).group(1)
				var2 = reglo.match(line).group(2)
				
				if (not isint(var2) and var2 not in symtab[filename]) or isint(var1):
					error = "Variable " + var2 + " not declared" + "in" + line
					return
				
				# global 5
				if isint(var1):
					error = "Expected variable" + "in" + line
				
				# global a = 5 
				if isint(var2):
					# move in a register the value(immeidate data avaialble)
					assemblycode.append("MVI D, ='" + str(var2) + "'")
					# move register in storage element(in DS)
					assemblycode.append("MOV " + '#' + str(var1) +",D")
					# push the symbol in symtab[filename] and symbol name along with #(representing a var)
					symtab[filename][var1] ='#' + str(var1)
					globtab[filename][var1] ='#' + str(var1)
					# push in pooltab current poolctr and in liitab[filename] with value and location counter(just for now)
					pooltab.append(pooltab_counter)
					littab[filename].append((var2,globtab[filename][var1]))
					littab2[filename][var2] = var1
					pooltab_counter = pooltab_counter + 1
					location_counter = location_counter + optab['MVI'] + optab['MOV']
				# global a = c
				else:
					# in pass 1 enter the symbol c from the symtab (we also get the value what type of var it is via it's symbol)
					assemblycode.append("MOV D," + str(symtab[filename][var2]))  # load to any register
					# push in symtab along with symbil
					symtab[filename][var1] ='#' + str(var1)
					globtab[filename][var1] ='#' + str(var1)
					assemblycode.append("MOV " + str(symtab[filename][var1]) + ',D ')  # load from that register
					location_counter = location_counter + optab['LDA'] + optab['STA']
				vartab[filename].append(var1)

			elif revar.match(line):
				var1 = revar.match(line).group(1)
				var2 = revar.match(line).group(2)
				#  var a = someundeclared
				if (not isint(var2) and var2 not in symtab[filename]) or isint(var1):
					error = "Variable " + var2 + " not declared" + "in" + line
					return
				# var 5 
				if isint(var1):
					error = " Syntax error => Expected variable " + "in" + line
					return
				# var a = 5
				if isint(var2):
					assemblycode.append("MVI D, ='" + str(var2) + "'")
					assemblycode.append("MOV " + '#' + str(var1) +",D")
					# push the symbol in symtab[filename] and current location counter just for now(will be updated in pass2
					symtab[filename][var1] ='#' + str(var1)
					pooltab.append(pooltab_counter)
					# push in pooltab and in liitab[filename] with value and location counter(just for now)
					littab[filename].append((var2, symtab[filename][var1]))
					littab2[filename][var2] = var1
					pooltab_counter = pooltab_counter + 1
					location_counter = location_counter + optab['MVI'] + optab['MOV']
				# var a  =d
				else:
					# in pass 1 enter the symbol c from the symtab (we also get the value what type of var it is via it's symbol)
					assemblycode.append("MOV D," + symtab[filename][var2])  # load to any register
					# push in symtab
					symtab[filename][var1] ='#' + str(var1)
					assemblycode.append("MOV " + symtab[filename][var1] + ',D ')  # load from that register
					location_counter = location_counter + optab['MOV'] + optab['MOV']
				vartab[filename].append(var1)

			# extern a 
			elif reext.match(line):
				var = reext.match(line).group(1)
				if isint(var):
					error = "Expected variable in " + line
					return
				# just enter in symbtab of that fiule. WIll be handled by linker seeing that $ symbol
				symtab[filename][var] = "$" + str(var)
			# extern function
			elif reextf.match(line):
				fname = reextf.match(line).group(1)
				symtab[filename][fname] = "$" + str(fname)

			elif replus.match(line):
				# var1 =var2 +var3
				var1 = replus.match(line).group(1)
				var2 = replus.match(line).group(2)
				var3 = replus.match(line).group(3)
				if isint(var1) or var1 not in symtab[filename]:
					error = "syntax error =>  " + line
					return

				# e.g-a=2+3
				if isint(var2) and isint(var3):
					assemblycode.append("MVI A, " + str(var2))
					assemblycode.append("ADI " + str(var3))
					assemblycode.append("STA " + str(symtab[filename][var1]))
					location_counter = location_counter + optab['MVI'] + optab['ADI'] + optab['STA']

				# eg- a=2+b
				elif isint(var2):
					if var3 not in symtab[filename]:
						error = "Variable " + var3 + " not declared in " + line
						return

					assemblycode.append("LDA " + str(symtab[filename][var3]))
					assemblycode.append("ADI " + str(var2))
					assemblycode.append("STA " + str(symtab[filename][var1]))
					location_counter = location_counter + optab['LDA'] + optab['ADI'] + optab['STA']

				# eg- a=b+2
				elif isint(var3):
					if var2 not in symtab[filename]:
						error = "Variable " + var3 + " not declared in " + line
						return
					assemblycode.append("LDA " + str(symtab[filename][var2]))
					assemblycode.append("ADI " + str(var3))
					assemblycode.append("STA " + str(symtab[filename][var1]))
					location_counter = location_counter + optab['LDA'] + optab['ADI'] + optab['STA']

				# eg a=b+c
				else:
					if var2 not in symtab[filename] or var3 not in symtab[filename]:
						error = "Variable not declared in " + line
						return
					# pick from symtable that particular vbariable 
					assemblycode.append("LDA " + str(symtab[filename][var2]))
					assemblycode.append("MOV B,A")
					assemblycode.append("LDA " + str(symtab[filename][var3]))
					assemblycode.append("ADD B")
					assemblycode.append("STA " + str(symtab[filename][var1]))
					location_counter = location_counter + optab['LDA'] + optab['MOV'] + optab['LDA'] + optab['ADD'] + optab['STA']

			elif reminus.match(line):
				var1 = reminus.match(line).group(1)
				var2 = reminus.match(line).group(2)
				var3 = reminus.match(line).group(3)
				if isint(var1) or var1 not in symtab[filename]:
					error = "syntax error =>  " + line
					return

				# e.g-a=2-3
				if isint(var2) and isint(var3):
					assemblycode.append("MVI A, " + str(var2))
					assemblycode.append("SUI " + str(var3))
					assemblycode.append("STA " + str(symtab[filename][var1]))
					location_counter = location_counter + optab['MVI'] + optab['SUI'] + optab['STA']

				# eg- a=2-b
				elif isint(var2):
					if var3 not in symtab[filename]:
						error = "Variable " + var3 + " not declared in " + line
						return

					assemblycode.append("MVI A, " + str(var2))
					assemblycode.append("MOV B," + str(symtab[filename][var3]))
					assemblycode.append("SUB B")
					assemblycode.append("STA " + str(symtab[filename][var1]))
					location_counter = location_counter + optab['LDA'] + optab['SUI'] + optab['STA']

				# eg- a=b-2
				elif isint(var3):
					if var2 not in symtab[filename]:
						error = "Variable " + var3 + " not declared in " + line
						return

					assemblycode.append("LDA " + str(symtab[filename][var2]))
					assemblycode.append("SUI " + str(var3))
					assemblycode.append("STA " + str(symtab[filename][var1]))
					location_counter = location_counter + optab['LDA'] + optab['SUI'] + optab['STA']

				# eg a=b-c
				else:
					if var2 not in symtab[filename] or var3 not in symtab[filename]:
						error = "Variable not declared in " + line
						return

					assemblycode.append("LDA " + str(symtab[filename][var3]))
					assemblycode.append("MOV B,A")
					assemblycode.append("LDA " + str(symtab[filename][var2]))
					assemblycode.append("SUB B")
					assemblycode.append("STA " + str(symtab[filename][var1]))
					location_counter = location_counter + optab['LDA'] + optab['MOV'] + optab['LDA'] + optab['SUB'] + optab['STA']

			# # used fro  variables and in multiply function both.should replace in multiply by someother symbol b
			elif remul.match(line):
				var1 = remul.match(line).group(1)
				var2 = remul.match(line).group(2)
				var3 = remul.match(line).group(3)
				if isint(var1) or var1 not in symtab[filename]:
					error = "syntax error =>  " + line
					return
				# c = 3*5
				if isint(var2) and isint(var3):
					assemblycode.append("MVI B, 0")
					assemblycode.append("MVI A, " + str(var3))
					location_counter = location_counter + optab["MVI"] + optab["MVI"]
					assemblycode.append("JZ #" + str(
						location_counter + optab["JZ"] + optab["MOV"] + optab["MVI"] + optab["ADD"] + optab["MOV"] +
						optab["MOV"] + optab["SUI"] + optab["JMP"]))
					assemblycode.append("MOV C,A")
					assemblycode.append("MVI A, " + str(var2))
					assemblycode.append("ADD B")
					assemblycode.append("MOV B,A")
					assemblycode.append("MOV A,C")
					assemblycode.append("SUI 1")
					assemblycode.append("JMP %" + str(location_counter))
					assemblycode.append("MOV A,B")
					assemblycode.append("STA " + str(symtab[filename][var1]))
					location_counter = location_counter + optab["JZ"] + optab["MOV"] + optab["MVI"] + optab["ADD"] + \
									   optab[
										   "MOV"] + optab["MOV"] + optab["SUI"] + optab["JMP"] + optab["MOV"] + optab[
										   "STA"]
				# c = 3*a
				elif isint(var2):
					if var3 not in symtab[filename]:
						error = "syntax error =>  " + line
						return
					assemblycode.append("MVI B, 0")
					assemblycode.append("LDA " + str(symtab[filename][var3]))
					location_counter = location_counter + optab["MVI"] + optab["LDA"]
					assemblycode.append("JZ #" + str(
						location_counter + optab["JZ"] + optab["MOV"] + optab["MVI"] + optab["ADD"] + optab["MOV"] +
						optab["MOV"] + optab["SUI"] + optab["JMP"]))
					assemblycode.append("MOV C,A")
					assemblycode.append("MVI A, " + str(var2))
					assemblycode.append("ADD B")
					assemblycode.append("MOV B,A")
					assemblycode.append("MOV A,C")
					assemblycode.append("SUI 1")
					assemblycode.append("JMP %" + str(location_counter))
					assemblycode.append("MOV A,B")
					assemblycode.append("STA " + str(symtab[filename][var1]))
					location_counter = location_counter + optab["JZ"] + optab["MOV"] + optab["MVI"] + optab["ADD"] + \
									   optab[
										   "MOV"] + optab["MOV"] + optab["SUI"] + optab["JMP"] + optab["MOV"] + optab[
										   "STA"]
				# c = b*3
				elif isint(var3):
					if var2 not in symtab[filename]:
						error = "syntax error =>  " + line
						return
					assemblycode.append("MVI B, 0")
					assemblycode.append("LDA " + str(symtab[filename][var2]))
					location_counter = location_counter + optab["MVI"] + optab["LDA"]
					assemblycode.append("JZ %" + str(
						location_counter + optab["JZ"] + optab["MOV"] + optab["MVI"] + optab["ADD"] + optab["MOV"] +
						optab["MOV"] + optab["SUI"] + optab["JMP"]))
					assemblycode.append("MOV C,A")
					assemblycode.append("MVI A, " + str(var3))
					assemblycode.append("ADD B")
					assemblycode.append("MOV B,A")
					assemblycode.append("MOV A,C")
					assemblycode.append("SUI 1")
					assemblycode.append("JMP %" + str(location_counter))
					assemblycode.append("MOV A,B")
					assemblycode.append("STA " + str(symtab[filename][var1]))
					location_counter = location_counter + optab["JZ"] + optab["MOV"] + optab["MVI"] + optab["ADD"] + \
									   optab[
										   "MOV"] + optab["MOV"] + optab["SUI"] + optab["JMP"] + optab["MOV"] + optab[
										   "STA"]
				# c = a*b
				else:
					if var2 not in symtab[filename] or var3 not in symtab[filename]:
						error = "syntax error =>  " + line
						return
					assemblycode.append("MVI B, 0")
					assemblycode.append("LDA " + str(symtab[filename][var2]))
					location_counter = location_counter + optab["MVI"] + optab["LDA"]
					# before this jump B is holding the sum in ith iteration, A is holding remanhing number of iterations
					assemblycode.append("JZ %" + str(
						location_counter + optab["JZ"] + optab["MOV"] + optab["LDA"] + optab["ADD"] + optab["MOV"] +
						optab["MOV"] + optab["SUI"] + optab["JMP"]))
					assemblycode.append("MOV C,A")
					assemblycode.append("LDA " + str(symtab[filename][var3]))
					assemblycode.append("ADD B")
					assemblycode.append("MOV B,A")
					assemblycode.append("MOV A,C")
					assemblycode.append("SUI 1")
					assemblycode.append("JMP %" + str(location_counter))
					assemblycode.append("MOV A,B")
					assemblycode.append("STA " + str(symtab[filename][var1]))
					location_counter = location_counter + optab["JZ"] + optab["MOV"] + optab["LDA"] + optab["ADD"] + optab["MOV"] + optab["MOV"] + optab["SUI"] + optab["JMP"] + optab["MOV"] + optab["STA"]

			elif rediv.match(line):
				var1 = rediv.match(line).group(1)
				var2 = rediv.match(line).group(2)
				var3 = rediv.match(line).group(3)
				if isint(var1) or var1 not in symtab[filename]:
					error = "Invalid line: " + line
					return
				# a = 6/3
				if isint(var2) and isint(var3):
					assemblycode.append("MVI B, " + str(var3))
					assemblycode.append("MVI A, " + str(var2))
					assemblycode.append("SUB B")
					assemblycode.append("MVI C, 0")
					location_counter = location_counter + optab["MVI"] + optab["MVI"] + optab["SUB"] + optab["MVI"]
					assemblycode.append("JM %" + str(
						location_counter + optab["JM"] + optab["MOV"] + optab["MOV"] + optab["ADI"] + optab["MOV"] +
						optab["MOV"] + optab["SUB"] + optab["JMP"]))
					assemblycode.append("MOV F,A")
					assemblycode.append("MOV A,C")
					assemblycode.append("ADI 1")
					assemblycode.append("MOV C,A")
					assemblycode.append("MOV A,F")
					assemblycode.append("SUB B")
					assemblycode.append("JMP %" + str(location_counter))
					assemblycode.append("MOV A,C")
					assemblycode.append("STA " + str(symtab[filename][var1]))
					location_counter = location_counter + optab["JM"] + optab["MOV"] + optab["MOV"] + optab["ADI"] + \
									   optab["MOV"] + optab["MOV"] + optab["SUB"] + optab["JMP"] + optab["MOV"] + optab[
										   "STA"]
				# a = 6/b
				elif isint(var2):
					if var3 not in symtab[filename]:
						error = "Invalid line: " + line
						return
					assemblycode.append("LDA " + str(symtab[filename][var3]))
					assemblycode.append("MOV B,A")
					assemblycode.append("MVI A, " + str(var2))
					assemblycode.append("SUB B")
					assemblycode.append("MVI C, 0")
					location_counter = location_counter + optab["LDA"] + optab["MOV"] + optab["MVI"] + optab["SUB"] + \
									   optab["MVI"]
					assemblycode.append("JM %" + str(
						location_counter + optab["JM"] + optab["MOV"] + optab["MOV"] + optab["ADI"] + optab["MOV"] +
						optab["MOV"] + optab["SUB"] + optab["JMP"]))
					assemblycode.append("MOV F,A")
					assemblycode.append("MOV A,C")
					assemblycode.append("ADI 1")
					assemblycode.append("MOV C,A")
					assemblycode.append("MOV A,F")
					assemblycode.append("SUB B")
					assemblycode.append("JMP %" + str(location_counter))
					assemblycode.append("MOV A,C")
					assemblycode.append("STA " + str(symtab[filename][var1]))
					location_counter = location_counter + optab["JM"] + optab["MOV"] + optab["MOV"] + optab["ADI"] + \
									   optab[
										   "MOV"] + optab["MOV"] + optab["SUB"] + optab["JMP"] + optab["MOV"] + optab[
										   "STA"]
				# a = b/6
				elif isint(var3):
					if var2 not in symtab[filename]:
						error = "Invalid line: " + line
						return
					assemblycode.append("MVI B, " + str(var3))
					assemblycode.append("LDA " + str(symtab[filename][var2]))
					assemblycode.append("SUB B")
					assemblycode.append("MVI C, 0")
					location_counter = location_counter + optab["MVI"] + optab["LDA"] + optab["SUB"] + optab["MVI"]
					assemblycode.append("JM %" + str(
						location_counter + optab["JM"] + optab["MOV"] + optab["MOV"] + optab["ADI"] + optab["MOV"] +
						optab["MOV"] + optab["SUB"] + optab["JMP"]))
					assemblycode.append("MOV F,A")
					assemblycode.append("MOV A,C")
					assemblycode.append("ADI 1")
					assemblycode.append("MOV C,A")
					assemblycode.append("MOV A,F")
					assemblycode.append("SUB B")
					assemblycode.append("JMP %" + str(location_counter))
					assemblycode.append("MOV A,C")
					assemblycode.append("STA " + str(symtab[filename][var1]))
					location_counter = location_counter + optab["JM"] + optab["MOV"] + optab["MOV"] + optab["ADI"] + \
									   optab[
										   "MOV"] + optab["MOV"] + optab["SUB"] + optab["JMP"] + optab["MOV"] + optab[
										   "STA"]
				# a = c/d
				else:
					if var2 not in symtab[filename] or var3 not in symtab[filename]:
						error = "Invalid line: " + line
						return
					# checking here whether c > d or not by calculating c-d
					assemblycode.append("LDA " + str(symtab[filename][var3]))
					assemblycode.append("MOV B,A")
					assemblycode.append("LDA " + str(symtab[filename][var2]))
					assemblycode.append("SUB B")

					assemblycode.append("MVI C, 0")
					location_counter = location_counter + optab["LDA"] + optab["MOV"] + optab["LDA"] + optab["SUB"] + \
									   optab["MVI"]
					# JM if positive , C contains current counter , F contains the current difference(c-n*d) , B = d
					assemblycode.append("JM %" + str(
						location_counter + optab["JM"] + optab["MOV"] + optab["MOV"] + optab["ADI"] + optab["MOV"] +
						optab["MOV"] + optab["SUB"] + optab["JMP"]))
					assemblycode.append("MOV F,A")
					assemblycode.append("MOV A,C")
					assemblycode.append("ADI 1")
					assemblycode.append("MOV C,A")
					assemblycode.append("MOV A,F")
					assemblycode.append("SUB B")
					assemblycode.append("JMP %" + str(location_counter))
					# store final answer
					assemblycode.append("MOV A,C")
					assemblycode.append("STA " + str(symtab[filename][var1]))
					location_counter = location_counter + optab["JM"] + optab["MOV"] + optab["MOV"] + optab["ADI"] + \
									   optab[
										   "MOV"] + optab["MOV"] + optab["SUB"] + optab["JMP"] + optab["MOV"] + optab[
										   "STA"]
					# if a < b

			elif reor.match(line):
				# var 1= var 2 | var 3
				var1 = reor.match(line).group(1)
				var2 = reor.match(line).group(2)
				var3 = reor.match(line).group(3)
				if isint(var1) or var1 not in symtab[filename]:
					error = "Invalid line: " + line
					return

				if isint(var2) and isint(var3):
					assemblycode.append("MVI A, " + str(var2))
					assemblycode.append("ORI " + str(var3))
					assemblycode.append("STA " + str(symtab[filename][var1]))
					location_counter = location_counter + optab['MVI'] + optab['ORI'] + optab['STA']
				elif isint(var2):
					if var3 not in symtab[filename]:
						error = "Invalid line: " + line
						return
					assemblycode.append("LDA " + str(symtab[filename][var3]))
					assemblycode.append("ORI " + str(var2))
					assemblycode.append("STA " + str(symtab[filename][var2]))
					location_counter = location_counter + optab['LDA'] + optab['ORI'] + optab['STA']

				elif isint(var3):
					if var2 not in symtab[filename]:
						error = "Invalid line: " + line
						return
					assemblycode.append("LDA " + str(symtab[filename][var2]))
					assemblycode.append("ORI " + str(var3))
					assemblycode.append("STA " + str(symtab[filename][var1]))
					location_counter = location_counter + optab['LDA'] + optab['ORI'] + optab['STA']

				else:
					if var2 not in symtab[filename] or var3 not in symtab[filename]:
						error = "Invalid line: " + line
						return
					# similar to add/subtract
					assemblycode.append("LDA " + str(symtab[filename][var2]))
					assemblycode.append("MOV B,A")
					assemblycode.append("LDA " + str(symtab[filename][var3]))
					assemblycode.append("ORA B")
					assemblycode.append("STA " + str(symtab[filename][var1]))
					location_counter = location_counter + optab['LDA'] + optab['MOV'] + optab['LDA'] + optab['ORA'] + \
									   optab['STA']

			elif reand.match(line):
				# var 1= var 2 & var 3
				var1 = reand.match(line).group(1)
				var2 = reand.match(line).group(2)
				var3 = reand.match(line).group(3)
				if isint(var1) or var1 not in symtab[filename]:
					error = "Invalid line: " + line
					return

				if isint(var2) and isint(var3):
					assemblycode.append("MVI A, " + str(var2))
					assemblycode.append("ANI " + str(var3))
					assemblycode.append("STA " + str(symtab[filename][var1]))
					location_counter = location_counter + optab['MVI'] + optab['ANI'] + optab['STA']
				elif isint(var2):
					if var3 not in symtab[filename]:
						error = "Invalid line: " + line
						return
					assemblycode.append("LDA " + str(symtab[filename][var3]))
					assemblycode.append("ANI " + str(var2))
					assemblycode.append("STA " + str(symtab[filename][var1]))
					location_counter = location_counter + optab['LDA'] + optab['ANI'] + optab['STA']

				elif isint(var3):
					if var2 not in symtab[filename]:
						error = "Invalid line: " + line
						return
					assemblycode.append("LDA " + str(symtab[filename][var2]))
					assemblycode.append("ANI " + str(var3))
					assemblycode.append("STA " + str(symtab[filename][var1]))
					location_counter = location_counter + optab['LDA'] + optab['ANI'] + optab['STA']

				else:
					if var2 not in symtab[filename] or var3 not in symtab[filename]:
						error = "Invalid line: " + line
						return
					# # similar to add/subtract
					assemblycode.append("LDA " + str(symtab[filename][var2]))
					assemblycode.append("MOV B,A")
					assemblycode.append("LDA " + str(symtab[filename][var3]))
					assemblycode.append("ANA B")
					assemblycode.append("STA " + str(symtab[filename][var1]))
					location_counter = location_counter + optab['LDA'] + optab['MOV'] + optab['LDA'] + optab['ANA'] + \
									   optab['STA']

			# if a < b
			elif reiflt.match(line):
				var1 = reiflt.match(line).group(1)
				var2 = reiflt.match(line).group(2)

				# if 2 < 3
				if isint(var1) and isint(var2):
					# ACC <-- 2 - 3
					assemblycode.append("MVI A, " + str(var1))
					assemblycode.append("SUI " + str(var2))
					# if SIGN BIT is 0 (i.e. positive)
					assemblycode.append("JP &&&" + str(ifs))
					# if ZERO BIT is 1
					assemblycode.append("JZ &&&" + str(ifs))
					ifs = ifs + 1
					location_counter = location_counter + optab['MVI'] + optab['SUI'] + optab['JP'] + optab['JZ']

				# if 2 < b
				elif isint(var1):
					if var2 not in symtab[filename]:
						error = "Invalid line: " + line
						return

					# ACC <-- b - 2
					assemblycode.append("LDA " + str(symtab[filename][var2]))
					assemblycode.append("SUI " + str(var1))
					# if SIGN BIT is 1 (negative)
					assemblycode.append("JM &&&" + str(ifs))
					# if ZERO BIT is 1
					assemblycode.append("JZ &&&" + str(ifs))
					ifs = ifs + 1
					location_counter = location_counter + optab['LDA'] + optab['SUI'] + optab['JM'] + optab['JZ']

				# if a < 3
				elif isint(var2):
					if var1 not in symtab[filename]:
						error = "Invalid line: " + line
						return

					# ACC <-- a - 3
					assemblycode.append("LDA " + str(symtab[filename][var1]))
					assemblycode.append("SUI " + str(var2))
					# if SIGN BIT is 0 (positive)
					assemblycode.append("JP &&&" + str(ifs))
					# if ZERO BIT is 1
					assemblycode.append("JZ &&&" + str(ifs))
					ifs = ifs + 1
					location_counter = location_counter + optab['LDA'] + optab['SUI'] + optab['JP'] + optab['JZ']

				# if a < b
				else:
					if var2 not in symtab[filename]:
						error = "Invalid line: " + line
						return
					if var1 not in symtab[filename]:
						error = "Invalid line: " + line
						return

					# ACC <-- a - b
					assemblycode.append("LDA " + str(symtab[filename][var2]))
					assemblycode.append("MOV B,A")
					assemblycode.append("LDA " + str(symtab[filename][var1]))
					# ACC <-- a - b
					assemblycode.append("SUB B")
					# if SIGN BIT is 0 (positive)
					assemblycode.append("JP &&&" + str(ifs))
					# if ZERO BIT is 1
					assemblycode.append("JZ &&&" + str(ifs))
					ifs = ifs + 1
					location_counter = location_counter + optab["LDA"] + optab["MOV"] + optab["LDA"] + optab["SUB"] + \
									   optab["JP"] + optab["JZ"]

			# if a > b
			elif reifgt.match(line):
				var1 = reifgt.match(line).group(1)
				var2 = reifgt.match(line).group(2)

				# if 3 > 2
				if isint(var1) and isint(var2):
					# ACC <-- 3 - 2
					assemblycode.append("MVI A, " + str(var1))
					assemblycode.append("SUI " + str(var2))
					# if SIGN BIT is 1 (negative)
					assemblycode.append("JM &&&" + str(ifs))
					# if ZERO BIT is 1
					assemblycode.append("JZ &&&" + str(ifs))
					ifs = ifs + 1
					location_counter = location_counter + optab["MVI"] + optab["SUI"] + optab["JM"] + optab["JZ"]

				# if 3 > b
				elif isint(var1):
					if var2 not in symtab[filename]:
						error = "Invalid line: " + line
						return

					# ACC <-- b - 3
					assemblycode.append("LDA " + str(symtab[filename][var2]))
					assemblycode.append("SUI " + str(var1))
					# if SIGN BIT is 0 (positive)
					assemblycode.append("JP &&&" + str(ifs))
					# if ZERO BIT is 1
					assemblycode.append("JZ &&&" + str(ifs))
					ifs = ifs + 1
					location_counter = location_counter + optab["LDA"] + optab["SUI"] + optab["JP"] + optab["JZ"]

				# if a > 2
				elif isint(var2):
					if var1 not in symtab[filename]:
						error = "Invalid line: " + line
						return

					# ACC <-- a - 2
					assemblycode.append("LDA " + str(symtab[filename][var1]))
					assemblycode.append("SUI " + str(var2))
					# if SIGN BIT is 1 (negative)
					assemblycode.append("JM &&&" + str(ifs))
					# if ZERO BIT is 1
					assemblycode.append("JZ &&&" + str(ifs))
					ifs = ifs + 1
					location_counter = location_counter + optab["LDA"] + optab["SUI"] + optab["JM"] + optab["JZ"]

				# if a > b
				else:
					if var2 not in symtab[filename]:
						error = "Invalid line: " + line
						return
					if var1 not in symtab[filename]:
						error = "Invalid line: " + line
						return

					# ACC <-- a - b
					assemblycode.append("LDA " + str(symtab[filename][var2]))
					assemblycode.append("MOV B,A")
					assemblycode.append("LDA " + str(symtab[filename][var1]))
					assemblycode.append("SUB B")
					# if SIGN BIT is 0 (postive)
					assemblycode.append("JM &&&" + str(ifs))
					# if ZERO BIT is 1
					assemblycode.append("JZ &&&" + str(ifs))
					ifs = ifs + 1
					location_counter = location_counter + optab["LDA"] + optab["MOV"] + optab["LDA"] + optab["SUB"] + \
									   optab["JM"] + optab["JZ"]

			# if a = b
			elif reifeq.match(line):
				var1 = reifeq.match(line).group(1)
				var2 = reifeq.match(line).group(2)

				# if 2 = 2
				if isint(var1) and isint(var2):
					assemblycode.append("MVI A, " + str(var1))
					assemblycode.append("SUI " + str(var2))
					assemblycode.append("JNZ &&&" + str(ifs))
					ifs = ifs + 1
					location_counter = location_counter + optab["MVI"] + optab["SUI"] + optab["JNZ"]

				# if 2 = a
				elif isint(var1):
					if var2 not in symtab[filename]:
						error = "Invalid line: " + line
						return
					assemblycode.append("LDA " + str(symtab[filename][var1]))
					assemblycode.append("SUI " + str(var1))
					assemblycode.append("JNZ &&&" + str(ifs))
					ifs = ifs + 1
					location_counter = location_counter + optab["LDA"] + optab["SUI"] + optab["JNZ"]

				# if a = 2
				elif isint(var2):
					if var1 not in symtab[filename]:
						error = "Invalid line: " + line
						return
					assemblycode.append("LDA " + str(symtab[filename][var1]))
					assemblycode.append("SUI " + str(var2))
					assemblycode.append("JNZ &&&" + str(ifs))
					ifs = ifs + 1
					location_counter = location_counter + optab["LDA"] + optab["SUI"] + optab["JNZ"]

				# if a = b
				else:
					if var2 not in symtab[filename]:
						error = "Invalid line: " + line
						return
					if var1 not in symtab[filename]:
						error = "Invalid line: " + line
						return
					assemblycode.append("LDA " + str(symtab[filename][var2]))
					assemblycode.append("MOV B,A")
					assemblycode.append("LDA " + str(symtab[filename][var1]))
					assemblycode.append("SUB B")
					assemblycode.append("JNZ &&&" + str(ifs))
					ifs = ifs + 1
					location_counter = location_counter + optab["LDA"] + optab["MOV"] + optab["LDA"] + optab["SUB"] + \
									   optab["JNZ"]

			# endif
			elif reendif.match(line):
				iftable[ifs - 1] = location_counter

			# loop
			elif reloop.match(line):
				var1 = reloop.match(line).group(1)

				if not isint(var1) and var1 not in symtab[filename]:
					error = "Invalid line: " + line
					return
				if isint(var1):
					assemblycode.append("PUSH E")
					assemblycode.append("MVI E, " + str(var1))
					location_counter = location_counter + optab["PUSH"] + optab["MVI"]
					symtab[filename]["loop" + str(loops)] = "%" + str(location_counter)
					loops = loops + 1
				else:
					assemblycode.append("PUSH E")
					assemblycode.append("LDA " + str(symtab[filename][var1]))
					assemblycode.append("MOV E,A")
					location_counter = location_counter + optab["PUSH"] + optab["LDA"] + optab["MOV"]
					symtab[filename]["loop" + str(loops)] = "%" + str(location_counter)
					loops = loops + 1
			# end loop
			elif reendloop.match(line):
				if loops == 0:
					error = "Invalid line: " + line
					return
				assemblycode.append("MOV A,E")
				assemblycode.append("SUI 1")
				assemblycode.append("MOV E,A")
				assemblycode.append("JNZ ~~~" + "loop" + str(loops - 1))
				loops -= 1
				assemblycode.append("POP E")
				location_counter = location_counter + optab["MOV"] + optab["SUI"] + optab["MOV"] + optab["JNZ"] + optab[
					"POP"]

			elif rearray.match(line):
				# to initialise any array
				var = rearray.match(line).group(1)
				lent = rearray.match(line).group(2)
				if not isint(lent) or isint(var):
					error = "Invalid line: " + line
					return
				arraytab[filename][var] = ["#" + str(var), lent]

			elif refunction.match(line):
				# directly jump. Come here only when function called
				assemblycode.append("JMP !!!" + str(function_counter))
				location_counter = location_counter + optab["JMP"]
				name = refunction.match(line).group(1)
				'''
				NOT IMPLEMENTED
				'''
				globtab[filename][name] = "#" + str(location_counter)
				# save into symbol address as while calling we would be needing that
				symtab[filename][name] ="#" + str(location_counter)
				function_counter = function_counter + 1

			elif renfun.match(line):
				# return top of stack
				assemblycode.append("RET")
				location_counter = location_counter + optab["RET"]
				# save the ending of function so that we can know where to jump when function is defined
				fcalls[function_counter - 1] = location_counter

			elif recall.match(line):
				# name of function
				name = recall.match(line).group(1)
				if name not in symtab[filename]:
					error = "Function " + name + " not declared in " + line
					return
				# check it's address in the symbol table(in pass 2 it would be available ) and jump there
				assemblycode.append("CALL ~~~" + name)
				location_counter = location_counter + optab["CALL"]

			# to assign value to element of array.
			# NAME[DISP] = VAL
			elif reassarr.match(line):
				name = reassarr.match(line).group(1)
				disp = reassarr.match(line).group(2)
				val = reassarr.match(line).group(3)
				if ( name not in arraytab[filename] ) or ( not isint(disp) ) or not ( isint(val) or val in symtab[filename]):
					error = "Invalid line: " + line
					return

				if (isint(val)):
					assemblycode.append("MVI A, " + str(val))
					assemblycode.append("STA " + str(arraytab[filename][name][0]) + "+" + str(disp))
					location_counter = location_counter + optab["MVI"] + optab["STA"]

				else:
					assemblycode.append("LDA " + str(symtab[filename][val]))
					assemblycode.append("STA " + str(arraytab[filename][name][0]) + "+" + str(disp))
					location_counter = location_counter + optab["LDA"] + optab["STA"]

			# minimum
			elif remin.match(line):
				var1 = remin.match(line).group(1)
				vas = remin.match(line).group(2)
				if isint(var1) or var1 not in symtab[filename]:
					error = "Invalid line: " + line
					return
				vas = vas.split(',')
				for i in range(len(vas)):
					vas[i] = vas[i].lstrip().rstrip()
				if isint(vas[0]):
					assemblycode.append("MVI A, " + str(vas[0]))
					location_counter = location_counter + optab["MVI"]
				elif vas[0] not in symtab[filename]:
					error = "Invalid line: " + line
				else:
					assemblycode.append("LDA " + symtab[filename][vas[0]])
					location_counter = location_counter + optab["LDA"]
				vas = vas[1:]
				for var in vas:
					if isint(var):
						assemblycode.append("MVI B, " + str(var))
						# current minimum value in C
						assemblycode.append("MOV C,A")
						assemblycode.append("SUB B")
						location_counter = location_counter + optab["MVI"] + optab["MOV"] + optab["SUB"]
						# if negative ie 0th argument(or prev min) is small jump and ztore current min in accumulator
						# otherwise curr arg will be small and hence move it to G
						assemblycode.append("JM %" + str(location_counter + optab["JM"] + optab["MOV"] + optab["JP"]))
						assemblycode.append("MOV G,B")
						assemblycode.append(
							"JP %" + str(location_counter + optab["JM"] + optab["MOV"] + optab["JP"] + optab["MOV"]))
						# move cuurent min value to A(accumulator)
						assemblycode.append("MOV G,C")
						assemblycode.append("MOV A,G")
						location_counter = location_counter + optab["JM"] + optab["MOV"] + optab["JP"] + optab["MOV"] + \
										   optab[
											   "MOV"]
					elif var not in symtab[filename]:
						error = "Invalid line: " + line
						return
					else:
						assemblycode.append("MOV C,A")
						assemblycode.append("LDA " + str(symtab[filename][var]))
						assemblycode.append("MOV B,A")
						assemblycode.append("MOV A,C")
						assemblycode.append("SUB B")
						location_counter = location_counter + optab["MOV"] + optab["LDA"] + optab["MOV"] + optab[
							"MOV"] + optab[
											   "SUB"]
						assemblycode.append("JM %" + str(location_counter + optab["JM"] + optab["MOV"] + optab["JP"]))
						assemblycode.append("MOV G,B")
						assemblycode.append(
							"JP %" + str(location_counter + optab["JM"] + optab["MOV"] + optab["JP"] + optab["MOV"]))
						assemblycode.append("MOV G,C")
						assemblycode.append("MOV A,G")
						location_counter = location_counter + optab["JM"] + optab["MOV"] + optab["JP"] + optab["MOV"] + \
										   optab[
											   "MOV"]
				assemblycode.append("STA " + str(symtab[filename][var1]))
				location_counter = location_counter + optab["STA"]

			elif remax.match(line):
				var1 = remax.match(line).group(1)
				vas = remax.match(line).group(2)
				if isint(var1) or var1 not in symtab[filename]:
					error = "Invalid line: " + line
					return
				vas = vas.split(',')
				for i in range(len(vas)):
					vas[i] = vas[i].lstrip().rstrip()
				if isint(vas[0]):
					assemblycode.append("MVI A, " + str(vas[0]))
					location_counter = location_counter + optab["MVI"]
				elif vas[0] not in symtab[filename]:
					error = "Invalid line: " + line
				else:
					assemblycode.append("LDA " + symtab[filename][vas[0]])
					location_counter = location_counter + optab["LDA"]
				vas = vas[1:]
				for var in vas:
					if isint(var):
						assemblycode.append("MVI B, " + str(var))
						assemblycode.append("MOV C,A")
						assemblycode.append("SUB B")
						location_counter = location_counter + optab["MVI"] + optab["MOV"] + optab["SUB"]
						assemblycode.append("JP %" + str(location_counter + optab["JP"] + optab["MOV"] + optab["JM"]))
						assemblycode.append("MOV G,B")
						assemblycode.append(
							"JM %" + str(location_counter + optab["JP"] + optab["MOV"] + optab["JM"] + optab["MOV"]))
						assemblycode.append("MOV G,C")
						assemblycode.append("MOV A,G")
						location_counter = location_counter + optab["JP"] + optab["MOV"] + optab["JM"] + optab["MOV"] + \
										   optab[
											   "MOV"]
					elif var not in symtab[filename]:
						error = "Invalid line: " + line
						return
					else:
						assemblycode.append("MOV C,A")
						assemblycode.append("LDA " + str(symtab[filename][var]))
						assemblycode.append("MOV B,A")
						assemblycode.append("MOV A,C")
						assemblycode.append("SUB B")
						location_counter = location_counter + optab["MOV"] + optab["LDA"] + optab["MOV"] + optab[
							"MOV"] + optab[
											   "SUB"]
						assemblycode.append("JP %" + str(location_counter + optab["JP"] + optab["MOV"] + optab["JM"]))
						assemblycode.append("MOV G,B")
						assemblycode.append(
							"JM %" + str(location_counter + optab["JP"] + optab["MOV"] + optab["JM"] + optab["MOV"]))
						assemblycode.append("MOV G,C")
						assemblycode.append("MOV A,G")
						location_counter = location_counter + optab["JP"] + optab["MOV"] + optab["JM"] + optab["MOV"] + \
										   optab[
											   "MOV"]
				assemblycode.append("STA " + str(symtab[filename][var1]))
				location_counter = location_counter + optab["STA"]

			elif rejump.match(line):
				loc = rejump.match(line).group(1)
				assemblycode.append("JMP ~~~" + str(loc))
				location_counter =location_counter + optab["JMP"]

			elif retag.match(line):
				loc = retag.match(line).group(1)
				symtab[filename][loc] = "#" + str(location_counter)

			
			# if line does not matches with any of the above line.
			elif line.lstrip().rstrip() != "":
				error = "Invalid line: " + line
				return

		filelentab[filename] = location_counter
		# all lines have been passed in pass1
		assemblycode.append("END")
		location_counter = location_counter + 1
		
		for var in vartab[filename]:
			assemblycode.append(var + " DS 1")
			symtab[filename][var] ="#" + str(location_counter)
			if var in globtab[filename]:
				globtab[filename][var] ="$" + str(location_counter)
			location_counter = location_counter + optab["DS"]

		for i, literal in enumerate(littab[filename]):
			literal = (literal[0], location_counter)
			littab2[filename][literal[0]] = location_counter
			littab[filename][i] = literal
			assemblycode.append("='" + str(literal[0]) + "'")
			location_counter = location_counter + 1

		for array in arraytab[filename]:
			assemblycode.append(str(array) + ' DS ' + str(arraytab[filename][array][1]))
			arraytab[filename][array][0] = location_counter
			location_counter = location_counter + optab["DS"]*int(arraytab[filename][array][1])

		assemblycode1lines = '\n'.join(assemblycode)
		pass1code = assemblycode

		with open(filename+".pass1", "w") as file:
			file.write(assemblycode1lines)
			file.close()

		pass2(filename)

def pass2(filename):
	assco = []
	for line in pass1code:
		# No special symbol in the line
		if "&&&" not in line and "!!!" not in line and "~~~" not in line and "#" not in line :
			assco.append(line)
		
		# JMP statements for IF
		elif "&&&" in line:
			ifp = line.split("&&&")[1]
			ifp = int(ifp)
			line = line.replace("&&&" + line.split("&&&")[1], "@" + str(iftable[ifp]))
			assco.append(line)

		# JMP statements for FUNCTION
		elif "!!!" in line:
			fnp = line.split("!!!")[1]
			fnp = int(fnp)
			line = line.replace("!!!" + line.split("!!!")[1], "@" + str(fcalls[fnp]))
			assco.append(line)

		# Any Variable Name
		elif "#" in line:
			varp = line.split("#")[1]
			varp = varp.split(',')
			varpe = varp[0]
			varpestripped = varpe.lstrip().rstrip()
			
			if(varpestripped in symtab[filename]):
				line = line.replace("#" + varpe, "@" + str(symtab[filename][varpestripped].strip('#')))
			elif "+" in line:
				varpestrip = varpestripped.split('+')[0]
				disp  = varpestripped.split('+')[1]
				line = line.replace("#" + varpe, "@" + str(int(arraytab[filename][varpestrip][0]) + int(disp)*1 ))
			else:
				line = line.replace("#", "@" )

			assco.append(line)

		# Call to Loops/Functions
		else:
			jc = line.split("~~~")[1]
			line = line.replace("~~~" + line.split("~~~")[1], str(symtab[filename][jc]))
			line = line.replace("#", "@" )
			assco.append(line)

	assemblycode2lines = '\n'.join(assco)


	with open(filename + ".pass2", "w") as file:
		file.write(assemblycode2lines)
		file.close()

	print("OPTAB : ", optab)
	print("IFTABLE : ", iftable)
	print("F CALLS : ", fcalls)
	print("POOLTAB : ", pooltab)
	print("LITTAB : ", littab)

if __name__ == "__main__":
	pass1(['test_ifelse.txt'])

if not error == "False" :
	print(error)
