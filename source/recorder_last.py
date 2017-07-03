#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import copy
import queue
import pyaudio
import binascii
import numpy as np
import pylab as pl
import matplotlib.pyplot as plt
import scipy.signal as signal

left_threshold = 0
right_threshold = 0
find_N = 256
Gdatanum = 3
#显示频谱和声谱图
def ploy_data(y,N=512,Fs=48000):
    N_FFT = (len(y) // N)* N
    x_f = np.fft.rfft(y[0:N_FFT]) / N_FFT
    y_f = 20*np.log10(np.clip(np.abs(x_f),1e-20,1e100))
    freqs = np.linspace(0,Fs//2,N_FFT//2+1)
    pl.subplot(2,1,1)
    pl.plot(freqs,y_f)
    pl.grid(True)
    pl.subplot(2,1,2)
    plt.specgram(y,NFFT=512,Fs=48000,noverlap=480)
    pl.grid(True)
    pl.show()
#默认进行512点的傅里叶变换
def my_fft(w, N_FFT=512, Fs=48000):
    freqs = np.linspace(0,Fs//2,N_FFT//2+1)
    y_f = np.fft.rfft(w[0:N_FFT]*signal.hanning(N_FFT,sym = 0)) / N_FFT
    ylog = 20*np.log10(np.clip(np.abs(y_f),1e-20,1e100))
    return freqs,ylog,y_f
#寻找各个区间的最高频率值
def find_max_index(y,flag=1):
    m = 0
    Max_Amp = 0
    global left_threshold
    global right_threshold
    if flag == 0:              #计算帧头的区间
        left_threshold = 81    #15000
        right_threshold = 83   #17250
    elif flag == 1:            #奇数bit频率区间高
        left_threshold = 174   #16312
        right_threshold = 182  #17062
    elif flag == 2:            #偶数bit频率区间低
        left_threshold = 166   #15562
        right_threshold = 174  #16312
    k = left_threshold
    while k < right_threshold:
        if y[k] > Max_Amp:
            Max_Amp = y[k]
            m = k
        k = k + 1
    return m  #返回频率的索引号
#左移
def LeftShift(l=[]):
    l = l[1:]
    l.append(0)
    return l
#异或操作
def MyXor(l1=[],l2=[]):
    result = [0]*8
    for i in range(8):
        result[i] = l1[i] ^ l2[i]
    return result
#add crc8 chk
def Calculate_Crc(s=None):
    crc = [0]*8
    ploy = [1,0,0,1,1,0,0,0,1]  #0x31
    for i in range(8):
        s.append(0)
    length = len(s)
    for i in range(length):
        if crc[0] & 1:
            crc = MyXor(crc, ploy)
        crc = LeftShift(crc)
        crc[7] = s[i]
    return crc
#带通滤波器
def FirHighPass(length,y):
    b = signal.remez(length,(0.0,0.24,0.26,0.38,0.40,0.50),(0.01,10,0.01)) # [0,115200]Hz  [12480,18240]
    for i in range(6):
        y = signal.lfilter(b,10,y)
    return y
#list转字符串或十进制
def listtochar(data,flag):
    b = ''
    for i in range(len(data)):
        b = b + str(data[i])
    if flag == 1:
        return b
    else:
        return int(b,2)
#[15k:17k]区间功率平均
def average_fft_in_15k_17k(data):
    global find_N
    freq, ylog, y = my_fft(data,find_N)
    j = find_max_index(ylog,0)
    xf = np.abs(y[81:91])
    xp = np.array([x*x for x in xf]) #平方
    avgf = 1 / 10 * np.average(xp, axis=0)
    return avgf, freq[j]
#字节转为ascii
def BitToChar(data):
    b = ''
    j = 0
    for i in range(len(data)):
        b = b + str(data[i])
    h = hex(int(b,2))[2:]
    s = binascii.a2b_hex(h).decode('utf-8')
    print("--------------------------")
    print(s)
    print("--------------------------")
#录音类
class Recorder(object):
    def __init__(self, channels=1, rate=48000, frames_per_buffer=1024):
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer

    def Write_Buffer(self):
        return RecordBuffer(self.channels, self.rate,
                            self.frames_per_buffer)

class RecordBuffer(object):
    def __init__(self, channels, rate, frames_per_buffer):
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self.perdata = np.zeros(0).astype(float)
        self._pa = pyaudio.PyAudio()
        self._stream = None

    def __enter__(self):
        print("Start Listening")
        return self

    def __exit__(self, exception, value, traceback):
        print("End Listening")
        self.close()

    def start_recording(self):
        # Use a stream with a callback in non-blocking mode
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer=self.frames_per_buffer,
                                        stream_callback=self.get_callback())
        self._stream.start_stream()
        return self

    def stop_recording(self):
        self._stream.stop_stream()
        return self

    def get_callback(self):
        def callback(in_data, frame_count, time_info, status):
            in_data = np.fromstring(in_data, dtype=np.short)
            self.perdata = np.hstack((self.perdata, in_data))
            return in_data, pyaudio.paContinue
        return callback

    def FindEdgeOnFre(self, data):
        global find_N
        i = 0
        s = []
        save = -1
        count = 0
        fft_Amp_threshold = 0
        t = len(data)
        print("全部数据的长度：")
        print(t)
        f01 = (164-2)*93.75
        f02 = (164+2)*93.75
        while i <= (t-15800):
            avgf, freq= average_fft_in_15k_17k(data[i:i+find_N])
            if i == 0:
                fft_Amp_threshold = 120
            if avgf >= fft_Amp_threshold:
                if count == 0 and freq > f01 and freq < f02:
                    print("进入时的i %d" % i)
                    print("进入时的freq %d" % freq)
                    save = copy.deepcopy(i)
                count = count + 1
                if (i-save) != (count-1) * 10:
                    count = 0
                elif count == 2 and i == save + 10:
                    i = i - (count - 1) * 10
                    s.append(i)
                    i = i + 15830
                    count = 0
                    save = -1
            i = i + 10
        return s

    def close(self):
        self._stream.close()
        self._pa.terminate()
#数据包进行解码
def Decode(data,Fs=48000):
    i = 1
    DesStr = []
    N_FFT = 512
    length = len(data)
    s = length // 480
    f11 = (168-2) * 93.75
    f12 = (168+2) * 93.75
    f21 = (172-2) * 93.75
    f22 = (172+2) * 93.75
    f31 = (176-2) * 93.75
    f32 = (176+2) * 93.75
    f41 = (180-2) * 93.75
    f42 = (180+2) * 93.75
    add_zero = np.zeros(N_FFT-400).astype(float)
    while i < s:
        max = 0
        e1 = i * 480 + 40
        e2 = (i+1) * 480 - 40
        w = np.hstack((data[e1:e2],add_zero))
        freq,ylog,yt = my_fft(w, N_FFT)
        j1 = find_max_index(ylog,1)
        j2 = find_max_index(ylog,2)
        if freq[j1] > f31 and freq[j1] < f32:
            DesStr.append(0)
        elif freq[j1] > f41 and freq[j1] < f42:
            DesStr.append(1)
        if freq[j2] > f11 and freq[j2] < f12:
            DesStr.append(0)
        elif freq[j2] > f21 and freq[j2] < f22:
            DesStr.append(1)
        i = i + 1
    return DesStr

#返回去掉包头和crc的数据
def MultipDecode(data, result,i):
    global Gdatanum
    order   = 0  #数据包的包号
    datanum = 0  #每个完整数据的包数量
    print("第%d数据包的数据：" % i)
    print(data,len(data))
    if Calculate_Crc(data[:-8]) == data[-8:]:
        order = listtochar(data[0:3],0)
        datanum = listtochar(data[3:6],0)
        if Gdatanum == datanum:
            if result[order] == 0:
                result[order] = data[6:-8]
        else:
            print("包数量不匹配丢弃")
    else:
        print("CRC校验出错丢弃")

########################################################################

if __name__=="__main__":
    oridata = []
    rec = Recorder()
    result = list(np.zeros(3).astype(int)) #存放每个包解析出来的bit数据
    with rec.Write_Buffer() as recfile:
        recfile.start_recording()
        time.sleep(4.0)
    recfile.stop_recording()
    #ploy_data(recfile.perdata)
    out = FirHighPass(21,recfile.perdata)
    #ploy_data(out)
    bodge = recfile.FindEdgeOnFre(out)
    print("其实帧的索引值：")
    print(bodge)
    for i in range(len(bodge)):
        d = Decode(out[bodge[i]:bodge[i]+15840])
        MultipDecode(d, result,i+1)  #去掉6bit包头和8位crc的数据
    j = -1
    for i in range(Gdatanum):
        if result[i] == 0:
            print("failure")
            exit()
        elif i == Gdatanum-1:
            while j > -50:
                if result[i][j] == 1:
                    oridata.extend(result[i][:j])
                    break
                j = j - 1
        else:
            oridata.extend(result[i])
    print("解调出来的原始数据：")
    print(oridata,len(oridata))
    BitToChar(oridata)
