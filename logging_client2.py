import requests #importa libreria requests que sirve para hacer solicitudes http
from datetime import datetime #importa clase del modulo datetime para trabajar con fechas y horas

url = "http://localhost:5001/logs" #define la url para el envio del log
headers = {"Authorization": "Bearer service3_key"} #define encabezados de la solicitud http, incluye un token de autenticacion
data = {
    "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), #fecha y hora actual
    "service_name": "service2", #nombre del servicio que envia el log
    "log_level": "ERROR",#tipo de log enviado
    "message": "Este es un mensaje de log de prueba" #mensaje a incluir en el log
}

response = requests.post(url, headers=headers, json=data) #envia solicitud http post en la url especificada

if response.status_code == 201: #si todo sale bien imprimir el mensaje
    print("Log enviado con éxito")
else:
    print("Error al enviar el log:", response.status_code) # si no sale bien imprimir este mensaje
