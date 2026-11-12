"""Build an A4 leaflet modelled on the upstream instruction.pdf.

Edit the paragraphs below and run this script to rebuild. Requires ReportLab,
PyMuPDF, pypdfium2 and the fonts specified below.
"""
from pathlib import Path
import io, json, sys, importlib.util
ROOT=Path(__file__).resolve().parents[2]/'existing-assets'/'pillboxes'/'nixos'
sys.path.insert(0,str(Path(__file__).resolve().parent/'vendor'))
import pymupdf as fitz
import pypdfium2 as pdfium
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from xml.sax.saxutils import escape

spec=importlib.util.spec_from_file_location('box_builder',Path(__file__).with_name('box_layout.py'))
box=importlib.util.module_from_spec(spec);spec.loader.exec_module(box)
pdfmetrics.registerFont(TTFont('Song','C:/Windows/Fonts/simsun.ttc'))
pdfmetrics.registerFont(TTFont('Hei','C:/Windows/Fonts/msyhbd.ttc'))
pdfmetrics.registerFont(TTFont('Yahei','C:/Windows/Fonts/msyh.ttc'))
W,H=595.276,841.89
OUT=ROOT/'output'

WARNING='无论是否与其他操作系统合用，安装 NixOS 均存在丢失磁盘上所有内容的风险。（参见【注意事项】）\n分区、格式化和写入安装镜像可能覆盖数据。操作前应备份重要文件，并确认目标磁盘。\n系统代际回滚不能代替个人文件或数据库备份。硬件驱动与固件的可用性因设备而异，请根据实际情况查阅官方文档。'
COLS=[
 [('发行版名称','通用名称：NixOS\n正式名称：NixOS GNU/Linux\n系统类别：基于 Linux 的操作系统'),
  ('内容','NixOS 是一个基于 Linux 的操作系统（OS）。操作系统包含能让计算机工作的一系列基本程序和实用工具。\nNixOS 使用 Nix 包管理器，以声明式配置描述软件包、系统服务与运行环境。'),
  ('性质','修改系统配置后，可构建新的系统代际。保留旧代际有助于切换和回滚；固定配置输入有助于在不同计算机上复现环境。'),
  ('适应平台','► 官方提供 x86_64（64 位 Intel / AMD）和 aarch64（64 位 ARM）安装镜像。\n► 盒内安装媒介适用于何种平台，以介质上的实际标注为准。'),
  ('规格','1 枚安装媒介。'),
  ('用法','使用 USB 设备引导。启动方式应根据硬件调整，一般使用 UEFI。\n图形镜像提供图形安装器；最小镜像通过命令行安装。安装前请参阅官方手册，确认磁盘、分区、引导器及网络配置。')],
 [('不良反应','首次安装或构建可能下载较多数据；没有可用二进制缓存时，部分软件可能需要本地构建。\n某些软件假定传统 Linux 文件布局，可能需要额外打包或兼容设置。发生错误时请保存日志，检查配置与网络连接。'),
  ('注意事项','► 满足硬件要求\n本盒桌面配置建议：AMD64 或 Intel 64 处理器；2 GB 内存（推荐 8 GB）；10 GB 可用磁盘空间。实际需求取决于所选桌面、软件及系统代际。\n► 安装前备份\n安装、分区、格式化和写入镜像可能导致数据丢失。双系统用户还应备份恢复密钥及引导信息。\n► 系统代际与回滚\n旧代际可帮助恢复系统配置，但不恢复个人文件，也不一定撤销数据库迁移；数据仍需单独备份。'),
  ('配置与更新','传统配置文件通常位于：\n/etc/nixos/configuration.nix\n修改后可先构建检查：\nnixos-rebuild build\n再构建并启用：\nsudo nixos-rebuild switch\n若使用 flake，请依照自己的配置入口操作。系统启动菜单可用于选择仍保留的旧代际。'),
  ('禁忌','出现或即将出现下列情况，请停止操作并确认恢复方案：\n► 未核对设备名即写入镜像或格式化。\n► 未备份即调整分区或覆盖数据。\n► 未经检查执行来自网络的脚本。\n► 尚未验证新代际就删除全部旧代际。')],
 [('系统相互作用','► 与 Windows 的相互作用\n双系统应提前规划分区与引导方式。共享文件系统时，Windows 的快速启动和休眠可能影响文件系统状态；请妥善关闭系统后再切换。修改磁盘或引导配置前，备份数据及加密恢复密钥。\n► 与其他 Linux 发行版的相互作用\nNixOS 的系统目录与软件管理方式可能不同，不宜直接套用依赖传统目录布局的安装脚本。'),
  ('贮藏','安装介质的存储条件以设备制造商标注为准。避免高温、潮湿与静电；妥善保存配置文件及重要数据的备份。'),
  ('包装','装有 NixOS 安装镜像的 USB 大容量存储设备。\n1 枚 / 盒。'),
  ('有效期','系统版本与维护期限以安装镜像及官方发布公告为准。请及时检查更新和版本支持状态。'),
  ('执行标准','软件授权：内含软件分别遵循各自的许可条款。\n设计授权：CC BY-SA 3.0。'),
  ('资料入口','下载：nixos.org/download/\n手册：nixos.org/manual/nixos/stable/\n软件与选项：search.nixos.org'),
  ('leaflet','改编自：moesoha/debian-media-box\n原作编审：@YukariChiba、@moesoha\n原作图形：@YJBeetle\nNix 标志：Simon Frankau、Tim Cuthbertson\nNixOS 改编 · 2026 年 10 月')]
]

