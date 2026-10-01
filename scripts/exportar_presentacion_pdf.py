"""Exporta un PDF estático desde la fuente del deck. Requiere reportlab.

No ejecuta la interactividad del HTML; incluye sus devoluciones como texto.
"""
import json
import sys
from html import escape
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generar_presentacion import fragmento  # noqa: E402
d=json.loads((ROOT/'docs/warroom/diapositivas.json').read_text())
fontdir=Path('/System/Library/Fonts/Supplemental')
if (fontdir/'Arial.ttf').exists():
    pdfmetrics.registerFont(TTFont('Deck',str(fontdir/'Arial.ttf')))
    pdfmetrics.registerFont(TTFont('DeckBold',str(fontdir/'Arial Bold.ttf')))
else:
    fontdir=Path('/usr/share/fonts/truetype/dejavu')
    pdfmetrics.registerFont(TTFont('Deck',str(fontdir/'DejaVuSans.ttf')))
    pdfmetrics.registerFont(TTFont('DeckBold',str(fontdir/'DejaVuSans-Bold.ttf')))
mono=next((p for p in [fontdir/'Courier New.ttf', Path('/System/Library/Fonts/Menlo.ttc'), Path('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')] if p.exists()), None)
if mono: pdfmetrics.registerFont(TTFont('Mono',str(mono)))
MONO='Mono' if mono else 'Deck'
W,H=960,540
BG=colors.HexColor('#0b1823');INK=colors.HexColor('#f2f6fa');MUTED=colors.HexColor('#acc1d0');ACCENT=colors.HexColor('#69e0c5');PANEL=colors.HexColor('#142b3b')
sec={x['id']:x for x in d['sections']}
c=canvas.Canvas(str(ROOT/'docs/presentacion-warroom.pdf'),pagesize=(W,H))
c.setTitle(d['title']);c.setAuthor('War Room · Alephee × Craftech × AWS')
def para(text,size=19,color=INK,bold=False):
    return Paragraph(escape(text),ParagraphStyle('p',fontName='DeckBold' if bold else 'Deck',fontSize=size,leading=size*1.25,textColor=color,spaceAfter=0))

def make_blocks(s,k):
    b=[]
    def add(text,size=19,color=INK,bold=False,gap=10):
        if text:b.append((para(text,size*k,color,bold),gap*k))
    add(sec[s['section']]['goal'],12,ACCENT,gap=14)
    add(s['title'],40 if s['kind']=='divider' else 29,INK,True,18)
    add(s['lead'],17,MUTED,gap=12)
    add(s['label'],11,colors.HexColor('#f6d78b'),gap=14)
    if s['kind']=='code':
        f=fragmento(s['code'],ROOT)
        fin=f['inicio']+len(f['lineas'])-1
        add(f"{f['file']} · líneas {f['inicio']}–{fin}",11,ACCENT,gap=8)
        for n,l in enumerate(f['lineas'],start=f['inicio']):
            b.append((Paragraph(f"<font color='#5b7488'>{n:>4}</font>  {escape(l).replace(' ','&nbsp;')}",ParagraphStyle('c',fontName=MONO,fontSize=11*k,leading=14*k,textColor=ACCENT if n in f['highlight'] else INK)),0))
        if f['caption']:add(f['caption'],15,MUTED,gap=8)
    if s['kind']=='decision':
        d=s['decision'];add(f"DECISIÓN {d['number']}",12,ACCENT,gap=8);add(d['question'],22,INK,True,gap=12)
        for o in d['options']:add(o,17,gap=8)
        add('PROPUESTA · '+d['proposal'],14,ACCENT,gap=8);add(d['file'],11,MUTED,gap=0)
    if s['kind']=='demo' and s.get('demo'):
        d=s['demo'];b.append((Paragraph(escape(d['command']),ParagraphStyle('m',fontName=MONO,fontSize=14*k,leading=18*k,textColor=ACCENT)),14*k))
        for w in d['watch']:add('•  '+w,18,gap=8)
        if d.get('fallback'):add('Respaldo · '+d['fallback'],13,MUTED,gap=0)
    for j,item in enumerate(s['items']):
        prefix=f'{j+1:02}  ' if s['kind']=='flow' else '•  '
        add(prefix+item,20 if s['kind']!='quiz' else 18,gap=12)
    if s['table']:
        t=s['table'];rows=[t['headers'],*t['rows']]
        values=[[para(v,15*k,ACCENT if i==0 else INK,i==0 or j==0) for j,v in enumerate(row)] for i,row in enumerate(rows)]
        table=Table(values,colWidths=[320,116,116,116,116])
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PANEL),('LINEBELOW',(0,0),(-1,-1),.5,colors.HexColor('#365166')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),12*k),('BOTTOMPADDING',(0,0),(-1,-1),12*k)]))
        b.append((table,15*k))
    if s['exercise']:
        e=s['exercise'];add(e['prompt'],19,gap=12)
        for i,x in enumerate(e['steps']):add(f'{i+1}. {x}',17,gap=8)
        add('ENTREGA · '+e['deliverable'],17,ACCENT,True,gap=10)
        add(f"{e['duration']} min de trabajo · {e['debrief']}",13,MUTED,gap=12)
    add(s['question'],19,INK,True,gap=10)
    for o in s['options']:add(o,17,gap=8)
    if s['answer']:add('DEVOLUCIÓN · '+s['answer'],14,ACCENT,gap=0)
    return b
scales=[]
for i,s in enumerate(d['slides']):
    k=1.0
    while True:
        blocks=make_blocks(s,k)
        heights=[b.wrap(W-100,H)[1]+gap for b,gap in blocks]
        total=sum(heights)
        if total<=H-100:break
        k-=.025
        if k<.65:raise ValueError(f'Diapositiva {i+1} demasiado densa para PDF')
    scales.append(k)
    c.setFillColor(BG);c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFont('Deck',9);c.setFillColor(MUTED)
    c.drawString(50,H-25,'ALEPHEE × CRAFTECH × AWS')
    c.drawRightString(W-50,H-25,sec[s['section']]['title']+' · '+sec[s['section']]['time'])
    y=H-55 if s['kind']!='divider' else (H+total)/2
    for (b,gap),height in zip(blocks,heights):
        actual=height-gap;b.drawOn(c,50,y-actual);y-=height
    c.setFillColor(MUTED);c.setFont('Deck',9);c.drawString(50,20,'PDF estático · las propuestas de decisión se incluyen; usar HTML para las notas')
    c.drawRightString(W-50,20,f'{i+1} / {len(d["slides"])}')
    c.setFillColor(ACCENT);c.rect(0,0,W*(i+1)/len(d['slides']),3,fill=1,stroke=0)
    c.showPage()
c.save()
print(f'PDF: {len(scales)} páginas; escala mínima {min(scales):.3f}')
