#!/usr/bin/env python3
"""Montagem Vídeo #1 - estágios 4-5: clips por cena, concat, música ambiente.
Rodar em background (h264 é lento em CPU).
"""
import json, os, subprocess

WORK = r"C:/Users/familia gidelu/Documents/Obsidian Vault/Projects/Ativos/Canal-Producao/video01"
INTRO_HOLD = 1.6
TAIL = 0.6

with open(os.path.join(WORK, "meta.json"), encoding="utf-8") as f:
    meta = json.load(f)

def run(cmd):
    print("RUN:", " ".join(cmd)[:160])
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ERR:", r.stderr[-800:])
        raise SystemExit(1)

def dur_of(path):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

# --- intro clip (silencioso) ---
intro_dur = INTRO_HOLD + meta[0]["duration"]*0.0 + 1.2
print("== intro ==")
run(["ffmpeg","-y","-f","lavfi","-t",str(intro_dur),"-i","anullsrc=r=44100:cl=stereo",
     "-f","lavfi","-i","color=c=0x140828:s=1280x720:r=30",
     "-filter_complex","[1:v]format=yuv420p,fade=t=out:st=1.0:d=0.4[v]",
     "-map","[v]","-map","0:a","-shortest",
     "-c:v","libx264","-preset","veryfast","-crf","23","-c:a","aac","-b:a","160k",
     os.path.join(WORK,"intro.mp4")])

# --- per-scene clips ---
list_txt = [os.path.join(WORK,"intro.mp4")]
for m in meta:
    sid = m["id"]; png=os.path.join(WORK,m["slide"]); mp3=os.path.join(WORK,m["audio"])
    dur = INTRO_HOLD + m["duration"] + TAIL
    out = os.path.join(WORK, f"{sid}.mp4")
    print(f"== clip {sid} ({dur:.1f}s) ==")
    fc = (f"[0:v]scale=1280:720,format=yuv420p,fade=t=in:st=0:d=0.4,"
          f"fade=t=out:st={dur-0.4:.2f}:d=0.4[v];"
          f"[1:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo[a]")
    run(["ffmpeg","-y","-loop","1","-t",f"{dur:.2f}","-i",png,"-i",mp3,
         "-filter_complex",fc,"-map","[v]","-map","[a]","-shortest",
         "-c:v","libx264","-preset","veryfast","-crf","23","-c:a","aac","-b:a","160k",
         out])
    list_txt.append(out)

# --- concat ---
listf = os.path.join(WORK,"list.txt")
with open(listf,"w") as f:
    for p in list_txt:
        f.write(f"file '{p}'\n")
print("== concat ==")
run(["ffmpeg","-y","-f","concat","-safe","0","-i",listf,"-c","copy",os.path.join(WORK,"base.mp4")])

# --- música ambiente (sintetizada) + mix ---
print("== musica ambiente ==")
import numpy as np, wave
def synth_bed(path, dur_s, sr=44100):
    t = np.linspace(0, dur_s, int(sr*dur_s), endpoint=False)
    # acordes ambientes suaves (A menor)
    freq = [220.0, 261.63, 329.63, 440.0]
    mix = np.zeros_like(t)
    for f in freq:
        mix += np.sin(2*np.pi*f*t) * 0.05
    # lfo lento
    lfo = 0.5 + 0.5*np.sin(2*np.pi*0.05*t)
    mix = mix * lfo
    mix = mix / np.max(np.abs(mix)) * 0.7
    pcm = (mix * 32767).astype(np.int16)
    with wave.open(path,"w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(pcm.tobytes())
base_dur = dur_of(os.path.join(WORK,"base.mp4"))
bed = os.path.join(WORK,"bed.wav")
synth_bed(bed, base_dur+1.0)
print(f"  bed gerado ({base_dur:.1f}s)")

print("== mix final ==")
run(["ffmpeg","-y","-i",os.path.join(WORK,"base.mp4"),"-i",bed,
     "-filter_complex","[0:a]aresample=44100[a0];[1:a]aresample=44100,volume=0.14[bg];[a0][bg]amix=inputs=2:duration=first:dropout_transition=0[a]",
     "-map","0:v","-map","[a]","-c:v","copy","-c:a","aac","-b:a","160k",
     os.path.join(WORK,"final.mp4")])

print("== verificar ==")
r = subprocess.run(["ffprobe","-show_entries","stream=codec_type,codec_name,width,height,sample_rate,channels",
                    "-of","json",os.path.join(WORK,"final.mp4")], capture_output=True, text=True)
print(r.stdout)
print("✅ VÍDEO FINAL PRONTO:", os.path.join(WORK,"final.mp4"))