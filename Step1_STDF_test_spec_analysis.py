from tkinter import Tk      
from tkinter.filedialog import askopenfilename
import csv, os
import pandas as pd
from Semi_ATE import STDF 

def get_stdf_data(file, test_name_lst):
    # It's a STDF parser, to parse stdf data based on input testname list

    stdf_name = os.path.basename(file)
    

    chip_data_lst = []
    chip_test_dict = {}
    
    # lot level test informaton, e.g. MIR
    part_name = "A12345"
    job_name = "Sort_xxx"
    job_verion = "V0.01"
    
    # wafer level test information, e.g. WIR
    wafer_id = "##"
    start_time = 123456789
    
    for REC in STDF.records_from_file(file):
        
        #print(REC.to_dict())
        rec = REC.to_dict()

        if rec['rec_id'] == "MIR":
            # lot test start, Key parameters: LOT_ID , PART_TYP , JOB_NAM , JOB_REV
            lot_id = rec['LOT_ID']
            part_name = rec['PART_TYP']
            job_name = rec['JOB_NAM']
            job_verion = rec['JOB_REV']
        
        if rec['rec_id'] == "WIR" :            
            # wafer test start: WAFER_ID, START_T
            # FT test don't have this
            wafer_id = rec['WAFER_ID']
            start_time = rec['START_T']
            
        if rec['rec_id'] == "WCR" :
            # wafer coordinate record: WAFER_FLAT, CENTER_X, CENTER_Y    
            # FT test don't have this
            pass
            
        if rec['rec_id'] == "PIR" :
            # chip test start
            pass
            
        if rec['rec_id'] == "PTR" :
            # chip test parametric result:
            # every chip has: TEST_TXT , RESULT , SITE_NUM
            # Some information only show at first time: LO_LIMIT, HI_LIMIT, LO_SPEC, HI_SPEC, UNITS
             
            test_name = rec['TEST_TXT']
            if test_name in test_name_lst:
                site_num = rec['SITE_NUM'] 
                result = rec['RESULT'] 
                tmp_chip_result_lst = chip_test_dict.get (site_num, [])
                tmp_chip_result_lst.append(result)
                chip_test_dict[site_num] = tmp_chip_result_lst
    
        if rec['rec_id'] == "PRR" :
            # chip test end: PART_ID, X_COORD, Y_COORD, SOFT_BIN, HARD_BIN, SITE_NUM
            # bad chip may not have full test item, need to complete empty terms
            site_num = rec['SITE_NUM'] 
            pid = rec['PART_ID'] 
            chipx = rec['X_COORD'] 
            chipy = rec['Y_COORD'] 
            soft_bin = rec['SOFT_BIN'] 
            hard_bin = rec['HARD_BIN']             

            chip_result_lst = chip_test_dict[site_num]
            # ['stdf_name', "TP_name", "TP_version" , "Part_id", "lot_id", "wfr_id", "PID", "X_COORD", "Y_COORD","soft_BIN", "hard_BIN", "site_NUM"] + test_name_lst
            chip_result_lst = [stdf_name, job_name, job_verion, part_name, lot_id, wafer_id, pid,chipx,chipy, soft_bin,hard_bin, site_num] + chip_result_lst
            
            if len (chip_result_lst) < len (test_name_lst):
                del_test_num = len (test_name_lst) - len (chip_result_lst)
                chip_result_lst = chip_result_lst + ["N/A"] * del_test_num
            
            # append chip level test dat to wafer level data set
            chip_data_lst.append(chip_result_lst)

            # dill stored chip level data
            del chip_test_dict[site_num]             
            
        if rec['rec_id'] == "WRR" :
            # wafer test end:  PART_CNT, GOOD_CNT
            # FT test don't have this
            pass
            
        if rec['rec_id'] == "MRR" :
            # lot test end: 
            return chip_data_lst



########################################################################################################
#   Below code are main flow   #########################################################################
########################################################################################################


# read CSV file, which defines testname list want to parse from STDF files
Tk().withdraw() 
tests_list_file = askopenfilename(filetypes=[("csv file","*.csv")],
                   title= "Select CSV for list of testnames want to parse from STDF!!!") 
#print(tests_list_file)

df = pd.read_csv(tests_list_file, index_col = False)
df.fillna("N/A")

test_name_lst = df['test_name'].tolist()
test_num_lst = df['test_num'].tolist()
test_lo_limit_lst = df['test_lo_limit'].tolist()
test_hi_limit_lst = df['test_hi_limit'].tolist()
test_lo_spec_lst = df['test_lo_spec'].tolist()
test_hi_spec_lst = df['test_hi_spec'].tolist()
test_unit_lst = df['test_unit'].tolist()

# add ohter information whants to parse from STDF
test_name_lst =  ['stdf_name', "TP_name", "TP_version" , "Part_id", "lot_id", "wfr_id", "PID", "X_COORD", "Y_COORD","soft_BIN", "hard_BIN", "site_NUM"] + test_name_lst

test_num_lst = [""] * 11 + ["test_num"] + test_num_lst
test_lo_limit_lst = [""] * 11 + ["lo_limit"] + test_lo_limit_lst
test_hi_limit_lst = [""] * 11 + ["hi_limit"] + test_hi_limit_lst
test_lo_spec_lst = [""] * 11 + ["lo_spec"] + test_lo_spec_lst
test_hi_spec_lst = [""] * 11 + ["hi_spec"] + test_hi_spec_lst
test_unit_lst = [""] * 11 + ["test_num"] + test_unit_lst

########################################################################################################
### start STDF parsing loop !!!
########################################################################################################

stdf_file = askopenfilename(filetypes=[("stdf.gz file","*.gz"),("stdf file","*.stdf")],
                           title= "Select stdf.gz or stdf that want to parsse !!!") 

#print(stdf_file)

wafer_data_set = get_stdf_data(stdf_file, test_name_lst)

out_csvfile = stdf_file.replace(".stdf", "").replace(".gz", "") + "_data.csv"
with open(out_csvfile, 'w', newline='') as f:
    writer = csv.writer(f)

    writer.writerow(test_num_lst)
    writer.writerow(test_lo_limit_lst)
    writer.writerow(test_hi_limit_lst)
    writer.writerow(test_lo_spec_lst)
    writer.writerow(test_hi_spec_lst)
    writer.writerow(test_unit_lst)

    writer.writerow(test_name_lst)
    writer.writerows(wafer_data_set) 