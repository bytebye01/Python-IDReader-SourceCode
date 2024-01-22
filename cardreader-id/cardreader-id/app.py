#RESTserver for fetching data from Thai national id card
from flask import Flask, Response,render_template,request,jsonify,render_template_string
from flask_cors import CORS
from smartcard.CardConnection import CardConnection
from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.System import readers
from smartcard.util import toHexString, toBytes
import smartcard
import json
import base64
from datetime import datetime
import logging
import time
from smartcard.CardMonitoring import CardMonitor, CardObserver
import requests
from datetime import datetime
import os
import sys
from flask import Flask, Response
from smartcard.CardRequest import CardRequest
from smartcard.Exceptions import CardRequestTimeoutException
import json
import tkinter as tk
from tkinter import messagebox
import pystray
import threading
import requests
from PIL import Image, ImageDraw
import signal
import webbrowser
import smartcard.pcsc
from smartcard.Exceptions import CardRequestTimeoutException
from smartcard.pcsc.PCSCExceptions import EstablishContextException
from tis620encoding import tis620encoding
from resourcepath import resource_path
from afunction import check_reader_connection,print_hyperlink


SELECT = [0x00, 0xA4, 0x04, 0x00, 0x08]
THAI_ID_CARD = [0xA0, 0x00, 0x00, 0x00, 0x54, 0x48, 0x00, 0x01]


app = Flask(__name__)
CORS(app)


