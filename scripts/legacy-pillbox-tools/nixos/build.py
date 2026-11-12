"""NixOS packaging adaptation built from the original v11 vector PDF."""
from pathlib import Path
import io, sys, re, hashlib, copy, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'vendor'))
import pymupdf as fitz
from pypdf import PdfReader,PdfWriter
from pypdf.generic import ContentStream,NameObject,ArrayObject,DictionaryObject,TextStringObject,FloatObject
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
import pypdfium2 as pdfium

SOURCE=ROOT.parent/'deconstruction'/'original-box.pdf'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='cdb273bbb9b4c934b7993c084713e76bef394fccd6f3a26fb00e31ee7c8125be'
W,H=413.858,634.961
pdfmetrics.registerFont(TTFont('CN','C:/Windows/Fonts/msyh.ttc'))
OUT=ROOT/'output';OUT.mkdir(exist_ok=True)
PAINT={b'f',b'F',b'f*',b'S',b's',b'B',b'B*',b'b',b'b*',b'Do',b'Tj',b'TJ',b"'",b'"'}

def category(i,op):
    if op not in PAINT:return None
    if i==4:return '白底'
    if op in (b'Tj',b'TJ',b"'",b'"'):return '旧文字'
    if 5<=i<=421:return 'background-stripes'
    if 435<=i<=821 and i!=804:return '旧标志'
    if 822<=i<=909 or i in (1480,1487):return 'dielines-and-folds'
    return '印刷辅助'

def isolated(ops,part):
    result=[]
    for i,(args,op) in enumerate(ops):
        if op in (b'BDC',b'EMC'):continue
        if op not in PAINT or category(i,op)==part:result.append((args,op))
        elif op in (b'f',b'F',b'f*',b'S',b's',b'B',b'B*',b'b',b'b*'):result.append(([],b'n'))
    return result

def colored_form(writer,page,name,kind):
    form=page['/Resources']['/XObject'][NameObject(name)].get_object()
    stream=ContentStream(form,writer);new=[]
    for args,op in stream.operations:
        if kind=='fill' and op==b'k':new.append(([FloatObject(.322),FloatObject(.467),FloatObject(.765)],b'rg'))
        elif kind=='stroke' and op==b'K':new.append(([FloatObject(.322),FloatObject(.467),FloatObject(.765)],b'RG'))
        else:new.append((args,op))
    stream.operations=new;form.set_data(stream.get_data())

def clean_svg(path,pale=False,wordmark=False):
    # Remove Inkscape guide layers explicitly. MuPDF otherwise paints hidden
    # guides. Replace the two unsupported gradients with the official colors;
    # preserve the official vector path geometry unchanged.
    ET.register_namespace('','http://www.w3.org/2000/svg')
    root=ET.parse(path).getroot()
    wanted={'layer3','g5329'} if wordmark else {'layer3'}
    for child in list(root):
        if child.tag.endswith('g') and child.get('id') not in wanted:root.remove(child)
    colors=('#d0dcee','#dcecf6') if pale else ('#5277c3','#7ebae4')
    for e in root.iter():
        style=e.get('style','')
        if 'fill:url(' in style:
            color=colors[0] if e.get('id')=='path3336-6' else colors[1]
            e.set('style',re.sub(r'fill:url\(#[^)]+\)',f'fill:{color}',style))
    # Expand SVG <use> references to their original vector paths. The PDF
    # converter otherwise cannot resolve references to ordinary path nodes.
    by_id={e.get('id'):e for e in root.iter() if e.get('id')}
    for parent in root.iter():
        for i,child in enumerate(list(parent)):
            if not child.tag.endswith('}use'):continue
            href=child.get('{http://www.w3.org/1999/xlink}href','').lstrip('#')
            if href not in by_id:continue
            clone=copy.deepcopy(by_id[href]);clone.attrib.pop('id',None)
            clone.set('transform',child.get('transform','')+' '+clone.get('transform',''))
            parent.remove(child);parent.insert(i,clone)
    xml=ET.tostring(root,encoding='utf-8',xml_declaration=True)
    src=fitz.open('svg',xml)
    return fitz.open('pdf',src.convert_to_pdf())

