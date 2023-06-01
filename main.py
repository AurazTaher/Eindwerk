#!/usr/bin/python
# -*- coding:utf-8 -*-
from screen import Screen
from modules.gps import GPSModule

gps = GPSModule(0,0,2,2) #positie en b & h

glasses = Screen(n_rows = 3, n_columns = 2) #maakt scherm
glasses.add_module(gps) # module toevoegen aan scherm
glasses.run() # tekent steeds nieuwe frames
    
