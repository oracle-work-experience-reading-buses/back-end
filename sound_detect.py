# Miscellaneous modules
import asyncio
import contextlib
import json
import requests
from datetime import datetime

# Modules for recording audio
import sounddevice as sd
import soundfile as sf

# Modules for reading and comparing audio
import os
import matplotlib.pyplot as plt
from scipy.io import wavfile
import imagehash
import PIL
import pickle

# Modules for both reading / writing audio
import wave

amount_of_people = 0

prev_files = {}

devices = sd.query_devices()
device = [i for i in range(len(devices)) \
          if "USB PnP Audio Device" \
          in devices[i]["name"]][0]

sd.default.device = [device, 0]

reference_data = {}

with contextlib.closing(wave.open("reference_sound.wav", "r")) as ref_file:
    reference_data = {
            "file" : ref_file,
            "hash" : pickle.load(open("reference_sound-hash.pckl", "rb")),
            "frame_count" : ref_file.getnframes(),
            "framerate" : float(ref_file.getframerate()),
            "duration" : ref_file.getnframes() / float(ref_file.getframerate())
    }

def record(counter):
    file_name = f"recorded_sound-{counter}.wav"

    if len(prev_files) > 3:
        os.remove(f"recorded_sound-{counter-4}.wav")
        prev_files.pop(counter-4, None)


    sample_rate = 44100
    duration = reference_data["duration"] 
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()

    sf.write(file_name, recording, sample_rate)
    prev_files[counter] = file_name
    return file_name

def get_file_hash(audio_file_path):
    figure = plt.figure()
    figure.patch.set_visible(False)

    image_name = os.path.basename(audio_file_path)[:len(audio_file_path)-4] + "-spectogram.png"
    sample_rate, samples = wavfile.read(audio_file_path)

    plt.specgram(samples, Fs=sample_rate)
    plt.axis("off")
    figure.savefig(image_name)

    plt.close(figure)

    image = PIL.Image.open(image_name).convert("LA").resize((16,16), PIL.Image.ANTIALIAS)
    img_hash = imagehash.phash(image, hash_size=8)

    os.remove(image_name)
    return img_hash

def compare_with_reference(audio_file_path):
    global amount_of_people

    reference_hash = reference_data["hash"]
    sound_hash = get_file_hash(audio_file_path)

    print(f"\nReference hash: {reference_hash}")
    print(f"{os.path.basename(audio_file_path)}'s hash: {sound_hash}")
    print(f"Amount of people: {amount_of_people}")

    if sound_hash == reference_hash: 
        amount_of_people += 1
        send_data()
        return True
    else: return False

def send_data():
    data = {
            "bus_no" : "422",
            "bus_route" : "2a",
            "people_count" : amount_of_people,
            "time" : datetime.now().strftime("%Y-%m-%d %T")
    }

    url = "http://reading-buses.cf/set_people"
    request = requests.post(url=url, data=data, verify=False)
    print(request.text)


def main():
    prev_file_name = "recorded_sound-0.wav"
    current_file_name = "recorded_sound-1.wav"
    cnt = 1

    while current_file_name != prev_file_name:
        current_file_name = record(cnt)
        compare_with_reference(current_file_name)
        cnt += 1

main()
