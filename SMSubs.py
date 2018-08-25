# -*- coding: utf-8 -*-
"""
Spyder Editor

This is the module of def's fro Soil Moisture
"""
# print("Hello from Anaconda")
import sys
import glob
import serial
import time
import os
# import fileinput
import dropbox
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
from csv import reader
from dateutil import parser
# from dateutil import relativedelta
# import calendar

access_token = "aelnjlQMStkAAAAAAACfyW27v2oV8u5PkHnMELuOUyGbZyOhhQPsBFWt2vffTrO4"
# for db instantation

StaDictHdgs = ["Station_Name_Old", "Station_Name_New", "Snsr0_Nm", "Snsr1_Nm",
               "Snsr2_Nm", "Snsr3_Nm", "SnsrRef_Nm", "Temp_Nm", "Report H.h"]
# insert to force change
# Another change
# yet another fake change

StaID_Dict_lcl = 'StationID_lcl.csv'
StaID_Dict_db = '/StationID_db.csv'

# Note the Station name/extension makes the controller (this program) unique
# right now, you cannot have two.

# lcl_txt = 'lclfile.txt'  # local file path
# db_txt = '/DbFile.txt'  # dropbox path

lcl_pdf = 'lclfile.pdf'  # local file path
db_pdf = '/dbpdf.pdf'  # dropbox path

# There are four files:  lcltxt:lclfile.txt, lclpdf: lclfile.pdf;
# dbtxt: dbfile.txt and dbpdf:dbfile.pdf

TitleDict = {"Delm": "Delmhorst Units", "Ohms": "Ohms", "Mbars": "Millibars"}
YaxisDict = {"Delm": "Delmhorst Units", "Ohms": "Ohms", "Mbars": "Millibars"}
LegendDict = {"Delm": "DUnits", "Ohms": "Ohms", "Mbars": "Mbar"}
StartColDict = {"Delm": 2, "Ohms": 2, "Mbars": 12, "Temp": 8}
HeadingsDict = {"Time": 1, "Vbat": 7, "Temp": 8}
# current, change when format changes.


def MakeStaDict(lcl_path, db_path):
    """
    This checks for the dictionary, makes one if it doesn't exist
    writes out headings.
    Only does anything in first time after initialization.
    formal parameters unused  TODO


    """
#    print(f'makestadict; lcl_path = {lcl_path}')
    if (os.path.exists(StaID_Dict_lcl)):
        filelen = len(open(StaID_Dict_lcl).readlines())
        print(StaID_Dict_lcl + " exists, length(lines) = " +
              str(filelen))  # should be a db dict
        download_file(StaID_Dict_lcl, StaID_Dict_db)  # necessary TODO  ???
        filelen = len(open(StaID_Dict_lcl).readlines())
        print(StaID_Dict_lcl + " DropBox D/L, length(lines) = " +
              str(filelen))  # should be a db dict
        pass
    else:
        fo = open(StaID_Dict_lcl, "w")
        # opens if not already, resets pointer to beginning
        fo.write(','.join(StaDictHdgs) + '\n')
#        fo.write("Station_Name_Old,Station_Name_New,Snsr0_Nm,Snsr1_Nm,"
#                 + "Snsr2_Nm,Snsr3_Nm,SnsrRef_Nm,Temp_Nm\n")

        # TODO figure out what to do if fails to upload.  Or init
        fo.close()
        print(StaID_Dict_lcl + " Dictionary created, initialized,  & uploaded")
        filelen = len(open(StaID_Dict_lcl).readlines())  # TODO--why
        upload_file(StaID_Dict_lcl, StaID_Dict_db)
        print("Station ID Dict len = " + str(filelen))  # TODO--why
    return
# TODO: Change upload/download to db_sdk_example error tolerant versions

def upload_file(lcl_f, db_f):
    dbx = dropbox.Dropbox(access_token)
    f = open(lcl_f, 'rb')
    # TODO rewrite for failed write--returning NONE? Not hanging up.
    dbx.files_upload(f.read(), db_f, mode=dropbox.files.WriteMode.overwrite,
                     mute=True)
    f.close()
    return


