import librosa
import matplotlib.pyplot as plt
from dtw import dtw

from numpy.linalg import norm

y1, sr1 = librosa.load("recorded_sound-2.wav")
y2, sr2 = librosa.load("test_for_beep.wav")

plt.subplot(1, 2, 1)
mfcc1 = librosa.feature.mfcc(y1, sr1)
librosa.display.specshow(mfcc1)

plt.subplot(1, 2, 2)
mfcc2 = librosa.feature.mfcc(y2, sr2)
librosa.display.specshow(mfcc2)

dist, cost, acc_cost, path = dtw(mfcc1.T, mfcc2.T, dist=lambda x, y: norm(x-y, ord=1))
print(f"Normalised distance: {dist}")

plt.imshow(cost.T, origin="lower", cmap=plt.get_cmap("gray"), interpolation="nearest")
plt.plot(path[0], path[1], "w")
plt.show()
