from os import environ
from django.db import models
# from django.core.files.storage import default_storage
# from google.cloud import pubsub_v1  # Google cloud publication subscribion library
import time           # time date libarary
import json           # Json paring
from google.cloud import storage  # Cloud storage GCP
from django.shortcuts import render
# from django.http import HttpResponse
# import argparse  # for Parsing
import io        # seting eniromental variable
import os        # setting enivromental varible
import xlwt
from django.http import HttpResponse





import mysql.connector


bucketname = 'bucketssrrr'   # bucket name at google cloud


# SQL Connection String strats
mydb = mysql.connector.connect(
    host="precision.org.pk",
    #host="35.226.163.82",
    user="precisi4_irfan",
    passwd="d6=P;rOz#Qj8",
    database="precisi4_ssr"
)
mycursor = mydb.cursor()
# SQL Connection String Ends


# JSON file Google cloud auttenticaion
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "newjsonkey.json"


# For urdu to english translation 
from google.cloud import translate_v2 as translate
translate_client = translate.Client()

class Resume(models.Model):
    audio_file = models.FileField(upload_to='bucketssrrr')


bucketName = environ.get('bucketssrrr')


# json object to go to translation page
def button_click(request):

    posts = []
    posts = get_buckets('1')

    context = {

        'posts': posts

    }
    # (request,the blog i am requestin,my json object)
    return render(request, 'blog/translation.html', context)


def translation(request):

    posts = []
    posts = get_buckets('0')
    context = {

        'posts': posts

    }
    # (request,the blog i am requestin,my json object)
    return render(request, 'blog/translation.html', context)
    # return render(request, 'blog/translation.html', {'tital': 'translation'})


def home(request):
    return render(request, 'blog/home.html', {'tital': 'Home'})


# called when traslation page load it get blob from gcp and data from mysql server
def get_buckets(flgBtnClick):

    # https://medium.com/p/1dbcab23c44/responses/show
    storage_client = storage.Client.from_service_account_json('newjsonkey.json')
    bucket = storage_client.get_bucket('bucketssrrr')

    blobs = bucket.list_blobs()

    myql_list = get_AudioName_mysql()
    posts = []
    for blob in blobs:
        # print(blob.name)

        if flgBtnClick == '1':
            if blob.name not in myql_list:
                blob.make_public()
                transcriber(blob.name, blob.updated, blob.public_url, posts)

    get_data_mysql_p1(posts)

    return posts


# get audio names from mysql for checking weather trancribed or not
def get_AudioName_mysql():

    sql = "select audioName from ssrDataa"
    mydb._open_connection()
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    my_list = []
    for x in myresult:
        my_list.append(x[0])

    mydb.close()
    return my_list


lstAdName = []
lstTranslation = []
lstConfidance = []
lstDate = []
lstUrl = []


# get already transcribed audies form page1 to incrase the speed
def get_data_mysql_p1(posts):

    # mycursor = mydb.cursor()
    sql = "select * from ssrDataa"
    mydb._open_connection()
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for x in myresult:

        lstAdName.append(x[0])
        lstTranslation.append(x[1])
        lstConfidance.append(x[3])
        lstDate.append(x[2])
        lstUrl.append(x[4])
     
   
        posts.append({
            'author': x[0],
            'content': x[1],
            'date_posted': x[2],
            'confidence': x[3],
            'urll': x[4],
            'tranlsation': x[5],

        })
        
#NLP

 

    mydb.close()


# translation page get data from mysql ............................. ends ....................

    # actual transcribe founciton to sent request to the server and store data in mysql
def transcriber(blob_name, datee, bob_url, posts):

    # urll = 'gs://bucketssrrr/SSR_8102019114925.wav'
    urll = 'gs://bucketssrrr/' + blob_name
    from google.cloud import speech_v1p1beta1 as speech  # GCP api
    client = speech.SpeechClient()

    audio = speech.types.RecognitionAudio(uri=urll)
    config = speech.types.RecognitionConfig(
        encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,

        #language_code='ur-PK',  # language code
        language_code='ur-in',  # language code
        # speaker diaraziation not working for urdu for now
        enable_speaker_diarization=True,
        diarization_speaker_count=2,  # Speak count not working for urdu now
        sample_rate_hertz=48000,  # audio sampel rage
        audio_channel_count=1)  # number of chanel used in aud

    operation = client.long_running_recognize(config, audio)
    response = operation.result(timeout=10000)

    transcrip = ""
    confidence = 0
    i = -1
    for result in response.results:
        transcrip = transcrip + result.alternatives[0].transcript
        confidence = confidence + result.alternatives[0].confidence
        i = i + 1


    result = translate_client.translate(
    transcrip, target_language='en')
    tranlsationenglish=result['translatedText']

    sql = "INSERT INTO ssrDataa (audioName, translation,datee,confidence,pubUrl,englishtranslation) VALUES (%s, %s, %s, %s, %s, %s)"
    mydb._open_connection()
    val = (blob_name, transcrip, datee, str(confidence / i), bob_url,tranlsationenglish)
    mycursor.execute(sql, val)
    mydb.commit()
    mydb.close()


# for detail Speech to text

#NLP

from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
client = language.LanguageServiceClient()
# here this is click when the user wants to go to next page for detail summary of text with word level confidacen
def detial_click(request):

    bob_name = request.GET.get("name")
    datee = request.GET.get("datee")
    audi_url = request.GET.get("publicurl")
    datee = request.GET.get("datee")

    posts = []
    main = []
    nlppart=[]
    
    posts = transcriberDetail(bob_name, main)
    #NLP here 
    urdutext=main[0]['transcrip']
    result = translate_client.translate(
    urdutext, target_language='en')
    tranlsationenglish=result['translatedText']

    

    document = language.types.Document(
    content=tranlsationenglish,
     type=language.enums.Document.Type.PLAIN_TEXT, )

