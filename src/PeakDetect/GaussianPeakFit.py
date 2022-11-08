#!/usr/bin/env python 
# -*- coding: utf-8 -*-
'''
Date: 2022-10-18 19:15:15
LastEditors: gakkispy && yaosenjun@cii.com
LastEditTime: 2022-10-27 16:42:10
FilePath: /overlap_project/src/PeakDetect/GaussianPeakFIt.py
'''
from typing import Any
import pandas as pd
from lmfit.models import GaussianModel, LinearModel, ExponentialModel
import numpy as np


# gaussian model with exponential background
'''
description: 
param {pd} data
param {list} peaks
param {list} valleys
return {*}
'''
def gaussian_with_exp(data:pd.DataFrame, peaks:list, valleys:list)->Any:
    params_dict = dict()
    exp_mod = ExponentialModel(prefix='exp_')
    pars = exp_mod.guess(data['y'], x=data['x'])
    max_peak = data['y'][peaks].max()
    mod = exp_mod
    if peaks:
        for index, peak in enumerate(peaks):
            tmp_prefix = 'pcm' + str(index) + '_'
            params_dict[tmp_prefix] = GaussianModel(prefix=tmp_prefix)
            pars.update(params_dict[tmp_prefix].make_params())
            pars[tmp_prefix + 'center'].set(data['x'][peak], min=data['x'][peak]-50, max=data['x'][peak]+50)
            pars[tmp_prefix + 'amplitude'].set(5, min=0.1, max=max_peak)
            pars[tmp_prefix + 'sigma'].set(10, min=.1, max = 50)
            mod += params_dict[tmp_prefix]
        out = mod.fit(data['y'], pars, x=data['x'])
        comps = out.eval_components(x=data['x'])
        return out, comps
    else:
        return 0,0


# gaussian model
def guassian(x, *params):
    num_func = int(len(params)/3)

    y_list = []

    for i in range(num_func):
        y = np.zeros_like(x)
        param_range = list(range(3*i, 3*(i+1), 1))
        amp = params[int(param_range[0])]
        ctr = params[int(param_range[1])]
        wid = params[int(param_range[2])]
        y += amp * np.exp(-(x - ctr)**2 / wid)
        y_list.append(y)
    
    y_sum = np.zeros_like(x)
    for i in y_list:
        y_sum += i

    y_sum += params[-1]

    return y_sum

