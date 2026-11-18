for _ in range(int(input())):
    n=int(input())
    if n in (1,3):
        print(-1)
    elif n%2==0:
        print((n-2)*'3'+'66')
    else:
        print((n-4)*'3'+'6366')