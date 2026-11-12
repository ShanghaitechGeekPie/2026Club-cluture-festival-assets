"""Extract elements from the original v11 instruction PDF, preserving vectors."""
from pathlib import Path
import hashlib
from pypdf import PdfReader,PdfWriter
from pypdf.generic import ContentStream,NameObject,DictionaryObject,ArrayObject,TextStringObject
import pypdfium2 as pdfium
from PIL import ImageChops

ROOT=Path(__file__).resolve().parent
SRC=ROOT/'原版-instruction.pdf'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()=='d4d091e470b436e1d52a6445a6aff27f0bc591f1eba1a60c7bf15c136d868cf3'
OUT=ROOT/'leaflet-elements';OUT.mkdir(exist_ok=True)
LAYERS=['title-banner','warning','section-bars','section-headings','body-text','table-lines','date-and-footer']
HEADINGS={307,401,506,607,749,831,946,1050,1387,1560,1762,1846,1951,2044,2137,2222}
PAINT={b'f',b'F',b'f*',b'S',b's',b'B',b'B*',b'b',b'b*',b'Do',b'Tj',b'TJ',b"'",b'"'}

def classify(ops):
    current=None;assigned={}
    for i,(a,o) in enumerate(ops):
        if o==b'BT':current=i
        elif o==b'ET':current=None
        if o not in PAINT:continue
        if o in (b'Tj',b'TJ',b"'",b'"'):
            if current in HEADINGS:kind='section-headings'
            elif current in (60,2273):kind='date-and-footer'
            elif current==219:kind='warning'
            else:kind='body-text'
        elif o==b'Do':kind='title-banner' if str(a[0])=='/Fm24' else 'date-and-footer'
        elif o==b'f':kind='warning' if i==207 else 'section-bars'
        elif o in (b'S',b's',b'B',b'B*',b'b',b'b*'):kind='table-lines'
        else:raise ValueError((i,a,o))
        assigned[i]=kind
    return assigned

def filtered(ops,kinds,chosen):
    out=[]
    for i,(a,o) in enumerate(ops):
        if o not in PAINT or kinds[i]==chosen:out.append((a,o))
        elif o in (b'f',b'F',b'f*',b'S',b's',b'B',b'B*',b'b',b'b*'):out.append(([],b'n'))
    return out

def clone():
    r=PdfReader(SRC);w=PdfWriter();w.clone_document_from_reader(r);p=w.pages[0]
    stream=ContentStream(p.get_contents(),w);ops=list(stream.operations)
    return w,p,stream,ops,classify(ops)

def save(w,path):
    with path.open('wb') as f:w.write(f)

for i,name in enumerate(LAYERS,1):
    w,p,s,ops,kinds=clone();s.operations=filtered(ops,kinds,name)
    p[NameObject('/Contents')]=w._add_object(s);path=OUT/f'{i:02d}-{name}.pdf';save(w,path)
    pdfium.PdfDocument(path)[0].render(scale=1.3).to_pil().save(OUT/f'{i:02d}-{name}-预览.png')

w,p,s,ops,kinds=clone();groups=[];props=DictionaryObject();all_ops=[]
for i,name in enumerate(LAYERS):
    ref=w._add_object(DictionaryObject({NameObject('/Type'):NameObject('/OCG'),NameObject('/Name'):TextStringObject(name)}));groups.append(ref)
    key=NameObject(f'/Layer{i}');props[key]=ref
    all_ops += [([],b'q'),([NameObject('/OC'),key],b'BDC')]+filtered(ops,kinds,name)+[([],b'EMC'),([],b'Q')]
p['/Resources'][NameObject('/Properties')]=props
w._root_object[NameObject('/OCProperties')]=DictionaryObject({NameObject('/OCGs'):ArrayObject(groups),NameObject('/D'):DictionaryObject({NameObject('/Order'):ArrayObject(list(reversed(groups))),NameObject('/ON'):ArrayObject(groups),NameObject('/RBGroups'):ArrayObject()})})
s.operations=all_ops;p[NameObject('/Contents')]=w._add_object(s)
path=OUT/'00-说明书分层总稿.pdf';save(w,path)
original=pdfium.PdfDocument(SRC)[0].render(scale=1.5).to_pil().convert('RGB')
rebuilt=pdfium.PdfDocument(path)[0].render(scale=1.5).to_pil().convert('RGB')
rebuilt.save(OUT/'00-说明书分层总稿-预览.png')
diff=ImageChops.difference(original,rebuilt);print('Pixel identical:',diff.getbbox() is None,'difference:',diff.getbbox())
