"""
Contains business logic.
Try/Except is written only in the Home view.
Any Exception raised will be caught in the Home view -
as the main Processing method is called from Home.
"""

from uuid import uuid4
from datetime import datetime

import speech_recognition
from pydub import AudioSegment

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from service_app import models


@require_http_methods(['GET', 'POST'])
def home_view(request):
    """
    Main Home page
    """
    try:

        # GET method, return HTML page
        if request.method == 'GET':
            samples = models.AudioDataModel.objects.all()

            pending_jobs = models.AudioDataModel.objects.filter(status='PEN').count()
            show_timer = False
            if pending_jobs > 0:
                show_timer = True
            return render(request, 'service/home.html', {'samples': samples, 'show_timer': show_timer})

        # POST request, process the uploaded Audio file
        uploaded_file = request.FILES['uploaded_file']
        audio_data = models.AudioDataModel.objects.create(uploaded_file=uploaded_file)

        # Begin processing
        process_uploaded_file(audio_data)

        return HttpResponseRedirect('/')

    except Exception as e:

        audio_data.status = 'ERR'
        audio_data.error_occurred = True
        audio_data.error_message = str(e)
        audio_data.save()

        return HttpResponse(f'Error: {str(e)}')


def process_uploaded_file(audio_data):
    """
    Call all other processing methods from this method
    """

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
