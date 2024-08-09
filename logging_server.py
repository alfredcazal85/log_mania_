# logging_server.py CLASE es un plano que define propiedades y comportamientos ejemplo color marca modelo de auto INSTANCIA es una manifestacion concreta de la clase rojo, hyundai, 2023
from flask import Flask, request, jsonify #FLASK clase que se usa para crear app web, REQUEST permite acceder datos de la solicitud (post y headers), JSONIFY convierte objetos python a json para enviar respuestas http
from flask_sqlalchemy import SQLAlchemy #es un orm - Object Relational Mapping, facilita interaccion con bases de datos sql usando python
from datetime import datetime #se utiliza para trabajar con fechas y horas

app = Flask(__name__) #variable representa la instancia de flask
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logs.db' #configura la uri de la base de datos, se usa sqlite y se guarda en logs.bd
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #desactiva el seguimiento de modificaciones en los objetos para ahorrar recursos

db = SQLAlchemy(app) #instancia que se asocia con flask para manejar base de datos

# Lista de API keys válidos para autenticación de solicitudes, para que servicios autorizados envien logs
API_KEYS = ["service1_key", "service2_key", "service3_key"]

class Log(db.Model): #clase que define la estructura de la tabla log, hereda DB.MODEL, para que adquiera propiedades y comportamientos, en este caso log hereda de DB.MODEL
    id = db.Column(db.Integer, primary_key=True) #identificador unico de log
    timestamp = db.Column(db.String(50), nullable=False) #cadena que guarda fecha y hora del evento
    service_name = db.Column(db.String(50), nullable=False) #Nombre del servicio que envia el log
    log_level = db.Column(db.String(20), nullable=False) #nivel del log (info, error, debug)
    message = db.Column(db.String(200), nullable=False) #mensaje del log
    received_at = db.Column(db.DateTime, default=datetime.utcnow) #fecha y hora que el servidor recibe el log, tacha utcnow porque recomienda usar datetime.now, dependiendo del entorno

    def to_dict(self): #es una funcion dentro de la clase log que convierte una instancia en un diccionario python, para serializar y que luego sea mas facil convertir a json
        return {
            "id": self.id, #identificador del unico del log
            "timestamp": self.timestamp, #fecha y hora del evento registrado
            "service_name": self.service_name, #nombre del servicio
            "log_level": self.log_level, #valor del atributo con el tipo de log 
            "message": self.message, #mensaje del log
            "received_at": self.received_at.isoformat() if self.received_at else None #fecha y hora que se recibio el log
        }

# Usa el contexto de la aplicación, el entorno que almacena info especifica para crear las tablas e interactuar con la base, 
with app.app_context():
    db.create_all()

@app.route('/logs', methods=['POST']) # es un decorador de la funcion receive_log, asociada con la ruta /logs para manejar las solicitudes post
def receive_log(): #funcion que maneja recepcion de logs
    api_key = request.headers.get('Authorization').split(" ")[1] #obtiene la api key del encabezado de la solicitud
    
    if api_key not in API_KEYS:
        return jsonify({"error": "Token inválido"}), 401 #si no es valida devuelve error token invalido

    data = request.get_json() #obtiene datos json del cuerpo solicitud http
    
    new_log = Log( #crea un nuevo objeto log con los datos recibidos
        timestamp=data['timestamp'],
        service_name=data['service_name'],
        log_level=data['log_level'],
        message=data['message']
    )
    
    db.session.add(new_log) #añade el nuevo log a la sesion de la base de datos
    db.session.commit() #guarda el log en la base de datos
    
    return jsonify({"message": "Log recibido"}), 201 #muestra un mensaje si el registro fue exitoso

@app.route('/logs', methods=['GET']) #define ruta logs para obtener solicitudes get 
def get_logs(): #funcion que maneja la obtencion de logs
    start_date = request.args.get('start_date') #obtiene parametros para filtrar por fecha
    end_date = request.args.get('end_date') #obtiene parametros para filtrar por fecha
    received_start_date = request.args.get('received_start_date') #obtiene parametros para filtrar por fecha
    received_end_date = request.args.get('received_end_date')
    
    query = Log.query #inicia consulta sobre tabla log
    
    if start_date and end_date: #filtra logs entre las fechas de timestamp
        query = query.filter(Log.timestamp.between(start_date, end_date))
    
    if received_start_date and received_end_date: #filtra logs entre las fechas de received que corresponde a la que se recibe el log
        query = query.filter(Log.received_at.between(received_start_date, received_end_date))
    
    logs = query.all() #ejecuta la consulta y trae los logs con los filtros aplicados
    return jsonify([log.to_dict() for log in logs]), 200 #devuelve los logs en formato json

if __name__ == '__main__': #comprueba si el script se esta ejecutando directamente 
    app.run(port=5001) #inicia el servidor flask en el puerto 5001
