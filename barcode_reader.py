#!/usr/bin/env python3

import cv2
from pyzbar import pyzbar
from datetime import date
from optparse import OptionParser
from time import strftime, localtime
from colorama import Fore, Back, Style

GREEN = (0, 255, 0)

status_color = {
	'+': Fore.GREEN,
	'-': Fore.RED,
	'*': Fore.YELLOW,
	':': Fore.CYAN,
	' ': Fore.WHITE,
}

def get_time():
	return strftime("%H:%M:%S", localtime())
def display(status, data):
	print(f"{status_color[status]}[{status}] {Fore.BLUE}[{date.today()} {get_time()}] {status_color[status]}{Style.BRIGHT}{data}{Fore.RESET}{Style.RESET_ALL}")

def get_arguments(*args):
	parser = OptionParser()
	for arg in args:
		parser.add_option(arg[0], arg[1], dest=arg[2], help=arg[3])
	return parser.parse_args()[0]

def display_bar(bar):
	display('+', f"Type:\t{Back.MAGENTA}{bar.type}{Back.RESET}")
	display('+', f"Data:\t{Back.MAGENTA}{bar.data.decode()}{Back.RESET}")
	display('+', f"Quality:\t{Back.MAGENTA}{bar.quality}{Back.RESET}")
	display('+', f"Orientation:\t{Back.MAGENTA}{bar.orientation}{Back.RESET}")
	print()
def draw_bar(image, bar):
	return cv2.rectangle(image, (bar.rect.left, bar.rect.top), (bar.rect.left+bar.rect.width, bar.rect.top+bar.rect.height), GREEN, 2)
def check_repeat_bar(bars, bar):
	for Bar in bars:
		if bar.type == Bar.type and bar.data == Bar.data:
			return True
	return False

if __name__ == "__main__":
	data = get_arguments(('-s', "--save", "save", "Name of the file to save Data extracted from the QR Code"),
						 ('-i', "--image", "image", "Load Image from the given file"))
	all_data = set()
	if data.image:
		try:
			image = cv2.imread(data.image)
		except:
			display('-', f"Error while reading {Back.MAGENTA}{data.image}{Back.RESET}")
		bars = pyzbar.decode(image)
		for bar in bars:
			display_bar(bar)
			all_data.add((bar.type, bar.data.decode()))
			image = draw_bar(image, bar)
		if len(bars) != 0:
			cv2.imshow("Barcode", image)
			cv2.waitKey()
		else:
			display('*', "No Barcode Detected in this Image")
			exit(0)
	else:
		video_capture = cv2.VideoCapture(0)
		while True:
			ret, frame = video_capture.read()
			if not ret:
				display('-', "Can't get the Frame from the Camera")
				break
			bars = pyzbar.decode(frame)
			for bar in bars:
				display_bar(bar)
				all_data.add((bar.type, bar.data.decode()))
				frame = draw_bar(frame, bar)
			cv2.imshow("Barcode", frame)
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
		video_capture.release()
		cv2.destroyAllWindows()
	all_data = list(all_data)
	if not data.save:
		data.save = f"{date.today()} {get_time()}"
	if len(all_data) > 0:
		with open(data.save, 'w') as file:
			file.write('\n\n'.join([f"Type:{bar[0]}\nData:{bar[1]}" for bar in all_data]))