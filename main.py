import requests
import shutil
import random
import os
import tinys3
import re
import boto3
import time
import json
try:
    from keys import *
except ImportError:
    ACCESS_KEY = raw_input("ACCESS KEY: ")
    SECRET_KEY = raw_input("SECRET KEY: ")
    BUCKET_ID = raw_input("BUCKET ID: ")

NUMBER_MAPPING = json.load(open("mapping.json"))

transcribe = boto3.client('transcribe', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY, region_name = 'us-east-1')
s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY, region_name = 'us-east-1')


def transcript_to_number(transcript):
    numbers = []
    for part in transcript.split(" "):
        if part in NUMBER_MAPPING:
            part = str(NUMBER_MAPPING[part])
        for number in re.findall("\d", part):
            numbers.append(number)
    return ''.join(numbers)


def get_code_from_transcript(job_name):
    potential_codes = []
    s3.download_file(BUCKET_ID, 'medical/{}.json'.format(job_name), '.tmp_json')
    for transcript in json.load(open(".tmp_json"))['results']['transcripts']:
        code = transcript_to_number(transcript['transcript'])
        if len(code) > 0:
            potential_codes.append(code)
    if len(potential_codes) > 0:
        return sorted(potential_codes, key=lambda k: len(k), reverse=True)[0]


def gen_captcha_image_name():
    return ''.join([str(random.randint(1, 9)) for i in range(10)])


def download_image(url, saveAs):
    response = requests.get(url, stream=True)
    with open(saveAs, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response


def trim_audio(audioFile, seconds=6):
    os.system('ffmpeg -i {} -ss 6 -vcodec copy -acodec copy {}.mp3'.format(audioFile, "temp"))
    os.system("mv temp.mp3 {}".format(audioFile))


def download_mp3(url, saveAs):
    response = requests.get(url, stream=True)
    with open(saveAs, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response


def gen_new_image_captcha():
    url = 'https://www.amazon.com/ap/captcha?appAction=SIGNIN&captchaObfuscationLevel=ape%3AaGFyZA%3D%3D&captchaType=image'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    res = requests.get(url, headers=headers)
    download_image(res.json().get('captchaImageUrl'), 'captchas/{}.jpg'.format(gen_captcha_image_name()))


def gen_new_audio_captcha():
    url = 'https://www.amazon.com/ap/captcha?appAction=SIGNIN&captchaObfuscationLevel=ape%3AaGFyZA%3D%3D&captchaType=audio'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    res = requests.get(url, headers=headers)
    fileName = 'captchas/{}.mp3'.format(gen_captcha_image_name())
    download_mp3(res.json().get('captchaImageUrl'), fileName)
    trim_audio(fileName)
    return fileName


def uploadFile(fileName):
    finalFileName = fileName.split('/')[-1]
    conn = tinys3.Connection(ACCESS_KEY,SECRET_KEY,tls=True)
    conn.upload(finalFileName, open(fileName,'rb'), BUCKET_ID)
    return "https://s3.amazonaws.com/{}/{}".format(BUCKET_ID, finalFileName)


def startTranscriptionJob(job_uri):
    job_name = "jobname" + str(random.randint(1, 10000))
    transcribe.start_medical_transcription_job(
        MedicalTranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat='mp3',
        LanguageCode='en-US',
        OutputBucketName=BUCKET_ID,
        Specialty="PRIMARYCARE",
        Type="CONVERSATION",
        Settings={
            'ShowAlternatives': True,
            'MaxAlternatives': 10,
            'ChannelIdentification': True,
        }

    )
    return job_name


def wait_for_transcription_job(job_name):
    while True:
        status = transcribe.get_medical_transcription_job(MedicalTranscriptionJobName=job_name)
        if status['MedicalTranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        print("Transcribing audio...")
        time.sleep(5)
    return status


if __name__ == '__main__':
    fileName = gen_new_audio_captcha()
    job_uri = uploadFile(fileName)
    job_name = startTranscriptionJob(job_uri)
    status = wait_for_transcription_job(job_name)
    code = get_code_from_transcript(job_name)
    print("Captcha Code: {}".format(code))
