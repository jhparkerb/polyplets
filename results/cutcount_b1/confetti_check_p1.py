import sys
p = 2147483647
def rows(path):
    d={}
    for line in open(path):
        n,v=line.split(); d[int(n)]=int(v)
    return d
res = rows("/home/jasonp/var/motley-h18/C18.p%d.out"%p)
C17 = rows("/home/jasonp/var/motley-h17/C17.out")
C16 = rows("/home/jasonp/var/motley-step0/rows/C16.out")
want={}
for line in open("/home/jasonp/var/motley-h17/triangle.txt"):
    if line.startswith("#"): continue
    n,H,v=line.split()
    if int(H)==18: want[int(n)]=int(v)
m=mm=0
for n in sorted(want):
    if n not in res or n not in C17 or n not in C16: continue
    pred = (want[n] + 2*C17[n] - C16[n]) % p
    if pred == res[n] % p: m+=1
    else:
        mm+=1; print("MISMATCH n=%d pred=%d meas=%d"%(n,pred,res[n]))
print("prime1 vs incumbent triangle: %d match, %d mismatch"%(m,mm))
