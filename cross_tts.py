from gtts import gTTS
from pydub import AudioSegment
import simpleaudio as sa
import tempfile
import os
play_obj = None
# 1) Metni tanımla
# 2) gTTS objesini oluştur ve geçici MP3 dosyasına kaydet
def play_tts(text):
    global play_obj
    tts = gTTS(text=text, lang='en', slow=False)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        mp3_path = fp.name
        tts.save(mp3_path)

    # 3) MP3 dosyasını pydub ile yükle
    sound = AudioSegment.from_mp3(mp3_path)

    # 4) simpleaudio ile çal
    play_obj = sa.play_buffer(
        sound.raw_data,
        num_channels=sound.channels,
        bytes_per_sample=sound.sample_width,
        sample_rate=sound.frame_rate
    )
    play_obj.wait_done()

    # 5) Geçici dosyayı sil
    os.remove(mp3_path)

def stop_tts():
    global play_obj
    if play_obj is not None:
        play_obj.stop()