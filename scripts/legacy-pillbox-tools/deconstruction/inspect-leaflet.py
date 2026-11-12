from pypdf import PdfReader
from pypdf.generic import ContentStream
r=PdfReader('原版-instruction.pdf');ops=ContentStream(r.pages[0].get_contents(),r).operations
for i,(a,o) in enumerate(ops):
    if o==b'BT':
        j=i+1
        while ops[j][1]!=b'ET':j+=1
        moves=[(k,str(ops[k][0])) for k in range(i+1,j) if ops[k][1] in (b'Td',b'Tm')]
        print('TEXT',i,j,moves[:2])
    elif o in (b'Do',b'f',b'S',b'B',b're'):
        print('PAINT',i,o.decode(),a)
