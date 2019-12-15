from __future__ import absolute_import, unicode_literals
from uuid import uuid4

import speech_recognition
from pydub import AudioSegment

from celery import shared_task
from django.utils import timezone

from service_app import models

@shared_task
def process_uploaded_file(audio_data_id):
    """
    Call all other processing methods from this method
    """

    # Get Audio data model
    audio_data = None
    audio_data = models.AudioDataModel.objects.get(id=audio_data_id)

    # Convert uploaded file into WAV format
    convert_into_wave(audio_data)

    # Extract the Transcript from WAV file
    transcribe_audio(audio_data)


def convert_into_wave(audio_data):
    """
    Converts the uploaded file into WAV, suitable for Speech Recognition
    """

    uploaded_file_name = audio_data.uploaded_file.name
    file_extension = uploaded_file_name.split('.')[-1].lower()
    exported_file_name = audio = None

    # Convert into WAV format
    if file_extension != 'wav':
        audio = AudioSegment.from_file(uploaded_file_name, file_extension)

        # Generate a unique name and then export as WAV
        exported_file_name = f'{str(uuid4())}.wav'
        audio.export(exported_file_name, format='wav')

    # Already a WAV file
    else:
        exported_file_name = uploaded_file_name

    # Now save the exported file name
    audio_data.exported_file_name = exported_file_name
    audio_data.save()

    return


def transcribe_audio(audio_data):
    """
    Extract transcript from WAV file
    """

    exported_file_name = audio_data.exported_file_name
    audio = transcript = None

    recognizer = speech_recognition.Recognizer()

    with speech_recognition.AudioFile(exported_file_name) as ef:
        audio = recognizer.record(ef)
        transcript = recognizer.recognize_google(audio)

    # Save the transcript in the database
    audio_data.transcript = transcript
    audio_data.status = 'COM'
    audio_data.time_taken = timezone.now() - audio_data.created_at
    print(timezone.now() - audio_data.created_at)
    audio_data.save()

    return