#!/usr/bin/python
# -*- coding:utf-8 -*-
from screen import Screen
from modules.gps import GPSModule

gps = GPSModule(0,0,3,2)

glasses = Screen(n_rows = 3, n_columns = 2)
glasses.add_module(gps)
glasses.run()
    
