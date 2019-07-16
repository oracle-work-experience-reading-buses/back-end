import matplotlib.pyplot as plt
from scipy.io import wavfile

plt.subplot(211)
ref_sample_rate, ref_samples = wavfile.read("recorded_sound-2.wav")
ref_power, ref_frequencies, ref_times, ref_img_axis = plt.specgram(ref_samples, Fs=ref_sample_rate)
plt.xlabel("Time")
plt.ylabel("Frequency")


plt.subplot(212)
ref_sample_rate, ref_samples = wavfile.read("reference_sound.wav")
ref_power, ref_frequencies, ref_times, ref_img_axis = plt.specgram(ref_samples, Fs=ref_sample_rate)
plt.xlabel("Time")
plt.ylabel("Frequency")

plt.show()
