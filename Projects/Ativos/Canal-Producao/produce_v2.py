#!/usr/bin/env python3
"""Produção V2 - slides procedurais cinematográficos + narração.
Arte generativa (constelações/partículas/olho geométrico) 100% original, sem copyright.
Slides gerados em 2560x1440 (alta res) pra permitir Ken Burns via zoompan no build.
"""
import asyncio, json, os, random, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WORK = r"C:/Users/familia gidelu/Documents/Obsidian Vault/Projects/Ativos/Canal-Producao/video02"
os.makedirs(WORK, exist_ok=True)

# VOICE: trocável; preferêncial ThalitaMultilingual (mais natural). Mantido Antonio p/ contraste de teste.
VOICE = "pt-BR-ThalitaMultilingualNeural"
RATE = "-4%"

# escala da arte (alto para Ken Burns)
SW, SH = 2560, 1440

GOLD = (245, 215, 110)
GOLD_HI = (255, 240, 180)
WHITE = (235, 232, 245)
PURPLE_TOP = (16, 8, 34)
PURPLE_BOT = (42, 14, 84)
ACCENT = (230, 184, 0)

SCENES = [
    ("c01",
     "A gente cresce ouvindo a mesma fórmula: estude, arrume um bom emprego, trabalhe duro, e um dia você será recompensado. Mas olha os números: a maioria das pessoas trabalha cada vez mais, e continua no mesmo lugar. Por quê? Porque trabalho duro sozinho não constrói riqueza. Ele constrói salário.",
     "Trabalhar duro ≠ riqueza",
     "A fórmula que te ensinaram está incompleta", "constellation"),
    ("c02",
     "Existe um ciclo invisível que prende a maioria das pessoas. Você ganha mais, então gasta mais. Consegue uma promoção, sobe o padrão de vida. Compra um carro melhor, uma casa maior, e as dívidas crescem junto. No fim, você corre cada vez mais rápido na mesma roda. A corrida dos ratos: trabalhar pra pagar contas que crescem na mesma velocidade do salário.",
     "A corrida dos ratos",
     "Ganha mais, gasta mais, roda mais rápido", "cycle"),
    ("c03",
     "E aqui está o ponto que muda tudo. Os ricos não ficam mais ricos porque trabalham mais. Eles ficam ricos porque compram ativos. Um ativo é qualquer coisa que coloca dinheiro no seu bolso: um negócio, um imóvel alugado, investimentos. Um passivo é o que tira dinheiro do bolso: um carro financiado, uma casa que só gera gastos. A classe média compra passivos achando que são ativos. Os ricos compram ativos até que eles paguem suas despesas.",
     "Ativo vs passivo",
     "Ativo coloca dinheiro no bolso. Passivo tira.", "eye"),
    ("c04",
     "Os ricos não trabalham por dinheiro, eles fazem o dinheiro trabalhar por eles. Enquanto você troca seu tempo por dinheiro, uma hora por dia, o dinheiro que você investe trabalha vinte e quatro horas por dia, sete dias por semana, sem férias, sem reclamar. Essa é a diferença entre trocar tempo por dinheiro e construir sistemas que geram dinheiro sem o seu tempo.",
     "Dinheiro trabalhando por você",
     "Seu tempo é limitado. Seus ativos não.", "rise"),
    ("c05",
     "Então o que substitui o esforço? Não é preguiça, é alavancagem. É construir coisas que funcionam sem você: um negócio com processos, investimentos que rendem, uma audiência que te segue, um produto digital que se vende enquanto você dorme. O esforço importa, mas importa na direção certa. Esforço em construir ativos, não em trocar mais horas por reais.",
     "O que substitui o esforço?",
     "Alavancagem: sistemas que funcionam sem você", "particles"),
    ("c06",
     "E a boa notícia? Você não precisa de milhões pra começar. O primeiro passo é pequeno e está ao seu alcance: antes de gastar com o que você quer, invista em algo que te gere retorno. Estude o que você precisa pra construir um ativo. Dedique uma parte da sua renda a isso. Troque uma hora de consumo por uma hora de construção. A riqueza não vem de trabalhar mais, vem de construir mais. Se este vídeo mexeu com você, compartilha com alguém que precisa ouvir isso. Se inscreve, ativa o sino, e me conta nos comentários: o que você vai construir essa semana?",
     "Comece pequeno",
     "Invista. Construa. A riqueza vem do que você constrói.", "horizon"),
]

