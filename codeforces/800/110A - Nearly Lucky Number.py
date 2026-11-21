num=input()
j=0
for i in num:
    if i in ('4','7'):
        j+=1
if j in (4,7):
    print('YES')
else:
    print('NO')