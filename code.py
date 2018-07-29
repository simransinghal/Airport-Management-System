#!/usr/bin/python
#coding=utf-8
import numpy as np
import pandas as pd
import re
import os
import sys
from openpyxl import load_workbook
from xlrd import open_workbook
import operator
import datetime
import time
from datetime import *
import sqlite3
import random
import string
from tabulate import tabulate

sq = sqlite3.connect("flight_detail.db")
sqcur = sq.cursor()

def seat_number(flight_num,Class):
    val = pd.read_sql_query("Select COUNT(*) as count from Passengers where FLIGHT_NUMBER=" + flight_num, sq)
    val = int(val['count'].iloc[0]) + 1
    seat = Class + "/" + str(val)
    return seat

def generate_pnr():
    while True:
        random = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(6)])
        df = pd.read_sql_query("Select * from Passengers where PNR=" + "'" + random + "'", sq)
        if (df.empty):
            return random

def booking():
    df = pd.read_sql_query("Select DISTINCT SOURCE as FLIGHT_STATIONS from Flights", sq)
    print ("list of all the cities with airport")
    print (df)
    while True:
        command = raw_input("Press 1 to book else press 2 to exit: ")
        if (command == '2'):
            return
        elif (command != '1'):
            continue
        board_air = (raw_input("Name of boarding station: ")).upper()
        des_air = (raw_input("Name of destination station: ")).upper()
        df = pd.read_sql_query("Select Flights.* from Flights,Passengers where SOURCE=" + "'" + board_air + "'" + " AND DESTINATION=" + "'" + des_air + "'" + " AND Flights.FLIGHT_NUMBER = Passengers.FLIGHT_NUMBER Having COUNT(Passengers.FLIGHT_NUMBER) < Flights.SIZE", sq)
        if (df.empty):
            print ("No flight on this route and if it is there than no vacancy available.")
        else:
            print tabulate(df, headers='keys', tablefmt='psql')
            flight_number = raw_input("Input flight number from available flights: ")
            try:
                val = int(flight_num)
            except ValueError:
                print("Flight number should be an integer")
                continue
            df = pd.read_sql_query("Select Flights.* from Flights,Passengers where FLIGHT_NUMBER=" + flight_number + "AND Flights.FLIGHT_NUMBER = Passengers.FLIGHT_NUMBER Having COUNT(Passengers.FLIGHT_NUMBER) < Flights.SIZE", sq)
            if (df.empty):
                print ("wrong flight number or no vacancy in flight...exit")
                continue
            first_name = (raw_input("First Name: ")).upper()
            if first_name == '':
                print("Incorrect input hence exit")
                continue
            last_name = (raw_input("Last Name: ")).upper()
            if last_name == '':
                print("Incorrect input hence exit")
                continue
            Age = int(raw_input("Enter your Age: "))
            try:
                val = int(Age)
            except ValueError:
                print("Incorrect input hence exit")
                continue
            Nationality = (raw_input("Nationality: ")).upper()
            if Nationality == '':
                print("Incorrect input hence exit")
                continue
            Mobile_number = int(raw_input("Enter your MObile Number: "))
            try:
                val = int(Mobile_number)
            except ValueError:
                print("Incorrect input hence exit")
                continue
            Class = (raw_input("Enter class Either B or E: ")).upper()
            Gender = (raw_input("Enter Gender Either M or F: ")).upper()
            if (Class != 'B' or Class != 'E'):
                Class = 'E'
            if (Gender != 'M' or Gender != 'F'):
                Gender = 'M'
            values = (flight_number, first_name, last_name, Age, Nationality, Mobile_number, Gender)
            print (values)
            command = (raw_input("Press Y if all infomations are correct and want to book flight else exit: ")).upper()
            if (command == 'Y'):
                PNR = generate_pnr()
                seat = seat_number(flight_number,Class)
                values = (flight_number,PNR, first_name, last_name, Age, Nationality,'N' ,Mobile_number,seat,'N',Gender)
                sqcur.execute("INSERT INTO PASSENGER VALUES (?,?,?,?,?,?,?,?,?,?,?)", values)
                sq.commit()
                print ("sucessfully booked ticket.")

def Flight_details():
    df = pd.read_sql_query("Select DISTINCT SOURCE as FLIGHT_STATIONS from Flights", sq)
    print ("\nlist of all the cities with airport")
    print (df)
    while True:
        command = (raw_input("\nInput name of the city for which you want to see flight details else print 1 to exit: ")).upper()
        if (command == '1'):
            return
        if (command.isalpha() != True):
            continue
        df = pd.read_sql_query("Select * from Flights where SOURCE=" + "'" + command + "'" + " OR DESTINATION=" + "'" + command + "'", sq)
        if (df.empty):
            print ("No flight on this route")
        else:
            print tabulate(df, headers='keys', tablefmt='psql')

def Flight_staff():
    while True:
        sqlquery = raw_input("\nTo see passengers who cleared security checkin press 6 else press 1 to exit: ")
        if (sqlquery == '1'):
            return
        if (sqlquery != '6'):
            continue
        flight_num = raw_input("Enter flight number: ")
        try:
            val = int(flight_num)
        except ValueError:
            print("Flight number should be an integer")
            continue
        count = pd.read_sql_query("Select COUNT(*) as count from Passengers where FLIGHT_NUMBER=" + flight_num + " AND Security_Checkin='Y'", sq)
        count = count['count'].iloc[0]
        total_passenger = pd.read_sql_query("Select COUNT(*) as count from Passengers where FLIGHT_NUMBER=" + flight_num, sq)
        total_passenger = total_passenger['count'].iloc[0]
        df = pd.read_sql_query("Select PNR,First_Name,Last_Name,Gender,`Class/Seat`,Mobile_number from Passengers where FLIGHT_NUMBER=" + flight_num + " ORDER BY First_Name,Last_Name", sq)
        if (df.empty):
            print ("No passenger has cleared the security checkin with this flight number or no flight exist with this number")
        else:
            print "\nTotal number of passengers who cleared security checkin for this flight are ",count,"out of",total_passenger,"total passengers."
            print ("Passenger details")
            print tabulate(df, headers='keys', tablefmt='psql')
            sqlquery = raw_input("Type Y if want to delete this information else N: ")
            if (sqlquery.upper() == 'Y'):
                sqcur.execute("delete from Passengers where FLIGHT_NUMBER=?", flight_num)
                sq.commit()
                print ("Information is deleted successfully.")

