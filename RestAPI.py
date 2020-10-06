from flask import Flask, request, render_template, send_file
from flask_cors import CORS
import json
from flask_restful import Api, Resource, reqparse
from dbHandlers import getNewCode, updAndGetNew


expiresAfter = 2 # Sati posle štampanja nakon kojega QR ističe
length = 5 #dužina koda


app = Flask(__name__, template_folder='./web/build', static_folder='./web/build/static')
CORS(app)
api = Api(app)
parser = reqparse.RequestParser()


class RequestHandler(Resource):
    def get(self):
        try:
            return {**getNewCode(length), 'dT': expiresAfter}, 200
        except Exception as err:
            print(err)
            return err.args, 500

    def patch(self):
        data = json.loads(request.data)
        print(data)
        try:
            return {**updAndGetNew(data['id'], length, expiresAfter), 'dT': expiresAfter}, 201
        except Exception as err:
            print(err)
            return err.args, 500

@app.route("/")
def index():
    return render_template("index.html")


api.add_resource(RequestHandler, "/api")

def runServer():
    app.run(debug=False)