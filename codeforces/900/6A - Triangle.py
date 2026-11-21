lis=list(map(int, input().split()))
lis.sort()
if sum(lis[1:3])>lis[3] or sum(lis[0:2])>lis[2]:
    print('TRIANGLE')
elif sum(lis[1:3])==lis[3] or sum(lis[0:2])==lis[2] and sum(lis[1:3])<lis[3]:
    print('SEGMENT')
else:
    print('IMPOSSIBLE')