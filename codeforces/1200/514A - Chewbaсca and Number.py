nums=input()
num=[int(x) for x in nums]
inv=[]
for i,j in enumerate(num):
    if i==0 and j==9:
        inv.append(9)
    elif j>=5:
        inv.append(9-j)
    else:
        inv.append(j)

invs=''.join(map(str, inv))
   
print(invs)


