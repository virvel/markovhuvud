#!/usr/bin/python3

import time
from Markovtext import Markover
import wave
import subprocess
import pyaudio
import json
import threading
import collections
from gpiozero import Button

BLOCKSIZE = 1024

def hook(pairs):
    ### Hook to read JSON into defaultdict(list)###

    d = collections.defaultdict(list)
    for k,v in pairs:
        d[k] = v  
    return d

def create_wave(sentence): 
    subprocess.run(['pico2wave', '--wave=test.wav', sentence])

def open_wave():
    return wave.open("test.wav", "rb")

def main():
    
    p = pyaudio.PyAudio()
    mrkv = Markover()

    try:
        with open('dict.json', 'r') as jsonfile:
            data = json.load(jsonfile, object_pairs_hook=hook)
    except IOError:
        with open('dict.json', 'w') as jsonfile:
            mrkv.generate_from_txt('/media/usbsticka/recept.txt')
            json.dump(mrkv.get_wordtable(), jsonfile)
    else:
        mrkv.set_wordtable(data)
   
    sentence = mrkv.get_next_sentence()
    print(sentence)
    
    create_wave(sentence)
    
    wf = open_wave()

    def dspcallback(in_data, frame_count, time_info, flag):
        data = wf.readframes(frame_count)
        return data, pyaudio.paContinue 

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=1,
                    rate=13000,
                    output=True,
                    frames_per_buffer=BLOCKSIZE,
                    stream_callback = dspcallback)

     
    stream.start_stream() 

    while stream.is_active():
        time.sleep(0.1)

    # Close everything
    stream.close()
    wf.close()
    p.terminate()

if __name__ == "__main__":
    main()
