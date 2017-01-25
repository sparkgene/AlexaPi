#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os
import unittest
import test_data
sys.path.append(os.pardir)
from avs import Avs

class AvsTest:
    def setUp(self):
        print("[STATE:AvsTest] setUp")

    def test_analyze_response(self):

    def tearDown(self):
        print("[STATE:AvsTest] tearDown")