@app.after_request
def after_request(response):
  response.headers.set('Access-Control-Allow-Origin', '*')
  response.headers.set('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.set('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response 



@app.route('/get_status')
def get_status():
    reader_connected = check_reader_connection()
    if not reader_connected:
        no_card_reader = 'ไม่พบเครื่องเสียบบัตร'
        no_card_reader_status = 901
        resultdict = {
            'status': no_card_reader_status,
            'message': no_card_reader
        }
        return Response(json.dumps(resultdict), mimetype='application/json')
    else:
        try:
            cardtype = AnyCardType()
            cardrequest = CardRequest(timeout=1, cardType=cardtype)
            cardservice = cardrequest.waitforcard()
            return Response("Card detected", mimetype='text/plain')
        except CardRequestTimeoutException:
            no_card = 'กรุณาเสียบบัตรประชาชน'
            no_card_status = 902
            resultdict = {
                'status': no_card_status,
                'message': no_card
            }
            return Response(json.dumps(resultdict), mimetype='application/json')
        except EstablishContextException as e:
            smartcard_error = 'เครื่องไม่พบตัวจัดการสมาร์ทการ์ด กรุณาเชื่อมต่อตัวอ่านบัตร'
            smartcard_error_status = 404
            resultdict = {
                'status': smartcard_error_status,
                'message': smartcard_error
            }
            return Response(json.dumps(resultdict), mimetype='application/json')


#Start get_data
@app.route('/')
def get_data():
    reader_connected = check_reader_connection()
    if not reader_connected:
        message = 'ไม่พบเครื่องเสียบบัตร'
        status = 901
        resultdict = {
            'Status': status,
            'Message': message
        }
        return jsonify(resultdict)
    else:
        try:
            cardtype = AnyCardType()
            cardrequest = CardRequest(timeout=1, cardType=cardtype)
            cardservice = cardrequest.waitforcard()
            stat = cardservice.connection.connect()

            REQ_CID = [0x80, 0xb0, 0x00, 0x04, 0x02, 0x00, 0x0d]
            REQ_THAI_NAME = [0x80, 0xb0, 0x00, 0x11, 0x02, 0x00, 0x64]
            REQ_ENG_NAME = [0x80, 0xb0, 0x00, 0x75, 0x02, 0x00, 0x64]
            REQ_GENDER = [0x80, 0xb0, 0x00, 0xE1, 0x02, 0x00, 0x01]
            REQ_DOB = [0x80, 0xb0, 0x00, 0xD9, 0x02, 0x00, 0x08]
            REQ_RELIGION = [0x80, 0xb0, 0x01, 0x67, 0x02, 0x00, 0x12]
            REQ_ADDRESS = [0x80, 0xb0, 0x15, 0x79, 0x02, 0x00, 0x64]
            REQ_ISSUER = [0x80, 0xb0, 0x00, 0xF6, 0x02, 0x00, 0x64]
            REQ_ISSUE = [0x80, 0xb0, 0x01, 0x67, 0x02, 0x00, 0x08] 
            REQ_ISSUE_EXPIRE = [0x80, 0xb0, 0x01, 0x6F, 0x02, 0x00, 0x08]
            
            DATA = [REQ_CID,REQ_THAI_NAME,REQ_ENG_NAME,REQ_GENDER,REQ_DOB,
            REQ_RELIGION,REQ_ADDRESS,REQ_ISSUER,REQ_ISSUE,REQ_ISSUE_EXPIRE]

            REQ_PHOTO_P1 = [0x80,0xB0,0x01,0x7B,0x02,0x00,0xFF]
            REQ_PHOTO_P2 = [0x80,0xB0,0x02,0x7A,0x02,0x00,0xFF]
            REQ_PHOTO_P3 = [0x80,0xB0,0x03,0x79,0x02,0x00,0xFF]
            REQ_PHOTO_P4 = [0x80,0xB0,0x04,0x78,0x02,0x00,0xFF]
            REQ_PHOTO_P5 = [0x80,0xB0,0x05,0x77,0x02,0x00,0xFF]
            REQ_PHOTO_P6 = [0x80,0xB0,0x06,0x76,0x02,0x00,0xFF]
            REQ_PHOTO_P7 = [0x80,0xB0,0x07,0x75,0x02,0x00,0xFF]
            REQ_PHOTO_P8 = [0x80,0xB0,0x08,0x74,0x02,0x00,0xFF]
            REQ_PHOTO_P9 = [0x80,0xB0,0x09,0x73,0x02,0x00,0xFF]
            REQ_PHOTO_P10 = [0x80,0xB0,0x0A,0x72,0x02,0x00,0xFF]
            REQ_PHOTO_P11 = [0x80,0xB0,0x0B,0x71,0x02,0x00,0xFF]
            REQ_PHOTO_P12 = [0x80,0xB0,0x0C,0x70,0x02,0x00,0xFF]
            REQ_PHOTO_P13 = [0x80,0xB0,0x0D,0x6F,0x02,0x00,0xFF]
            REQ_PHOTO_P14 = [0x80,0xB0,0x0E,0x6E,0x02,0x00,0xFF]
            REQ_PHOTO_P15 = [0x80,0xB0,0x0F,0x6D,0x02,0x00,0xFF]
            REQ_PHOTO_P16 = [0x80,0xB0,0x10,0x6C,0x02,0x00,0xFF]
            REQ_PHOTO_P17 = [0x80,0xB0,0x11,0x6B,0x02,0x00,0xFF]
            REQ_PHOTO_P18 = [0x80,0xB0,0x12,0x6A,0x02,0x00,0xFF]
            REQ_PHOTO_P19 = [0x80,0xB0,0x13,0x69,0x02,0x00,0xFF]
            REQ_PHOTO_P20 = [0x80,0xB0,0x14,0x68,0x02,0x00,0xFF]

            PHOTO = [REQ_PHOTO_P1,REQ_PHOTO_P2,REQ_PHOTO_P3,REQ_PHOTO_P4,REQ_PHOTO_P5,
            REQ_PHOTO_P6,REQ_PHOTO_P7,REQ_PHOTO_P8,REQ_PHOTO_P9,REQ_PHOTO_P10,REQ_PHOTO_P11
            ,REQ_PHOTO_P12,REQ_PHOTO_P13,REQ_PHOTO_P14,REQ_PHOTO_P15,REQ_PHOTO_P16,REQ_PHOTO_P17,
            REQ_PHOTO_P18,REQ_PHOTO_P19,REQ_PHOTO_P20]

            photobytearray = bytearray();
            apdu = SELECT+THAI_ID_CARD
            response, sw1, sw2 = cardservice.connection.transmit( apdu )

            resultlist = list();

            for d in DATA:
                response, sw1, sw2 = cardservice.connection.transmit( d )
                if sw1 == 0x61:
                    GET_RESPONSE = [0X00, 0XC0, 0x00, 0x00 ]
                    apdu = GET_RESPONSE + [sw2]
                    response, sw1, sw2 = cardservice.connection.transmit( apdu )
                    result = ''
                    for i in response:
                        result = result + tis620encoding[i]
                    resultlist.append(result)  
            
            
            cardtype = AnyCardType()
            cardrequest = CardRequest( timeout=1, cardType=cardtype )

            try:
                cardservice = cardrequest.waitforcard()
            except:
                resultdict = {
                    'status': 'inactive : No card reader found. Please check your card reader connection.)'
                }
                return json.dumps(resultdict)

            cardservice.connection.connect()

            apdu = SELECT+THAI_ID_CARD
            response, sw1, sw2 = cardservice.connection.transmit( apdu )

            for d in PHOTO:
                response, sw1, sw2 = cardservice.connection.transmit( d )
                if sw1 == 0x61:
                    GET_RESPONSE = [0X00, 0XC0, 0x00, 0x00 ]
                    apdu = GET_RESPONSE + [sw2]
                    response, sw1, sw2 = cardservice.connection.transmit( apdu )
                    photobytearray.extend(bytearray(response))
            base64_encoded = base64.b64encode(bytes(photobytearray)).decode('utf-8')  # encode เป็น base64 string
            sharp = ("#")
            spacing = (" ")
            nameth_formatted = resultlist[1]
            nameen_formatted = resultlist[2]
            address_formatted = resultlist[6]
            issuer_formatted = resultlist[7]
            nameth = nameth_formatted.replace(sharp, spacing)
            nameen = nameen_formatted.replace("#", " ")
            address = address_formatted.replace("#", " ")
            issuer = issuer_formatted.replace("/", " ")
            
            gender_text = resultlist[3]
            if gender_text == "1":
                gender_text = "ชาย"
            elif gender_text == "2":
                gender_text = "หญิง"
            else:
                gender_text = "อื่นๆ"

            birthdate = resultlist[4]
            birthdate_obj = datetime.strptime(birthdate, '%Y%m%d')
            formatted_birthdate = birthdate_obj.strftime('%d/%m/%Y')
            formatted_birthdate_year = int(formatted_birthdate[6:10])
            formatted_birthdate_month = int(formatted_birthdate[3:5])
            formatted_birthdate_day = int(formatted_birthdate[0:2])
            current_date = datetime.now()
            current_date_str = current_date.strftime('%d/%m/%Y %H:%M')
            current_date_int_year = int(current_date_str[6:10]) + 543
            current_date_int_month = int(current_date_str[3:5])
            current_date_int_day = int(current_date_str[0:2])
            year_age = str(current_date_int_year - formatted_birthdate_year - ((current_date_int_month, current_date_int_day) < (formatted_birthdate_month, formatted_birthdate_day)))
            month_age = str(current_date_int_month - formatted_birthdate_month)
            day_age = str(current_date_int_day - formatted_birthdate_day)
            age = str((year_age," ปี "))
            age_formatted01 = age.replace("'", "")
            age_formatted02 = age_formatted01.replace("," , "")
            age_formatted03 = age_formatted02.replace("(","")
            age_formatted04 = age_formatted03.replace(")","")
            issuedate = resultlist[8]
            issuedate_obj = datetime.strptime(issuedate, '%Y%m%d')
            formatted_issuedate = issuedate_obj.strftime('%d/%m/%Y')
            expiredate = resultlist[9]
            expiredate_obj = datetime.strptime(expiredate, '%Y%m%d')
            formatted_expiredate = expiredate_obj.strftime('%d/%m/%Y')

            religion_slice = resultlist[5]
            formatted_religion_slice = f"{religion_slice[16:18]}"
            if formatted_religion_slice == "01":
                religion_text = "พุทธ"
            elif formatted_religion_slice == "02":
                religion_text = "อิสลาม"
            elif formatted_religion_slice == "03":
                religion_text = "คริสต์"
            elif formatted_religion_slice == "04":
                religion_text = "พราหมณ์-ฮินดู"
            elif formatted_religion_slice == "05":
                religion_text = "ซิกข์"
            elif formatted_religion_slice == "06":
                religion_text = "ยิว"
            elif formatted_religion_slice == "07":
                religion_text = "เชน"
            elif formatted_religion_slice == "08":
                religion_text = "โซโรอัสเตอร์"
            elif formatted_religion_slice == "09":
                religion_text = "บาไฮ"
            elif formatted_religion_slice == "00":
                religion_text = "ไม่นับถือศาสนา"
            else:
                religion_text = "ไม่ทราบ"
            message = 'ปกติ'
            status =200
            resultdict = {
                'Status': status,
                'Message': message,
                'Today':current_date_str,
                'ID Number':resultlist[0],
                'Thai Name':nameth,
                'English Name':nameen,
                'Gender':gender_text,
                'Date of Birth':formatted_birthdate,
                'Age':age_formatted04,
                'Religion':religion_text,
                'Address':address,
                'Issuer':issuer,
                'Date of Issue':formatted_issuedate,
                'Date of Expiry':formatted_expiredate,
                'Photo(base64)':base64_encoded
            }
            return Response(json.dumps(resultdict), mimetype='application/json')
        
        except CardRequestTimeoutException:
            message = 'กรุณาเสียบบัตรประชาชน'
            status = 902
            resultdict = {
                'Status': status,
                'Message': message
            }
            return Response(json.dumps(resultdict), mimetype='application/json')
        


# app routeของเดิมของ def get_data
# @app.route('/')
# def show_axios_page():
#     return render_template('axios.html')
        
        

        
@app.route('/submit_form', methods=['POST'])
def submit_form():
    if request.method == 'POST':
        IDno = request.form['IDno']
        THName = request.form['THName']
        ENName = request.form['ENName']
        Gender = request.form['Gender']
        dob = request.form['DOB']
        Age = request.form['Age']
        Religion = request.form['Religion']
        Address = request.form['Address']
        Issuer = request.form['Issuer']
        doi = request.form['DOI']
        doe = request.form['DOE']
        Photobase64 = request.form['Photobase64']

        filename = f"form_data_{IDno}_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
        with open(filename, 'w',encoding='utf-8') as file:
            file.write(f"ID Number: {IDno}\n")
            file.write(f"Thai Name: {THName}\n")
            file.write(f"English Name: {ENName}\n")
            file.write(f"Gender: {Gender}\n")
            file.write(f"Date of Birth: {dob}\n")
            file.write(f"Age: {Age}\n")
            file.write(f"Religion: {Religion}\n")
            file.write(f"Address: {Address}\n")
            file.write(f"Issuer: {Issuer}\n")
            file.write(f"Date of Issue: {doi}\n")
            file.write(f"Date of Expiry: {doe}\n")
            file.write(f"Photo(base64): {Photobase64}\n")
        return "Form submitted successfully and data saved!"
    return "Error in submitting form"



@app.route('/shutdown', methods=['GET'])
def shutdown():
    os.kill(os.getpid(), signal.SIGINT)
    return 'Server shutting down...'

def start_flask_app():
    app.run(port=5000)  # กำหนดพอร์ตให้ Flask

def exit_app(icon, item):
    requests.get('http://127.0.0.1:5000/shutdown')  # เรียกใช้ /shutdown endpoint
    icon.stop()

def open_web_page(icon, item):
    webbrowser.open("http://localhost:5000")

def create_tray_icon():
    image = Image.open(resource_path(r'assets\\Logo.png'))
    menu = (
        pystray.MenuItem('Open', open_web_page),
        pystray.MenuItem('Exit', exit_app),
    )
    icon = pystray.Icon("name", image, "ID Reader", menu)
    icon.run()

if __name__ == '__main__':
    flask_thread = threading.Thread(target=start_flask_app)
    flask_thread.start()
    create_tray_icon()
    