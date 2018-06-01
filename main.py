from time import sleep, time
from sys import exit
import os
import RPi.GPIO as GPIO 
import datetime
import pyaudio
import wave
import sys
from matrix_keypad import RPi_GPIO

kp = RPi_GPIO.keypad(columnCount = 3)  


os.system('clear')

GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(16, GPIO.OUT)
GPIO.add_event_detect(26,GPIO.FALLING)
GPIO.setwarnings(False)
beep = True
hard = False
outfile=open('Play_Count.txt','a')

def bip(error_wav, ch):
	chunk=ch
	wf = wave.open(error_wav, 'rb')
	p = pyaudio.PyAudio()
	# open stream based on the wave object which has been input.
	stream = p.open(format =
	                p.get_format_from_width(wf.getsampwidth()),
	                channels = wf.getnchannels(),
	                rate = wf.getframerate(),
	                output = True)
	# read data (based on the chunk size)
	data = wf.readframes(chunk)
	# play stream (looping from beginning of file to the end)
	while data != '':
	    # writing to the stream is what *actually* plays the sound.
	    stream.write(data)
	    data = wf.readframes(chunk)
	# cleanup stuff.
	stream.close()    
	p.terminate()



with open('clues/hard.txt') as f:
	hard=f.readlines()
	hard_passcode  = [x.split(',')[0] for x in hard]
	hard_audio  = [x.split(',')[1] for x in hard]
with open('clues/easy.txt') as f:
	easy=f.readlines()
	easy_passcode  = [x.split(',')[0] for x in easy]
	easy_audio  = [x.split(',')[1] for x in easy]
playcount=0
#Define a function to compare keypad input to a passcode
def story():
	attempt = "____"	
	counter = 0  #can be defined outside the function
	while True: #time()<timeout: True:
		digit = None
		stop_sound=False
		digit = kp.getKey()
		if digit == None:
			if "_" in attempt: # digit == None:
				while digit == None:
					digit = kp.getKey()
						#os.system('omxplayer --no-osd --no-keys audio/beep.wav')
					input_state = GPIO.input(26)
					if GPIO.event_detected(26):
						attempt= "____"
						counter = 0
					if input_state == False:
						hard=False
					else: # input_state == True:
						hard = True
				bip('audio/beep.wav',1024)
				if hard==False:
		        		passcode = easy_passcode
		        		audio=easy_audio
				else:
		        		passcode = hard_passcode
			        	audio= hard_audio
				attempt = (attempt[1:] + str(digit))  
			else:
	# Check for passcode match
				if (attempt in passcode):	#if code is in list
					counter +=1
					for i, j in enumerate(passcode):		#find index of pass code in array
						if j == attempt:
							#print audio[i]
							sleep(0.01)
							os.system('omxplayer --vol 194 %s > /dev/null 2>&1' %(audio[i]))  #play corresponding clue
							if attempt == passcode[0]:
								print'---start---'
								start_time=datetime.datetime.now()
							if attempt == passcode[-1]:
								end_time=datetime.datetime.now()
								duration=end_time-start_time	
								time_entered=datetime.datetime.now().date()
								line='%s\t%s\n'%(end_time,duration)
								outfile.write(line)
					attempt="____"
					sleep(0.01)
				if (attempt not in passcode):								#if code is incorrect, plays dif audio file and waits for another try
					counter += 1
					#print "Entered digit count: %s"%counter
					if (counter >= 4):
						#print attempt
						sleep(0.25)
			                        bip('audio/error.wav',2048)
						attempt = "____"
						sleep(0.01)
						counter = 0
		sleep(0.05)
		
running = True
outfile.write('Restart\n')

while running == True:
	GPIO.output(16,True)
	story()


