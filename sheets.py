import gspread
# import pdb
import datetime
import os
from oauth2client.service_account import ServiceAccountCredentials
URL = os.environ['VR_gsheet_url']
SHEET_NAME = 'VRFolio'
scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('CAMSCAS-6ac566f0e517.json', scope)


def get_sheet_dict(sheet_url,worksheet_name):
    gc = gspread.authorize(credentials)
    wkb = gc.open_by_url(sheet_url)
    wks = wkb.worksheet(worksheet_name)
    
    v_list = wks.get_all_values()
    heading = v_list[0]
    v_list_of_dict = []
    for v in v_list[2:]:
        # pdb.set_trace()
        v_list_of_dict.append(dict((heading[i],v[i]) for i in range(len(v))))
        
    return v_list_of_dict
    
def clear_google_sheet(sheet_url, worksheet_name):
    gc = gspread.authorize(credentials)
    wkb = gc.open_by_url(sheet_url)
    wks = wkb.worksheet(worksheet_name)
    
    wks.resize(rows=1)
    
# Add a record to the end of google sheet url supplied
# no need to pass index
def add_record_from_dict(sheet_url, worksheet_name, dict_rec):
    # one at a time
    gc = gspread.authorize(credentials)
    wkb = gc.open_by_url(sheet_url)
    wks = wkb.worksheet(worksheet_name)
    values_list = [ i for i in wks.row_values(1) if i]
    dict_rec["#"] = wks.row_count #index = row_count + 1(next item) - 1(1st row heading)
    if not set(dict_rec.keys()) == set(values_list):
        raise Exception("Dictionary is not well formed for the sheet.")
    new_row = []
    for i in values_list:
        new_row.append(dict_rec[i])
    wks.append_row(new_row)
    

def create_vr_dict(int_id, str_name, str_units_owned, str_pf_pert, str_cost_unit_value, str_last_unit_price, str_cost_value, str_mkt_valu, str_return_abs, str_return_pert,  str_day_chng_abs, str_day_chng_pert, str_vro_rating, str_last_updated, str_status, str_update_ts):
    return {
        "id"                      : str(int_id),
        "Mutual Fund Name"        : str_name,
        "Units"                   : str_units_owned,
        "Overall Portfolio Share9in %)" : str_pf_pert,
        "Cost Value(Units)"       : str_cost_unit_value,
        "Market Value(Unit)"      : str_last_unit_price,
        "Cost Value(Portfolio)"   : str_cost_value,
        "Market Value(Portfolio)" : str_mkt_valu,
        "Return"                  : str_return_abs,
        "Return(in %) - 2"        : str_return_pert,
        "Return - Day"            : str_day_chng_abs,
        "Return - Day(in %)"      : str_day_chng_pert,
		"VRO Ratings"             : str_vro_rating,		
		"Last Updated(VR)"        : str_last_updated, # add year her
        "Row Fetch Status"        : str_status,
        "Last Run"                : str_update_ts
    }
    
    
def batch_update_gsheet(sheet_url, worksheet_name, list_rec, ts):
    gc = gspread.authorize(credentials)
    wkb = gc.open_by_url(sheet_url)
    wks = wkb.worksheet(worksheet_name)
    
    rc = len(list_rec)
    # cc = len(list_rec[0].keys())
    # cc = len(list_rec[0])
    print("number of rows:"+str(wks.row_count))
    wks.resize(rc+10,16) #Column count must be set
    print("number of rows after resize:"+str(wks.row_count))
    # wks.add_rows(rc+10-wks.row_count)
    print('A1:P'+str(rc+1)) # Update The colum heading here
    cell_list = wks.range('A1:P'+str(rc+1))
    i = 0
    j = 0
    
    # Column header here
    #################################
    cell_list[0] = "id"                      
    cell_list[1] = "Mutual Fund Name"        
    cell_list[2] = "Units"                   
    cell_list[3] = "Overall Portfolio Share(in %)"
    cell_list[4] = "Cost Value(Units)"       
    cell_list[5] = "Market Value(Unit)"
    cell_list[6] = "Cost Value(Portfolio)"
    cell_list[7] = "Market Value(Portfolio)"
    cell_list[8] = "Return"
    cell_list[9] = "Return(in %) - 2"
    cell_list[10] = "Return - Day"
    cell_list[11] = "Return - Day(in %)"
    cell_list[12] = "VRO Ratings"
    cell_list[13] = "Last Updated(VR)"
    cell_list[14] = "Row Fetch Status"
    cell_list[15] = "Last Run"
    
    for cell in cell_list[16:]:
        # print(list_rec[i])
        if(j==0):
            cell.value = list_rec[i]['id']
        elif(j==1):
            cell.value = list_rec[i]['Mutual Fund Name']
        elif(j==2):
            cell.value = list_rec[i]["Units"] 
        elif(j==3):
            cell.value = list_rec[i]['Overall Portfolio Share(in %)'] 
        elif(j==4):
            cell.value = list_rec[i]['Cost Value(Units)'] 
        elif(j==5):
            cell.value = list_rec[i]['Status']
        elif(j==6):
            cell.value = list_rec[i]['Order Date']
        elif(j==7):
            cell.value = list_rec[i]['Days Left']
        elif(j==8):
            cell.value = list_rec[i]['Price']
        elif(j==9):
            cell.value = str(datetime.datetime.now())
            j=-1 # made0 in increment step
            i+=1
        elif(j==10):
            cell.value = list_rec[i]['Order ID']
        elif(j==11):
            cell.value = list_rec[i]['Order ID']
        elif(j==12):
            cell.value = list_rec[i]['Order ID']
        elif(j==13):
            cell.value = list_rec[i]['Order ID']
        elif(j==14):
            cell.value = list_rec[i]['Order ID']
        elif(j==15):
            cell.value = list_rec[i]['Order ID']
        elif(j==15):
            j= - 1 # To be made 0 in increment at bottom
            i += 1
        j += 1
        # cell.value = 'O_o'
    
    wks.update_cells(cell_list) # Update in batch

    
def save_vr_folio(dict_rows):
    if 'VRFolio' in dict_rows:
        list_vr_folio = dict_rows['VRFolio']
    else:
        list_vr_folio = []
    
    # batch update
    batch_save_list = []
    
    for i in list_vr_folio:
        dict_save = create_vr_dict(
        i['id'],
        i['str_name'],
        i['str_units_owned'],
        i['str_pf_pert'],
        i['str_cost_unit_value'],
        i['str_last_unit_price'],
        i['str_cost_value'],
        i['str_mkt_valu'],
        i['str_return_abs'],
        i['str_return_pert'],
        i['str_day_chng_abs'],
        i['str_day_chng_pert'],
        i['str_vro_rating'],
        i['str_last_updated'],
        i['str_status'],        
        str(datetime.datetime.now()
        )
        
        # add_record_from_dict(URL,SHEET_NAME,dict_save) #one at a time
        
        # Append to batch list
        batch_save_list.append(dict_save)
    
    batch_update_gsheet(URL,SHEET_NAME, batch_save_list, str(datetime.datetime.now()))
    
if __name__ == '__main__':
    # clear_google_sheet(URL, SHEET_NAME)
    # add_record_from_dict(URL,SHEET_NAME,create_order_dict('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', str(datetime.datetime.now())))
    batch_update_gsheet(URL,
        SHEET_NAME, [
        create_order_dict('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', str(datetime.datetime.now())),
        create_order_dict('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', str(datetime.datetime.now())),
        create_order_dict('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', str(datetime.datetime.now())),
        create_order_dict('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', str(datetime.datetime.now()))],
        str(datetime.datetime.now()))