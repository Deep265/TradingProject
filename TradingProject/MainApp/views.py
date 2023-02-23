# System imports
import json
import os
import csv

# Django Imports
from django.shortcuts import render
from .models import candles,csvs
from datetime import datetime
from django.http import JsonResponse,HttpResponse,FileResponse
from django.utils.encoding import smart_str

# Async Imports
from asgiref.sync import sync_to_async
import asyncio
# import aiofiles
# from aiocsv import AsyncReader

# Create your views here.


# Helper Function
# Takes only number from a given string
# Volume contains a string object
def nums(s):
    s1 = ""
    for i in s:
        if i.isdigit():
            s1 += i
    return float(s1)



# Writes the candle attributes (open,close,high,low,date,id) to Database
@sync_to_async
def model_writer(path):
    i=0
    with open(path, 'r') as f:
        reader = csv.reader(f)

        for row in reader:
            if i == 0:
                continue
            else:
                candle_object = candles(csv=f, id=i, open=float(row[3]), high=float(row[4]), low=float(row[5]),
                                              close=float(row[6]), date=datetime.fromtimestamp(int(row[1])))
                candle_object.save()
            i += 1


# For writing a json file and storing it to filesystem
def json_writer(data,file_name):
    json_path = os.path.realpath(os.path.dirname(__file__))
    json_path = os.path.join(json_path,"JSON file")
    json_path = os.path.join(json_path,file_name.split('\\')[-1].replace(".txt",'.json').replace('.csv','.json'))
    # the file exists then create a new file else update old
    if not os.path.exists(json_path):
        with open(json_path,'w') as f:
            j = json.dumps({'data':data},indent=4)
            f.write(j)
    else:
        print(json_path)
        with open(json_path,'r+') as f:
            j = json.load(f)
            j['data'].append(data)
            f.seek(0)
            json.dump(j,f,indent=4)
        print("Written")

@sync_to_async
def converter(path,n):


    # Stores all the attributes
    new_data_list = []

    i=0
    # Opening the file with csv reader and performing time frame operation
    # This can also be done by using pandas
    with open(path,'r') as f:
        reader = csv.reader(f)
        op = []
        high = []
        low  = []
        close = []
        volume = []
        date = []
        time = []
        for row in reader:
            if i==0:
                i = i+1
                continue
            else:

                op.append(float(row[3]))
                high.append(float(row[4]))
                low.append(float(row[5]))
                close.append(float(row[6]))
                volume.append(nums(row[7]))
                date.append(int(row[1]))
                time.append(row[2])
                # n is the timeframe given by the user
                if (i+1)%n==0:
                    new_data = dict()
                    new_data['OPEN'] = op[0]
                    new_data['HIGH'] = max(high)
                    new_data['LOW'] = min(low)
                    new_data['CLOSE'] = close[-1]
                    new_data['DATE'] = date[0]
                    new_data['BANKNIFTY'] = row[0]
                    new_data['VOLUME'] = volume[-1]
                    new_data['TIME'] = time[0]

                    op.clear()
                    high.clear()
                    low.clear()
                    close.clear()
                    date.clear()
                    time.clear()
                    volume.clear()
                    new_data_list.append(new_data)

                    # new_data_list.append(new_data)



            i=i+1
    json_writer(new_data_list, path.split('/')[-1])
    json_path = os.path.realpath(os.path.dirname(__file__))
    json_path = os.path.join(json_path, "JSON file")
    json_path = os.path.join(json_path, path.split('\\')[-1].replace(".txt", '.json').replace(".csv",'.json'))
    return json_path







async def get_csv(request):
    '''
    Gets the csv file and TimeFrame from the user and asynchronously call model_writer and converter function

    model_writer = Saves the candles to the Database having the attributes (id,open,close,high,low,date) which can be accessed using uploaded file.
    converter = Writes a json file to a given TimeFrame given by the user.
    The JSON File created is stored in the file system in MainApp/JSON file.

    The function returns a json file once the user click on submit button.

    :param request:
    :return: JSON File
    '''
    if request.method == "POST":
        file = request.FILES.get('file')
        time_frame = float(request.POST.get('time_frame'))
        # Saving the File in Database
        f = csvs(file=file)
        f.save()
        task1 = asyncio.ensure_future(model_writer(f.file.path))
        print("Model Write done")
        task2 = asyncio.ensure_future(converter(f.file.path,time_frame))
        print("Converted done")
        await asyncio.wait([task1,task2])


        # File Response (Sending Download JSON file)
        fp = task2.result()
        response = FileResponse(open(fp,'rb'),content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=%s' % smart_str('file.json')
        return response


    return render(request,'upload_csv.html')