def font(size, bold=False):
    for p in ([r"C:/Windows/Fonts/timesbd.ttf" if bold else r"C:/Windows/Fonts/times.ttf",
               r"C:/Windows/Fonts/georgiab.ttf" if bold else r"C:/Windows/Fonts/georgia.ttf",
               r"C:/Windows/Fonts/arialbd.ttf" if bold else r"C:/Windows/Fonts/arial.ttf"]):
        try: return ImageFont.truetype(p, size)
        except Exception: continue
    return ImageFont.load_default()

def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def glow_layer(size, r=12):
    """helper: gaussian blur pass"""
    return None

def add_glow(img, color, xy, radius, alpha):
    """draw a soft glow dot"""
    d = ImageDraw.Draw(img)
    x, y = xy
    for i in range(radius, 0, -1):
        a = int(alpha * (i/radius))
        d.ellipse([x-i,y-i,x+i,y+i], fill=(color[0],color[1],color[2],a))
    return img

def paint_background(draw):
    for y in range(SH):
        t = y/(SH-1)
        c = tuple(int(PURPLE_TOP[i]+(PURPLE_BOT[i]-PURPLE_TOP[i])*t) for i in range(3))
        draw.line([(0,y),(SW,y)], fill=c)

def draw_stars(img, n=140, rng=None):
    rng = rng or random
    d = ImageDraw.Draw(img)
    for _ in range(n):
        x = rng.randint(0,SW); y = rng.randint(0,SH)
        r = rng.choice([1,1,1,2,2,3])
        a = rng.randint(30,120)
        col = (GOLD[0],GOLD[1],GOLD[2],a) if rng.random()<0.6 else (WHITE[0],WHITE[1],WHITE[2],a)
        d.ellipse([x-r,y-r,x+r,y+r], fill=col)
    return img

def draw_constellation(img):
    d = ImageDraw.Draw(img)
    rng = random.Random(7)
    pts = [(rng.randint(200,SW-200), rng.randint(180,SH-380)) for _ in range(14)]
    # linhas de código (triângulos) conectando pontos
    for i in range(len(pts)):
        for j in range(i+1,len(pts)):
            if abs(pts[i][0]-pts[j][0])+abs(pts[i][1]-pts[j][1]) < 500 and rng.random()<0.5:
                d.line([pts[i],pts[j]], fill=(230,184,0,60), width=2)
    for x,y in pts:
        add_glow(img,GOLD,(x,y),7,110)
        d.ellipse([x-3,y-3,x+3,y+3], fill=GOLD_HI)
    return img

def draw_cycle(img):
    """triângulo + olho = símbolo do código oculto"""
    d = ImageDraw.Draw(img)
    cx, cy = SW//2, 360
    R = 260
    # triângulo
    tri = [(cx,cy-R),(cx+int(R*math.cos(math.radians(30)))*1, cy+int(R*math.sin(math.radians(30)))*1), (cx-int(R*math.cos(math.radians(30)))*1, cy+int(R*math.sin(math.radians(30)))*1)]
    # ajuste simples: triângulo equilátero
    tri = [(cx, cy-R), (cx+R*math.sqrt(3)/2, cy+R/2), (cx-R*math.sqrt(3)/2, cy+R/2)]
    d.polygon([(int(x),int(y)) for x,y in tri], outline=(245,215,110,120), width=4)
    d.polygon([(int(x),int(y)) for x,y in tri], fill=(245,215,110,14))
    # olho
    ey, erx, ery = cy, 90, 54
    d.ellipse([cx-erx, ey-ery, cx+erx, ey+ery], fill=(240,238,240,235))
    d.ellipse([cx-erx, ey-ery, cx+erx, ey+ery], outline=(230,184,0), width=4)
    d.ellipse([cx-30, ey-30, cx+30, ey+30], fill=(10,8,16))
    d.ellipse([cx-8, ey-12, cx+8, ey+4], fill=(255,255,255,220))
    # raios
    for ang in range(0,360,45):
        a=math.radians(ang); x1=cx+int(R*math.cos(a)); y1=cy+int(R*math.sin(a))
        x2=cx+int((R+60)*math.cos(a)); y2=cy+int((R+60)*math.sin(a))
        d.line([(x1,y1),(x2,y2)], fill=(245,215,110,90), width=3)
    return img