def download_file(lcl_f, db_f):
    dbx = dropbox.Dropbox(access_token)
    f = open(lcl_f, 'w')    # overwrites local file
    dbx.files_download_to_file(lcl_f, db_f)
    f.close()
    return


def get_time():
    # t = time.localtime(time.time)
    now = datetime.now()
    strnow = now.strftime("%m/%d/%y %H:%M")
    # format to make sheets, whatever work
    # print (strnow)
    return strnow


def Mx_B(Rx, RL, RH, BarL, BarH):
    # //note r0, r1 in ohms, bar1, bar0 in actual Bar *10
    # //also used for the Delm calc--which has neg slope
    if (Rx > RH):
        retval = 0
    else:
        denom = RH-RL
    if (denom == 0):
        denom = 1  # //shouldn't happen
    if BarH >= BarL:
        retval = ((BarH-BarL) * (Rx-RL)) / denom + BarL
    num = BarH - BarL
    if BarH < BarL:
        retval = BarL - (((BarL - BarH) * (Rx - RL)) / denom)
    #    num = (BarL-BarH)

    return retval


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
        : left in (rpm) for portability to RPi

        : see https://www.dropbox.com/developers-v1/core/start/python
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i) for i in range(2, 25)]
# Start at COM2--COM1 on Windows is bogus.
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
        # TODO Jeez, Louise--this is 26 * 26 to go thru?  Talk about overkill
        # RPi has alais serial0 and serial1???
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


def trimfile(f, xdays):
    """
    finds the last time stamp in file f (the master file)
    returns a file ftrim that starts xdays before the last time stamp, ends
    with last time stamp.
    if there is no timestamp xdays back, returns the entire file f
    trimfile is a working file.  Not archived.  The master file (f)
    is the only one archived

    """
#    print(f'in ftrim , filename = {f} days = {xdays}')
    with open(f, 'r') as fr:
        xlines = reader(fr)
        iline = 0
        for L in xlines:
#            print(f'L = {L}')
            if iline > 0:    # skip over header
                last_time = L[HeadingsDict["Time"]]
            iline += 1      # can do with enumerate--save variable
        if (iline <= 1):
            print("bailing out of ftrim!!!")
            return fr
        lstimeobj = datetime.strptime(last_time, "%m/%d/%y %H:%M")
        first_time = lstimeobj - timedelta(days=xdays)

    with open("ftrim.csv", 'w') as fw:
        with open(f, 'r') as fr:
            xlines = reader(fr)
            iline = 0
            for L in xlines:
                # print ("searching for first time", L )
                if (iline == 0):
                    fw.write(','.join(L)+'\n')
                    # print ("first line, ", L)
                else:
                    if datetime.strptime(L[HeadingsDict["Time"]],
                                         "%m/%d/%y %H:%M") > first_time:
                        # print ("short file")
                        # return f
                        fw.write(','.join(L)+'\n')

                iline += 1

    return "ftrim.csv"

def plotSM(Param, IDs,  FileName, pdf_base, xdays):
    # TODO add in a days parameter in the call. Also filename
    # TODO label plot = Station Name == filename w/o extension
    # TODO change the plot labels to the StaDict headings
    """
    Produces a plot starting at end of file time stamp (most recent entry)
    (time stamp format 04/19/18 13:41
     back for xdays. The (pdf) plot is named:
     "SM_Param_ndays.pdf" and stored locally and on dropbox.

    Param = String such as Delm, Ohms, Mbars (currently not used)
    Param is only used to label the plot
    IDs is a list == dictionary entry for this file
    FileName = name of local .txt file with Data in it.
    (csv): Station Name, TimeStamp,Data0, Data1, Data2, Data3, Vbat, Temp

   Example: plotSM("Ohms", "localdat.txt", "Marsanne", 3)
   would go to localdat.txt file  (which is actually a csv)
   go back three days, create a pdf plot of labeled "Ohms"
   create or overwrite file labeled Marsanne_3_days.pdf;
   stored locally and pushed to DB
    TODO--put in error handling in case lclfile is corrupted.

    """
