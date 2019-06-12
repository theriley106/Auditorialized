import requests
import shutil
import random
import os

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
	res = requests.get(url)
	download_image(res.json().get('captchaImageUrl'), 'captchas/{}.jpg'.format(gen_captcha_image_name()))

def gen_new_audio_captcha():
	url = 'https://www.amazon.com/ap/captcha?appAction=SIGNIN&captchaObfuscationLevel=ape%3AaGFyZA%3D%3D&captchaType=audio'
	res = requests.get(url)
	fileName = 'captchas/{}.mp3'.format(gen_captcha_image_name())
	download_mp3(res.json().get('captchaImageUrl'), fileName)
	trim_audio(fileName)


if __name__ == '__main__':
	for i in range(25):
		gen_new_audio_captcha()
