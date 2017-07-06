# l=[12,1414,1,235,11]
# c=[69,6]
# for i,a in enumerate(l):
# 	print(a,i)
# 	if (a==1):
# 		count=len(c)
# 		for q in range(count):
# 			l.append(l[q+i+1])

# print(l)			

# macro
# incr
# var a=5
# var b=10
# mend
# var c=1
# incr
# c=a+b

l=[12,1414,1,235,11]
c=[124,484,141,2346,53,26,43,62,346,34,6,43643]
print(l)
l=l+c
print(l)  

# both these cases are working in macro
# var d=1
# var e=1
# macro
# incr add,bdd
# var add=5
# var bdd=10
# mend
# var c=1
# incr add=d,bdd=e
# c=d+e

# macro
# incr
# var a=5
# var b=10
# mend
# var c=1
# incr
# c=a+b