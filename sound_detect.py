import soundfile as sf
import sounddevice as sd
from datetime import datetime as dt

devices = sd.query_devices()
device = [i for i in range(len(devices)) \
          if "USB PnP Audio Device" \
          in devices[i]["name"]][0]

sd.default.device = [device, 0]
print(sd.default.device)

sample_rate = 44100
duration = 4
recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
sd.wait()
sf.write("recorded_sound.wav", recording, sample_rate)