def draw_text(c,x,y,s,size=7,angle=0):
    c.saveState();c.translate(x,H-y);c.rotate(angle);c.setFillColorRGB(0,0,0);c.setFont('CN',size);c.drawString(0,0,s);c.restoreState()

def para(c,x,y,s,width=158,size=6,leading=8.5):
    p=Paragraph(s.replace('\n','<br/>'),ParagraphStyle('p',fontName='CN',fontSize=size,leading=leading,wordWrap='CJK'))
    _,h=p.wrap(width,1000);p.drawOn(c,x,H-y-h);return y+h

def new_text():
    buf=io.BytesIO();c=canvas.Canvas(buf,pagesize=(W,H))
    draw_text(c,95.419,30.989,'NixOS',16)
    draw_text(c,95.419+pdfmetrics.stringWidth('NixOS','CN',16)+1,30.989-7,'®',6)
    draw_text(c,95.419,75.694,'请仔细阅读安装说明并在管理员指导下使用',7)
    draw_text(c,95.419,84.094,'安装前请备份数据，谨慎分区',7)
    for y in [105.786,338.769,380.175]:
        draw_text(c,95.419,y,'NixOS',16)
        nx=95.419+pdfmetrics.stringWidth('NixOS','CN',16)
        draw_text(c,nx+1,y-7,'®',6)
        gx=nx+7
        draw_text(c,gx,y,' GNU/Linux',16)
        draw_text(c,gx+pdfmetrics.stringWidth(' GNU/Linux','CN',16)+1,y-7,'™',6)
    for y in [131.786,406.175]:draw_text(c,95.419,y,'盒装安装媒介',19)
    for y in [39.988,280.932,334.788,575.956]:
        draw_text(c,263.435,y,'— Flash drive',8);draw_text(c,263.435,y+13,'— x86_64',8)
    for y in [91,386]:draw_text(c,319,y-6,'®',4.5)
    draw_text(c,64.714,340.773,'NixOS',6.46,90);draw_text(c,73.711,346.313,'GNU/Linux',6.46,90)
    draw_text(c,345.589,277.173,'声明式配置 · 系统代际回滚',6,90)
    draw_text(c,356.587,283.893,'网站查询：www.nixos.org',6,90)
    # These values are package-design information, not a fabricated release.
    for x,label,value in [(69.45,'产品批号','NixOS'),(59.447,'设计日期','2026-10-28'),(49.444,'有效期至','参见发行说明')]:
        draw_text(c,x,364.674,label,7,-90);draw_text(c,x,446.314,value,7,-90)
    y=para(c,95.419,443,'NixOS 是一个基于 Linux 的操作系统（OS）。提供您安装在计算机上使用。操作系统就是能让您的计算机工作的一系列基本程序和实用工具。',158,5.7,7.2)+5
    y=para(c,95.419,y,'NixOS 不只是一个纯粹的操作系统：它使用 Nix 包管理器，通过声明式配置描述软件包、系统服务与运行环境。将系统配置构建为新的系统代际。以便于在不同的计算机上复现相同的环境',158,5.7,7.2)+5
    y=para(c,95.419,y,'硬件要求(桌面):AMD64 或 Intel64处理器\n2GB内存 （推荐8GB）\n10GB硬盘可用空间\n安装前备份所有段数据，谨慎分区\n安装方法，发行说明，注意事项等详见说明书\n系统回滚不能替代个人文件与数据库备份。\n许可协议：MIT，内含软件分别遵循各自许可条款。\n网站主页：https://nixos.org/download/',158,5.7,7.2)
    assert y < 574, f'正文超出原版区域：{y}'
    draw_text(c,159.932,621.563,'改编自 github.com/moesoha/debian-media-box',4)
    draw_text(c,262.436,620.042,'NixOS 20261028',6)
    c.save();return buf.getvalue()

