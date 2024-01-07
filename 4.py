from flask import Flask, request, render_template, Response
from flask_table import Table, Col, ButtonCol

from pyorbital.orbital import Orbital
from pyorbital import tlefile

from datetime import datetime, timezone, timedelta
utc_time = datetime(2023, 10, 16, 0, 0)

def raschot(utc_time, lon, lat, alt, horizon, mH, length):
    utc_time# = datetime(2023, 10, 16, 0, 0)
    lon #37.5242
    lat #55.6947
    alt #165 #Высота станции (м)
    i=0
    az=0
    h=0 #Высота спутника (град)
    n=0
    mH#=0
    length
    horizon#=0
    a=[]
    sats=['METEOR-M2 2', 'METEOR-M2 3', 'NOAA 18', 'NOAA 19', 'METOP-B', 'METOP-C']
    orbital = Orbital('METEOR-M2 2', tle_file='tle.txt')
    passTimes=orbital.get_next_passes(utc_time, length, lon, lat, alt, tol=0.0001, horizon=horizon)
    while i<len(sats):
        sat=sats[i]
        orbital = Orbital(sat, tle_file='tle.txt')
        passTimes=orbital.get_next_passes(utc_time, length, lon, lat, alt, tol=0.0001, horizon=horizon)
        print(sat,len(passTimes))
        while n<len(passTimes):

            if len(passTimes)!=0:
                time = passTimes[n][0]
                time1 = passTimes[n][1]
                time2 = passTimes[n][2]

                az,h=orbital.get_observer_look(time, lon, lat, alt)
                az,h1=orbital.get_observer_look(time1, lon, lat, alt)
                az,h2=orbital.get_observer_look(time2, lon, lat, alt)

                #print(sat, passTimes[n][0].strftime('%Y.%m.%d %H:%M'))
                h=str('{:.2f}'.format(round(h,2)))
                h1=str('{:.2f}'.format(round(h1,2)))
                h2=str('{:.2f}'.format(round(h2,2)))
                a.append(dict(name=sat, timeUp=passTimes[n][0].strftime('%Y.%m.%d %H:%M:%S'), hUp=h, timeMax=passTimes[n][2].strftime('%Y.%m.%d %H:%M:%S'), hMax=h2, timeSet=passTimes[n][1].strftime('%Y.%m.%d %H:%M:%S'), hSet=h, lon=lon, lat=lat, alt=alt, horizon=horizon, button='button'))
            n+=1
        n=0
        i+=1

    n=0
    while n<len(a):
        h=float(a[n].get('hMax'))
        if h<mH:
            print('pop',a[n],h,'<',mH,n)
            a.pop(n)
            print()
            n-=1
        # else:
        #     print(a[n],h,mH,n)
        n+=1

    n=0
    sorted_a = sortByDate(a)
    for i in range(len(sorted_a)):  
        if i>0:
            if sorted_a[i].get('timeUp')<sorted_a[i-1].get('timeSet'):
                time=sorted_a[i-1].get('timeSet')
                time = datetime.strptime(time, '%Y.%m.%d %H:%M:%S')
                time+=timedelta(seconds=1)

                sat=sorted_a[i].get('name')
                timeUp=sorted_a[i].get('timeUp')
                timeMax=sorted_a[i].get('timeMax')
                h2=sorted_a[i].get('hMax')
                timeSet=sorted_a[i].get('timeSet')
                h1=sorted_a[i].get('hSet')

                orbital = Orbital(sat, tle_file='tle.txt')
                az,h=orbital.get_observer_look(time, lon, lat, alt)

                h=str('{:.2f}'.format(round(h,2)))

                sorted_a[i]=(dict(name=sat, timeUp=time.strftime('%Y.%m.%d %H:%M:%S'), hUp=h, timeMax=timeMax, hMax=h2, timeSet=timeSet, hSet=h1, lon=lon, lat=lat, alt=alt, horizon=horizon, button='button'))

                print('пересекаются',time,timeUp,sat,h)

    n=0
    while n<len(sorted_a):
        if n>0:
            if sorted_a[n].get('timeUp')>sorted_a[n].get('timeSet'):
                print('pop',sorted_a[n].get('timeUp'),'>',sorted_a[n].get('timeSet'),n,len(sorted_a))
                sorted_a.pop(n)
                print()
                n-=1

        n+=1

    
    return sorted_a

