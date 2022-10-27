#!/usr/bin/env python 
# -*- coding: utf-8 -*-
'''
Date: 2022-10-18 19:15:05
LastEditors: gakkispy && yaosenjun@cii.com
LastEditTime: 2022-10-27 20:14:17
FilePath: /overlap_project/src/PeakDetect/PeakDetect.py
'''

import re
import numpy as np
import pandas as pd
from findpeaks import findpeaks
from src.PeakDetect.Filter import get_filters, data_with_filted
from src.PeakDetect.OverlapPeakParse import OverlapPeakParse
from src.PeakDetect.GetPeakWidth import GetPeakWidth

class PeakDetect():
    '''
    PeakDetect use findpeaks to detect peaks and valleys, and then use lmfit to fit the peaks.
    for actune mission, will return the fwhm of the main peak.
    '''
    '''
    description: 
    param {*} self
    param {pd} data
    param {int} target
    param {float} threshold
    param {float} min_distance
    param {bool} denoise
    param {str} filter_name
    param {str} peak_type
    param {float or None} peak_num
    return {*}
    '''
    def __init__(self, 
                 data: pd.DataFrame, 
                 target:int, 
                 mark:float,
                 threshold:float, 
                 min_distance:float, 
                 denoise:bool=False, 
                 need_fit:bool=False,
                 filter_name:str="savgol_filter", 
                 peak_type:str="gaussian", 
                 peak_num:float or None=None)->None:
        self.data = data
        self.target = target
        self.mark = mark
        self.threshold = threshold
        self.min_distance = min_distance
        self.denoise = denoise
        self.need_fit = need_fit
        self.peak_type = peak_type
        self.peak_num = peak_num
        self.filter_name = filter_name
        self.correction_factor = 1.0
        self.overlap_peak = False
        self.parsing_peak_data_list = []

    def overlap_peak_judge(self, peak_index:list)->None:
        for i in range(len(peak_index) - 1):
            if self.data['x'][peak_index[i + 1]] - self.data['x'][peak_index[i]] < self.min_distance:
                self.overlap_peak = True
                break
            
    def find_peaks(self,):
        if self.denoise:
            filter = get_filters(self.filter_name)
            self.data = data_with_filted(filter, self.data)
        fp = findpeaks(method='topology', interpolate=10, lookahead=100, limit=self.min_distance)
        try:
            peak_results = fp.fit(self.data['y'])
            peak_index, valley_index, highest_peak = self.peak_process(peak_results)
        except Exception as e:
            print(e)
            peak_index = []
            valley_index = []
            highest_peak = []
        main_peak_without_fit = highest_peak
        return peak_index, valley_index, main_peak_without_fit
        
    def peak_detect(self):
        '''
        peak_detect work flow:
        1. if denoise is True, use filter to denoise the data.
        2. use findpeaks to detect peaks and valleys.
            2.1 the result of findpeaks is a dict, which contains persistence and df, both of them are pandas.DataFrame.
            2.2 df contains the index of peaks and valleys, and the value of peaks and valleys.
            2.3 more detail about findpeaks, please refer to https://erdogant.github.io/findpeaks/pages/html/findpeaks.findpeaks.html#findpeaks.findpeaks.findpeaks.peaks1d
        3. data process for the result of findpeaks. remove the peaks and valleys which are too small. And the final result is a list of index of peaks and valleys.
        4. judge whether there is overlap peak.
            4.1 if there is overlap peak, use OverlapPeakParse to parse the overlap peak.
            4.2 the result of OverlapPeakParse contains the main peak's index, a list of the parsed peaks'value, and a list of the parsed peaks'index.
        5. use scipy.signal.peak_widths to get the width of the main peak. The rel_height is the self.mark.
        '''

        # find peaks without overlap peak parse
        peak_index, valley_index, main_peak_without_fit = self.find_peaks()
        correction_factor = self.target / main_peak_without_fit[0]

        self.overlap_peak_judge(peak_index)
        if self.overlap_peak and self.need_fit:
            overlap_pear_parser = OverlapPeakParse(self.data, peak_index, valley_index, self.threshold, self.peak_type, self.peak_num)
            parsing_peak_data_list, parsing_peak_index_list, main_peak = overlap_pear_parser.parse_overlap_peak()
            self.parsing_peak_data_list = parsing_peak_data_list
            return parsing_peak_index_list, valley_index, main_peak, correction_factor
            # width_result = []
            # for i in range(len(parsing_peak_data_list)):
            #     WidthGetter = GetPeakWidth(self.data, parsing_peak_data_list[i], parsing_peak_index_list[i], self.need_fit, self.peak_type, self.correction_factor)
            #     width_result.append(WidthGetter.get_peak_width())
            # main_width = width_result[main_peak_index]
            # return main_width
        else:
            return [peak_index], valley_index, main_peak_without_fit, correction_factor
            # WidthGetter = GetPeakWidth(self.data, self.data['y'][peak_index], peak_index, self.need_fit, self.peak_type, self.correction_factor)
            # width_result = WidthGetter.get_peak_width()
            # return width_result

    def peak_width_detect(self):
        peak_index, valley_index, main_peak, correction_factor = self.peak_detect()
        width_result_list = []
        for i in range(len(peak_index)):
            if self.overlap_peak and self.need_fit:
                tmp_data = pd.DataFrame({'x':self.data['x'], 'y': self.parsing_peak_data_list[i]})
            else:
                tmp_data = self.data
            WidthGetter = GetPeakWidth(tmp_data, [peak_index[i]], main_peak, self.mark, self.need_fit, self.peak_type, self.peak_num)
            width_result_list.append(WidthGetter.get_peak_width())
        
        # there will be some values shifted, so we need to shift them back
        width_result_list = np.array(width_result_list, dtype=np.float64)
        width_result_list[:,0] *= correction_factor
        return width_result_list

    def main_peak_width_detect(self,):
        width_result_list = self.peak_width_detect()
        # temprary find main peak index 
        _main_peak_index = np.argmax(width_result_list[:, 1])
        width_result = width_result_list[_main_peak_index, 0]
        return width_result

    

    def get_fwhm(self, result):
        fwhm_list = []
        for key, value in result.params.items():
            if re.search('fwhm', key):
                fwhm_list.append(value.value)
        return fwhm_list


    '''
    description: 
    param {*} self
    param {dict} peaks
    return {list, list} peak_index_list, valley_index_list
    '''
    def peak_process(self, peaks:dict):
        df = peaks['df']
        df['x'] = self.data['x']
        peak_index= df[lambda df: df['peak'] == True]
        highest_peak_value = df.loc[peak_index.index.tolist()]['y'].max()
        highest_peak_index = df.loc[peak_index.index.tolist()]['y'].idxmax()
        highest_peak_x = df['x'][highest_peak_index]
        highest_peak = [highest_peak_x, highest_peak_value, highest_peak_index]
        peak_index_list = peak_index.loc[peak_index.y.gt(self.threshold * highest_peak_value)].index.tolist()
        valley_index = df[lambda df: df['valley'] == True]
        valley_index_list = valley_index.loc[valley_index.y.gt(self.threshold * highest_peak_value)].index.tolist()
        return peak_index_list, valley_index_list, highest_peak


    # def main(self,):
    #     self.correction_factor =  self.target / center_list[main_peak_index]

    #     peak_index, valley_index = self.peak_detect()
    #     result, comps = self.peak_fit(peak_index, valley_index)
    #     main_peak_index = self.seek_main_peak(result)
    #     fwhm = self.get_fwhm(result)[main_peak_index] * self.correction_factor
    #     return fwhm

        