import assembler

error = "False"
startaddfile = {}
filelentab = assembler.filelentab
globtab = assembler.globtab

def findfile(string, files):
	for file in files:
		if string in globtab[file.split('.')[0]] and "$" in globtab[file.split('.')[0]][string]:
			return file.split('.')[0], globtab[file.split('.')[0]][string].split("$")[1]
	return "Not found", "-1"

def link(fileNames):
	global error
	global startaddfile
	global filelentab
	global globtab
	startaddfile = {}
	filelentab = assembler.filelentab
	globtab = assembler.globtab
	error = "False"
	memadd = 0
	for filename in fileNames:
		startaddfile[filename.split('.')[0]] = memadd
		memadd = memadd + filelentab[filename.split('.')[0]]

	lincode = []

	for filenam in fileNames:
		filename = filenam.split('.')[0]
		with open(filename + '.pass2', 'r') as file:
			lines = file.read().split('\n')
			file.close()
		print("Linker start -------------------------------------------------------------")
		for line in lines:
			# No variables to link
			if '$' not in line and '@' not in line:
				lincode.append(line)

			# Unlinked local variables
			if '@' in line:
				addr = line.split('@')[1]
				addrtmp = addr.split(',')[0]
				# print(addr1[0])
				addr2 = str(int(addrtmp) + startaddfile[filename])
				line = line.replace('@' + addrtmp, '@' + addr2)
				lincode.append(line)

			# Unlinked Global Variables
			if '$' in line:
				var = line.split('$')[1]
				vara = var.split(',')[0]
				# print(var, vara)
				# fname, add = findfile(line.split('$')[1], fileNames)
				fname, add = findfile(var, fileNames)
				if fname == "Not found":
					error = "External variable " + line.split('$')[1] + " not found: " + line
					print(error)
					return
				line = line.replace('$' + vara, "@" + str(int(add) + startaddfile[fname]))
				lincode.append(line)
			# print(line)
	with open(fileNames[0].split('.')[0] + '.linked', 'w') as file:
		file.write("\n".join(lincode))
		file.close()


if __name__ == "__main__":
	FilesTesting = ['test_ext_a.txt','test_ext_b.txt']
	assembler.pass1(FilesTesting)
	link(FilesTesting)