#!/usr/bin/env python 
# -*- coding: utf-8 -*-
'''
Date: 2022-10-18 19:15:05
LastEditors: gakkispy && yaosenjun@cii.com
LastEditTime: 2022-10-19 10:26:59
FilePath: /overlap_project/src/PeakDetect/PeakDetect.py
'''

import numpy as np
import scipy.signal as signal
from findpeaks import findpeaks
from Filter import get_filters, data_with_filted
from GaussianPeakFIt import gaussian_with_exp

class PeakDetect():
    def __init__(self, data, threshold, min_distance, denoise=False, filter_name="savgol_filter", peak_type="gaussian", peak_num=None):
        self.data = data
        self.threshold = threshold
        self.min_distance = min_distance
        self.denoise = denoise
        self.peak_type = peak_type
        self.peak_num = peak_num
        self.filter_name = filter_name

    def peak_detect(self):
        if self.denoise:
            filter = get_filters(self.filter_name)
            self.data = data_with_filted(filter, self.data)
        if self.peak_type == "gaussian":
            peak_index, valley_index = self.gaussian_peak_detect()
            return peak_index, valley_index
            
    def peak_fit(self, peaks, valleys):
        if self.peak_type == "gaussian":
            out, comps = gaussian_with_exp(self.data, peaks, valleys)
            return out, comps


    def gaussian_peak_detect(self):
        fp = findpeaks(method='topology', interpolate=10, lookahead=100, limit=self.min_distance)
        try:
            peak_results = fp.fit(self.data['y'])
            peak_index, valley_index = self.peak_process(peak_results, self.data, self.threshold)
        except:
            peak_index = []
            valley_index = []

        return peak_index, valley_index
    
    def peak_process(self, peaks):
        df = peaks['df']
        df['x'] = self.data['x']
        peak_index= df[lambda df: df['peak'] == True]
        highest_peak = df.loc[peak_index.index.tolist()]['y'].max()
        peak_index_list = peak_index[lambda peak_index: peak_index['y'] > self.threshold * highest_peak].index.tolist()
        valley_index = df[lambda df: df['valley'] == True]
        valley_index_list = valley_index[lambda valley_index: valley_index['y'] > self.threshold * highest_peak].index.tolist()
        return peak_index_list, valley_index_list

    def get_fwhm(self,):
        peak_index, valley_index = self.peak_detect()
        result, comps = self.peak_fit(peak_index, valley_index)
        fwhm = result.params['fwhm'].value
        return fwhm

        