import urllib.request 
import json 
import csv

apiUrl = "https://www.hko.gov.hk/cis/dailyExtract/dailyExtract_2022.xml"

with urllib.request.urlopen(apiUrl) as response:
   html = response.read().decode()

#print(html)

htmljson=json.loads(html)
year="2022"
fullDate=""
month=""
csvFormatheader=["Date","MeanPressure","MaxDeg","MeanDeg","MinDeg","MeanDewPoint","MeanRelativeHumidity","MeanAmountofCloud","TotalRainfall"]
csvFormat=[]
date=0
# MeanPressure  1
# MaxDeg  2
# MeanDeg 3
# MinDeg  4
# MeanDewPoint 5
# MeanRelativeHumidity 6
# MeanAmountofCloud 7
# TotalRainfall 8

def addZeroToMonth(m):
    if (m<10):
        return "0"+str(m)
    return str(m)

def checkTrace(d):
    if(d=="Trace"):
        csvFormat.append("0.05")
    else:
        csvFormat.append(d.replace(" ", ""))


with open('dataset.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)

    writer.writerow(csvFormatheader)
    for m in range(len(htmljson["stn"]['data'])):
        month=addZeroToMonth(htmljson["stn"]['data'][m]["month"])
        for d in range(len(htmljson["stn"]['data'][m]["dayData"])-2): 
            date=str(htmljson["stn"]['data'][m]["dayData"][d][0])
            
            
            fullDate=year+"-"+month+"-"+date
            csvFormat.append(fullDate)
            for c in range(1,9):
                
                if c==8:
                    checkTrace(htmljson["stn"]['data'][m]["dayData"][d][c])
                else:
                    csvFormat.append(htmljson["stn"]['data'][m]["dayData"][d][c].replace(" ", ""))
        
            
            writer.writerow(csvFormat)
            csvFormat.clear()