def security_personnel():
    while True:
        sqlquery = raw_input("\nFor clearing security checkin for passengers press 6 else press 1 to exit: ")
        if (sqlquery == '1'):
            return
        if (sqlquery != '6'):
            continue
        pnr = raw_input("Enter PNR num: ")
        flight_num = raw_input("Enter flight_num: ")
        try:
            val = int(flight_num)
        except ValueError:
               print("Flight number should be an integer")
               continue
        df = pd.read_sql_query("Select * from Passengers where PNR=" + "'" + pnr + "'" + " AND FLIGHT_NUMBER=" + flight_num, sq)
        if (df.empty):
            print ("No passenger with this details.")
        else:
            print ("Passenger details")
            print tabulate(df, headers='keys', tablefmt='psql')
            sqlquery = raw_input("Type Y if all the information are correct else N: ")
            if (sqlquery.upper() == 'Y'):
                sqcur.execute("update Passengers set Security_Checkin='Y' where PNR = " + "'" + pnr + "'")
                sq.commit()
                print ("Passenger can succesfully board the flight")
            else:
                sqcur.execute("update Passengers set Security_Checkin='N' where PNR = " + "'" + pnr + "'")
                sq.commit()
                print ("Passenger cannot board the flight as not cleared security check-in.")

def passenger():
    while True:
        print ("\nPress 1 to see e-ticket of already booked flight details")
        print ("press 4 for doing web-checkin")
        print ("press 2 to exit")
        print ("press 3 for new booking")
        sqlquery = raw_input("Input: ")
        if (sqlquery == '1' or sqlquery == '4'):
            pnr = raw_input("Enter your PNR number: ")
            last_name = (raw_input("Enter your Last name: ")).upper()
            df = pd.read_sql_query("Select PNR,First_Name, Last_Name, Passengers.FLIGHT_NUMBER, SOURCE, DESTINATION, PRICE,DEPARTURE_TIME,ARRIVAL_TIME from Passengers,Flights where Passengers.FLIGHT_NUMBER=Flights.FLIGHT_NUMBER AND PNR=" + "'" + pnr + "'" + " AND Last_Name=" + "'" + last_name + "'", sq)
            if (df.empty):
                print ("No passenger with this detail")
            else:
                print ("Your Ticket details")
                print tabulate(df, headers='keys', tablefmt='psql')
            if (sqlquery == '4'):
                df = pd.read_sql_query("Select `Class/Seat` as seat from Passengers where PNR=" + "'" + pnr + "'" + " AND Last_Name=" + "'" + last_name + "'", sq)
                seat = df['seat'].iloc[0]
                sqlquery = (raw_input("\nPress Y if want to do web-checking: ")).upper()
                if (sqlquery == 'Y'):
                    sqcur.execute("update Passengers set Web_Checkin='Y' where PNR = " + "'" + pnr + "'")
                    sq.commit()
                    print "Web checkin is done succesfully your seat number is",seat
        elif (sqlquery == '3'):
            booking()
        elif (sqlquery == '2'):
            return

def Passengers_details():
    while True:
        sqlquery = raw_input("\nTo get the list and count of passengers who are either coming and going from particular station press 6 else press 1 to exit: ")
        if (sqlquery == '1'):
            return
        if (sqlquery != '6'):
            continue
        name = (raw_input("Enter airport name: ")).upper()
        count = pd.read_sql_query("Select COUNT(*) as count from Passengers,Flights where Passengers.FLIGHT_NUMBER=Flights.FLIGHT_NUMBER AND (SOURCE=" + "'" + name + "'" + " OR DESTINATION="+"'" + name + "'" +")", sq)
        count = count['count'].iloc[0]
        df = pd.read_sql_query("Select PNR,First_Name,Last_Name,Gender,`Class/Seat`,Mobile_number,Passengers.FLIGHT_NUMBER,SOURCE,DESTINATION from Passengers,Flights where Passengers.FLIGHT_NUMBER=Flights.FLIGHT_NUMBER AND (SOURCE=" + "'" + name + "'" + " OR DESTINATION="+"'" + name + "')", sq)
        if (df.empty):
            print ("No passenger has booked flight from this route no flight exist on this station name.")
        else:
            print "Total of passengers are:",count
            print ("Passenger details")
            print tabulate(df, headers='keys', tablefmt='psql')

def main():
    while True:
        command = raw_input("\nPress S if Security Personnel.\nPress F if Flight Staff.\nPress P if Passengers.\nTo know the details of all flights departing and arriving from particular airport press 1.\nList of all passengers arriving or departing from particular airport press 2.\nPress E to exit.\nInput: ")
        if (command.upper() == "E"):
            sqcur.close()
            sq.close()
            sys.exit()
        elif (command.upper() == "S"):
            security_personnel()
        elif (command.upper() == "F"):
            Flight_staff()
        elif (command.upper() == "P"):
            passenger()
        elif (command == "1"):
            Flight_details()
        elif (command == "2"):
            Passengers_details()

if __name__ == "__main__":
    main()