def tra(sat, time, lon, lat, alt, horizon):
    i=0
    str=''
    orbital = Orbital(sat, tle_file='tle.txt')
    az,h=orbital.get_observer_look(time, lon, lat, alt)

    if h<horizon:
        while h<horizon:
            time+=timedelta(seconds=1)
            az,h=orbital.get_observer_look(time, lon, lat, alt)

            print(sat, time, lon, lat, alt, horizon, h)
            
    
    if h>=horizon:
        str+='Satellite '+sat
        str+='Start date & time '+time.strftime('%Y.%m.%d %H:%M:%S')
        str+='\n'
        str+='Time (UTC) Azimuth Elevation'
        str+='\n'

        az,h=orbital.get_observer_look(time, lon, lat, alt)
        print('Satellite ', sat, time.strftime('%H:%M:%S'), round(az,2), round(h,2))
        str+=time.strftime('%H:%M:%S')+' '+'{:.2f}'.format(round(az,2))+' '+'{:.2f}'.format(round(h,2))+'\n'
        
    while h>=horizon:
        time+=timedelta(seconds=1)
        az,h=orbital.get_observer_look(time, lon, lat, alt)
        str+=time.strftime('%H:%M:%S')+' '+'{:.2f}'.format(round(az,2))+' '+'{:.2f}'.format(round(h,2))+'\n'
        print(time.strftime('%H:%M:%S'),round(az,2),round(h,2))
    
    return str

#  \|/сортировка\|/

def sortByDate(a):
    def strToDate(dstring):
        date_string=dstring.get('timeUp')

        return datetime.strptime(date_string, '%Y.%m.%d %H:%M:%S')
    return sorted(a, key=strToDate)

class ItemTable(Table):
    name = Col('Имя спутника')
    timeUp = Col('Время восхода спутника')
    timeSet = Col('Время захода спутника')
    hMax = Col('Высота кульминации')
    button=ButtonCol('скачать', endpoint='download', url_kwargs=dict(name='name',timeUp='timeUp',lon='lon',lat='lat',alt='alt',horizon='horizon'))

app = Flask(__name__)

@app.route('/')
def login():
    if request.method == 'POST':
        print("if request.method == 'POST':")

        lon = float(request.form['lon'])
        lat = float(request.form['lat'])
        alt = float(request.form['h'])   #Высота станции (м)

        horizon = float(request.form['hor'])
        Mh = float(request.form['Mh'])

        timeForm = request.form['time']
        length = int(request.form['length'])
        print('timeForm:',timeForm)

        utc_time = datetime(timeForm[0:3], timeForm[4:6], timeForm[7:9], 0, 0)

        print('timeForm:',timeForm[0:3], timeForm[4:6], timeForm[7:9], 0, 0)

        sorted_a = raschot(utc_time, lon, lat, alt, horizon, Mh, length)
    else:
        return render_template('index1.html')

@app.route("/forward/", methods=['GET','POST'])
def forward():
    lon = float(request.form['lon'])
    lat = float(request.form['lat'])
    alt = float(request.form['h'])   #Высота станции (м)

    horizon = int(request.form['hor'])
    Mh = float(request.form['Mh'])

    timeForm = request.form['time']
    length = int(request.form['length'])
    
    print('timeForm:',timeForm[0:4], timeForm[5:7], timeForm[8:10], timeForm[11:13], timeForm[14:17])
    utc_time = datetime(int(timeForm[0:4]), int(timeForm[5:7]), int(timeForm[8:10]), int(timeForm[11:13]), int(timeForm[14:17]))
    
    sorted_a = raschot(utc_time, lon, lat, alt, horizon, Mh, length)

    table = ItemTable(sorted_a)

    return table.__html__()

@app.route('/download/', methods=['GET','POST'])
def download():
    args = request.args
    sat=args.get('name')
    time=args.get('timeUp')

    lon=float(args.get('lon'))
    lat=float(args.get('lat'))
    alt=float(args.get('alt'))

    horizon=float(args.get('horizon'))

    time = datetime.strptime(time, '%Y.%m.%d %H:%M:%S')
    s=tra(sat, time, lon, lat, alt, horizon)

    return Response(
        s,
        mimetype="text/txt",
        headers={"Content-disposition":
                 "attachment; filename="+sat+".txt"})

if __name__ == '__main__':
    app.run()