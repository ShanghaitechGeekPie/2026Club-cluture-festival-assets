from pypdf import PdfReader
from pypdf.generic import ContentStream
from collections import Counter
r=PdfReader('original-box.pdf');ops=ContentStream(r.pages[0].get_contents(),r).operations
stack=[]
for i,(a,o) in enumerate(ops):
    if o==b'q':stack.append(i)
    if o==b'Q':
        begin=stack.pop();depth=len(stack)
        if depth in (1,2):
            sub=ops[begin:i+1];paint=[(j+begin,op.decode(),str(args)[:80]) for j,(args,op) in enumerate(sub) if op in (b'Do',b'f',b'S',b'B')]
            if paint:print(begin,i,'depth',depth,'paints',paint[:8], 'count',len(paint))
