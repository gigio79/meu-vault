#!/usr/bin/env python3
"""Montagem V2 - slides com Ken Burns (zoompan) cinematográfico.
Cada cena: zoom lento/pan na imagem 2560x1440 -> output 1920x1080.
Estágios 4-5: clips + concat + música ambiente.
"""
import json, os, subprocess

WORK = r"C:/Users/familia gidelu/Documents/Obsidian Vault/Projects/Ativos/Canal-Producao/video02"
TAIL = 0.6
BACK_HOLD = 0.8  # respiro antes da próxima cena

with open(os.path.join(WORK,"meta.json"),encoding="utf-8") as f:
    meta=json.load(f)

def run(cmd):
    print("RUN:", " ".join(cmd)[:150])
    r=subprocess.run(cmd,capture_output=True,text=True)
    if r.returncode!=0:
        print("ERR:",r.stderr[-900:]); raise SystemExit(1)

def dur(p):
    r=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p],capture_output=True,text=True)
    return float(r.stdout.strip())

# zoompan: frame-based. fps=30. zoom de 1.0 -> 1.12 com pan suave.
# input 2560x1440; zoompan trabalha frames; d = duração*fps.
FPS=30

def clip_cmd(sid,png,mp3,dur_s,idx):
    out=os.path.join(WORK,sid+".mp4")
    frames=int(dur_s*FPS)
    # alternar direção do zoom (in/out) entre cenas p/ variedade
    if idx%2==0:
        zoom_expr=f"min(1.0+0.14*on/{frames},1.14)"
    else:
        zoom_expr=f"max(1.14-0.14*on/{frames},1.0)"
    # pan sutil horizontal dependendo da cena
    x_expr=f"(iw-iw/zoom)*({idx%3}/3)"
    vf=(f"zoompan=z='{zoom_expr}':x='{x_expr}':y='(ih-ih/zoom)/2':"
        f"d={frames}:s=1920x1080:fps={FPS},format=yuv420p,"
        f"fade=t=in:st=0:d=0.4,fade=t=out:st={dur_s-0.4:.2f}:d=0.4[v]")
    fc=vf+";[1:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo[a]"
    run(["ffmpeg","-y","-loop","1","-i",png,"-i",mp3,
         "-filter_complex",fc,"-map","[v]","-map","[a]",
         "-t",f"{dur_s:.2f}","-r",str(FPS),
         "-c:v","libx264","-preset","veryfast","-crf","22","-c:a","aac","-b:a","160k",
         out])
    return out

listf_lines=[]
# intro (black, breve)
intro=os.path.join(WORK,"intro.mp4")
run(["ffmpeg","-y","-f","lavfi","-t",str(1.6),"-i","anullsrc=r=44100:cl=stereo",
     "-f","lavfi","-i","color=c=0x10081f:s=1920x1080:r=30",
     "-filter_complex","[1:v]format=yuv420p,fade=t=out:st=1.2:d=0.4[v]",
     "-map","[v]","-map","0:a","-c:v","libx264","-preset","veryfast","-crf","22",
     "-c:a","aac","-b:a","160k","-shortest",intro])
listf_lines.append(intro)

for i,m in enumerate(meta):
    dur_s=BACK_HOLD+m["duration"]+TAIL
    print(f"== {m['id']} ({dur_s:.1f}s) ==")
    c=clip_cmd(m["id"],os.path.join(WORK,m["slide"]),os.path.join(WORK,m["audio"]),dur_s,i)
    listf_lines.append(c)

listf=os.path.join(WORK,"list.txt")
with open(listf,"w") as f:
    for p in listf_lines: f.write(f"file '{p}'\n")
print("== concat ==")
run(["ffmpeg","-y","-f","concat","-safe","0","-i",listf,"-c","copy",os.path.join(WORK,"base.mp4")])

print("== musica ambiente ==")
import numpy as np, wave
base_dur=dur(os.path.join(WORK,"base.mp4"))
def synth_bed(path,dur_s,sr=44100):
    t=np.linspace(0,dur_s,int(sr*dur_s),endpoint=False)
    mix=np.zeros_like(t)
    for f in [110,164.81,220,246.94]:  # A menor ampla, grave e ambiente
        mix+=np.sin(2*np.pi*f*t)*0.04
    lfo=0.5+0.5*np.sin(2*np.pi*0.03*t)
    mix=mix*lfo
    mix=mix/np.max(np.abs(mix))*0.6
    pcm=(mix*32767).astype(np.int16)
    with wave.open(path,"w") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(pcm.tobytes())
bed=os.path.join(WORK,"bed.wav"); synth_bed(bed,base_dur+1.0)

print("== mix ==")
run(["ffmpeg","-y","-i",os.path.join(WORK,"base.mp4"),"-i",bed,
     "-filter_complex","[0:a]aresample=44100[a0];[1:a]aresample=44100,volume=0.12[bg];[a0][bg]amix=inputs=2:duration=first:dropout_transition=0[a]",
     "-map","0:v","-map","[a]","-c:v","copy","-c:a","aac","-b:a","160k",
     os.path.join(WORK,"final.mp4")])
print("✅ VÍDEO V2 PRONTO:",os.path.join(WORK,"final.mp4"))