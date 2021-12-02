# -*- coding: utf-8 -*-
"""
Need to implement other protocols to login, in case phone number is not there
Also phone number data is messy need to clean it up and reupload to database

"""
import unittest

import sys
from datetime import datetime

import logging 
import time

from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QMessageBox
from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem, QMainWindow, QStackedWidget, QPushButton,QHBoxLayout, QLabel, QCheckBox
from PyQt5.QtCore import pyqtSlot, QDate, QTime, QDateTime, Qt, QThread, QTimer


#set up the widget class for this stacked page

#%% Functions -> Might move into utility function repo
def my_round(x,nearest):
    #returns to the nearest int so if 4 then quarter, 2 is half
    return int(round(x*nearest)/nearest)

def convert_hrs_units(hrs):
    return hrs*4

#%% classes
class ParticipantModel():
    
    """retrieves query values for participant"""
    def __init__(self):
        self.con = None
        self.my_cursor = None

    def connect_to_db(self):
        """
        connect to db returns the sql goldenhearts db

        Returns
        -------
        sql_connector : database

        """
        #connnect to sql database SEND THIS AS A UTIL FUNCTION OR SOMETHING
        sql_connector = mysql.connector.connect(user='root', password='Colts1704',
                        host='127.0.0.1',
                        database='goldenhearts')
        
        return sql_connector

    def number_exists_query(self,member_number):
        """
        check_member submits a query based on phone number of member and returns the connector
        and result
        
        Returns
        -------
        con : mysql connector
        
        result : INT
            DESCRIPTION: participant id 

        """
        self.con = self.connect_to_db()
        #need to buffer cursor commands
        self.my_cursor = self.con.cursor(buffered=True)
        #submit query for phone number and validate check in
        sql_query = "SELECT ParticipantID FROM contact WHERE PhoneNumber ='%s'" % (member_number)
        self.my_cursor.execute(sql_query)
        query_return = self.my_cursor.fetchone()
        if query_return != None:
            participant_id = str(query_return[0])
            return participant_id
        else:
            return None

    def request_id_query(self, phone_number):
        self.con = self.connect_to_db()
        #need to buffer cursor commands
        self.my_cursor = self.con.cursor(buffered=True)
        self.my_cursor.execute("SELECT ParticipantID FROM contact WHERE PhoneNumber='%s'" %(phone_number))
        #submit query for phone number and validate check in

        id_num = self.my_cursor.fetchone()
        
        self.my_cursor.execute("SELECT FirstName,LastName FROM participant WHERE ParticipantID='%s'" %(id_num))
        rows = self.my_cursor.fetchone()

        if rows: 
            print("true")
            first_name = rows[0]
            last_name = rows[1]
            
            return first_name, last_name
        
        else:
            first_name = None
            last_name = None
            print("No member detected")
            return first_name, last_name

    def check_duplicate_checkin(self, participant_id):
        """check if member has already checked in SQL, inputs is string participant id"""
        print('participant id', participant_id)
        self.my_cursor = self.con.cursor(buffered=True)
        self.my_cursor.execute("SELECT * FROM checkin WHERE  ParticipantID='%s' AND CheckOutTime IS NULL" % (participant_id))
        self.con.commit()
        dup_exists_query = self.my_cursor.fetchone()
        
        return dup_exists_query

    def checkin_query(self, participant_id, timein):
        """check the participant into MYSQL database with respective id and time"""
        self.sql_query = """INSERT INTO checkin (ParticipantID,CheckInTime) VALUES (%s,%s)"""
        self.my_cursor.execute(self.sql_query, (participant_id, timein))
        self.con.commit()

    def checkout_member(self,participant_id, time_in, timeout):
        time_in = time_in[0]
        hrs, units = self.calculate_time_difference(time_in, timeout)
        self.my_cursor.execute("""
            UPDATE checkin 
            SET ParticipantID=%s, 
            CheckOutTime=%s,
            Hours=%s,
            Units=%s
            WHERE ParticipantID=%s AND CheckOutTime is NULL
            """, (participant_id, timeout, hrs, units, participant_id))    
        self.con.commit()

    def duplicate_checkout_query(self, participant_id, timeout):
        """check if user has clicked on checkout repeatedly, if none then we have no information"""
        self.my_cursor.execute("SELECT CheckInTime FROM checkin WHERE  ParticipantID='%s' AND CheckOutTime IS NULL" % (participant_id))
        time_in = self.my_cursor.fetchone()

        if time_in == None:
            return True, time_in
        else:
            return False, time_in

    def calculate_time_difference(self,time_in, timeout):
        """calculate the time  difference  between time in and time out and converts to int hours
        """
        #print("time difference calc", time_in, timeout)
        delta = (timeout - time_in).total_seconds()/3600
        delta = my_round(delta,4)
        units = convert_hrs_units(delta)
        print('delta time difference', delta, units)

        return delta, units


class MemberLogin(QWidget):
    """Controls and Views the widgets for member login"""
    def __init__(self):
        #inherit original class properties 
        super(MemberLogin,self).__init__()
        loadUi("resources/member_checkin.ui",self)
        self.model = ParticipantModel()

        #member buttons
        self.checkin_btn.clicked.connect(self.checkin_mem)
        self.checkout_btn.clicked.connect(self.checkout_mem)
        #self.return_btn.clicked.connect(lambda:ui_utils.go_to_screen(Ui_MainWindow,widget))

    def checkin_mem(self):
        """
        login member submits query to golden heart checkintable database for participant id based on phone number
        checks if the user has already established a connection and if so 
        """
        phone_number = self.phone_number_entry.text()
        id_num = self.model.number_exists_query(phone_number)
        #phone_number, id_num, time_in = self.retrieve_inputs()
        self.validate_inputs(phone_number, id_num, "Checked In")

    def checkout_mem(self):
        """
        Checkout mem function submits query to goldenheart checkin table database for participant id based on phone number
        where they have not checked out on that specific date and stamps a check out time accordingly   
        """
        #enter user phone number in the qline entry text also need to put a parser 
        phone_number, id_num, timeout = self.retrieve_inputs()
        self.validate_inputs(phone_number, id_num,"Checked Out")

        bool_dup, time_in = self.model.duplicate_checkout_query(id_num,timeout)
        if bool_dup:
            self.error_msg.setText("Member has not checked in")
        else:
            self.model.checkout_member(id_num,time_in,timeout)
            self.error_msg.setText("Checked out")

    def retrieve_inputs(self):
        """retrieve the inputs from user and submit query for id num and time"""
        phone_number = self.phone_number_entry.text()
        id_num = self.model.number_exists_query(phone_number)
        time = datetime.now()

        return phone_number, id_num, time 

    def validate_inputs(self, phone_number, id_num, in_out):
        """validate the phone number and id number logins are correct and that there are no duplicates
        inputs - phone number,id number, in_out as string of "Checked In" "Checked Out"
        returns the participant id as a string and phone number"""
        if len(phone_number)==0:
            self.error_msg.setText("Please input all fields")
        elif(id_num==None):
            self.error_msg.setText("Member not found")
        else: 
            self.error_msg.setText(in_out)

            check_in_dup = self.model.check_duplicate_checkin(id_num)                    
            if check_in_dup == None: # that means member has not checked in so we begin check in protocol
                time_in = datetime.now()
                self.model.checkin_query(id_num, time_in)
            else: 
                self.error_msg.setText("Member has already checked in")
            
