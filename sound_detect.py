import audioop
import pyaudio
import wave
import numpy as np

from sys import byteorder
from array import array
from struct import pack

reference_sound_path = "reference_sound.wav"
output_sound_path = "recorded_sound.wav"

input_device = 0

_THRESHOLD = 500
_CHUNK_SIZE = 1024
_FORMAT = pyaudio.paInt16
_RATE = 44100

def is_silent(data):
    return max(data) < _THRESHOLD

def normalize(data):
    _MAXIMUM = 16384
    times = float(_MAXIMUM)/max(abs(i) for i in data)
    r = array("h")
    
    for i in data:
        r.append(int(i*times))
    # fixed by oliver
    return r

def trim(data):
    def _trim(data):
        sound_started = False
        r = array("h")
        
        data = [data] if not isinstance(data, array) else data
        
        for i in data:
            if not sound_started and abs(i) > _THRESHOLD:
                sound_started = True
                r.append(i)
            elif sound_started:
                r.append(i)
        return r
    
#    data = _trim(data)
#    data.reverse()
#    data = _trim(data)
#    data.reverse()
    
    return data

def add_silence(data, secs):
    
    r = array("h", [0 for i in range(int(secs*_RATE))])
    
    r.extend(data) # line which errors
    r.extend([0 for i in range(int(secs*_RATE))])
    return r
    
def record():
    global input_device
    global _RATE
    
    p = pyaudio.PyAudio()
    
    input_device = [i for i in range(p.get_device_count()) \
                    if "USB PnP Audio Device: Audio" \
                    in p.get_device_info_by_index(i).get("name")][0]
                         
    if input_device == 0: 
        raise OSError("Could not find USB microphone device")

    _RATE = int(p.get_device_info_by_index(input_device)["defaultSampleRate"])

    # We get the correct mic
    stream = p.open(format=_FORMAT, channels=1, rate=_RATE, input=True, 
                    output=True, frames_per_buffer=_CHUNK_SIZE, 
                    input_device_index=input_device)
    # valid stream
    num_silent = 0
    sound_started = False
    
    r = array("h")
    
    while True:
        data = array("h", stream.read(_CHUNK_SIZE, exception_on_overflow=False))
        if byteorder == "big":
            data.byteswap()
        r.extend(data)
        
        silent = is_silent(data)
        
        if silent and sound_started:
            num_silent += 1
        elif not silent and not sound_started:
            sound_started = True
            
        if sound_started and num_silent > 30:
            break
            
    sample_width = p.get_sample_size(_FORMAT)
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    r = normalize(r)
    r = trim(r)

    r = add_silence(r, 0.5)
    return sample_width, r
        
def record_to_file(path):
    sample_width, data = record()
    data = pack("<" +   ("h" * len(data)), *data)
    
    wf = wave.open(path, "wb")
    wf.setnchannels(1)
    wf.setsampwidth(sample_width)
    wf.setframerate(_RATE)
    wf.writeframes(data)
    wf.close()
        
if __name__ == "__main__":
    record_to_file(output_sound_path)
        
        
        
