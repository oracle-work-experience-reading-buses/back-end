import soundfile as sf
import sounddevice as sd
import os
import wave

prev_files = {}

devices = sd.query_devices()
device = [i for i in range(len(devices)) \
          if "USB PnP Audio Device" \
          in devices[i]["name"]][0]

sd.default.device = [device, 0]

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
    print(f"Recording \"{file_name}\"...")

    sample_rate = 44100
    duration = 4
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()

    sf.write(file_name, recording, sample_rate)
    prev_files[counter] = file_name
    counter += 1
    print(f"Finished recording \"{file_name}\"\n")

