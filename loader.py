def convert(filename, offset=0):
	filename = filename[0]
	with open(filename.split('.')[0] + '.linked', 'r') as file:
		lines = file.read().split('\n')
		file.close()

	asscode = []

	for line in lines:
		if '@' in line:
			varp = line.split('@')[1]
			varp = varp.split(',')[0].lstrip().rstrip()
			add = int(varp)
			add = str(add + offset)
			line = line.replace('@' + varp, add)
			asscode.append(line)

		elif '%' in line:
			varp = line.split('%')[1].lstrip().rstrip()
			add = int(varp)
			add = str(add + offset)
			line = line.replace('%' + line.split('%')[1], add)
			asscode.append(line)
		else:
			asscode.append(line)

	asscode.append('HLT')

	with open(filename.split('.')[0] + '.loaded', 'w') as file:
		file.write('\n'.join(asscode))
		file.close()


if __name__ == "__main__":
    convert(['test.txt'])