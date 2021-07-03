#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import re
from area import area_data as area


header = ["地址", "市(縣)", "區(鄉鎮市)", "村(里)", "鄰", "路(街道)", "段", "巷", "弄", "號", "樓", "其它"]
factor = ["市", "縣", "區", "鄉", "鎮", "村", "里", "鄰", "路", "街", "段", "巷", "弄", "號", "樓"]
split_factor = "([市縣區鄉鎮村里鄰路街道段巷弄號樓F(])"
ch_num = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
ar_num = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "1"]


addr = pd.read_csv("addresses.txt", names = header)
addr.head()

#主程式
for index, row in addr.iterrows():
    ad = row["地址"]
    ad = ad.replace("臺", "台")
    ad = ad.replace("-", "之")
    addr_split0 = re.split(split_factor, ad)
    
    #括號內訊息合併
    addr_split = []
    if "(" in addr_split0 :
        for i in range( len(addr_split0)):
            if addr_split0[i] != "(" :
                addr_split.append( addr_split0[i])
            else :
                addr_split.append( "".join(addr_split0[i::]))
                break
    else :
        addr_split = addr_split0
    
    #行政區劃合併
    addr_split_list =[]
    if len(addr_split)%2 == 0:
        for i in range(int(len(addr_split)/2)) :
            addr_split_list.append(addr_split[2*i]+addr_split[2*i+1])
    else : 
        for i in range(int(len(addr_split)/2)) :
            addr_split_list.append(addr_split[2*i]+addr_split[2*i+1])
        addr_split_list.append(addr_split[-1])
    
    #幾樓之幾合併
    for i in range(len(addr_split_list)) :
        if str(addr_split_list[i]) != "" :
            if str(addr_split_list[i])[0] == "之" or str(addr_split_list[i])[0] == "-" :
                addr_split_list[i-1] = str(addr_split_list[i-1]) + str(addr_split_list[i])[:2]
                addr_split_list[i] = str(addr_split_list[i])[2::]   
    
    #刪除重複資訊
    addr_list = []
    for item in addr_split_list :
        if item not in addr_list and item != "" :
            addr_list.append(item)
    
    
    #將整理出之資訊依類別填入dataframe
    for item in addr_list :
        for col in addr.columns :
            if str(addr[col][index]) == "nan" :
                if str(item)[-1] in col and str(item)[-1] != ")" :
                    addr[col][index] = str(item)
                    break
                      
        #樓(之)格式不一致而搬出整理
        if str(addr["樓"][index]) == "nan" :           
            if "樓之" in str(item) or   "F之" in str(item) or "F" in str(item) :
                addr["樓"][index] = str(item)     
        
    #處理備註
        #先檢查該項資料(item)有無填入至資料格中，有則宣告check為真
        check = False
        for col in addr.columns :
            if str(item) == addr[col][index] :
                check = True
                
        #資料格已有資料(item)，則後續處理不成立，反之成立
        if str(addr["其它"][index]) == "nan" :
            if not check and str(item) is not "nan" :
                addr["其它"][index] = str(item)
        else :
            if not check and str(item) is not "nan" :
                addr["其它"][index] = str(addr["其它"][index]) + str(item)
                
    #處理園區街
    if addr["路(街道)"][index] == "街" and "園區" in addr["其它"][index] :
        addr["路(街道)"][index] = "園區街"
        addr["其它"][index] = addr["其它"][index].replace("園區", "")
    if addr["其它"][index] == "" :
        addr["其它"][index] = np.nan

#阿拉伯數字、中文數字轉換 / 之與其他分離
for index, row in addr.iterrows():
    for j in range(10) :
        if str(addr["段"][index]) != "nan" :
            addr["段"][index] = str(addr["段"][index]).replace(ar_num[j], ch_num[j])


#將應當沒問題與也許有問題之地址分離

processed_yes = pd.DataFrame(columns = header)
processed_no = pd.DataFrame(columns = header)
for index, row in addr.iterrows():
    C = addr["市(縣)"][index]
    D = addr["區(鄉鎮市)"][index]
    
    if str(addr["其它"][index]) == "nan" and D in area[C] :
        processed_yes = processed_yes.append(row)
    else :
        processed_no = processed_no.append(row)
        
processed_yes = processed_yes.reset_index(drop=True)
processed_no = processed_no.reset_index(drop=True)

