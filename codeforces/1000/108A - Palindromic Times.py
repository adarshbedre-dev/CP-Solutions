h,m=list(input().split(':'))
if int(h)==23 and int(m)>32:
    print('00:00')
elif int(h) in range(6,10) or (int(h)==5 and int(m)>=50):
    print('10:01')
elif int(h) in range(16,20) or (int(h)==15 and int(m)>=51):
    print('20:02')
elif int(m)<int(h.zfill(2)[::-1]):
    print(h+':'+h[::-1])
else:
    print(str(int(h)+1).zfill(2)+':'+str(int(h)+1).zfill(2)[::-1])
