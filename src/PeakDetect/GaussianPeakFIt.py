#!/usr/bin/env python 
# -*- coding: utf-8 -*-
'''
Date: 2022-10-18 19:15:15
LastEditors: gakkispy && yaosenjun@cii.com
LastEditTime: 2022-10-18 20:52:18
FilePath: /overlap_project/src/PeakDetect/GaussianPeakFIt.py
'''
from lmfit.models import GaussianModel, LinearModel, ExponentialModel
import numpy as np


# gaussian model with exponential background
def gaussian_with_exp(data, peaks, valleys):
    exp_mod = ExponentialModel(prefix='exp_')
    pars = exp_mod.guess(data['y'], x=data['x'])
    gauss_main = GaussianModel(prefix='gauss_main_')
    pars.update(gauss_main.make_params())
    if len(peaks) > 1:
        gauss_side = GaussianModel(prefix='gauss_side_')
        pars.update(gauss_side.make_params())
        pars['gauss_side_center'].set(data['x'][peaks[1]], min=data['x'][peaks[1]]-50, max=data['x'][peaks[1]]+50)
        pars['gauss_side_sigma'].set(5, min=0.1, max=50)
        pars['gauss_side_amplitude'].set(10, min=0, max=150)
        mod = exp_mod + gauss_main + gauss_side
        out = mod.fit(data['y'], pars, x=data['x'])
        comps = out.eval_components(x=data['x'])
    else:
        mod = exp_mod + gauss_main
        out = mod.fit(data['y'], pars, x=data['x'])
        comps = out.eval_components(x=data['x'])
    return out, comps


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

