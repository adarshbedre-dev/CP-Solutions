s=list(input())
v=['a','A','e','E','i','I','o','O','u','U','y','Y']
for i in range(len(s)):
    if s[i] in v:
        s[i]=''
s=''.join(s)
s=s.lower()
for j in s:
    print('.'+j,end='')