"""
Registro de un usuario: 0 tokens
Cada usuario obtiene 10 tokens
Almacenar una sentencia en la DB cuesta 1 token
Recuperar la sentencia almacenada en la BD cuesta 1 token
"""

from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.SentencesDatabase
users = db["Users"]

class Register(Resource):
    def post(self):

        postedData = request.get_json()                     #obtener datos publicados por el usuario


        username = postedData["username"]
        password = postedData["password"] #"123xyz"

        #cifra la password del usuario
        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        #Almacena el nombre de usuario y contraseña en la BD
        users.insert({
            "Username": username,
            "Password": hashed_pw,
            "Sentence": "",
            "Tokens":10
        })

        retJson = {
            "status": 200,
            "msg": "You successfully signed up for the API"
        }
        return jsonify(retJson)

def verifyPw(username, password):                         #funcion, verifica si la password ingresada esta almacenada el la BD
    hashed_pw = users.find({
        "Username":username
    })[0]["Password"]

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False

def countTokens(username):                                #devuelve el numero de tokens del usuario
    tokens = users.find({
        "Username":username
    })[0]["Tokens"]
    return tokens

class Store(Resource):
    def post(self):
        #paso 1 obtener datos del usuario
        postedData = request.get_json()

        #paso 2 lee los datos
        username = postedData["username"]
        password = postedData["password"]
        sentence = postedData["sentence"]

        #paso 3 verifica que el usuario y pass conciden con los almacenados en la BD
        correct_pw = verifyPw(username, password)

        if not correct_pw:
            retJson = {
                "status":302
            }
            return jsonify(retJson)

        #paso 4 verifica que el usuario tiene suficientes tokens
        num_tokens = countTokens(username)
        if num_tokens <= 0:
            retJson = {
                "status": 301
            }
            return jsonify(retJson)

        #paso 5 actualizar la sentencia, restar un token  y devolver un status 200O
        users.update({
            "Username":username
        }, {
            "$set":{
                "Sentence":sentence,
                "Tokens":num_tokens-1
                }
        })

        retJson = {
            "status":200,
            "msg":"Sentence saved successfully"
        }
        return jsonify(retJson)

class Get(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]

        #Step 3 verify the username pw match
        correct_pw = verifyPw(username, password)
        if not correct_pw:
            retJson = {
                "status":302
            }
            return jsonify(retJson)

        num_tokens = countTokens(username)
        if num_tokens <= 0:
            retJson = {
                "status": 301
            }
            return jsonify(retJson)

        #el usuario paga!
        users.update({
            "Username":username
        }, {
            "$set":{
                "Tokens":num_tokens-1
                }
        })



        sentence = users.find({
            "Username": username
        })[0]["Sentence"]
        retJson = {
            "status":200,
            "sentence": str(sentence)
        }

        return jsonify(retJson)




api.add_resource(Register, '/register')
api.add_resource(Store, '/store')
api.add_resource(Get, '/get')


if __name__=="__main__":
    app.run(host='0.0.0.0')
