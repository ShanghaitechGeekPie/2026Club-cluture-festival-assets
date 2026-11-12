"""Extract the three native OCGs from the upstream v11 vector PDF.

Requires pypdf and pypdfium2. No rasterization is applied to the output PDFs.
"""
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream, NameObject
import pypdfium2 as pdfium

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'original-box.pdf'
LAYERS = [('/MC0', '01-图层1-主要设计'), ('/MC1', '02-图层2-空图层'),
          ('/MC2', '03-arch-related-架构文字')]

for chosen, name in LAYERS:
    reader = PdfReader(SOURCE)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    page = writer.pages[0]
    stream = ContentStream(page.get_contents(), writer)
    output, active = [], None
    for operands, op in stream.operations:
        if op == b'BDC' and operands[0] == '/OC':
            assert active is None
            active = str(operands[1])
            continue
        if op == b'EMC' and active is not None:
            active = None
            continue
        if active == chosen or active is None:
            output.append((operands, op))
    assert active is None
    stream.operations = output
    page[NameObject('/Contents')] = writer._add_object(stream)
    path = HERE / (name + '.pdf')
    with path.open('wb') as handle:
        writer.write(handle)
    doc = pdfium.PdfDocument(path)
    bitmap = doc[0].render(scale=1.5, fill_color=(255,255,255,255))
    bitmap.to_pil().save(HERE / (name + '-预览.png'))
    print(name, 'operations:', len(output), 'page:', doc[0].get_size())
