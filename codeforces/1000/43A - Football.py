from collections import Counter
n=int(input())
lis=[input() for _ in range(n)]
ctr=Counter(lis)
print(ctr.most_common(1)[0][0])