def draw_particles(img):
    d = ImageDraw.Draw(img)
    rng = random.Random(99)
    cx, cy = SW//2, 400
    # cone/ascensão de partículas douradas
    for _ in range(90):
        # distribuição em cone para cima
        yy = rng.randint(cy-320, cy+80)
        spread = (cy+80-yy)/320 * 500
        xx = cx + rng.uniform(-spread, spread)
        r = rng.choice([2,3,4,5])
        a = rng.randint(40,160)
        add_glow(img,GOLD,(int(xx),int(yy)),r+4,a)
        d.ellipse([xx-r,yy-r,xx+r,yy+r], fill=GOLD_HI)
    return img

def draw_rise(img):
    d = ImageDraw.Draw(img)
    # linhas de ascensão + seta pra cima (dinheiro subindo)
    cx = SW//2
    for i in range(9):
        x = cx + (i-4)*46
        d.line([(x, 520),(x, 300)], fill=(245,215,110,70), width=3)
        d.polygon([(x-14,315),(x+14,315),(x,285)], fill=(245,215,110,90))
    for yy in range(300,521,40):
        d.ellipse([cx-14,yy-14,cx+14,yy+14], fill=(245,215,110,20))
    return img

def draw_horizon(img):
    d = ImageDraw.Draw(img)
    cx=SW//2
    # sol/oásis minimalista e linhas de horizonte (início de jornada)
    d.ellipse([cx-150,300,cx+150,600], outline=(245,215,110,60), width=3)
    for i,off in enumerate([-260,-130,0,130,260]):
        y=560-i*12
        d.line([(cx+off-60,y),(cx+off+60,y)], fill=(245,215,110,80), width=3)
    return img

STYLES = {"constellation":draw_constellation,"cycle":draw_cycle,"eye":draw_cycle,"particles":draw_particles,"rise":draw_rise,"horizon":draw_horizon}

def render_text(img, title, sub):
    d = ImageDraw.Draw(img)
    f_title = font(132, bold=True)
    lines = wrap(d, title, f_title, SW-320)
    y = SH//2 - 120
    for ln in lines:
        # sombra
        tw = d.textlength(ln, font=f_title)
        d.text(((SW-tw)//2+3, y+3), ln, font=f_title, fill=(10,8,16,160))
        d.text(((SW-tw)//2, y), ln, font=f_title, fill=GOLD)
        y += 150
    f_sub = font(66)
    if sub:
        y += 6
        for ln in wrap(d, sub, f_sub, SW-420):
            tw = d.textlength(ln, font=f_sub)
            d.text(((SW-tw)//2, y), ln, font=f_sub, fill=(205,202,220,220))
            y += 80
    # barra dourada inferior + faixa binária
    d.rectangle([SW//2-420, SH-40, SW//2+420, SH-38], fill=ACCENT)

def make_slide(sid, title, sub, style_name, out):
    img = Image.new("RGBA",(SW,SH),(0,0,0,0))
    base = Image.new("RGBA",(SW,SH),(0,0,0,255))
    paint_background(ImageDraw.Draw(base))
    img.paste(base,(0,0))
    draw_stars(img)
    STYLES[style_name](img)
    render_text(img,title,sub)
    # leve blur de brilho geral (profundidade)
    glow = img.filter(ImageFilter.GaussianBlur(6))
    img = Image.blend(img, glow, 0.12)
    img = img.convert("RGB")
    img.save(out)
    print(f"  slide {sid}: {out}")

async def tts(text, out):
    import edge_tts
    await edge_tts.Communicate(text, VOICE, rate=RATE).save(out)

def probe(p):
    r=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p],capture_output=True,text=True)
    return float(r.stdout.strip())

async def main():
    meta=[]
    for sid,nar,title,sub,style in SCENES:
        mp3=os.path.join(WORK,sid+".mp3"); png=os.path.join(WORK,sid+".png")
        print(f"[{sid}] voz+slide ({style})...")
        await tts(nar,mp3)
        make_slide(sid,title,sub,style,png)
        meta.append({"id":sid,"audio":sid+".mp3","slide":sid+".png","duration":probe(mp3),"title":title,"sub":sub,"style":style})
        print(f"  voz {sid}: {meta[-1]['duration']:.1f}s")
    with open(os.path.join(WORK,"meta.json"),"w",encoding="utf-8") as f: json.dump(meta,f,ensure_ascii=False,indent=2)
    print("\n✅ Estágios 1-3 V2 concluídos. Total:", f"{sum(m['duration'] for m in meta)/60:.1f}min")

asyncio.run(main())