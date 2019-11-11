from os import environ
from django.db import models
#from django.core.files.storage import default_storage
#from google.cloud import pubsub_v1  # Google cloud publication subscribion library
import time           # time date libarary
import json           # Json paring
from google.cloud import storage  # Cloud storage GCP
from django.shortcuts import render
#from django.http import HttpResponse
#import argparse  # for Parsing
import io        # seting eniromental variable
import os        # setting enivromental varible




import mysql.connector

bucketname = 'bucketgcssr'   # bucket name at google cloud

mydb = mysql.connector.connect(
        host="precision.org.pk",
        user="precisi4_irfan",
        passwd="d6=P;rOz#Qj8",
        database="precisi4_ssr"
    )

# JSON file Google cloud auttenticaion
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcpcri.json"


class Resume(models.Model):
    audio_file = models.FileField(upload_to='bucketgcssr')


bucketName = environ.get('bucketgcssr')


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
    storage_client = storage.Client.from_service_account_json('gcpcri.json')
    bucket = storage_client.get_bucket('bucketgcssr')

    blobs = bucket.list_blobs()


    myql_list=get_AudioName_mysql()  
    posts = []
    for blob in blobs:
        # print(blob.name)
        
        if flgBtnClick=='1':
            if blob.name not in myql_list:
                blob.make_public()
                transcriber(blob.name, blob.updated, blob.public_url, posts)
                
    get_data_mysql_p1(posts)
 
    return posts


# get audio names from mysql for checking weather trancribed or not
def get_AudioName_mysql():

    mycursor = mydb.cursor()
    sql = "select audioName from ssrDataa"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    my_list = []
    for x in myresult:
        my_list.append(x[0])

    return my_list    




#get already transcribed audies form page1 to incrase the speed
def get_data_mysql_p1(posts):
    
    mycursor = mydb.cursor()
    sql = "select * from ssrDataa"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for x in myresult:
         posts.append({
        'author': x[0],
        'content': x[1],
        'date_posted': x[2],
        'confidence': x[3],
        'urll': x[4],

     })


# translation page get data from mysql ............................. ends ....................
     # actual transcribe founciton to sent request to the server and store data in mysql 
def transcriber(blob_name, datee, bob_url, posts):

    #urll = 'gs://bucketgcssr/SSR_8102019114925.wav'
    urll = 'gs://bucketgcssr/' + blob_name
    from google.cloud import speech_v1p1beta1 as speech  # GCP api
    client = speech.SpeechClient()

    audio = speech.types.RecognitionAudio(uri=urll)
    config = speech.types.RecognitionConfig(
        encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,

        language_code='ur-PK',  # language code
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

   # posts.append({
    #    'author': blob_name,
     #   'content': transcrip,
     #   'date_posted': datee,
      #  'confidence': str(confidence / i),
       # 'urll': bob_url

    #})

   

    mycursor = mydb.cursor()


    sql = "INSERT INTO ssrDataa (audioName, translation,datee,confidence,pubUrl) VALUES (%s, %s, %s, %s, %s)"
    val = (blob_name,transcrip,datee,str(confidence / i),bob_url )
    mycursor.execute(sql, val)
    mydb.commit()

   # sql = "UPDATE audios SET status ='2' where file='"+blob_name+"'"
    #mycursor.execute(sql)
    #mydb.commit()
  

# password d6=P;rOz#Qj8


# for detail Speech to text




#here this is click when the user wants to go to next page for detail summary of text with word level confidacen  
def detial_click(request):

    bob_name = request.GET.get("name")
    datee = request.GET.get("datee")
    audi_url = request.GET.get("publicurl")
    datee = request.GET.get("datee")

    posts = []
    main = []
    posts = transcriberDetail(bob_name, main)

    context = {

        'posts': posts,
        'main': main,
        'text': bob_name,
        'datee': datee,
        'audi_url': audi_url,


    }
    # (request,the blog i am requestin,my json object)
    return render(request, 'blog/translationdetail.html', context)


def transcriberDetail(blob_name, main):

    posts = []

    #urll = 'gs://bucketgcssr/SSR_8102019114925.wav'
    urll = 'gs://bucketgcssr/' + blob_name
    from google.cloud import speech_v1p1beta1 as speech  # GCP api
    client = speech.SpeechClient()

    audio = speech.types.RecognitionAudio(uri=urll)
    config = speech.types.RecognitionConfig(
        encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,

        language_code='ur-PK',  # language code
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
            confidence = word_info.confidence
            word = word_info.word
            start_time = word_info.start_time
            end_time = word_info.end_time
            posts.append({
                'word': word,
                'start_time': start_time.seconds + start_time.nanos * 1e-9,
                'end_time': end_time.seconds + end_time.nanos * 1e-9,
                'confidence': confidence
            })

    return posts


# word level confidance ends here .........................ends..................