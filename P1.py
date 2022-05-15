from cgitb import small
from copy import copy
from email import message
from encodings import utf_8
from logging import NullHandler
import math
from mimetypes import init
from token import EQUAL
import bitarray
import binascii
from bitarray.util import int2ba, ba2int, ba2hex, hex2ba
import random

from pip import main

# Big_PrimeTable = {0: 499, 1: 383, 2: 937, 3: 1069,
#                   4: 811, 5: 643, 6: 151, 7: 97, 8: 89, 9: 43, 10: 23, 11: 733, 12: 179, 13: 11, 14: 31, 15: 43}
# 檔名 10個 bit，決定檔名長度，40個 bit檔案長度<檔案最大4G>，15個bit放Shift,Multiply,Prime
Small_PrimeTable = {0: 29, 1: 5, 2: 7, 3: 11,
                    4: 13, 5: 17, 6: 19, 7: 23}
replace_Cipher = []


def Message_Encoder(msg):
    msg = bitarray.bitarray(
        '0010001001011101010101000011101001010010111100011110010011100')
    msg_len = len(msg)

    minum = 0
    maxum = 0
    if msg_len <= 1000:
        frist_choice = int(msg_len/3)
        last_choice = int(msg_len*4/5)
        choose2 = ba2int(msg[last_choice:last_choice+2])
        choose1 = ba2int(msg[frist_choice:frist_choice+2])
        print(choose1, choose2)
        if not choose2 == choose1:
            maxum = Small_PrimeTable[choose2]
            minum = Small_PrimeTable[choose1]
        else:
            maxum = Small_PrimeTable[choose2]
            maxum = Small_PrimeTable[(choose2+1) % 8]
        if maxum < minum:
            tmp = minum
            minum = maxum
            maxum = tmp
        shift_Num = ba2int(msg[-10:]) % maxum
        Create_Replace_Cipher(shift_Num, minum, maxum)
        renew = Enctypt_plainText(msg)
        fin = Decrypt_plainText(renew)
    else:
        return 0
    return msg


def pa_load(filename, filelen, shift_Num, MultiplyPrime, ModPrime):
    filename_encode = filename.encode("UTF-8")
    hex_filename = binascii.b2a_hex(filename_encode)
    filename_bitstring = hex2ba(hex_filename)
    filename_len = len(filename_bitstring)
    filename_bit = bitarray.bitarray(10)
    filename_bit.setall(0)
    # print(filename_len)
    file_lenbit = int2ba(filename_len)
    #print('original:', file_lenbit)
    filename_bit[10-len(file_lenbit):] = file_lenbit
    # print(filename_bit[10-len(file_lenbit):])
    print('after:', len(filename_bit), filename_bit)
    # -----------------------------------------
    fileContent_lenbit = bitarray.bitarray(40)
    fileContent_lenbit.setall(0)
    fileContent_bit = int2ba(filelen)
    fileContent_lenbit[40-len(fileContent_bit):] = fileContent_bit
    # -----------------------------------------
    shift_Num_lenbit = bitarray.bitarray(5)
    shift_Num_lenbit.setall(0)
    shift_Num_bit = int2ba(shift_Num)
    shift_Num_lenbit[5-len(shift_Num_bit):] = shift_Num_bit
    # -----------------------------------------
    MultiplyPrime_lenbit = bitarray.bitarray(5)
    MultiplyPrime_lenbit.setall(0)
    MultiplyPrime_bit = int2ba(MultiplyPrime)
    MultiplyPrime_lenbit[5-len(MultiplyPrime_bit):] = MultiplyPrime_bit
    # -----------------------------------------
    ModPrime_lenbit = bitarray.bitarray(5)
    ModPrime_lenbit.setall(0)
    ModPrime_bit = int2ba(ModPrime)
    ModPrime_lenbit[5-len(ModPrime_bit):] = ModPrime_bit
    total_paLoad = bitarray.bitarray(0)
    total_paLoad += filename_bit
    total_paLoad += fileContent_lenbit
    total_paLoad += shift_Num_lenbit
    total_paLoad += MultiplyPrime_lenbit
    total_paLoad += ModPrime_lenbit
    print('fileContent_lenbit:', fileContent_lenbit)
    print('shift_Num_lenbit:', shift_Num_lenbit)
    print('MultiplyPrime_lenbit:', MultiplyPrime_lenbit)
    print('ModPrime_lenbit:', ModPrime_lenbit)
    print(total_paLoad)
    print(len(total_paLoad))
    return total_paLoad


def de_pa_load(paLoad):
    # filename, filelen, shift_Num, MultiplyPrime, ModPrime
    filename_bit = paLoad[0:10]
    filelen_bit = paLoad[10:50]
    shift_Num_bit = paLoad[50:55]
    MultiplyPrime_bit = paLoad[55:60]
    ModPrime_bit = paLoad[60:65]
    fileName_len = ba2int(filename_bit)
    fileContent_len = ba2int(filelen_bit)
    shift_Num = ba2int(shift_Num_bit)
    MultiplyPrime = ba2int(MultiplyPrime_bit)
    ModPrime = ba2int(ModPrime_bit)
    print('fileName_len:', fileName_len)
    print('fileContent_len:', fileContent_len)
    print('shift_Num_len:', shift_Num)
    print('MultiplyPrime:', MultiplyPrime)
    print('ModPrime', ModPrime)
    return (fileName_len, fileContent_len, shift_Num, MultiplyPrime, ModPrime)


def Create_Replace_Cipher(shift_Num, MultiplyPrime, ModPrime):
    index = shift_Num
    replace_Cipher.append(shift_Num)
    for i in range(ModPrime-1):
        index = (index+MultiplyPrime) % ModPrime
        replace_Cipher.append(index)
    print(replace_Cipher)


def Enctypt_plainText(msg):
    ModPrime = len(replace_Cipher)
    slice_N = int(len(msg)/ModPrime)
    print(slice_N, len(msg), ModPrime)
    renew = bitarray.bitarray(len(msg))
    for i in range(slice_N):
        for j in range(ModPrime):
            renew[i*ModPrime+j] = msg[i*ModPrime+replace_Cipher[j]]
    for i in range(len(msg) % ModPrime):
        renew[i+slice_N*ModPrime] = msg[len(msg)-i-1]
    print('msgbefore:', msg)
    print('msgafter:', renew)
    return renew


def Decrypt_plainText(msg):
    ModPrime = len(replace_Cipher)
    slice_N = int(len(msg)/ModPrime)
    print(slice_N, len(msg), ModPrime)
    recover = bitarray.bitarray(len(msg))
    for i in range(slice_N):
        for j in range(ModPrime):
            recover[i*ModPrime+replace_Cipher[j]] = msg[i*ModPrime+j]
    for i in range(len(msg) % ModPrime):
        recover[i+slice_N*ModPrime] = msg[len(msg)-i-1]
    print('msgbefore:', msg)
    print('msgdecrypt:', recover)
    return recover


if __name__ == '__main__':
    # file_name = '111作品集.pdf'.encode("UTF-8")
    # binary_name = binascii.b2a_hex(file_name)
    # print(binary_name)
    # file_name_bitstring = hex2ba(binary_name)
    # print(file_name_bitstring)
    # print(len(file_name_bitstring))
    # file_name_hex = ba2hex(file_name_bitstring)
    # print(binascii.a2b_hex(file_name_hex).decode("UTF-8"))
    paload = pa_load('11作品集.pdf', 1000000000000, 3, 4, 5)
    de_pa_load(paload)
    # Message_Encoder(b'0')