#    print(f'Param ={Param}, IDs ={IDs}, FileName = {FileName}, \
#          pdf_base ={pdf_base}, xdays = {xdays}')
    with open(FileName, 'r') as f:
        xlines = reader(f)
        iline = 0
        for L in xlines:     # count lines,

            if iline > 0:            # skip over header
                last_time = L[HeadingsDict["Time"]]
                last_Vbat = L[HeadingsDict["Vbat"]]
                last_temp = L[HeadingsDict["Temp"]]
            iline += 1

    with open(trimfile(FileName, xdays), 'r') as ftrim:
        data = list(reader(ftrim))
# must strip .txt off FileName--else it gets used.
    FileBase = str(FileName.split('.')[0])
    titleTmStamp = f'{last_time}  {last_temp}(C) {last_Vbat}V'
    titleID = f'{FileBase} (last {xdays} days)'


#    titleTmStamp = (last_time + ' ' + last_temp + "(C) " + last_Vbat + 'V ')
#    titleID = FileName + " last " + str(xdays) + " days"

# set up plot
    fig, ax1 = plt.subplots()
    ax1.set_xlabel(titleTmStamp, color="orange")
    ax1.set_ylabel(YaxisDict[Param], color="blue")
# TODO--this only works for ohms; need to have an ohms adjust?
# TODO--make an Ohms adjust routine.  Keep raw and adjusted?
    tfact = .064     # temperature offset factor
    toff = 23
    plt.title(titleID, fontsize=12, weight="bold", color="blue")
    # pyplot.axis('auto')
    # plt.grid(True)
    # plt.xticks(rotation=45)

    col = StartColDict[Param]
#    print ("col = ", col)
    tcol = StartColDict["Temp"]
#    print ("temp col = ",tcol)
    #tfact = .06
    #t0 = 27--original equation used 23C might want to fiddle.
    #but t0=27 and tfact = .04 seems to work pretty well.

    Line0 = [float(i[col])/(1+tfact*(toff-float(i[tcol])))
             for i in data[1::]]
#    print ("line0= ", Line0)
    Line1 = [float(i[col+1])/(1+tfact*(toff-float(i[tcol])))
             for i in data[1::]]
#    print ("line1= ", Line1)
    Line2 = [float(i[col+2])/(1+tfact*(toff-float(i[tcol]))) for i in data[1::]]
#    print ("line2= ", Line2)
    Line3 = [float(i[col+3])/(1+tfact*(toff-float(i[tcol]))) for i in data[1::]]
#    Line1 = [float(i[col+1]) for i in data[1::]]
#    Line2 = [float(i[col+2]) for i in data[1::]]
#    Line3 = [float(i[col+3]) for i in data[1::]]
    Temp = [float(i[StartColDict["Temp"]]) for i in data[1::]]
    # print ('temp = ' + Temp)
    time = [parser.parse(i[1]) for i in data[1::]]
    mx = 2      # markersize
    plt.xticks(fontsize=8, rotation=45)
    plt.yticks(fontsize=8, color="red")

    ax1.grid(linestyle='-', linewidth='0.5', color='red')
    ax1.grid(True)

    if (IDs['Snsr0_Nm'] != "None"):
        ax1.plot(time, Line0, "ro-", label=IDs['Snsr0_Nm'], markersize=mx)
    if (IDs['Snsr1_Nm'] != "None"):
        ax1.plot(time, Line1, 'gx-', label=IDs['Snsr1_Nm'], markersize=mx)
    if (IDs['Snsr2_Nm'] != "None"):
        ax1.plot(time, Line2, 'b^-', label=IDs['Snsr2_Nm'], markersize=mx)
    if (IDs['Snsr3_Nm'] != "None"):
        ax1.plot(time, Line3, 'ms-', label=IDs['Snsr3_Nm'], markersize=mx)

    ax2 = ax1.twinx()
    ax2.set_ylabel('Temp(c)', color="yellow")
    ax2.set_ylim(15, 30)
    plt.yticks(fontsize=8, color="yellow")
    plt.plot(time, Temp, 'yx--', label=IDs['Temp_Nm'], markersize=mx)
    # plots, but need twinx() assigned

    ax1.legend(loc=2, prop={'size': 8})
    ax2.legend(loc=1, prop={"size": 8})

    lcl_pdf_file = pdf_base + "_" + str(xdays) + ".pdf"
    db_pdf_file = "/" + lcl_pdf_file
