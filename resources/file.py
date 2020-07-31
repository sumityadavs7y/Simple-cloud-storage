import os
import traceback
from flask_restful import Resource
from flask import request, send_file, send_from_directory, current_app

from schemas.file import FileSchema
from libs import file_helper
import storage

file_schema = FileSchema()


class FileUpload(Resource):
    @classmethod
    def put(cls):
        data = file_schema.load(request.files)
        if data['file'].filename == '':
            return {'message': 'file not added'}, 400
        if file_helper.check_file_if_present_by_name(data['file'].filename):
            return {'message': 'file already exist'}
        try:
            id, filename = file_helper.save_file(data['file'])
            return {'id': id}, 201
        except:
            traceback.print_exc()
            return {'message': 'Internal Server error'}, 500


class File(Resource):
    @classmethod
    def get(cls, id: str):
        if file_helper.check_file_if_present(id):
            file_path = file_helper.join_file(id)
            if file_path is not None:
                return send_from_directory(directory=file_path.rsplit('/', 1)[0], filename=file_path.rsplit('/', 1)[1])
                # return send_file(file_path)
            else:
                return {'message': 'file got corrupted'}, 400
        else:
            return {'message': 'file not found'}, 404
    @classmethod
    def delete(cls, id: str):
        try:
            result = [x for x in filter(
                lambda x: x['id'] == id, storage.files)]
            if len(result) == 0:
                return {'message': 'file not found'}, 404
            # os.remove(file_helper.get_path(id))
            file_helper.delete_file(id)
            res = list(filter(lambda x: x['id'] == id, storage.files))[0]
            index = storage.files.index(res)
            del storage.files[index]
            return {'message': 'file deleted'}, 200
        except:
            traceback.print_exc()
            return {'message': 'file delete failed'}, 500


class Files(Resource):
    @classmethod
    def get(cls):
        return storage.files, 200
