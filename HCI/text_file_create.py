from numpy import NAN
from library_inventory.modules import json_data_sort as js
import pandas as pd
from library_inventory.modules.file_conversion import FUJITSU_index
import numpy as np
import json

def extract_and_convert_data(file_path, excel_save_path,text_save_path):
    df=js.json2excel_operation(file_path, excel_save_path)
    fi=FUJITSU_index()
    json_file_name=file_path.split("/")[-1]
    text_save_name=json_file_name.split(".")[0]    
    new_json_file_name="epc_sort_"+json_file_name
    new_file_path=file_path.replace(json_file_name,new_json_file_name)
    with open(new_file_path) as json_jile:
        j = json.load(json_jile)
    
    df_np=df.to_numpy()
    index = df.index
    # print(index)
    columns = df.columns
    new_list = []
    for row in df_np:
        new_row = []
        for item in row:
            if item == []:
                new_item = None
            else:
                new_item = item
            new_row.append(new_item)
        new_list.append(new_row)
    new_array = np.array(new_list)
    # print(new_array)
    new_df = pd.DataFrame(data=new_array,
                          index=index, columns=columns)
    
    new_df = new_df.dropna(how='all', axis=1)
    column = new_df.columns
    new_df = new_df.iloc[:,-1]
    # print(new_df)
    # columns=new_df.columns
    # print(column[-1])
    # print(index[3])
    data_list=[]
    library_code="01"
    device_code="01"
    for i,row in enumerate(new_df):
        scan_area=row.split("-")[0]
        time = j[index[i]][-1][-2]
        date = j[index[i]][-1][-1]
        year_month_day_split = date.split("/")
        month = fi.convert(str(int(year_month_day_split[1])))
        day = fi.convert(str(int(year_month_day_split[2])))
        name = index[i][-8:]
        while len(name) < 15:
            name=name+" "
        # print(len(name))
        hour_minute_second_split=time.split(":")
        hour = fi.convert(hour_minute_second_split[0])
        # print(hour)
        minute = hour_minute_second_split[1]
        second = hour_minute_second_split[2]
        data = scan_area+name+library_code+device_code+month+day+hour+minute+second+"\r"+"\n"
        data=data.encode("shiftjis")
        data_list.append(data)
    
    
    with open(text_save_path+"/"+text_save_name,"wb") as f:
        f.writelines(data_list)

    return new_df

if __name__ == '__main__':
    file_path = "C:/Users/staffa/Documents/Code/python/20HCI04/json/20210915.json"
    excel_save_path = "C:/Users/staffa/Desktop/ヴェンキー作業用/"
    text_save_path = "C:/Users/staffa/Documents/Code/python/20HCI04/text"
    extract_and_convert_data(file_path, excel_save_path,text_save_path)
