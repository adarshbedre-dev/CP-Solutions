n,m,p=list(input().split())
mat=[list(input()) for _ in range(int(n))]
dirs=[(0,1), (0,-1), (1,0), (-1,0)]
lis=[]
for i in range(int(n)):
    for j in range(int(m)):
        if mat[i][j]==p:
            for di, dj in dirs:
                ni, nj = i + di, j + dj
                if 0 <= ni < int(n) and 0 <= nj < int(m):
                    lis.append(mat[ni][nj])                
slis=set(lis)
print(sum(1 if k!='.' and k!=p else 0 for k in slis))