# Detects the sentiment of the text
    response = client.analyze_entities(
    document=document,
     encoding_type='UTF32',
    )
    for entity in response.entities:
        nlppart.append({
            'word':entity.name,
            'type':client.enums.Entity.Type(entity.type).name
        })


    context = {

        'posts': posts,
        'main': main,
        'text': bob_name,
        'textenglish':tranlsationenglish,
        'datee': datee,
        'audi_url': audi_url,
        'nlppart':nlppart,


    }
    # (request,the blog i am requestin,my json object)
    return render(request, 'blog/translationdetail.html', context)

def get_type(type):
        return client.enums.Entity.Type(entity.type).name

def transcriberDetail(blob_name, main):

    # check if already Inserted to ssrDictionary using audio name/blobname
    flagDntInst = 0
    # mycursor = mydb.cursor()
    mydb._open_connection()
    sql = "select  audioName from ssrDictionary where audioName='" + blob_name + "' LIMIT 2"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for x in myresult:
        flagDntInst = 1

    posts = []

    # urll = 'gs://bucketssrrr/SSR_8102019114925.wav'
    urll = 'gs://bucketssrrr/' + blob_name
    from google.cloud import speech_v1p1beta1 as speech  # GCP api
    client = speech.SpeechClient()

    audio = speech.types.RecognitionAudio(uri=urll)
    config = speech.types.RecognitionConfig(
        encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,

        #language_code='ur-PK',  # language code
        language_code='ur-in',  # language code
        # speaker diaraziation not working for urdu for now
        enable_speaker_diarization=True,
        diarization_speaker_count=2,  # Speak count not working for urdu now
        sample_rate_hertz=48000,  # audio sampel rage
        audio_channel_count=1)  # number of chanel used in aud

    operation = client.long_running_recognize(config, audio)
    response = operation.result(timeout=10000)

    transcrip = ""
    confidence = 0
    for result in response.results:
        alternative = result.alternatives[0]
        transcrip = format(alternative.transcript)
        confidence = alternative.confidence
        main.append({
            'transcrip': transcrip,
            'blob_name': blob_name,
            'confidence': confidence})
        for word_info in alternative.words:
            confidence = format(word_info.confidence)
            word = word_info.word
            start_time = word_info.start_time
            end_time = word_info.end_time
            posts.append({
                'word': word,
                'start_time': start_time.seconds + start_time.nanos * 1e-9,
                'end_time': end_time.seconds + end_time.nanos * 1e-9,
                'confidence': confidence


            })
            # insertion to Mysql For WordDictionary here
            if flagDntInst == 0:
                sql = "INSERT INTO ssrDictionary (words,audioName, confidance,endTime,startTime) VALUES (%s, %s, %s, %s, %s)"
                val = (word, blob_name, confidence, end_time.seconds + end_time.nanos * 1e-9, start_time.seconds + start_time.nanos * 1e-9)
                mycursor.execute(sql, val)
                mydb.commit()

    mydb.close()
    return posts


# word level confidance ends here .........................ends..................


# download data from in excel formate

def download_excel_data(request):
        # content-type of response
    response = HttpResponse(content_type='application/ms-excel')

    # decide file name
    response['Content-Disposition'] = 'attachment; filename="SSRWordDictinary.xls"'

    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')

    # adding sheet
    ws = wb.add_sheet("sheet1")

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True

    # column header names, you can use your own headers here
    columns = ['Transcription Name', 'Word', 'Confidance', 'Start Time', 'End  Time', ]

    # write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    # get your data, from database or from a text file...
    data = get_data()  # dummy method to fetch data.

    for my_row in data:
        row_num = row_num + 1
        ws.write(row_num, 0, my_row[0], font_style)
        ws.write(row_num, 1, my_row[1], font_style)
        ws.write(row_num, 2, my_row[2], font_style)
        ws.write(row_num, 3, my_row[3], font_style)
        ws.write(row_num, 4, my_row[4], font_style)

    wb.save(response)
    return response


def get_data():
    # mycursor = mydb.cursor()
    mydb._open_connection()
    sql = "select  * from ssrDictionary "
    mycursor.execute(sql)
    data = mycursor.fetchall()
    mydb.close()
    return data


# download all transcription

def download_excel_transcription(request):
    # content-type of response
    response = HttpResponse(content_type='application/ms-excel')

    # decide file name
    response['Content-Disposition'] = 'attachment; filename="SSRTranslation.xls"'

    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')

    # adding sheet
    ws = wb.add_sheet("sheet1")

    # Sheet header, first row
    row_num = 0
    row_index = 0

    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True

    # column header names, you can use your own headers here
    columns = ['AudioName Name', 'Translation', 'Confidance', 'InterviewTime', 'Audio URL', ]

    # write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    # get your data, from database or from a text file...

    for my_row in lstAdName:
        row_num = row_num+1
        ws.write(row_num, 0, lstAdName[row_index], font_style)
        ws.write(row_num, 1, lstTranslation[row_index], font_style)
        ws.write(row_num, 2, lstConfidance[row_index], font_style)
        ws.write(row_num, 3, lstDate[row_index], font_style)
        ws.write(row_num, 4, lstUrl[row_index], font_style)
        row_index=row_index+1

    wb.save(response)
    return response
