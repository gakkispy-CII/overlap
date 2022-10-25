#!/usr/bin/env python 
# -*- coding: utf-8 -*-
'''
Date: 2022-10-11 16:35:14
LastEditors: gakkispy && yaosenjun@cii.com
LastEditTime: 2022-10-18 20:56:38
FilePath: /overlap_project/tests/test_simple.py
'''
# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest

from PeakDetect.simple import add_one


class TestSimple(unittest.TestCase):

    def test_add_one(self):
        self.assertEqual(add_one(5), 6)


if __name__ == '__main__':
    unittest.main()
