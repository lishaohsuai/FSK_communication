#-*- coding: utf-8 -*-
class Payload:
    def __init__(self,text):
        self.rawData = str(text)
        self.bitArray = []
        self.__asciiArray = []
        self.bits_length = 0
        self.__Convert2BitsArray()

    # 变成单个字符 ['h', 'e', 'l', 'l', 'o']
    def __split2Array(self):
        return list(self.rawData)
    # h==104  [104, 101, 108, 108, 111, 32]
    def __ascii(self, char):
        return ord(char)

    def __Convert2BitsArray(self):
        string_array = self.__split2Array()   
        self.__asciiArray = [self.__ascii(c) for c in string_array]
        for i in self.__asciiArray:
            for j in list("{0:08b}".format(i)): # '01101000' == h == 104
                self.bitArray.append(int(j))    # '01101000' ==  0, 1, 1, 0, 1, 0, 0, 0,
        self.bits_length = len(self.bitArray)

    def plotBinaryData(self):
        pass
if __name__=="__main__":
    test = Payload("hello world")
    #字符串 二进制数组 ascill数组 二进制数组长度 
    print(test.rawData,test.bitArray,test._Payload__asciiArray,test.bits_length)
    
