'''
Date: 2022-09-29 08:53:56
LastEditors: gakkispy && yaosenjun@cii.com
LastEditTime: 2022-10-11 11:21:17
FilePath: /peak_utils/tools/read_mzxml.py
'''
#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import xml
import time
import base64
import struct
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt

# 读取 .mzXML 文件；Reading .mzXML files;


def read_mzxml(mzXML_file, env='Development'):
    dom = xml.dom.minidom.parse(mzXML_file)
    root = dom.documentElement

    if root.hasAttribute('scanCount'):
        scanCount = root.getAttribute('scanCount')
        print('Root element: {}'.format(scanCount))

    # 获取子节点；Get the child node;
    scan_list = root.getElementsByTagName('scan')

    # 定义一个空列表，用于存储所有的谱图；Define a list to store all the spectrogram;
    point_list = []
    tic_list = []
    # 计算算法时间；Calculate the algorithm time;
    start = time.perf_counter()
    # 遍历所有的谱图；Traverse all the spectrogram;
    for scan in tqdm(scan_list):
        try:
            peaks_count = scan.getAttribute('peaksCount')
            retention_time = scan.getAttribute('retentionTime')
            scan_num = scan.getAttribute('num')
        except Exception as e:
            print(e + '请检查文件属性是否正确！')
            pass
        retention_time = float(retention_time[2: -1])
        # 获取所有的峰；Get all the peaks;
        peaks = scan.getElementsByTagName('peaks')[0]
        peaks_count = int(peaks_count) * 2

        # base64解码；Decode base64;
        peaks_base64 = peaks.firstChild.data
        peaks_bytes = base64.b64decode(peaks_base64)
        # 解码后的数据为二进制，需要转换为float；Decoded data is binary, need to convert to float;
        peaks_bytes_float = struct.unpack(
            '!' + str(peaks_count) + 'f', peaks_bytes)
        # 将解码后的数据存入列表；Store the decoded data in the list;
        point_list.append(peaks_bytes_float)
        # 获取所有的TIC；Get all the TIC;
        tic = sum(peaks_bytes_float[1::2])
        tic_list.append((retention_time, tic, peaks_count))
    # 转换为numpy数组；Convert to numpy array;
    point_list = np.array(point_list)
    tic_list = np.array(tic_list)
    # 计算算法时间；Calculate the algorithm time;
    end = time.perf_counter()
    if (env == 'Development'):
        print('算法时间：', end - start)
        plt.figure()
        plt.plot(tic_list[:, 0], tic_list[:, 1], 'k-')
        plt.xlabel('Retention Time')
        plt.ylabel('Intensity')
        plt.title('TIC graphic')
        plt.show()

    # 展示图谱；Display the spectrogram;
    if (env == 'Development'):
        for i in range(0, 5):
            plt.figure()
            plt.plot(point_list[i][0::2], point_list[i][1::2], '-')
            plt.xlabel('m/z')
            plt.ylabel('Intensity')
            plt.title('Spectrogram')
            plt.show()

    return point_list, tic_list, scan_num
