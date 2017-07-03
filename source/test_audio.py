# -*-coding='utf-8'
import wave
from pyaudio import PyAudio,paInt16
from source import decode
class audio_test:
    def __init__(self):
        self.framerate=48000
        self.NUM_SAMPLES=2000#9600#
        self.channels=1
        self.sampwidth = 2
        self.TIME = 8
        self.chunk = 1024
        self.stream = None
        # self.stream_open()


    def save_wave_file(self,filename,data):
        ''' save teh date to the wavefile'''
        wf=wave.open(filename,'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.sampwidth) # 暂时不清楚这个的作用
        wf.setframerate(self.framerate) # 采样频率 
        wf.writeframes(b"".join(data))
        wf.close()
    def stream_open(self):
        pa = PyAudio()
        self.stream=pa.open(format = paInt16,channels=1,
            rate=self.framerate,input = True,
            frames_per_buffer=self.NUM_SAMPLES
            )
        # print(type(self.stream))
    def stream_clase(self):
        self.stream.close()
    def my_record(self):
        pa = PyAudio()
        self.stream=pa.open(format = paInt16,channels=1,
            rate=self.framerate,input = True,
            frames_per_buffer=self.NUM_SAMPLES
            )
        my_buf=[]
        count = 0
        while count<self.TIME*20:#控制录音事件
            string_audio_data = self.stream.read(self.chunk)
            my_buf.append(string_audio_data)
            count+=1
            print('.',end = " ")
        print('.')
        print(my_buf)
        self.save_wave_file('01.wav', my_buf)
        
        return my_buf
        
        # stream.close()


    
    def play(self):
        wf=wave.open(r"01.wav",'rb')
        p=PyAudio()
        stream=p.open(format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),rate=wf.getframerate(),output=True)
        number = wf.getnframes()
        
        while True:
            data = wf.readframes(1024)
            number = number - self.chunk
            if (number < self.chunk): 
                break
            if data=="":break
            stream.write(data)
        stream.close()
        p.terminate() # 释放资源

    def ploy_data(y, t ,singal):
        N_prntbits=singal.l_N_prntbits
        Fdev=singal.l_Fdev
        Fbit=singal.l_Fbit
        Fs=singal.l_Fs

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

if __name__=="__main__":
    test= audio_test()
    test.my_record()
    print("over")
    test.play()


