"""Separate visual elements of the exact upstream v11 PDF (no tracing).

The operator ranges apply only to this SHA-256-verified upstream PDF. Graphics
state, clipping, embedded fonts, original coordinates and form objects remain
intact. Elements are divided by suppressing unselected paint operators.
"""
import hashlib
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ContentStream, NameObject, DictionaryObject,
                           ArrayObject, TextStringObject)
import pypdfium2 as pdfium

ROOT=Path(__file__).resolve().parent
SRC=ROOT/'original-box.pdf'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()=='cdb273bbb9b4c934b7993c084713e76bef394fccd6f3a26fb00e31ee7c8125be', '需要原版 v11 box.pdf'
DEST=ROOT/'box-elements';DEST.mkdir(exist_ok=True)
PAINT={b'f',b'F',b'f*',b'S',b's',b'B',b'B*',b'b',b'b*',b'Do',b'Tj',b'TJ',b"'",b'"'}
LAYERS=['background-stripes','debian-logo','text','dielines-and-folds','barcode-and-print-marks']

def category(i,op):
    if op not in PAINT:return None
    if i==4:return '白底'
    if op in (b'Tj',b'TJ',b"'",b'"'):return 'text'
    if 5<=i<=421:return 'background-stripes'
    if 435<=i<=821 and i!=804:return 'debian-logo'
    if 822<=i<=909 or i in (1480,1487):return 'dielines-and-folds'
    return 'barcode-and-print-marks'

def remove_original_marks(ops):
    return [(i,a,o) for i,(a,o) in enumerate(ops) if o not in (b'BDC',b'EMC')]

def filtered(indexed,name,white_backdrop=False):
    out=[]
    for i,a,o in indexed:
        if o not in PAINT or category(i,o)==name or (white_backdrop and i==4):
            out.append((a,o))
        elif o in (b'f',b'F',b'f*',b'S',b's',b'B',b'B*',b'b',b'b*'):
            # Keep the path terminator even when a painting is hidden.
            out.append(([],b'n'))
    return out

def clone():
    reader=PdfReader(SRC);writer=PdfWriter();writer.clone_document_from_reader(reader)
    page=writer.pages[0];stream=ContentStream(page.get_contents(),writer)
    return writer,page,stream,remove_original_marks(stream.operations)

def write(writer,path):
    with path.open('wb') as f:writer.write(f)

for n,name in enumerate(LAYERS,1):
    # The original wave and logo use blend modes that rely on a painted white
    # backing; a viewer's transparent-page preview is not an equivalent base.
    writer,page,stream,ops=clone();stream.operations=filtered(ops,name,white_backdrop=True)
    page[NameObject('/Contents')]=writer._add_object(stream)
    path=DEST/f'{n:02d}-{name}.pdf';write(writer,path)
    doc=pdfium.PdfDocument(path);doc[0].render(scale=1.5).to_pil().save(DEST/f'{n:02d}-{name}-预览.png')

# A single PDF with independently switchable layers. Each layer runs its own
# balanced copy of the original graphics program, so hiding a layer cannot
# leave a half-built path or disturb another layer's transforms.
writer,page,stream,ops=clone(); groups=[];properties=DictionaryObject();all_ops=[]
for n,name in enumerate(['白底']+LAYERS):
    ocg=DictionaryObject({NameObject('/Type'):NameObject('/OCG'),NameObject('/Name'):TextStringObject(name)})
    ref=writer._add_object(ocg);groups.append(ref);key=NameObject(f'/Part{n}');properties[key]=ref
    all_ops += [([],b'q'),([NameObject('/OC'),key],b'BDC')]+filtered(ops,name)+[([],b'EMC'),([],b'Q')]
page['/Resources'][NameObject('/Properties')]=properties
writer._root_object[NameObject('/OCProperties')]=DictionaryObject({
    NameObject('/OCGs'):ArrayObject(groups),NameObject('/D'):DictionaryObject({
        NameObject('/Order'):ArrayObject(list(reversed(groups))),NameObject('/ON'):ArrayObject(groups),NameObject('/RBGroups'):ArrayObject()})})
stream.operations=all_ops;page[NameObject('/Contents')]=writer._add_object(stream)
path=DEST/'00-元素分层总稿.pdf';write(writer,path)
doc=pdfium.PdfDocument(path);doc[0].render(scale=1.5).to_pil().save(DEST/'00-元素分层总稿-预览.png')
print('Completed:', DEST)
