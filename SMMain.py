# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 07:55:41 2018

@author: Rich
"""
# import sys
# import glob
# TODO This is a comment to test out GitHub stuff
# TODO This is a change made on git hub????
# TODO--this is being done in "new_master" branch
# locally (i think); can we push and merge????
import contextlib
import serial
import time
import os
from decimal import Decimal
# import in_place
import fileinput
# import dropbox
from datetime import datetime, timedelta
# import datetime, timedelta
# from matplotlib import pyplot, dates
import csv
# from dateutil import parser
from shutil import copyfile
# from sys import exit

import SMSubs
serial_ports = SMSubs.serial_ports
get_time = SMSubs.get_time
# local_file = SMSubs.lcl_txt
StaDict_lcl = SMSubs.StaID_Dict_lcl
StaDict_db = SMSubs.StaID_Dict_db
StaRespHdgs = ['StaID', 'Sns0', 'Sns1', 'Sns2', 'Sns3',
               'SnsRef', 'Vbat', 'Temp']
DataFileFldCnt = len(StaRespHdgs)-1 # will be used by counting commas
# TODO  Add in BCC fld
# to make dict out of Station Response
StaDictHdgs = SMSubs.StaDictHdgs
DataFileHdgs = ['Station', 'DateTime', 'Ohms0', 'Ohms1', 'Ohms2', 'Ohms3',
                'OhmsRef', 'Vbat', 'Temp']
# this is comment in VC studio editor to force change
AlmMin = 2  # alrm delay in minutes
AlarmDelay = round(Decimal(AlmMin/60), 3)      # TODO alarm Delay in hours--later read from DB File
PrintTimes = False


def ser_wrt(Com, wrtstr):
    '''
    write wrtstr to Com"
    has character by character delay--poor

    '''

    try:
        ser = serial.Serial(Com, baudrate=9600, timeout=None)
    except serial.SerialException as e:
        print(f"could not open serial port '{Com}': {e}")
        return False
    wrtlist = list(wrtstr)
    for num, char in enumerate(wrtlist):
        # print(f"num = {num}, char = {char}")
        ser.write(char.encode())
#        written = num
        time.sleep(.015)
#        inchar = ser.read()
#        print(f'read char ={inchar}' ) # echo it
#        i = 0
#        while i < 100000:
#            i = i + 1
    # written = ser.write(wrtstr.encode(encoding="utf-8"))
#    ser.write(b'\n')
#    print(f'ser_wrt wrote {written+1} bytes')
    ser.close()
    return True
# ???? there may be more error checking on write??


def makefile(fpath):
    """ checks for existence of file at path
        if there, returns
        if not, creates

    """


def GetLine(COM, howlong):
    """
    Opens port COM
    waits until how long has elapsed
    min string len should be 3--"AOK"
    if <3, had to be timeout, returns "AWOL"
 # TODO --make str len a parameter ?????
    strips comments (start with //)

    """
    at0 = time.time()
    goodline = False
    # ser.timeout = 1
    if howlong is 0:
        howlong = None
    try:
        ser = serial.Serial(COM, baudrate=9600, timeout=howlong)
    except serial.SerialException as e:
        print(f"could not open serial port '{COM}': {e}")
        return "None"

    while not goodline:
        at0 = time.time()
        lineraw = (ser.readline().decode(encoding='UTF-8',
                   errors='ignore'))
        at1 = time.time()
        if (PrintTimes):
            print(f'Elapsed time for readline: {at1-at0}')
        # Note--if timeout min len is 1--\n
        # errors= 'ignore'--means ignore undecodeable characters
        line = lineraw.replace('\x00', '')  # necessary?
        # TODO add error checking; such as BCC
#        print(f"line in getline {line}")
        if(len(line) < 1):     # timeout --len = 1
            # print(f"short/timeout; line = {line}, length = {len(line)}")
            return "AWOL"
        if (len(line) > 1):   # why 1 vs 2 --- throw out excess \n
            goodline = True
            # leave most error checking to main
    ser.close
    return line


def GetNewbie():
#    print ("Start GetNewbie")
    if ((len(open(StaDict_lcl).readlines())) == 1):
        # print("first dict entry--no search")
        return "Newbie_1"   # only called if "newbie", this is first entry
# TODO  This makes no sense!!!!!!!!!!!!!--Or, does it?????
    i = 1
    max = 5
    foundentry = True
    while(i <= max) and (foundentry == True):
        StaAdrX = "Newbie_" + str(i)
#        print("trying StaArX = " + StaAdrX)
        with open(StaDict_lcl) as csvfile:
            reader = csv.DictReader(csvfile)
            foundentry = False
            # print ("got here in newbie")
            # print ("searching for " + StaAdrX)
            for row in reader:
#                print(f"row in csvreader ={row['Station_Name_Old']}; StaAdrX = {StaAdrX}")
                if (row['Station_Name_Old'] == StaAdrX):  # already used
                    foundentry = True
#                    print(f"foundentry (inside for) = {foundentry}")
#            print(f"foundentry = {foundentry}")
            i += 1
    # print("leaving GetNewbie = " + StaAdrX)
    return StaAdrX

def ReplaceInFile(FilePath, Old, New):
    """
    Goes through file at FilePath, line by line, and replaces any occurencs of
    string Old with string New.  It creates new file temp--copies
    over with changes.  Then removes (os.remove) FilePath and renames temp
    to FilePath
    """
#    print(f'FilePath = {FilePath}, Old = {Old}, New = {New})\n')
    fin = open(FilePath)
    fout = open("temp.txt", "wt")
    for line in fin:
#        print((f'line in .csv before change {line}\n'))
#        print((f'line in .csv after .replace{line.replace(Old, New)}\n'))
        fout.write(line.replace(Old, New))
#        print((f'line in .csv after change {line}\n'))
    fin.close()
    fout.close()
    os.remove(FilePath)
    os.rename("temp.txt", FilePath)
#    os.remove("temp.txt")


def tellStation(dictentry, alrmmin):
    """
    Station thinks its address is curAdr; this function tells the Station
    its new address is NewAdr.  It also tells it current time and time
    to send next report.  Example:
    "Newbie, Newbie_1, Oct 25 2017 18:35:33,Oct 25 2017 18:35:43, BCC"
    Station Responds with normal report, but uses NewAdr = Newbie_1
    This function waits for response before updating dictionary & files
    Returns True if successful (Station responds with correct address)
    False if not.
    StaDictHdgs = ["Station_Name_Old", "Station_Name_New", "Snsr0_Nm",
                   "Snsr1_Nm", "Snsr2_Nm", "Snsr3_Nm", "SnsrRef_Nm", "Temp_Nm"]
    """
#    print(f"Dictentry = {dictentry}")
    CurAdr = dictentry['Station_Name_Old']
    NewAdr = dictentry['Station_Name_New']
    now = datetime.now()
    arpt = (Decimal(dictentry['Report H.h'])*60)
#    print(f"type of rpt {arpt} {type(arpt)}")
    arpt = int(round(arpt))  # should go to nearest
#    print(f'(tellStation), report time = {arpt}')

    strnow = now.strftime("%b %d %Y %H:%M")
#    print("now time =", strnow)
    alarm = now + timedelta(minutes=arpt)

    stralarm = alarm.strftime("%b %d %Y %H:%M")
#    print("alarm time = ", stralarm)
    outstr = f'{CurAdr},{NewAdr},{strnow},{stralarm},0\r'  # make a byte str
#    print(f"outstr to be sent = {outstr}")
#    time.sleep(5)
    ser_wrt(COM, outstr)  # if Station responds AOK, update
    StaResp = GetLine(COM, 50)    # sb "AOK"; "AWOL" if no response
#    print(f"Immediate Station Response is {StaResp}")
    if "AOK" in StaResp:
        # change cur adr to new adr--sort of unconditional.
        print(StaResp)
        if (CurAdr != NewAdr):
            ReplaceInFile(StaDict_lcl, CurAdr, NewAdr)
            print(f" Station Name changed from {CurAdr} to {NewAdr}")
#        with fileinput.FileInput(StaDict_lcl, inplace=True) as f:
#            for line in f:
#                print(line.rstrip().replace(CurAdr, NewAdr))
#        f.close()   # necessary?
        SMSubs.upload_file(StaDict_lcl, StaDict_db)
    elif "AWOL" in StaResp:
        print(StaResp)
    else:
        print(f'Unknown Resp: {StaResp}')
    return StaResp


def MakeDictEntry(StaAdr):
    """
    chks for/makes dictionary entry in _lcl
    returns dict entry list

    """
# At program init, this StaDict was formed.
    entryfound = False
#    print(f'StaAdr in makedict = {StaAdr}')
    with open(StaDict_lcl) as fr:
        for num, row in enumerate(fr):
            if(num == 0):     # headings row
                pass
            else:
                # print(f' num = {num}, row = {row}')
                dictsplit = row.split(',')
#                print(f'dictsplit = {dictsplit}')
                dictline = dict(zip(StaDictHdgs, dictsplit))
                if (dictline["Station_Name_Old"] == StaAdr):
                    entryfound = num    # FWIW, could be True
#                    print(f'in makedict dictline (existing) = {dictline}')
                    # no need to update db file--no change
                    return dictline
# There is never a "Newbie" in the Dict.  Need to find the next Newbie_N
    if not entryfound:  # ???? not in dict,make new entry (file also?)
        if (StaAdr == "Newbie"):
            StaAdr = GetNewbie()
        with open(StaDict_lcl, "a+") as fo:
#            outstr = ("{},{},{},{},{},{},{},{},{:.3 ".format(StaAdr, StaAdr,
#                      "Snsr0_Nm", "Snsr1_Nm", "Snsr2_Nm", "Snsr3_Nm",
#                      "SnsrRef_Nm", "Temp_Nm\n"))
            outstr = (f'{StaAdr},{StaAdr},Snsr0_Nm,Snsr1_Nm,Snsr2_Nm,'
                      f'Snsr3_Nm,SnsrRef_Nm,Temp_Nm,{AlarmDelay}\n')
#            outstr = f'','join(S)   '
            print(f"New station dictionary entry = {outstr}")
            fo.write(outstr)
# have dictionary entry, new or created
# cannot update files until Station has been told and responded.
        dictline = dict(zip(StaDictHdgs, outstr.split(',')))
        SMSubs.upload_file(StaDict_lcl, StaDict_db)     # upload it to DB
        print(f'dictline at new entry creation ={dictline}')
        return dictline

def makefiles(dictline):
    """ makefiles(dictline) checks for/creates local/db files named for entry
    # first, checks for local file named for Station Old--s.b. same as Station
    New.  If doesn't exist, make a local and db file of that name +.txt
    returns a list with 'old', 'new' names

    StaDict has been updated already all to do is make datafile
    if dict[0] != dict[1], rename file to dict[0] name
    StaDictHdgs = ["Station_Name_Old", "Station_Name_New", "Snsr0_Nm", "Snsr1_Nm",
               "Snsr2_Nm", "Snsr3_Nm", "SnsrRef_Nm", "Temp_Nm"]
    """
    filenm = dictline['Station_Name_Old']+'.txt'
#    print(f"in makefiles, dictline = {dictline}")
#    print(f'file name = {filenm}')

#    filenmnew = dictline['Station_Name_New']+'.txt'

    if(os.path.exists(filenm)):
        # if this is first time, filenm doesn't exist
        # filelen = len(open(newnm).readlines())
        # print(f'filename {filenm} exists')
        if(dictline['Station_Name_Old'] != dictline['Station_Name_New']):
            # have had a name station change
            oldnm = dictline['Station_Name_Old'] + '.txt'
            newnm = dictline['Station_Name_New'] + '.txt'
            print(f'name change from {oldnm} to {newnm}')
        # adding exception handling
            try:
                copyfile(oldnm, newnm)
                dictline['Station_Name_Old'] = dictline['Station_Name_New']
                print('copied....')
                return newnm
            except IOError as e:
                print("Unable to copy file. %s" % e)
                return "Error"
#                exit(1)
        else:
            return filenm

    else:

        fo = open(filenm, "w")     # creates and opens
        fo.write(','.join(DataFileHdgs) + '\n')
#        fo.write("Station, DateTime, Ohms0, Ohms1, Ohms2, Ohms3," +
#                 " OhmsRef, Vbat, Temp\n")
        fo.close()
        print(f"file {filenm}  created & header written")
        return filenm  # done--created new data file
# we have an existing file
    print('why are we returning should not???')
    return "Should Not"


@contextlib.contextmanager
def stopwatch(message):
    """Context manager to print how long a block of code took."""
    t0 = time.time()
    try:
        yield
    finally:
        t1 = time.time()
        print('Total elapsed time for %s: %.3f' % (message, t1 - t0))
        return


def make_resp_dict(line):
    """ takes string line splits into list on ','
        zips with StaHdsDict
        StaRespHdgs = ['StaID', 'Sns0', 'Sns1', 'Sns2', 'Sns3',
        'SnsRef', 'Vbat', 'Temp']
        to make dict with values
    """
    linelist = line.split(',')
    return dict(zip(StaRespHdgs, linelist))


if __name__ == '__main__':
    # see http://ibiblio.org/g2swap/byteofpython/read/module-name.html
    comlist = serial_ports()
    ser = serial.Serial(comlist[0], 9600)   # change:  [0] s.b. 1st
    COM = ser.port
    print("Hello, World. Connected to " + COM + ' @ ' + get_time())
    ser.close()  # close if not needed
    # insert to force change
    SMSubs.MakeStaDict(StaDict_lcl, StaDict_db)  # in case there is none

    while 1:
        # At this point, the only acceptable response is a station response
        # if not at least DataFileFldCnt fields, ignore?.
        # could be more if commas in Station Names???

        fldcnt = 0
        while fldcnt < DataFileFldCnt:
            staline = GetLine(COM, None)  # None is forever (blocking)
            fldcnt = staline.count(',')
            # TODO-- this is where to put in BCC check
            if (fldcnt) < DataFileFldCnt:  # Got an invalid response
                # could be AWOL
#                print(f'Not enough flds; = {fldcnt}; should be {DataFileFldCnt}')
                print(f'\n{staline}', end ='')
#                bstr = staline.encode('utf-8').hex()
#                print(f'Bad Response = 0X {bstr}\n')
                fldcnt = 0  # not necessary
            
        # Got a response with enough fields;
        t0 = time.time()  # for timing
        SMSubs.download_file(StaDict_lcl, StaDict_db)  # This needs to be done
        te = time.time()-t0
#        print(f'Dictionary download time = {te}')
# in parallel with GetLine. Station is hung up dring download TODO
# TODO--how to recover from not being able to access DropBox/
# --handle in upload/download?

        StaLine_dict = make_resp_dict(staline)
        # makes dict from comma delimited string
        dictline = MakeDictEntry(StaLine_dict['StaID'])  # chks/creates entry
        # returns dict list; station names not updated yet
        # print(f'MakeDictEntry returned {dictline}' )
        te = time.time()-t0
#        print(f'after MakeDictEntry time = {te}')
        tellStation(dictline, AlarmDelay)   # tells Station to update, if new
        # second param is alarm time delay from current time
        # updates StaDict_lcl ONLY if Station says AOK
        # dictadr[0] is now last vestige of old address?
        te = time.time()-t0
#        print(f'after tellStation time = {te}')
        DataFileNm = makefiles(dictline)  # chks for/creates local/db files entry
        # makefiles returns a list = to names, headings, etc.

        # TODO deletes if we can figure out how to do it.  Linux, maybe

        local_file = DataFileNm         #
#        print(f'local file to be appended = {DataFileNm}')
        db_pdf_base = '/' + local_file
        with open(local_file, "a+") as fo:
            # open for append, create if not existing
            # TODO  clean this up--open file once, with, etc.
            if len(staline) > 2 and staline[0] != "/":
                # TODO This check should no longer be required???
                # Station block sends newlines--ignore and ignore comments
                linelist = []
                linelist = staline.split(',')   # print (linelist)
                linelist.insert(1, get_time())  # print (linelist)
                line = ",".join(linelist)    # print (line)
                print('latest report:', line, end='')
                fo.write(line)
        # have to reset line ptr to zero?
                filelen = 0
                fo.seek(0)      # go back to beginning
                for xline in fo:
                    filelen += len(xline)
#                print("            ****break for readability--not in file; " +
#                      "file length = " + str(filelen) + "  *********")
        te = time.time()-t0
#        print(f'after append time = {te}')
        SMSubs.upload_file(local_file, ("/" + local_file))  #store raw data?
        te = time.time()-t0
#        print(f'after upload time = {te}')
        # FIXME make two local files--raw ohms & temp corrected ohms
        # FIXME conversions to millibars, etc. off of raw ohms
        #
        lfstrip = local_file.split('.')[0]
#        print(f'local file = {local_file}, .split = {lfstrip}')
        SMSubs.plotSM("Ohms", dictline,  local_file,
                      local_file.split('.')[0], 3)    # stores in locally
