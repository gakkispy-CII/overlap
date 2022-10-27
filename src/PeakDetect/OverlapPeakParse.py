#!/usr/bin/env python 
# -*- coding: utf-8 -*-
'''
Date: 2022-10-26 11:37:35
LastEditors: gakkispy && yaosenjun@cii.com
LastEditTime: 2022-10-27 17:20:43
FilePath: /overlap_project/src/PeakDetect/OverlapPeakParse.py
'''

import re
import numpy as np
import pandas as pd
from src.PeakDetect.GaussianPeakFIt import gaussian_with_exp

class OverlapPeakParse():

    '''
    description: 
    param {*} self
    param {pd} data
    param {list} peaks
    param {list} valleys
    param {float} threshold
    param {str} peak_type
    param {float} peak_num
    param {*} self
    return {*}
    '''
    def __init__(self, 
                 data:pd.DataFrame, 
                 peaks:list, 
                 valleys:list, 
                 threshold:float, 
                 peak_type:str="gaussian", 
                 peak_num:float or None=None)->None:
        super(OverlapPeakParse, self).__init__()
        self.data = data
        self.peaks = peaks
        self.valleys = valleys
        self.threshold = threshold
        self.peak_type = peak_type
        self.peak_num = peak_num

    def peak_fit(self, ):
        if self.peak_type == "gaussian":
            out, comps = gaussian_with_exp(self.data, self.peaks, self.valleys)
            return out, comps

    def parse_overlap_peak(self, ):
        out, comps = self.peak_fit()
        height_list, parsing_peak_data_list,  parsing_peak_index_list = [], [], []
        for key, value in comps.items():
            if not re.search('exp', key):
                parsing_peak_data_list.append(value)
        for key, value in out.params.items():
            if re.search('height', key):
                height_list.append(value.value)

        main_peak_y = max(height_list)
        for i in range(len(height_list)):
            try:
                peak_index = np.where(np.array(parsing_peak_data_list[i]) == height_list[i])[0][0]
            except Exception as e:
                peak_index = np.abs(np.array(parsing_peak_data_list[i]) - height_list[i]).argmin()
            parsing_peak_index_list.append(peak_index)
            if height_list[i] == main_peak_y:
                main_peak_index = peak_index
                main_peak_x = self.data['x'][peak_index]
        
        return parsing_peak_data_list, parsing_peak_index_list, [main_peak_x, main_peak_y, main_peak_index]

