#!/usr/bin/env python3 
 # -*- coding: utf-8 -*-
'''
Date: 2022-09-29 08:53:56
LastEditors: gakkispy && yaosenjun@cii.com
LastEditTime: 2022-10-20 10:54:28
FilePath: /overlap_project/tools/get_files.py
'''
import os
from tqdm import tqdm


class GetFiles(object):
    def __init__(self, dir, type):
        super(GetFiles, self).__init__
        self.type = type or '.mzxml'
        self.root = os.path.dirname(os.path.abspath(__file__))
        self.dir = dir or os.path.join(self.root, 'data/')
        self.files = []

    # 遍历目录寻找文件；Traversing directories to find the files;

    def seek_root(self,):
        for root, dirs, files in os.walk(self.dir):
            for file in tqdm(files):
                if os.path.splitext(file)[1] == '.' + self.type:
                    self.files.append(os.path.join(root, file))

    # 获取文件路径列表；Get the file list with path;
    def get_files(self,):
        files_with_path = []
        self.seek_root()
        for file in self.files:
            files_with_path.append(os.path.join(self.dir, file))
        return files_with_path