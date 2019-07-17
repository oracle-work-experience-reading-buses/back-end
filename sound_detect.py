import asyncio
import contextlib

# Modules for recording audio
import sounddevice as sd
import soundfile as sf
import wave

# Modules for reading and comparing audio
import os
import matplotlib.pyplot as plt
from scipy.io import wavfile
import imagehash
import PIL
import pickle

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

def record():
    counter = 1
    while True:
        if len(prev_files) >= 3:
            print("Creating \"test_for_beep.wav\"...")
            infiles = [prev_files[_file] for key,_file \
                       in enumerate(prev_files)]
            outfile = "test_for_beep.wav"

            data = []
            for infile in infiles:
                w = wave.open(infile, "rb")
                data.append([w.getparams(), w.readframes(w.getnframes())])
                w.close()
            
            output = wave.open(outfile, "wb")
            output.setparams(data[0][0])
            output.writeframes(data[0][1])
            output.writeframes(data[1][1])
            output.writeframes(data[2][1])
            output.close()
        if len(prev_files) > 3:
            os.remove(f"recorded_sound-{counter-4}.wav")
            prev_files.pop(counter-4, None)

        file_name = f"recorded_sound-{counter}.wav"

        sample_rate = 44100
        duration = reference_data["duration"] 
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
        sd.wait()

        sf.write(file_name, recording, sample_rate)
        prev_files[counter] = file_name
        counter += 1

def get_file_hash(audio_file_path):
    figure = plt.figure()

    image_name = os.path.basename(audio_file_path)[:len(audio_file_path)-4] + "-spectogram.png"
    sample_rate, samples = wavfile.read(audio_file_path)
    plt.specgram(samples, Fs=sample_rate)
    plt.axis("off")
    figure.savefig(image_name, bbox_inches=0)

    image = PIL.Image.open(image_name)
    return imagehash.phash(image, hash_size=16)

def compare_with_reference(audio_file_path):
    reference_hash = reference_data["hash"]
    sound_hash = get_file_hash(audio_file_path)

    print(f"Reference hash: {reference_hash}")
    print(f"{os.path.basename(audio_file_path)}'s hash: {sound_hash}")

def main():
    compare_with_reference("recorded_sound-9.wav")


main()