def text(c,x,y,s,size=9,font='Song'):
    c.setFillColorRGB(0,0,0);c.setFont(font,size);c.drawString(x,H-y,s)

def para(c,x,y,s,w,size=9,leading=11.4,font='Song'):
    style=ParagraphStyle('body',fontName=font,fontSize=size,leading=leading,wordWrap='CJK',allowWidows=0,allowOrphans=0)
    content=escape(s).replace('►','<font name="Yahei">▶</font>').replace('\n','<br/>')
    p=Paragraph(content,style)
    _,h=p.wrap(w,1000);p.drawOn(c,x,H-y-h)
    return y+h

def build():
    buf=io.BytesIO();c=canvas.Canvas(buf,pagesize=(W,H))
    text(c,25.5,33,'编制日期：2026 年 10 月 28 日',9)
    text(c,25.5,45,'改编自 Debian 小药盒；请核对盒内介质的版本和架构。',9)
    text(c,25.5,57,'请仔细阅读说明书并在熟悉系统安装的人员指导下使用。',9)
    c.setFillColor(HexColor('#c9c9c9'));c.rect(117,H-148,268,78,stroke=0,fill=1)
    c.saveState();clip=c.beginPath();clip.rect(117,H-148,268,78);c.clipPath(clip,stroke=0)
    c.setStrokeColor(HexColor('#ffffff'));c.setLineWidth(1)
    for y in range(69,200,12):c.line(117,H-y,385,H-y+50)
    c.restoreState();c.setStrokeColorRGB(0,0,0);c.setLineWidth(.8)
    c.line(25.5,H-70,385,H-70);c.line(25.5,H-148,385,H-148)
    text(c,134,111,'NixOS 盒装安装媒介说明书',13,'Yahei')
    text(c,134,132,'请仔细阅读说明书并在管理员指导下使用',9,'Yahei')
    text(c,185,165,'警示语',9,'Hei')
    warn_end=para(c,35,171,WARNING,340,8.8,11.4,'Hei')
    bottoms=[]
    for col,sections in enumerate(COLS):
        x=25.5+col*184.25;y=286 if col<2 else 26
        for title,body in sections:
            c.setFillColor(HexColor('#cecece'));c.rect(x,H-y-22,173,22,stroke=0,fill=1)
            text(c,x+3,y+15,'【'+title+'】',9,'Hei')
            y=para(c,x,y+28,body,173,8.7,11.0)+9
        bottoms.append(y)
    if warn_end>278 or max(bottoms)>802:raise ValueError(f'内容超出版面：警示语 {warn_end}，各栏 {bottoms}')
    text(c,454,790,'NixOS GNU/Linux',9,'Yahei');text(c,485,804,'20261028',9,'Yahei')
    c.save();doc=fitz.open('pdf',buf.getvalue());page=doc[0]
    logo=box.clean_svg(ROOT/'artwork'/'nixos.svg',wordmark=True)
    page.show_pdf_page(fitz.Rect(34,89,108,133),logo,0)
    page.show_pdf_page(fitz.Rect(486,810,568,834),logo,0)
    doc.set_metadata({'title':'NixOS 盒装安装媒介说明书','author':'Adapted from moesoha/debian-media-box; NixOS logo Simon Frankau and Tim Cuthbertson'})
    target=OUT/'nixos-pillbox-leaflet.pdf';doc.save(target,garbage=4,deflate=True)
    pdfium.PdfDocument(target)[0].render(scale=1.8).to_pil().save(OUT/'nixos-pillbox-leafletpreview.png')
    (ROOT/'leaflet.svg').write_text(page.get_svg_image(text_as_path=False),encoding='utf-8')
    print('Created:',target,'warning end:',warn_end,'column ends:',bottoms)

if __name__=='__main__':
    content_file=ROOT/'leaflet-content.json'
    if content_file.exists():
        content=json.loads(content_file.read_text(encoding='utf-8'))
        WARNING,COLS=content['警示语'],content['栏目']
    else:
        content_file.write_text(json.dumps({'警示语':WARNING,'栏目':COLS},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    build()
