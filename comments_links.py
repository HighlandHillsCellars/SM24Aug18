# -*- coding: utf-8 -*-
"""

On start, check for the existence of a file "StationDict.csv"  If it doesn't 
exist, create it and write the header line
StaID,StaID_new, DateTime, Sns0, Sns1, Sns2, Sns3, SnsRef, Vbat, Temp

When a station reports with, for example, ID of Newbie, use csv.DictReader
csvdictfile = csv.DictReader(open("StationDict.csv"))
remoteID = RemoteID  #(string)
string
for entry in csvdictfile:
    if entry[StaID] = remoteID:




https://courses.cs.washington.edu/courses/cse140/13wi/csv-parsing.html
Created on Thu Apr 12 12:58:09 2018
Usage of csv.DictReader
CSV, or "comma-separated values", is a common file format for data.
The csv module helps you to elegantly process data stored within a CSV file.
Also see the csv documentation.

This guide uses the following example file, people.csv.

id,name,age,height,weight
1,Alice,20,62,120.6
2,Freddie,21,74,190.6
3,Bob,17,68,120.0
Your Python code must import the csv library.

import csv
Open the file by calling open and then csv.DictReader.

input_file = csv.DictReader(open("people.csv"))
You may iterate over the rows of the csv file by iterating ove input_file. (Similarly to other files, you need to re-open the file if you want to iterate a second time.)

for row in input_file:
    print row
When you iterate over a normal file, each iteration of the loop produces a single string that represents the contents of that line. When you iterate over a CSV file, each iteration of the loop produces a dictionary from strings to strings. They keys are the names of the columns (from the first row of the file, which is skipped over), and the values are the data from the row being read. For example, the above loop prints the following:

{'age': '20', 'height': '62', 'id': '1', 'weight': '120.6', 'name': 'Alice'}
{'age': '21', 'height': '74', 'id': '2', 'weight': '190.6', 'name': 'Freddie'}
{'age': '17', 'height': '68', 'id': '3', 'weight': '120.0', 'name': 'Bob'}
To print the entire contents of the DictReader, you might execute the following code:

Finally, here is a complete example usage of csv.DictReader using people.csv. This example finds the oldest person within the file and that person's age.

import csv

input_file = csv.DictReader(open("people.csv"))

max_age = None
oldest_person = None
for row in input_file:
    age = int(row["age"])
    if max_age == None or max_age < age:
        max_age = age
        oldest_person = row["name"]

if max_age != None:
    print "The oldest person is %s, who is %d years old." % (oldest_person, max_age)
else:
    print "The file does not contain any people."
And the output from this program:

The oldest person is Freddie, who is 21 years ol

Links
https://www.tandfonline.com/doi/full/10.1080/23311916.2016.1251729 (equations/approach for conversion to pressure)

see: https://www.dropbox.com/s/95fjeq5ib250se1/GypsumTemp.pdf?dl=0
for temp equation

********************************************************************************************************


@author: Rich
"""

