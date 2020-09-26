# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 16:27:18 2020

@author: mzeigha
"""


import pandas as pd
import numpy as np


unit_list_emisssion = pd.read_stata("unit-list-emisssion.dta")
                  
unit_list_emisssion.to_csv (r'unit_list_emisssion.csv', index = False, header=True)