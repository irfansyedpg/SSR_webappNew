from django.shortcuts import render
from django.http import HttpResponse
import argparse  # for Parsing
import io        # seting eniromental variable
import os        # setting enivromental varible
import wave      # Audio stero to mono

from pydub import AudioSegment  # audio import
import pydub                  # audio import
bucketname = 'bucketirfansyed'   # bucket name at google cloud
from google.cloud import storage  # Cloud storage GCP

import json           # Json paring
import time           # time date libarary
from google.cloud import pubsub_v1  # Google cloud publication subscribion library
from django.core.files.storage import default_storage
from django.db import models
from os import environ

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/syed.irfanullah/Desktop/speech/gcpcri.json"  # JSON file Google cloud auttenticaion


class Resume(models.Model):
    audio_file = models.FileField(upload_to='bucketirfansyed')


bucketName = environ.get('bucketirfansyed')


# json object
posts = [
    {
        'author': 'SSR_321_321',
        'content': 'Urdu content',
        'date_posted': '10/16/2019'

    },
]


def button_click(request):

    get_buckets()

    context = {

        'posts': posts

    }
    #(request,the blog i am requestin,my json object)
    return render(request, 'blog/home.html', context)


def home(request):
    return render(request, 'blog/home.html', {'tital': 'About'})


def about(request):
    return render(request, 'blog/about.html', {'tital': 'About'})


def get_buckets():

    # https://medium.com/p/1dbcab23c44/responses/show
    storage_client = storage.Client.from_service_account_json('C:/Users/syed.irfanullah/Desktop/speech/gcpcri.json')
    bucket = storage_client.get_bucket('bucketirfansyed')

    blobs = bucket.list_blobs()

    for blob in blobs:
        # print(blob.name)
        transcriber(blob.name)


def transcriber(blob_name):

    #urll = 'gs://bucketirfansyed/SSR_8102019114925.wav'
    urll = 'gs://bucketirfansyed/' + blob_name
    from google.cloud import speech_v1p1beta1 as speech  # GCP api
    client = speech.SpeechClient()

    audio = speech.types.RecognitionAudio(uri=urll)
    config = speech.types.RecognitionConfig(
        encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,

        language_code='ur-PK',  # language code
        enable_speaker_diarization=True,  # speaker diaraziation not working for urdu for now
        diarization_speaker_count=2,  # Speak count not working for urdu now
        sample_rate_hertz=48000,  # audio sampel rage
        audio_channel_count=2)  # number of chanel used in aud

    operation = client.long_running_recognize(config, audio)
    response = operation.result(timeout=10000)

    transcrip = ""
    for result in response.results:
        transcrip = transcrip + result.alternatives[0].transcript

    posts.append({
        'author': 'SSR_321_321',
        'content': transcrip,
        'date_posted': '10/16/2019'

    })
    # return transcrip
