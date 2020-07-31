import os
import binascii
import storage
import numpy as np

from flask import current_app


def save_file(file, name: str = None) -> str:
    id = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
    extension = get_extension(file)
    filename = f'{file.filename}'
    temp_file_path = get_temp_filepath(filename)
    check_file_and_create()
    file.save(temp_file_path)
    split_file(temp_file_path,filename,id)
    os.unlink(temp_file_path)
    return id, file.filename

def delete_file(id: str):
    filename = get_filename_by_id(id)
    index = [i for i,value in enumerate(storage.files) if value['id']==id][0]
    n_chunks = storage.files[index]['chunks']
    print(n_chunks)
    for i in range(1,n_chunks+1):
        n_node=1
        chunk_path=''
        while 1:
            if n_node>current_app.config['NODE_COUNT']:
                break
            chunk_path = os.path.join(current_app.config['UPLOAD_FOLDER'],f'node_{n_node}',f'{get_filename_without_extension(filename)}_{i}{get_extension_from_filename(filename)}')
            if os.path.isfile(chunk_path):
                print(chunk_path)
                os.unlink(chunk_path)
            else:
                n_node=n_node+1
    
def check_file_and_create():
    for i in range(1,current_app.config['NODE_COUNT']+1):
        node_path = os.path.join(current_app.config['UPLOAD_FOLDER'],f'node_{i}')
        if not os.path.isdir(node_path):
            os.mkdir(node_path)
    temp_path =os.path.join(current_app.config['UPLOAD_FOLDER'],'temp')
    if not os.path.isdir(temp_path):
        os.mkdir(temp_path)
    temp_download_path = os.path.join(current_app.config['UPLOAD_FOLDER'],'temp_download')
    if not os.path.isdir(temp_download_path):
        os.mkdir(temp_download_path)

def get_temp_filepath(filename: str)->str:
    return os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp',f'{filename}')

def get_filepath(filename: str, folder='uploads') -> str:
    return os.path.join(current_app.config['UPLOAD_FOLDER'], f'{filename}')


def get_basename(file: str) -> str:
    filename = file
    return os.path.split(filename)[1]


def get_extension(file) -> str:
    filename = file.filename
    return os.path.splitext(filename)[1]

def get_extension_from_filename(filename: str)->str:
    return os.path.splitext(filename)[1]

def get_filename_without_extension(filename: str)->str:
    return filename.rsplit('.',1)[0]

def get_path(id: str, folder: str = 'uploads') -> str:
    result = [x for x in filter(lambda x: x['id'] == id, storage.files)]
    if len(result) == 0:
        return None
    filename = result[0]['file_name']
    print(result[0]['file_name'])
    return get_filepath(filename)

def get_filename_by_id(id:str)->str:
    result = [x for x in filter(lambda x: x['id'] == id, storage.files)]
    if len(result) == 0:
        return None
    return result[0]['file_name']

def split_file(file_path: str,filename: str,id: str):
    # saving files into chunks
    partnum=0
    input = open(file_path,'rb')
    while 1:
        chunk = input.read(current_app.config['SIZE_PER_SLICE'])
        if not chunk: 
            break
        # getting size of nodes to distribute equaly
        size_array=np.array([],dtype=int)
        for i in range(1,current_app.config['NODE_COUNT']+1):
            node_path= os.path.join(current_app.config['UPLOAD_FOLDER'],f'node_{i}')
            size = len([name for name in os.listdir(node_path) if os.path.isfile(os.path.join(node_path, name))])
            size_array = np.append(size_array,size)
        smallest_node=size_array.argsort()[:current_app.config['REDUNDANCY_COUNT']+1]
        partnum=partnum+1
        for n in smallest_node:
            filename_without_extension= get_filename_without_extension(filename)
            extension = get_extension_from_filename(filename)
            chunk_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'],f'node_{n+1}',f'{filename_without_extension}_{partnum}{extension}')
            fileobj = open(chunk_file_path,"wb")
            fileobj.write(chunk)
            fileobj.close()
    input.close()
    storage.files.append({
                'id': id,
                'file_name': filename
            })
    index = [i for i,value in enumerate(storage.files) if value['file_name']==filename][0]
    storage.files[index]['chunks']=partnum

def join_file(id:str)->str:
    output_filename = get_filename_by_id(id)
    output_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'],'temp_download',output_filename)
    print(output_filepath)
    index = [i for i,value in enumerate(storage.files) if value['file_name']==output_filename][0]
    n_chunks = storage.files[index]['chunks']
    output=open(output_filepath,'wb')
    for i in range(1,n_chunks+1):
        n_node=1
        chunk_path=''
        while 1:
            if n_node>current_app.config['NODE_COUNT']:
                print(f'{i} part not found')
                return None
            chunk_path = os.path.join(current_app.config['UPLOAD_FOLDER'],f'node_{n_node}',f'{get_filename_without_extension(output_filename)}_{i}{get_extension_from_filename(output_filename)}')
            if os.path.isfile(chunk_path):
                break
            else:
                n_node=n_node+1
    
        fileobj = open(chunk_path,'rb')
        while 1:
            filebytes = fileobj.read(current_app.config['SIZE_PER_SLICE'])
            if not filebytes:
                break
            output.write(filebytes)
        fileobj.close()
    output.close()
    return output_filepath

def check_file_if_present(id: str)->bool:
    arr = [i for i,value in enumerate(storage.files) if value['id']==id]
    if len(arr)==0:
        return False
    return True

def check_file_if_present_by_name(filename: str)->bool:
    arr = [i for i,value in enumerate(storage.files) if value['file_name']==filename]
    if len(arr)==0:
        return False
    return True