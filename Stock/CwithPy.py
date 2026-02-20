import PySerial
import time 
#Example values which will be assigned to our arduino's values
brate=115200
restT=.1
puertoPC="Port4"
x=10 #data requested/will be modified
#Connect our arduino or ESP o las dos via a serial port:
arduino = serial.Serial(port=puertoPC,baudrate=brate , timeout=restT) 
def extract_data(x): 
	   arduino.write(bytes(x, 'utf-8')) #requesting data which arduESP will use
	   time.sleep(0.05) 
	   weight = arduino.readline() 
	   return weight 
