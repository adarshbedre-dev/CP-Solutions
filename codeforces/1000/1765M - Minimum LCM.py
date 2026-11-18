for _ in range(int(input())):
    n=int(input())
    a=next((i for i in range(2,int(n**0.5)+1) if n%i==0),1)
    if a==1:
        print(1,n-1)
    else:
        print(n//a, n-n//a)
    

            
    #print(a)        
    '''if i==1:
                print(1,n-1)
            else:
                print(n//i,n-n//i)'''
            

    '''lis=[]
    i=2
    while 1<i<n:
        if n%i==0:
          lis.append(i)'''
    '''i+=1
    print(lis)
    if lis==[]:
      print(1,n-1)
    else:
     m=math.prod(lis[1:])
     print(m,n-m)'''
