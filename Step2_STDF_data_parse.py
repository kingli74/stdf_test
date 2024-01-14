from tkinter import Tk      
from tkinter.filedialog import askopenfilename
import csv, os
import pandas as pd
from Semi_ATE import STDF 


Tk().withdraw() 
filename = askopenfilename(filetypes=[("stdf.gz file","*.gz"),("stdf file","*.stdf")],title= "Select stdf of stdf.gz") 
print(filename)

def get_stdf_testname(file):

    
    csvfile = file.replace(".stdf", "").replace(".gz","") + "_testname_limits_list.csv"
    test_dict ={}
    for REC in STDF.records_from_file(file):

        #print(REC.to_dict())
        rec = REC.to_dict()
    
        if rec['rec_id'] == "PTR" :
            # lo_limit , hi_limit, lo_spec, hi_spec only occur once. not repeat for every chips test.
            
            test_name = rec['TEST_TXT'] 
            test_num = rec['TEST_NUM']    
            test_lo_limit =  rec['LO_LIMIT']    
            test_hi_limit =  rec['HI_LIMIT']   
            test_lo_spec =  rec['LO_SPEC']    
            test_hi_spec =  rec['HI_SPEC']   
            test_unit =  rec['UNITS']   

            # first time item will have deltail test limits & specs
            if test_name not in test_dict.keys():                
                test_dict[test_name] = [test_name , test_num, test_lo_limit, test_hi_limit, test_lo_spec, test_hi_spec, test_unit]
            
        if rec['rec_id'] == "PRR" :
            # chip test end, once hit good chip. all test items /limits / specs/ units collection done.
            if rec['HARD_BIN'] == 1:
    
                with open(csvfile, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['test_name', 'test_num', 'test_lo_limit', 'test_hi_limit', 'test_lo_spec', 'test_hi_spec', 'test_unit'])
        
                    for row in test_dict.values():
                        writer.writerow(row)    
                break

get_stdf_testname(filename)