#    print("lcl_pdf_file = " + lcl_pdf_file)
#    try:
#        os.remove(lcl_pdf_file)
#    except OSError:
#        print(lcl_pdf_file + " already exists; should not happen")
#        pass
    plt.savefig(lcl_pdf_file, facecolor="g", transparent=False,
                bbox_inches="tight")
#    print('problem, blows up if exists.  Open for write?')
    upload_file(lcl_pdf_file, db_pdf_file)
    plt.close('all')
    # fig.close   ???? getting wornings about too many figs open

    return


def newplotSM(Param, filenam, ndays):   # Param, filenam strings, days int

    """
    Param = String such as Delm, Ohms, Mbars
    filenam = name of local file with the parameter to be plotted in it.
    Main does conversion.  "Param" is passed for labelling and file naming purposes.
	filenam format (csv): Station Name, TimeStamp,Item0, Item1, Item2, Item3, ItemRef, Vbat, Temp
	This sub produces a plot that extends from the end of file time stamp
	(most recent entry) back for ndays. The (pdf) plot is named:
		"SM_Param_ndays.pdf" and stored locally and on dropbox.
	For instance, a call of newplotSM("Ohms", "localdat.txt", 3) would go to localdat.txt file
	go back three days, create a pdf plot of Ohms for the last three days (or start of file, if not that long)
	create or overwrite a file named SM_Ohms_3_days.pdf; which is stored locally and pushed to DB
    The title of the File is "%Param %ndays %timedate".  i.e Ohms 3 days 01/02/18 03:04:05
	"filenam" only has ohms.  Delm , Mbars, etc. have to be called.

    """
    datacol = 2     #data starts in col 2
    tempcol = 8     #temp in col 8
    with open (filenam, 'r') as f:          #filenam has to be created and made correct by SMmain
        data = list(reader(f))
#list data is a list with everything in it    #print("data = ",data)

#set up plot
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Time')
    # ToDo  !!! lost Time off the plot  Can't see iot
    ax1.set_ylabel(Param, color="blue")
    plt.title((Param + ' ' + get_time()) + " days== " +
              str(ndays), fontsize=12, weight="bold", color="red")
    plt.grid(True)
    # plt.xticks(rotation=45)

    # This is simply a plotting routine, has no awareness

    Line0 = [float(i[datacol]) for i in data[1::]]
    Line1 = [float(i[datacol+1]) for i in data[1::]]
    Line2 = [float(i[datacol+2]) for i in data[1::]]
    Line3 = [float(i[datacol+3]) for i in data[1::]]
    Temp = [float(i[tempcol]) for i in data[1::]]
    # print ('temp = ' + Temp)

    timex = [parser.parse(i[1]) for i in data[1::]]
    mx = 2      # markersize
    plt.xticks(rotation=45)
    ax1.grid(linestyle='-', linewidth='0.5', color='red')
    ax1.grid(True)

    ax1.plot(timex, Line0, "ro-", label=(LegendDict[Param]+"0"), markersize=mx)
    ax1.plot(timex, Line1, 'gx-', label=(LegendDict[Param]+"1"), markersize=mx)
    ax1.plot(timex, Line2, 'b^-', label=(LegendDict[Param]+"2"), markersize=mx)
    ax1.plot(timex, Line3, 'ms-', label=(LegendDict[Param]+"3"), markersize=mx)

    ax2 = ax1.twinx()
    ax2.set_ylabel('Temp(c)')
    ax2.set_ylim(15, 25)
    plt.plot(timex, Temp, 'yx--', label="Temp(C)", markersize=mx)
    # plots, but need twinx() assigned

    ax1.legend(loc=2, prop={'size': 8})

    try:
        os.remove(lcl_pdf)
    except OSError:
        print(lcl_pdf + " already exists; should not happen")
        pass
    plt.savefig(lcl_pdf, facecolor="g", transparent=False)
    # problem, blows up if exists.  Open for write?
    upload_file(lcl_pdf, db_pdf)
    plt.close

    return
