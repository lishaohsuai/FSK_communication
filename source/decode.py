#-*- coding: utf-8 -*-
import wave
import copy
import numpy as np
import scipy.signal as si
import binascii
import matplotlib.pyplot as pl
import matplotlib.pyplot as plt
from source import test_findedge
class Decode:
    def __init__(self,singal):
        self.singal = singal
        # self.fir_high_new()
        
    def BitToChar(self,data):
        b = ''
        len_data = 0
        len_data = len(data)//8  #防止报错  会丢弃 8的余数
        # print(len(data),"参加解析的数据的长度")
        for i in range(len_data*8):
            b = b + str(data[i])
        h = hex(int(b,2))[2:]
        s = binascii.a2b_hex(h).decode('utf-8')#s = binascii.a2b_hex(h).decode('utf-8')
        return s
    # 返回滤波后的数据
    # wav 或者 是list
    def fir_high_new(self,filename=r"./audio/1K_audio.wav"):
        # f = wave.open(r"./read_audio/lyj.wav", "rb")
        if type(filename) == type(""):
            f = wave.open(filename, "rb")
            params = f.getparams()
            nchannels, sampwidth, framerate, nframes = params[:4]
            str_data = f.readframes(nframes)
            print(type(str_data))
            wave_data = np.fromstring(str_data, dtype=np.short)
            f.close()
            b,a = si.butter(3,0.13,'highpass')
            sf = si.filtfilt(b,a,wave_data)
            sf = si.filtfilt(b,a,sf)
            sf = si.filtfilt(b,a,sf)
            sf = si.filtfilt(b,a,sf)

        else:
            # str_data = filename
            # wave_data = np.fromstring(filename, dtype=np.short)
            wave_data = b"".join(filename) 
            sf = np.fromstring(wave_data, dtype=np.short)

        # print(len(str_data))
        # exit(0)
        # time = np.arange(0, nframes) * (1.0 / framerate)
        # wave_data = str_data

        # b,a = si.butter(3,0.13,'highpass')
        # sf = si.filtfilt(b,a,wave_data)
        # sf = si.filtfilt(b,a,sf)
        # sf = si.filtfilt(b,a,sf)
        # sf = si.filtfilt(b,a,sf)
      
        t = np.arange(0,len(sf),1,dtype=np.float)
        # print("读取录音后的文件图形")
        # self.ploy_data(sf,t,self.singal)
        # exit(0)

        # one_bit_point = framerate // self.singal.l_Fbit
        # print("单个bit的点数量%s"%one_bit_point)
        FE = test_findedge.FindEdge(sf)
        de_string = ""
        for i in range(len(FE)//2):
            de_string = de_string + self.decode_one_string(sf,i,FE)
        print(de_string)    
    # 对滤波后的数据进行解帧
    # 数据，第几帧
    def decode_one_string(self,sf,num_string,FE):
        # FE = test_findedge.FindEdge(sf)
        full_value = sf[FE[num_string]:FE[num_string*2+1]]
        t_count = 0
        x = []  # store 512 points
        frequence_all = []
        tt_count = 186
        tt_mark_count1 = 0 #记录的下标
        tt_mark_count2 = 0
        zero = list(np.zeros(200))
        full_value = np.hstack((full_value[0:],zero))
        for i in full_value[480:]:
            if( t_count>=0 and t_count<(480) ):
                x.append(i)
                if(len(x)>=480):
                    freqs = np.linspace(0, 48000//2, 512//2 + 1)
                    xs = x[0:400] # 取400个点  补足 0 
                    zero = list(np.zeros(112))
                    # xs.append(zero)
                    xs = np.hstack((xs[0:400],zero))
                    xf = np.fft.rfft(xs)/512
                    xfp = 20*np.log10(np.clip(np.abs(xf), 1e-20, 1e100))
                    temp1 = xfp[186]
                    temp2 = xfp[194]
                    for j in xfp[186:]:
                        if(temp1 < j):
                            if(tt_count < 194 and tt_count > 186):
                                temp1 = j
                                tt_mark_count1 = tt_count
                        if(temp2 < j):
                            if(tt_count < 202 and tt_count > 194):
                                temp2 = j
                                tt_mark_count2 = tt_count
                        tt_count = tt_count + 1  
                    x = []
                    if(tt_mark_count1!=0 and tt_mark_count2!=0):
                        frequence_all.append(tt_mark_count1)
                        frequence_all.append(tt_mark_count2)
                    tt_mark_count1 = 0
                    tt_mark_count2 = 0
                    tt_count = 186
            
            t_count = t_count + 1 
            if(t_count >= 480):
                t_count = 0
        print("对应频率的下标:",frequence_all)
        print("下标的个数:",len(frequence_all))
        print("第 %s 帧"%num_string)
        return self.four_door_new(frequence_all)     
    def four_door_new(self,number):

        temp = []
        j = 0
        flag = 0
        for i in number:
            if i == 184 :
                j = 1
                continue
            if(i < 194 and i > 186):
                if(i > 184 and i < 190):
                    temp.append(0)
                else:
                    temp.append(1)
                j = j + 1
            if(i < 202 and i > 194):
                if(i > 194 and i < 198):
                    temp.append(0)
                else:
                    temp.append(1)
                j = j + 1
            
        # temp.insert(0,0)
        ##self.BitToChar(temp[32:-16])
        print("解析完的数据:",temp)
        print("数据的个数:",len(temp))
        temp_temp = ""
        for i in range(len(temp)-8):
            if(i<len(temp)//8 - 1):
                temp_temp = temp_temp + self.BitToChar(temp[i*8:(i+1)*8])
        

        temp_crc = copy.deepcopy(temp)
        crc = test_findedge.Calculate_Crc(temp_crc[:-8])
        if crc == temp[-8:]:
            print("解码成功，数据被成功接收")
            # print("the original data is:",temp_temp)
        else:
            print("解码失败，数据被丢弃")
        return temp_temp[1:]
        
        
        # print(temp)
        # elif (number>)



    def ploy_data(self,y,t,m):
        N_prntbits=self.singal.l_N_prntbits
        Fdev=self.singal.l_Fdev
        Fbit=self.singal.l_Fbit
        Fs=self.singal.l_Fs

        N_FFT = len(y) #// 10
        pl.subplot(3,1,1)
        # ff, tt, Sxx = si.spectrogram(y, Fs)
        # pl.pcolormesh(tt, ff, Sxx)     # 时间-频谱图
        plt.specgram(y, NFFT=512, Fs=48000, noverlap=480)
        pl.xlabel('Time (s)')
        pl.ylabel('Frequency (Hz)')
        pl.title('Original VCO output versus time')
        pl.subplot(3,1,2)
        pl.plot(t[0:Fs*N_prntbits//Fbit],y[0:Fs*N_prntbits//Fbit]) # 时间-幅度  完整波形图
        pl.xlabel('Time (s)')
        pl.ylabel('Amplitude (V)')
        pl.title('Amplitude of carrier versus time')
        pl.grid(True)
        freqs = np.linspace(0, Fs//2, N_FFT//2 + 1) # 
        xs = y[:N_FFT] #* si.hann(N_FFT, sym=0)
        xf = np.fft.rfft(xs)/N_FFT
        xfp = 20*np.log10(np.clip(np.abs(xf), 1e-20, 1e100))# cut top and low
        pl.subplot(3,1,3)
        pl.plot(freqs,xfp[:len(freqs)])# 频谱图 
        pl.xlabel('Frequence (s)')
        pl.ylabel('Amplitude (V)')
        pl.title('Amplitude & Frequence')
        pl.grid(True)
        pl.show()

