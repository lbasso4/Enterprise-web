import PySerial
import time 
#Example values which will be assigned to our arduino's values
brate=115200
restT=.1
puerto="Port4"
#Connect our arduino or ESP o las dos via a serial port:
arduino = serial.Serial(port=puerto,baudrate=brate , timeout=restT) 
def extract_data(x): 
	   arduino.write(bytes(x, 'utf-8')) 
	   time.sleep(0.05) 
	   data = arduino.readline() 
	   return data 
while True: 
	   num = input("Enter a number: ") # Taking input from user 
	   value = write_read(num) 
	   print(value) # printing the value 
