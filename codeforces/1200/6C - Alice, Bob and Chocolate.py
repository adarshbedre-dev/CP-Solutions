n=int(input())
l=list(map(int, input().split(' ')))
a=0
b=0
i=0
j=n-1
ta=0
tb=0
while i<=j:
  if ta<=tb:
    ta+=l[i]
    i+=1
    a+=1
  else:
    tb+=l[j]
    j-=1
    b+=1
    
print(a,b)