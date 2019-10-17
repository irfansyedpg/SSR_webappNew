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
    storage_client = storage.Client.from_service_account_json('C:/Users/syed.irfanullah/Desktop/speech/gcpcri.json')
    bucket = storage_client.get_bucket('bucketirfansyed')

    blobs = bucket.list_blobs()
    posts = []
    for blob in blobs:
        # print(blob.name)
        blob.make_public()
        transcriber(blob.name, blob.updated, blob.public_url, posts)

    return posts


def transcriber(blob_name, datee, bob_url, posts):

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
    confidence = 0
    for result in response.results:
        transcrip = transcrip + result.alternatives[0].transcript
        confidence = confidence + result.alternatives[0].confidence

    posts.append({
        'author': blob_name,
        'content': transcrip,
        'date_posted': datee,
        'confidence': str(confidence),
        'urll': bob_url

    })
    # return posts
