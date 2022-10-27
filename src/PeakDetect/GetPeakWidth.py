#!/usr/bin/env python 
# -*- coding: utf-8 -*-
'''
Date: 2022-10-18 19:16:48
LastEditors: gakkispy && yaosenjun@cii.com
LastEditTime: 2022-10-27 20:08:52
FilePath: /overlap_project/src/PeakDetect/GetPeakWidth.py
'''

import numpy as np
import pandas as pd
from scipy.signal import peak_widths


class GetPeakWidth():

    '''
    description: 
    param {*} self
    param {pd} data
    param {list} peaks_index
    param {list} main_peak
    param {float} threshold
    param {bool} need_fit
    param {str} peak_type
    param {float} peak_num
    param {*} self
    return {*}
    '''
    def __init__(self, 
                 data:pd.DataFrame, 
                 peaks_index:list, 
                 main_peak:list, 
                 threshold:float, 
                 need_fit:bool = True, 
                 peak_type:str = "gaussian", 
                 peak_num:float or None =None)->None:
        super(GetPeakWidth, self).__init__()
        self.data = data
        self.peaks_index = peaks_index
        self.threshold = threshold
        self.need_fit = need_fit
        self.peak_type = peak_type
        self.peak_num = peak_num
        self.main_peak = main_peak

    def get_peak_width(self,):
        if self.need_fit:
            peak_width = peak_widths(self.data['y'], self.peaks_index, rel_height=self.threshold)
            scale = (self.data['x'].values[-1] - self.data['x'].values[0]) / len(self.data['x'])
            peak_width = [peak_width[0][0] * scale, peak_width[1][0]]
        else:
            peak_width = [self.get_origin_peak_width(), self.main_peak[1]]
        return peak_width

    def get_origin_peak_width(self,):
        target_peak_height = self.main_peak[1] * self.threshold
        target_peak_left_list = self.data.iloc[:self.main_peak[2]]
        target_peak_left = target_peak_left_list[target_peak_left_list['y'] < target_peak_height].index[-1]
        target_peak_right = target_peak_left_list[target_peak_left_list['y'] > target_peak_height].index[0]
        interpolate_target = np.interp(target_peak_height, self.data['y'][target_peak_left:target_peak_right], self.data['x'][target_peak_left:target_peak_right])
        return (self.data['x'][self.main_peak[2]] - interpolate_target) * 2