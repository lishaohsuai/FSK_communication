#-*- coding: utf-8 -*-
import numpy as np
import scipy.io.wavfile as wf
import wave
import matplotlib.pyplot as pl
import scipy.signal as si
import os
import matplotlib.pyplot as plt
from source import test_findedge
class Signal:
    def __init__(self, payload):
        self.singal = np.zeros(0).astype(float)
        self.payload = payload
        self.l_A = 10000       #transmitted signal amplitude
        self.l_Fbit = 100       #simulated bitrate of data
        self.l_Fc = 17250      #simulate a carrier frequency of 1kHz
        self.l_Fdev = 375      #frequency deviation, make higher than bitrate
        self.l_Fs = 48000   #17250*3    # 51750    #sampling frequency for the simulator, must be higher than twice the carrier frequency
        self.l_N = 64          #how many bits to send
        self.l_A_n = 0.10      #noise peak amplitude
        self.l_N_prntbits = 25 #number of bits to print in plots
        self.singal_cos = None # 叠加的波形
		#the following variables setup the system
        self.__signal_generet()
        self.data = self.payload.bitArray # 0101 序列

    def ploy_data(self,y,t,m):
        N_prntbits=self.l_N_prntbits
        Fdev=self.l_Fdev
        Fbit=self.l_Fbit
        Fs=self.l_Fs

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

    def AddAudioData(self,y,n,N,fbit):
        filename = "1K_audio"
        f1 = wave.open("1K_new.wav","rb")
        params = f1.getparams()
        nchannels,sampwidth,framerate,nframes = params[:4]
        str_data = f1.readframes(n)
        f1.close()
        wave_data = np.fromstring(str_data,dtype = np.short)
        wave_data.shape = -1,2
        wave_data = wave_data.T
        # 叠加音频
        # print(type(y))
        # y = (wave_data[0]+y[:len(wave_data[0])])
        # print(type(y))
        if os.path.exists('./audio') == False:
            os.makedirs('./audio')
        print("写入音频的数据",len(y))
        wf.write("./audio/{0}.wav".format(filename),len(y)//N*fbit,y.astype(np.dtype('i2')))
        return y

    def __signal_generet(self):
        pass

    def new_FSK(self,data_in):
        N = self.payload.bits_length + 1
        fc=self.l_Fc
        fs=self.l_Fs
        fbit=self.l_Fbit
        A=self.l_A
        fdev=self.l_Fdev 
        t = np.arange(0,float(N)/float(fbit),1/float(fs),dtype=np.float)
        w = np.zeros(0).astype(float)
        count = fs//fbit
        # print("一帧所拥有的点数:",count)
        # w = np.hstack((w,np.hanning(count)))
        # self.singal = np.hstack((self.singal,np.multiply(np.ones(count),fc)))
        y = np.zeros(0)
        for i in range(len(data_in)):
            w = np.hstack((w,np.hanning(count)))
            if i == 0: #帧头
                t_one_bit = np.arange(0,float(1)/float(fbit),1/float(fs),dtype=np.float)
                self.singal = np.multiply(np.ones(count),fc)
                # print(len(self.singal),count)
                y = A * np.cos(2*np.pi*np.multiply(self.singal,t_one_bit)) * np.hanning(count)
                continue
            if i == range(len(data_in))[len(data_in)-1]: #帧尾部
                t_one_bit = np.arange(0,float(1)/float(fbit),1/float(fs),dtype=np.float)
                self.singal = np.multiply(np.ones(count),fc)
                y = np.hstack((y,A * np.cos(2*np.pi*np.multiply(self.singal,t_one_bit)) * np.hanning(count)))
                break
            if i % 2 == 1:# 
                if data_in[i] == 0:
                    self.singal = np.multiply(np.ones(count),fc+fdev)
                    y_tmp = 0.5*A * np.cos(2*np.pi*np.multiply(self.singal,t_one_bit)) * np.hanning(count)
                else:
                    self.singal = np.multiply(np.ones(count),fc+2*fdev)
                    y_tmp = 0.5*A * np.cos(2*np.pi*np.multiply(self.singal,t_one_bit)) * np.hanning(count)
            else:
                if data_in[i] == 0:
                    self.singal = np.multiply(np.ones(count),fc+fdev*3)
                    y = np.hstack((y,np.add(y_tmp[-1*count:],0.5 * A * np.cos(2*np.pi*np.multiply(self.singal,t_one_bit)) * np.hanning(count))))
                else:
                    self.singal = np.multiply(np.ones(count),fc+fdev*4)
                    y = np.hstack((y,np.add(y_tmp[-1*count:],0.5 * A * np.cos(2*np.pi*np.multiply(self.singal,t_one_bit)) * np.hanning(count))))
        return y    
        
        # y = A * np.cos(2*np.pi*np.multiply(self.singal,t)) * w
        # 音频增加函数
        #y = self.AddAudioData(y,len(y),(N-1)//2+1,fbit)
        
        # self.singal_cos = y
        # print(len(y),"y的长度")
        
        #self.ploy_data(y,t[:len(y)],self.singal)

    # top_tail_CRC plus to this system and divide
    # 一帧的排列方式
    # 0 + 序列号 8 位 + 数据（<=48）+ crc + 0
    def crc_plus(self):
        temp_data = self.data # >50 个devide the data
        index = 0
        temp = []
        # print(temp_data,"原始数据")
        ss = []  #存贮中间数据
        while (len(temp_data) - index*48 > 48):
            ss = [int(i) for i in list("{0:08b}".format(ord(str(index))))]
            temp.append([ x for x in temp_data[ (48*index):(index+1)*48]])
            ss.extend(temp[index])
            test_findedge.Calculate_Crc(ss)
            temp[index] = ss
            temp[index].insert(0,0)
            temp[index].append(0)
            index = index + 1
        ss = [int(i) for i in list("{0:08b}".format(ord(str(index))))]
        temp.append(temp_data[index*48:])
        ss.extend(temp[index])
        test_findedge.Calculate_Crc(ss)
        temp[index] = ss
        temp[index].insert(0,0)
        temp[index].append(0)
        
        # ===============================
        y = [] # 记录音频数据
        for i in range(len(temp)):
            y.extend(self.new_FSK(temp[i]))
        y = np.array(y)
        print(len(y),"要写入音频的数据的位数")
        print("总共 %d 个bit位数据"%(len(y) // 480) ) 
        N = len(y)//480
        fbit=self.l_Fbit
        self.AddAudioData(y,len(y),N,fbit)  



        




    
