#!/usr/bin/env python3
"""Produção Vídeo #1 - O Código Oculto
Gera TTS (voz pt-BR) + slides (Pillow) + sidecar JSON para o vídeo.
Estágios 1-3 do pipeline.
"""
import asyncio, json, os, subprocess
from PIL import Image, ImageDraw, ImageFont

WORK = r"C:/Users/familia gidelu/Documents/Obsidian Vault/Projects/Ativos/Canal-Producao/video01"
VOICE = "pt-BR-AntonioNeural"   # voz masculina de narração
RATE  = "-5%"                    # um pouco mais lenta/profunda pra tom misterioso

# (id, narração, título do slide, subtítulo do slide)
SCENES = [
    ("c01",
     "A gente cresce ouvindo a mesma fórmula: estude, arrume um bom emprego, trabalhe duro, e um dia você será recompensado. Mas olha os números: a maioria das pessoas trabalha cada vez mais, e continua no mesmo lugar. Por quê? Porque trabalho duro sozinho não constrói riqueza. Ele constrói salário.",
     "Trabalhar duro ≠ riqueza",
     "A fórmula que te ensinaram está incompleta"),
    ("c02",
     "Existe um ciclo invisível que prende a maioria das pessoas. Você ganha mais, então gasta mais. Consegue uma promoção, sobe o padrão de vida. Compra um carro melhor, uma casa maior, e as dívidas crescem junto. No fim, você corre cada vez mais rápido na mesma roda. Kiyosaki chama isso de corrida dos ratos: trabalhar pra pagar contas que crescem na mesma velocidade do salário.",
     "A corrida dos ratos",
     "Ganha mais, gasta mais, roda mais rápido"),
    ("c03",
     "E aqui está o ponto que muda tudo. Os ricos não ficam mais ricos porque trabalham mais. Eles ficam ricos porque compram ativos. Um ativo é qualquer coisa que coloca dinheiro no seu bolso: um negócio, um imóvel alugado, investimentos. Um passivo é o que tira dinheiro do bolso: um carro financiado, uma casa que só gera gastos. A classe média compra passivos achando que são ativos. Os ricos compram ativos até que eles paguem suas despesas.",
     "Ativo vs passivo",
     "Ativo coloca dinheiro no bolso. Passivo tira."),
    ("c04",
     "Kiyosaki resume em uma frase: os ricos não trabalham por dinheiro, eles fazem o dinheiro trabalhar por eles. Enquanto você troca seu tempo por dinheiro, uma hora por dia, o dinheiro que você investe trabalha vinte e quatro horas por dia, sete dias por semana, sem férias, sem reclamar. Essa é a diferença entre trocar tempo por dinheiro e construir sistemas que geram dinheiro sem o seu tempo.",
     "Dinheiro trabalhando por você",
     "Seu tempo é limitado. Seus ativos não."),
    ("c05",
     "Então o que substitui o esforço? Não é preguiça, é alavancagem. É construir coisas que funcionam sem você: um negócio com processos, investimentos que rendem, uma audiência que te segue, um produto digital que se vende enquanto você dorme. O esforço importa, mas importa na direção certa. Esforço em construir ativos, não em trocar mais horas por reais.",
     "O que substitui o esforço?",
     "Alavancagem: sistemas que funcionam sem você"),
    ("c06",
     "E a boa notícia? Você não precisa de milhões pra começar. O primeiro passo é pequeno e está ao seu alcance: antes de gastar com o que você quer, invista em algo que te gere retorno. Estude o que você precisa pra construir um ativo. Dedique uma parte da sua renda a isso. Troque uma hora de consumo por uma hora de construção. A riqueza não vem de trabalhar mais, vem de construir mais. Se este vídeo mexeu com você, compartilha com alguém que precisa ouvir isso. Se inscreve, ativa o sino, e me conta nos comentários: o que você vai construir essa semana?",
     "Comece pequeno",
     "Invista. Construa. A riqueza vem do que você constrói."),
]

def font(size, bold=False):
    paths = [r"C:/Windows/Fonts/arialbd.ttf" if bold else r"C:/Windows/Fonts/arial.ttf"]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()

def wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def make_slide(sid, title, sub, out):
    W, H = 1280, 720
    # gradiente roxo escuro (a marca)
    top = (20, 8, 40); bot = (45, 12, 80)
    img = Image.new("RGB", (W, H))
    dr = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H-1)
        c = tuple(int(top[i] + (bot[i]-top[i])*t) for i in range(3))
        dr.line([(0, y), (W, y)], fill=c)
    # barra dourada no topo
    dr.rectangle([0, 0, W, 6], fill=(230, 184, 0))
    # título central (dourado)
    f_title = font(86, bold=True)
    lines = wrap(dr, title, f_title, W-160)
    y = H//2 - 90
    for ln in lines:
        tw = dr.textlength(ln, font=f_title)
        dr.text(((W-tw)//2, y), ln, font=f_title, fill=(245, 215, 110))
        y += 100
    # subtítulo (branco suave)
    f_sub = font(44)
    if sub:
        y += 10
        for ln in wrap(dr, sub, f_sub, W-240):
            tw = dr.textlength(ln, font=f_sub)
            dr.text(((W-tw)//2, y), ln, font=f_sub, fill=(200, 200, 215))
            y += 54
    img.save(out)
    print(f"  slide {sid}: {out}")

async def tts(text, out):
    import edge_tts
    await edge_tts.Communicate(text, VOICE, rate=RATE).save(out)

def probe_dur(path):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

async def main():
    os.makedirs(WORK, exist_ok=True)
    meta = []
    for sid, nar, title, sub in SCENES:
        mp3 = os.path.join(WORK, f"{sid}.mp3")
        png = os.path.join(WORK, f"{sid}.png")
        print(f"[{sid}] gerando voz + slide...")
        await tts(nar, mp3)
        make_slide(sid, title, sub, png)
        dur = probe_dur(mp3)
        meta.append({"id": sid, "audio": sid+".mp3", "slide": sid+".png",
                     "duration": dur, "title": title, "sub": sub})
        print(f"  voz {sid}: {dur:.1f}s")
    with open(os.path.join(WORK, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print("\n✅ Produção estágios 1-3 concluída.")
    total = sum(m["duration"] for m in meta)
    print(f"Total narração: {total:.1f}s (~{total/60:.1f} min)")

asyncio.run(main())