def logos():
    doc=fitz.open();p=doc.new_page(width=W,height=H)
    snow=clean_svg(ROOT/'artwork'/'nix-snowflake.svg',pale=True)
    word=clean_svg(ROOT/'artwork'/'nixos.svg',wordmark=True)
    p.show_pdf_page(fitz.Rect(116,135,231,250),snow,0)
    p.show_pdf_page(fitz.Rect(139,401,208,470),snow,0)
    for r in [(264,78,320,99),(264,373,320,394)]:p.show_pdf_page(fitz.Rect(r),word,0)
    return doc.tobytes(garbage=4,deflate=True)

def make():
    reader=PdfReader(SOURCE);writer=PdfWriter();writer.clone_document_from_reader(reader)
    page=writer.pages[0];old=ContentStream(page.get_contents(),writer);ops=list(old.operations)
    for n in ['/Fm0','/Fm1','/Fm16']:colored_form(writer,page,n,'fill')
    for n in [f'/Fm{x}' for x in range(6,16)]+['/Fm17','/Fm18']:colored_form(writer,page,n,'stroke')
    layers=['白底','background-stripes','dielines-and-folds','印刷辅助'];groups=[];properties=DictionaryObject();out=[]
    def new_layer(name):
        ref=writer._add_object(DictionaryObject({NameObject('/Type'):NameObject('/OCG'),NameObject('/Name'):TextStringObject(name)}));groups.append(ref)
        key=NameObject(f'/Part{len(groups)}');properties[key]=ref;return key
    for name in layers:
        key=new_layer(name)
        out += [([],b'q'),([NameObject('/OC'),key],b'BDC')]+isolated(ops,name)+[([],b'EMC'),([],b'Q')]
    page['/Resources'][NameObject('/Properties')]=properties
    old.operations=out;page[NameObject('/Contents')]=writer._add_object(old)
    # Add new vector artwork and type as separately switchable PDF layers.
    for name,data in [('NixOS标志',logos()),('NixOS文字',new_text())]:
        overlay=PdfReader(io.BytesIO(data)).pages[0]
        key=new_layer(name)
        overlay['/Resources'][NameObject('/Properties')]=DictionaryObject({key:properties[key]})
        cs=ContentStream(overlay.get_contents(),writer)
        cs.operations=[([NameObject('/OC'),key],b'BDC')]+cs.operations+[([],b'EMC')]
        overlay[NameObject('/Contents')]=cs
        page.merge_page(overlay,over=True)
    writer._root_object[NameObject('/OCProperties')]=DictionaryObject({
        NameObject('/OCGs'):ArrayObject(groups),NameObject('/D'):DictionaryObject({
            NameObject('/Order'):ArrayObject(list(reversed(groups))),NameObject('/ON'):ArrayObject(groups),NameObject('/RBGroups'):ArrayObject()})})
    writer.add_metadata({'/Title':'NixOS 小药盒 | 原版刀模改编','/Author':'Adapted from moesoha/debian-media-box; NixOS logo by Simon Frankau and Tim Cuthbertson'})
    target=OUT/'nixos-pillbox-layered-actual-size.pdf'
    with target.open('wb') as f:writer.write(f)
    d=fitz.open(target);ap=fitz.open();p=ap.new_page(width=595.276,height=841.89)
    x=(p.rect.width-W)/2;y=(p.rect.height-H)/2;p.show_pdf_page(fitz.Rect(x,y,x+W,y+H),d,0)
    ap.save(OUT/'nixos-pillbox-a4-print.pdf',garbage=4,deflate=True)
    pdfium.PdfDocument(target)[0].render(scale=2).to_pil().save(OUT/'nixos-pillbox-preview.png')
    print('Built',target)

if __name__=='__main__':make()
