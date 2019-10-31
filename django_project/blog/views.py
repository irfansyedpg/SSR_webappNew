from django.shortcuts import render
from django.http import HttpResponse
import argparse  # for Parsing
import io        # seting eniromental variable
import os        # setting enivromental varible
import wave      # Audio stero to mono
from django.contrib import messages
import pyodbc


bucketname = 'bucketgcssr'   # bucket name at google cloud
from google.cloud import storage  # Cloud storage GCP

import json           # Json paring
import time           # time date libarary
from google.cloud import pubsub_v1  # Google cloud publication subscribion library
from django.core.files.storage import default_storage
from django.db import models
from os import environ

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcpcri.json"  # JSON file Google cloud auttenticaion


class Resume(models.Model):
    audio_file = models.FileField(upload_to='bucketgcssr')


bucketName = environ.get('bucketgcssr')


# json object


def button_click(request):

    posts = []
    posts = get_buckets()

    context = {

        'posts': posts

    }
    #(request,the blog i am requestin,my json object)
    return render(request, 'blog/translation.html', context)


def translation(request):

    posts = []
    posts = get_buckets()
    context = {

        'posts': posts

    }
    #(request,the blog i am requestin,my json object)
    return render(request, 'blog/translation.html', context)
    # return render(request, 'blog/translation.html', {'tital': 'translation'})


def home(request):
    return render(request, 'blog/home.html', {'tital': 'Home'})


def get_buckets():

    # https://medium.com/p/1dbcab23c44/responses/show
    storage_client = storage.Client.from_service_account_json('gcpcri.json')
    bucket = storage_client.get_bucket('bucketgcssr')

    blobs = bucket.list_blobs()
    posts = []
    for blob in blobs:
        # print(blob.name)
        blob.make_public()
        transcriber(blob.name, blob.updated, blob.public_url, posts)

    return posts


def transcriber(blob_name, datee, bob_url, posts):

    #urll = 'gs://bucketgcssr/SSR_8102019114925.wav'
    urll = 'gs://bucketgcssr/' + blob_name
    from google.cloud import speech_v1p1beta1 as speech  # GCP api
    client = speech.SpeechClient()

    audio = speech.types.RecognitionAudio(uri=urll)
    config = speech.types.RecognitionConfig(
        encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,

        language_code='ur-PK',  # language code
        enable_speaker_diarization=True,  # speaker diaraziation not working for urdu for now
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

    posts.append({
        'author': blob_name,
        'content': transcrip,
        'date_posted': datee,
        'confidence': str(confidence / i),
        'urll': bob_url

    })

    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=vcoe1.aku.edu;' # server name
                      'Database=cmapp;'      # DB Name 
                      'uid=coe1;'
                      'pwd=coe1.aku;')

    cursor = conn.cursor()
   
    cursor.execute("INSERT INTO Table_1 (transcription,id,date_upload) VALUES (?,?,?) ",(transcrip,blob_name,datee))
    conn.commit()
    conn.close()
    # return posts


# for detail Speech to text


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
    #(request,the blog i am requestin,my json object)
    return render(request, 'blog/translationdetail.html', context)


def transcriberDetail(blob_name, main):

    posts = []
  # posts.append({
    #    'author': blob_name,
    #    'content': transcription,
    #   'date_posted': datee,
    #  'confidence': confidance,
    # 'urll': atudio_url

  # })

    #urll = 'gs://bucketgcssr/SSR_8102019114925.wav'
    urll = 'gs://bucketgcssr/' + blob_name
    from google.cloud import speech_v1p1beta1 as speech  # GCP api
    client = speech.SpeechClient()

    audio = speech.types.RecognitionAudio(uri=urll)
    config = speech.types.RecognitionConfig(
        encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,

        language_code='ur-PK',  # language code
        enable_speaker_diarization=True,  # speaker diaraziation not working for urdu for now
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
