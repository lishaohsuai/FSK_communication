#-*- coding: utf-8 -*-
from source import load , my_fsk, decode ,test_audio 

cls_origin = load.Payload("hello world")
# 产生了 四个对未来有效的结果
# self.rawData = str(text)  字符串
# self.bitArray = []        0,1,0,1序列
# self.__asciiArray = []    十进制序列[104, 101, 108, 108, 111, 32, 119, 111, 114, 108, 100]
# self.bits_length = 0      0,1,0,1序列的长度

print("发送的序列:",cls_origin.bitArray)
signal1 = my_fsk.Signal(cls_origin)
signal1.crc_plus()


# exit()
# 产生了对未来有效的结果
# ./audio/{0}.wav  叠加后的波形
# self.singal_cos = y  叠加后的数据


class_audio = test_audio.audio_test()
class_decode = decode.Decode(signal1)

while True:
	print("开始录音~")
	temp = class_audio.my_record()
	# class_decode.fir_high_new("./audio/1K_audio.wav")
	class_decode.fir_high_new(temp)
	# class_decode.fir_high_new("01.wav")


# 把音频录到wav文件中 文件名为 01.wav
print("开始录音~")

temp = class_audio.my_record()
class_decode.fir_high_new("01.wav")

# class_decode = decode.Decode(signal1)
# 
# class_decode.fir_high_new("./audio/1K_audio.wav")
print("结束录音~")
# class_decode.fir_high_new("01.wav")
# while True:



# 对wav文件进行解析
# 主要用了decode的fir_high_new()函数
# 借助了 参数类的一些变量
# 会产生一个解析了的字符串


