"""#11: free / one-sided polyplet amplitude ratios and growth constants.
free(n) ~ a(n)/8 and one-sided(n) ~ a(n)/4 asymptotically (D4 order 8, rotation
group order 4); the symmetric corrections are O((sqrt(lambda)/lambda)^n) -> 0. So
8*free/a -> 1, 4*onesided/a -> 1, and both share lambda = 7.110 with fixed.
Data: results/free_onesided_polyplets.txt + b006770 (n=20 candidate flagged).
"""
import numpy as np
a   = [0,1,4,20,110,638,3832,23592,147941,940982,6053180,39299408,257105146,
 1692931066,11208974860,74570549714,498174818986,3340366308393,22471158811164,
 151609203011580,1025573519362016]
free=[0,1,2,5,22,94,524,3031,18770,118133,758381,4915652,32149296,211637205,
 1401194463,9321454604,62272330564,417546684096,2808898025438,18951156321090,
 128196711128365]
one =[0,1,2,6,34,166,991,5931,37196,235456,1514618,9826177,64284947,423241426,
 2802300793,18642694440,124544085550,835091956750,5617792259411,37902303297525,
 256393397108358]
N=len(a)-1
print("  n      8*free/a       4*onesided/a   (->1 as symmetric terms die ~lambda^-n/2)")
for n in range(6,N+1):
    tag=" (cand)" if n==20 else ""
    print(f" {n:2d}    {8*free[n]/a[n]:.7f}    {4*one[n]/a[n]:.7f}{tag}")

def biased_lambda(seq):
    ns=[];lam=[]
    for n in range(2,N+1):
        ns.append(n);lam.append((seq[n]/seq[n-1])*n/(n-1))
    ns=np.array(ns,float);lam=np.array(lam)
    L=lam[-8:];M=ns[-8:];B=np.vstack([np.ones_like(M),1/M**2]).T
    c,*_=np.linalg.lstsq(B,L,rcond=None);return c[0]
print()
print(f"biased lambda (theta=-1):  fixed={biased_lambda(a):.4f}  free={biased_lambda(free):.4f}  "
      f"one-sided={biased_lambda(one):.4f}   (all should be 7.110)")
# amplitude-ratio convergence rate: residual (8free/a - 1) should decay ~ lambda^(-n/2)
res=np.array([abs(8*free[n]/a[n]-1) for n in range(6,N+1)])
ns=np.arange(6,N+1)
sl=np.polyfit(ns,np.log(res),1)[0]
print(f"8*free/a residual decay: e^({sl:.3f} n)  ->  base {np.exp(sl):.4f}  "
      f"(predict 1/sqrt(lambda)={1/np.sqrt(7.11):.4f})")
