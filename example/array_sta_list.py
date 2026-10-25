import jsonpickle
import os
from types import SimpleNamespace
import sys

infilename = "heatmap.json"
with open(infilename, "r") as inf:
    rawdata=inf.read()
    rawdata=rawdata.replace('heatmap','spam')
    mydata = jsonpickle.decode(rawdata)
mydata = SimpleNamespace(mydata)
goodArray=mydata.good_arrays[0]
for arr in mydata.good_arrays:
    print(type(arr))

# sta_list=[]
# with open('array_sta_list','w') as file1:
#     count_array=0
#     array_sta_list=[]
#     for arr in mydata.good_arrays:
#         #count_array+=1
#         for sta in arr.array.sta_list:
#                 array_sta_list.append(sta)
#                 #text=(f'{sta.netwrk} {sta.name} {0.0} {sta.loc.lat} {sta.loc.lon} {0.0} {0.0} {sta.start} {sta.stop}\n')
#                 text=(f'{count_array} {sta.netwrk} {sta.name} {0.0} {sta.loc.lat} {sta.loc.lon} {0.0} {0.0} {sta.start} {sta.stop}\n')
#                 file1.writelines(text)

# command=f"awk -F, '!seen[$1>$2 ? $1 FS $2 : $2 FS $1]++' array_sta_list > temp_sta"
# os.system(command)
# rm_command=f"mv -f temp_sta array_sta_list"
# os.system(rm_command)
