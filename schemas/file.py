from werkzeug.datastructures import FileStorage
from marshmallow import Schema, fields


class FileStorageField(fields.Field):

    default_error_messages = {
        "invalid": "Not a valid Image"
    }

    def _deserialize(self, value, *args, **kwargs):
        if value is None:
            return None

        if not isinstance(value, FileStorage):
            self.fail("invalid")

        return value


class FileSchema(Schema):
    file = FileStorageField(required=True)
