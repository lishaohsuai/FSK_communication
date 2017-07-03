# -*- coding:utf-8 -*-
import time
import copy
import queue
import pyaudio
import binascii
import numpy as np
import pylab as pl
import matplotlib.pyplot as plt
import scipy.signal as signal

find_N = 256
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
        left_threshold = 91    #15000
        right_threshold = 93   #17250
    elif flag == 1:            #奇数bit频率区间高
        left_threshold = 174   #16312
        right_threshold = 182  #17062
    elif flag == 2:            #偶数bit频率区间低
        left_threshold = 166   #15562
        right_threshold = 174  #16312
    k = left_threshold
    while k < right_threshold:  # 找到这个区间幅度de最大值
        if y[k] > Max_Amp:    
            Max_Amp = y[k]
            m = k
        k = k + 1
    return m  #返回频率的索引号
    
def average_fft_in_17k_19k(data):
    global find_N
    freq, ylog, y = my_fft(data,find_N)
    j = find_max_index(ylog,0)  # 返回幅度的最大值
    xf = np.abs(y[91:93])
    xp = np.array([x*x for x in xf]) 
    avgf = 1 / 10 * np.average(xp, axis=0) # 能量
    return avgf, freq[j]

def FindEdge(data):
    global find_N
    i = 0
    s = []
    save = -1
    count = 0
    f01 = 17250 - 187.5
    f02 = 17250 + 187.5
    fft_Amp_threshold = 0
    len_t = len(data)
    # 找头
    while i <= (len_t - find_N):
        avgf, freq = average_fft_in_17k_19k(data[i:i+find_N]) # 返回最大幅度和平均功率
        if(i == 0):
            # 参数 250 120000
            fft_Amp_threshold = 250
        if( avgf >= fft_Amp_threshold): # 超过门限
            if( count == 0 and freq > f01 and freq < f02):
                save = copy.deepcopy(i)
            count = count + 1
            if(i - save)!=(count -1 )*20: # 判断是否连续
                count = 0
            elif count == 2 and i == save + 20:
                # i = i - (count - 1) * 20
                if (len(s) >= 1):
                    if(save - s[len(s)-1] > 480):
                        s.append(save)
                else:
                    s.append(save)
                # print("s中的数据",s)
                # return s
                save = -1

        i = i + 20
    print("s中的数据",s)
    return s

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
    for i in range(8): 
        s[len(s)-i-1] = crc[7-i]
    return crc
