import datetime
import numpy as np
import os
import pdb
import pywt
from scipy import signal
from sklearn.cluster import KMeans
import soundfile as sf
import time
import wave

# Not installed with conda:
# pip install soundfile

def sample_time_str(x, samplerate):
    return str(datetime.timedelta(seconds=x/samplerate))

class Silence():
    def __init__(self, start, duration, end):
        self.start    = start
        self.duration = duration
        self.end      = end


class Song():
    def __init__(self, number, samplerate, end_first_silence, start_last_silence, expansion, full_data):
        self.number = number
        self.track_name = f"Track_{str(self.number).zfill(2)}"
        self.samplerate = samplerate
        self.start  = end_first_silence - expansion*samplerate if end_first_silence > expansion*samplerate else end_first_silence
        self.end    = start_last_silence + expansion*samplerate if start_last_silence + expansion*samplerate < len(full_data) else start_last_silence
        self.data   = full_data[self.start:self.end]
    
    def export_wav(self, output_folder):
        sf.write(f"{output_folder}/{self.track_name}.wav", self.data, self.samplerate)
        print(f"{self.track_name} exported!")

    def info(self):
        start_str = sample_time_str(self.start, self.samplerate)
        end_str   = sample_time_str(self.end,   self.samplerate)
        duration  = sample_time_str(self.end - self.start, self.samplerate)
        info = f"{self.track_name} found between {start_str} and {end_str} that last for {duration}"
        print(info)


def get_threshold_kmeans(data):
    # TODO: Reimplementar. No funciona bien.
    # Cluster para el umbral
    sub_samples = np.array([abs(x) for i, x in enumerate(data) if i%1000==0])
    km = KMeans(n_clusters=3)
    audio_km = km.fit_predict(sub_samples.reshape(-1, 1))

    threshold = sum(km.cluster_centers_)[0]/2

    print("Centros de los clusters", km.cluster_centers_)
    print("threshold", threshold)

    return threshold


def binarize_to_array(data, threshold):
    return np.array([int(x >= threshold) for x in data])


def find_silences(seconds_consider_silence, binary_data, samplerate):
    # This list contain a list of Silence instances
    silences = []

    # Init vars used in the loop
    state = ''
    start = 0
    duration = 0

    for i in range(0, len(binary_data)):
        # New sample is a silence
        if binary_data[i] == 0:
            if state == 'silence':
                # Increase state
                duration += 1
            else:
                # Reset state
                state = 'silence'
                start = i
        # New sample is not Silence
        elif state == 'silence':
            # If silence is long enough then append.
            if duration >= seconds_consider_silence*samplerate:
                silences.append(Silence(start, duration, start + duration))

            # Reset state
            state = 'sound'
            duration = 0
    
    # for s in silences:
    #     print(s.start, s.duration, s.end)
    
    return silences


def main():
    """
    
    User defined parameters:
    - filename:                 path to input file
    - manual_thold:             {float, None}: Manual threshold between x and x to binarize input data. If None it is automatically deteceted.
    - seconds_consider_silence: Required seconds to identify a data sequence of binarized 0's as a silence.
    - min_song_length:          Required seconds to identify a data sequence of binarized 1's as a song.
    - seconds_expand_song:      Seconds to add at the beginning and end of a detected song.

    Outputs:
    - Songs are exported to wav into the folder 'splitted'  
    """

    # User defined parameters
    filename = "../src/wav/recording_167_rehearsal.wav"
    manual_thold = 0.65
    seconds_consider_silence = 5
    min_song_length = 90
    seconds_expand_song = 3

    # To translate time in seconds to a sample number, use: sample_number = seconds * sample_rate
    
    # Create output folder
    output_folder = "splitted"
    os.makedirs(output_folder, exist_ok=True)

    # Read data and samplerate from audiofile
    data, samplerate  = sf.read(filename)
    print("Audio Total Time:", str(datetime.timedelta(seconds=len(data)/samplerate)))

    # Data binarization
    threshold = manual_thold if manual_thold is not None else get_threshold_kmeans(data)
    binary_data = binarize_to_array(data, threshold)

    # Looking for songs. The approach is to look for silences, their start, duration and finish.
    # Analazing data between the end of a silence and the beginning of the following silence a song can be identified.
    silences = find_silences(seconds_consider_silence, binary_data, samplerate)

    print("Looking for songs")
    track_number = 0
    for silences_starts, silences_ends in zip(silences[1:], silences[:-1]):
        end_current_silence = silences_ends.end
        start_next_silence  = silences_starts.start

        # Continuous sound with minimum length to be considered as a song
        if start_next_silence - end_current_silence > min_song_length * samplerate:
            track_number += 1
            curr_song = Song(track_number, samplerate, end_current_silence, start_next_silence, seconds_expand_song, data)
            curr_song.info()
            curr_song.export_wav(output_folder)

if __name__ == "__main__":
    main()