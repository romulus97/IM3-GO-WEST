# -*- coding: utf-8 -*-
"""
Created on Mon Oct  8 11:45:39 2018

@author: jkern
"""

############################################################################
#                           UC/ED Simulation

# This file simulates power system/market operations 
############################################################################

############################################################################
# Simulates power system operations for as many simulation days as
# specified (max is 365)
days = 2

import wrapper
wrapper.sim(days)
