import os
import json
import shutil
from flask import Flask, jsonify, url_for
from flask_restful import Api
from flask_cors import CORS
from marshmallow import ValidationError

from resources.file import FileUpload, File, Files
from ma import ma
from libs import file_helper

app = Flask(__name__)

CORS(app)

# app.config.from_json('config.json')
with open('config.json') as config_file:
    con = json.load(config_file)
    for key, val in con.items():
        app.config[key.upper()] = val

app.config['UPLOAD_FOLDER'] = os.path.abspath(app.config['STORAGE_DIRECTORY'])
api = Api(app)


@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify(err.messages), 400


@app.before_first_request
def empty_folder():
    folder = app.config['UPLOAD_FOLDER']
    # make folder empty
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    # CREATING FOLDERS
    for i in range(1,app.config['NODE_COUNT']+1):
        os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'],f'node_{i}'))
    # creating temp folder
    file_helper.check_file_and_create()

api.add_resource(FileUpload, "/files")
api.add_resource(File, '/files/<string:id>')
api.add_resource(Files, '/files/list')

if __name__ == "__main__":
    ma.init_app(app)
    app.run(port=5000, debug=True)
