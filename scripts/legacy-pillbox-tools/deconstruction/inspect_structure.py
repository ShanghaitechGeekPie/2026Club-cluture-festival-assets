from pypdf import PdfReader
from pypdf.generic import ContentStream
from collections import Counter
r=PdfReader('original-box.pdf');ops=ContentStream(r.pages[0].get_contents(),r).operations
depth=0;begin=0
for i,(a,o) in enumerate(ops):
    if o==b'q':
        if depth==0:begin=i
        depth+=1
    elif o==b'Q':
        depth-=1
        if depth==0:
            sub=ops[begin:i+1]; c=Counter(op.decode('latin1') for _,op in sub)
            refs=[str(args) for args,op in sub if op in (b'Do',b'Tf',b'k',b'K',b'gs')]
            print(begin,i,dict(c),' '.join(refs)[:500])
    elif depth==0 and o not in (b'BDC',b'EMC'):
        print(i,'TOP',o,a if o not in (b'c',b'l',b'm',b'Tj',b'TJ') else '')
