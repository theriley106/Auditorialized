import requests
import shutil
import random

def gen_captcha_image_name():
	return ''.join([str(random.randint(1, 9)) for i in range(10)])

def download_image(url, saveAs):
	response = requests.get(url, stream=True)
	with open(saveAs, 'wb') as out_file:
	    shutil.copyfileobj(response.raw, out_file)
	del response

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
	download_mp3(res.json().get('captchaImageUrl'), 'captchas/{}.mp3'.format(gen_captcha_image_name()))

if __name__ == '__main__':
	for i in range(25):
		gen_new_image_captcha()
