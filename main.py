#!/usr/bin/python3

import os
import time
from Markovtext import Markover
import wave
import subprocess
import pyaudio
import json
import threading
import collections
from gpiozero import LED, Button

BLOCKSIZE = 128

def hook(pairs):
    ### Hook to read JSON into defaultdict(list)###

    d = collections.defaultdict(list)
    for k,v in pairs:
        d[k] = v  
    return d


def avg(x):
    if len(x) > 0:
        return sum(x)/len(x)
    else:
        return 0

def read_from_usb(m):
    os.unlink('dict.json')
    with open('dict.json', 'w') as jsonfile:
        m.generate_from_txt('/media/usbsticka/input.txt')
        json.dump(m.get_wordtable(), jsonfile)

    print("finished read from usb")
    
def read_std(m):
    os.unlink('dict.json')
    with open('dict.json', 'w') as jsonfile:
        m.generate_from_txt('std.txt')
        json.dump(m.get_wordtable(), jsonfile)


    print("finished read from std")

def main():
   
    led = LED(17)
    usb_button = Button(14)
    std_button = Button(18)
    
    p = pyaudio.PyAudio()
    mrkv = Markover()
    std_button.when_pressed = lambda : read_std(mrkv)
    usb_button.when_pressed = lambda : read_from_usb(mrkv)
    
    try:
        with open('dict.json', 'r') as jsonfile:
            data = json.load(jsonfile, object_pairs_hook=hook)
    except IOError:
        with open('dict.json', 'w') as jsonfile:
            mrkv.generate_from_txt('std.txt')
            json.dump(mrkv.get_wordtable(), jsonfile)
    else:
        mrkv.set_wordtable(data)
  
    while True: 
        sentence = mrkv.get_next_sentence()
        print(sentence)
        subprocess.run(['pico2wave', '--wave=voice.wav', sentence])

        wf = wave.open("voice.wav", "rb")

        def dspcallback(in_data, frame_count, time_info, flag):
            led.off()
            data = wf.readframes(frame_count)
            if avg(data) > 130:
                led.on()
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
        stream.close()


    # Close everything
    stream.close()
    wf.close()
    p.terminate()

if __name__ == "__main__":
    main()
