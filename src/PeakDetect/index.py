#!/usr/bin/env python 
# -*- coding: utf-8 -*-
'''
Date: 2022-10-19 09:45:22
LastEditors: gakkispy && yaosenjun@cii.com
LastEditTime: 2022-10-27 11:24:24
FilePath: /overlap_project/src/PeakDetect/index.py
'''
from src.PeakDetect import PeakDetect, OverlapPeakParse, GetPeakWidth



class PeakProcess():
    def __init__(self,
                data, 
                target = 432,
                mark=0.5, 
                accuracy = 0.1, 
                min_distance = 5, 
                denoise = False, 
                filter_name = "savgol_filter", 
                peak_type = "gaussian", 
                peak_num = 0, 
                env = "Development"):
        self.data = data
        self.target = target
        self.mark = mark
        self.accuracy = accuracy
        self.min_distance = min_distance
        self.denoise = denoise
        self.filter_name = filter_name
        self.peak_type = peak_type
        self.peak_num = peak_num
        self.env = env

    def run(self):
        detector = PeakDetect(self.data, 
                              self.accuracy, 
                              self.min_distance, 
                              self.denoise, 
                              self.filter_name, 
                              self.peak_type, 
                              self.peak_num)
        if self.mark == 0.5:
            return detector.ltq_ac_tune()

    def find_peak_width(self, peak_index:list):
        # detector = PeakDetect(self.data, self.target, 
        peak_width = GetPeakWidth(self.data, peak_index)
        return peak_width.run()