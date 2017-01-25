#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os
import unittest
sys.path.append(os.pardir)
from avs import Avs


class AvsTest(unittest.TestCase):
    def setUp(self):
        print("[STATE:AvsTest] setUp")


    def tearDown(self):
        print("[STATE:AvsTest] tearDown")


    def test_analyze_response(self):
        print("[STATE:AvsTest] test_analyze_response")

        def dummy_func(x):
            print(x)

        with open("testdata_basic.txt","rb") as inf:
            data = inf.read()
        avs = Avs(dummy_func)
        ret = avs.analyze_response("bdf5caea-954f-4c7a-8b5c-30482cefd588", data)
        print("[STATE:AvsTest] basic")
        print(ret)

        with open("testdata_ask.txt","rb") as inf:
            data = inf.read()
        avs = Avs(dummy_func)
        ret = avs.analyze_response("b4310007-b012-49a3-bd26-f8103c823a25", data)
        print("[STATE:AvsTest] ask")
        print(ret)

        with open("testdata_flash_bleafing.txt","rb") as inf:
            data = inf.read()
        avs = Avs(dummy_func)
        ret = avs.analyze_response("091805e0-bf6e-4982-8dbb-e89a82dafad5", data)
        print("[STATE:AvsTest] flash bleafing")
        print(ret)


    def test_change_state(self):
        print("[STATE:AvsTest] change state")

        def dummy_func(x):
            print("")

        with open("testdata_ask.txt","rb") as inf:
            data = inf.read()
        avs = Avs(dummy_func)
        ret = avs.analyze_response("b4310007-b012-49a3-bd26-f8103c823a25", data)

        avs.change_state(ret)
        self.assertEqual(True, avs.active())


        with open("testdata_basic.txt","rb") as inf:
            data = inf.read()
        avs = Avs(dummy_func)
        ret = avs.analyze_response("bdf5caea-954f-4c7a-8b5c-30482cefd588", data)

        avs.change_state(ret)
        self.assertEqual(False, avs.active())

        print(ret)

if __name__ == '__main__':
    unittest.main()
