
README file for development of grid operations model for the U.S. Western Interconnection
created through the IM3 program at PNNL and NC State University.

DATA:

PSERC/CAISO 240-bus production cost model dataset: 
URL: https://pserc.wisc.edu/research/public_reports.aspx
Report and data appendum available in M-21 files.

Current generator data from the 2016 eGRID dataset (published in 2018):
URL: https://www.epa.gov/egrid/download-data
Data available in zipped historic data archive for 1996-2016

DATA CLEANING AND MODEL DEVELOPMENT CODE:

All code (python) is currently hosted at https://github.com/romulus97/IM3_WECC. 

-- CURRENT CONTENTS --

/Archive - miscellaneous files related to 240-bus PCM

/Model - current files needed to run python/pyomo version of the 240-bus PCM developed by Jim Price at CAISO

/generator_placement - data and files being used to map 2016 eGRID generator database to 240-bus PCM topology. 

Main script is 'mapper.py', which looks for unique pairings between a tuple of (U.S. state, WECC planning area) and bus in the 240-bus PCM, and then assigns eGRID generators to buses according to their individual tuple. eGRID generators that cannot be identified are then matched (if possible) to a generator in the '2026 Common Case Generator List 05-20-2016.xlsx' database. If a generator match is found, we record the node of the generator for the full PCM administered by WECC. In the file 'WECC240 data for IEEE PES 2011GM0942.xls', we look for this node (or its closest numerical neighbor) and then record the corresponding WECC240 bus. This is currently done manually, but could be automated if the process of matching eGRID to 2026 Common Case generators by string identifiers could be coded.




