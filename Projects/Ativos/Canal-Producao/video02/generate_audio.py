import asyncio, edge_tts, os, subprocess

async def main():
    text = open('narration_script.txt', 'r', encoding='utf-8').read()
    os.makedirs('audio', exist_ok=True)
    communicate = edge_tts.Communicate(text, 'pt-BR-ThalitaMultilingualNeural', rate='-4%')
    await communicate.save('audio/audio_final.mp3')
    print('✅ Áudio gerado: audio/audio_final.mp3')
    
    # Verifica duração
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', 'audio/audio_final.mp3'], capture_output=True, text=True)
    dur = float(r.stdout.strip())
    print(f'Duração: {dur:.1f}s ({dur/60:.1f} min)')

asyncio.run(main())