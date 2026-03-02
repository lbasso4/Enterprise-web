import serial
import requests
import time

# Configuració del port USB de l'Arduino
# Canvia 'COM3' pel port on tens connectat l'Arduino
SERIAL_PORT = 'COM3'
BAUD_RATE = 9600
FLASK_URL = 'http://127.0.0.1:5000/escaneig'

def llegir_arduino():
    print("Esperant dades de l'Arduino...")
    
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Espera que l'Arduino s'inicialitzi
    
    while True:
        if ser.in_waiting > 0:
            linia = ser.readline().decode('utf-8').strip()
            print(f"Rebut: {linia}")
            
            # Format esperat: NFC:BOB001,PES:0.750
            # Separem les dades
            if linia.startswith('NFC:'):
                parts = linia.split(',')
                codi_nfc = parts[0].replace('NFC:', '')
                pes_kg = float(parts[1].replace('PES:', ''))
                
                # Enviar les dades a Flask
                dades = {
                    'codi_nfc': codi_nfc,
                    'pes_kg': pes_kg
                }
                
                resposta = requests.post(FLASK_URL, json=dades)
                print(f"Resposta Flask: {resposta.json()}")

if __name__ == '__main__':

    llegir_arduino()
