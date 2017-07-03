# -*- coding: utf-8 -*-
import pyaudio
import wave

chunk = 1024

wf=wave.open(r"01.wav",'rb')

p = pyaudio.PyAudio()

# 打开声音输出流
stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
                channels = wf.getnchannels(),
                rate = wf.getframerate(),
                output = True)
number = wf.getnframes()
# 写声音输出流进行播放
while True:
    number = number - chunk
    if (number < chunk): 
        break
    data = wf.readframes(chunk)
    if data == "": break
    stream.write(data)

stream.close()
p.terminate()
