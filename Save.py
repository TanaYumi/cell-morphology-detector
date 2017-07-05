# -*- coding: utf-8 -*-
"""
Created on Tue Oct  4 18:43:45 2016

@author: tanakayumiko
"""
import pandas as pd

def Save(state, sample_file):
    state.to_csv(sample_file)