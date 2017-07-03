舍弃的代码.cpp
def Fsk(self):
    N = self.payload.bits_length + 1
    data_in = self.payload.bitArray
    data_in.insert(0,0)

    fc=self.l_Fc
    fs=self.l_Fs
    fbit=self.l_Fbit
    A=self.l_A
    fdev=self.l_Fdev 
    t = np.arange(0,float(N)/float(fbit),1/float(fs),dtype=np.float)
    w = np.zeros(0).astype(float)
    count = fs//fbit
    print("一帧所拥有的点数:",count)
    # w = np.hstack((w,np.hanning(count)))
    # self.singal = np.hstack((self.singal,np.multiply(np.ones(count),fc)))
    for i in range(len(data_in)):
        w = np.hstack((w,np.hanning(count)))
        if i == 0:
            self.singal = np.hstack((self.singal,np.multiply(np.ones(count),fc)))
            # m = np.hstack((m,np.multiply(np.ones(count),fc)))
            continue
        if data_in[i] == 0 and i % 2 == 0:
            self.singal = np.hstack((self.singal,np.multiply(np.ones(count),fc+fdev)))
        elif data_in[i] == 0 and i % 2 == 1:
            self.singal = np.hstack((self.singal,np.multiply(np.ones(count),fc+fdev*2)))
        elif data_in[i] == 1 and i % 2 == 0:
            self.singal = np.hstack((self.singal,np.multiply(np.ones(count),fc+fdev*3)))
        elif data_in[i] == 1 and i % 2 == 1:
            self.singal = np.hstack((self.singal,np.multiply(np.ones(count),fc+fdev*4)))
    y = np.zeros(0)
   
    y = A * np.cos(2*np.pi*np.multiply(self.singal,t)) * w
    y = self.AddAudioData(y,len(y),N,fbit)
    self.singal_cos = y
    #self.ploy_data(y,t,self.singal)
def Fsk(self):
    N = self.payload.bits_length + 1
    data_in = self.payload.bitArray
    data_in.insert(0,0)

    fc=self.l_Fc
    fs=self.l_Fs
    fbit=self.l_Fbit
    A=self.l_A
    fdev=self.l_Fdev 
    t = np.arange(0,float(N)/float(fbit),1/float(fs),dtype=np.float)
    w = np.zeros(0).astype(float)
    count = fs//fbit
    print("一帧所拥有的点数:",count)
    # w = np.hstack((w,np.hanning(count)))
    # self.singal = np.hstack((self.singal,np.multiply(np.ones(count),fc)))
    for i in range(len(data_in)):
        w = np.hstack((w,np.hanning(count)))
        if i == 0:
            self.singal = np.hstack((self.singal,np.multiply(np.ones(count),fc)))
            # m = np.hstack((m,np.multiply(np.ones(count),fc)))
            continue
        if data_in[i] == 0 and i % 2 == 0:
            self.singal = np.hstack((self.singal,np.multiply(np.ones(count),fc+fdev)))
        elif data_in[i] == 0 and i % 2 == 1:
            self.singal = np.hstack((self.singal,np.multiply(np.ones(count),fc+fdev*2)))
        elif data_in[i] == 1 and i % 2 == 0:
            self.singal = np.hstack((self.singal,np.multiply(np.ones(count),fc+fdev*3)))
        elif data_in[i] == 1 and i % 2 == 1:
            self.singal = np.hstack((self.singal,np.multiply(np.ones(count),fc+fdev*4)))
    y = np.zeros(0)
   
    y = A * np.cos(2*np.pi*np.multiply(self.singal,t)) * w
    y = self.AddAudioData(y,len(y),N,fbit)
    self.singal_cos = y
    #self.ploy_data(y,t,self.singal)

    def oldFindEdge(self,y):
        y0 = np.abs(y)
        j = len(y0)
        mark_point = 0
        mark_count = 0
        for i in range(j-6):
            avgf = np.average(y0[i:i+6],axis=0)
            if avgf > 500:
                mark_point = i
                mark_count = mark_count + 1
                q = mark_point
                for t in range(40):
                    avgtemp = np.average(y0[q:q+6],axis=0)
                    q = q + t
                if(mark_count > 40):
                    break
        while j >= 0:
            avgf = np.average(y0[j-6:j],axis=0)
            if avgf > 500:
                break
            j = j - 1
        return y[i:j]
    def FindEdgeold2(self, data):
        i = 0
        threshold = 200
        count = 0
        f01 = (184-2)*93.75
        f02 = (184+2)*93.75
        data0 = np.abs(data)
        t = len(data0)
        while i < (t-6):
            aver = np.average(data0[i:i+6],axis=0)
            if aver > threshold:
                if count == 0:
                    save = copy.deepcopy(i)
                count = count + 1
                if count == 40 and i == save + 39:
                    i = i - count
                    break
                elif (i-save) != (count-1):
                    count = 0
            i = i + 1
        j = t
        while j >= 0:
            avgf = np.average(data0[j-6:j],axis=0)
            if avgf > 500:
                break
            j = j - 1
        return data[i:j]
    def FindEdge(self,y):
        y0 = np.abs(y) // 1
        j = len(y0)
        for i in range(j-6):
            avgf = np.average(y0[i:i+6],axis=0)
            if avgf > 500:
                xs = y[i:400] # 取400个点  补足 0 
                zero = list(np.zeros(112))
                # xs.append(zero)
                xs = np.hstack((xs[0:400],zero))
                xf = np.fft.rfft(xs)/512
                xfp = 20*np.log10(np.clip(np.abs(xf), 0, 1e100))
                xfp = np.abs(xfp)
                temp = xfp[150]
                tt_count = 150
                tt_mark_count = 0 
                for t in xfp[150:]:
                    if(temp < t):
                        temp1 = t
                        tt_mark_count = tt_count
                    tt_count = tt_count + 1
                if(tt_mark_count==184):
                    break
        while j >= 0:

            avgf = np.average(y0[j-6:j],axis=0)
            if avgf > 500:
                break
            j = j - 1

        return y[i:j]

    def four_door(self,number):
        temp = []
        for i in range(len(number)):
            if i == 0:
                continue
            if(number[i]>=198 and i % 2 == 1):
                temp.append(1)
            elif((number[i]>=190  and number[i] < 194 )and i % 2 == 1):
                temp.append(0)
            if((number[i]<190  )and i % 2 == 0):
                temp.append(0)
            elif((number[i]>=194  and number[i] < 198 )and i % 2 == 0):
                temp.append(1)
        self.BitToChar(temp[0:])