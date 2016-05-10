# encoding: utf-8

import sys, os
import httplib2
from apiclient import discovery
from apiclient.http import MediaFileUpload
import oauth2client
import json
import time
import datetime
import random



# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = os.environ['CONFIG_DIR'] + 'google_drive_client_secret.json'
APPLICATION_NAME = 'SVVPA'
        
        
def get_credentials():    
    credential_path = os.path.join(os.environ['CONFIG_DIR'], 'google-drive-credentials.json')
    store           = oauth2client.file.Storage(credential_path)
    credentials     = store.get()
    if not credentials or credentials.invalid:
        flow            = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME        
        credentials     = oauth2client.tools.run_flow(flow, store, oauth2client.tools.argparser.parse_args(args=[]))
        print u"[{}] {}: Guardando credenciales en {}".format(datetime.datetime.now(), __file__, credential_path)
    return credentials
        
        
   
def uploadImage(file):
    try:
        credentials     = get_credentials()
        http            = credentials.authorize(httplib2.Http())
        service         = discovery.build('drive', 'v3', http=http)
        file_metadata   = { 'name' : os.path.basename(file), 'parents' : ["0Bwse_WnehFNKWERoYS1wYnMwVVk"]}
        media           = MediaFileUpload(file,  mimetype='image/jpg')#, resumable=True)
        data            = service.files().create(body = file_metadata,        #TODO: CHECK: en principio solo hace falta la URL
                                                 media_body = media).execute()#, 
                                                 #fields = ('id', 'webViewLink')).execute()
        #print ('File ID: %s' % data.get('id'))
        return data
    
    except Exception as e:
        print u"[{}] {}: ERROR! Hubo un error inesperado al subir el archivo a google drive:\n{}".format(datetime.datetime.now(), __file__, repr(e))
    
    
def uploadVideo(file):
    try:
        credentials     = get_credentials()
        http            = credentials.authorize(httplib2.Http())
        service         = discovery.build('drive', 'v3', http=http)
        file_metadata   = { 'name' : 'SVVPA/videos' + os.path.basename(file)}
        media           = MediaFileUpload(file,  mimetype='video/mp4', resumable=True)
        request         = service.files().create(body = file_metadata,
                                                 media_body = media, 
                                                 fields = ('id'))
                                                 
        data = None
        while data is None:
            status, data = request.next_chunk()                                               
        #print ('File ID: %s' % data.get('id'))
        return data
    
    except Exception as e:
        print u"[{}] {}: ERROR! Hubo un error inesperado al subir el archivo a google drive:\n{}".format(datetime.datetime.now(), __file__, repr(e))




def run_query(self, query=''): 
    datos = ['localhost', os.environ['MYSQL_USER'], os.environ['MYSQL_PASS'], os.environ['MYSQL_DB']] 
    
    conn = MySQLdb.connect(*datos) # Conectar a la base de datos 
    cursor = conn.cursor()         # Crear un cursor 
    cursor.execute(query)          # Ejecutar una consulta 
    
    if query.upper().startswith('SELECT'): 
        data = cursor.fetchall()   # Traer los resultados de un select 
    else: 
        conn.commit()              # Hacer efectiva la escritura de datos 
        data = None 
    
    cursor.close()                 # Cerrar el cursor 
    conn.close()                   # Cerrar la conexión 
    
    return data            
        


      
         
         
if __name__ == "__main__":
    #TEMPORAL!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #file = '/home/dlopez/Downloads/2016_04_04_15_11_40_8745_14_52_234_566_305_1.jpg' #sys.argv[1]
    file = '/home/dlopez/temp/video.mp4' #sys.argv[1]
    
    id   = os.path.basename(file).split(".")[0].strip()
        
    for i in range(20):
        if file.endswith('.jpg'):
            data = uploadImage(file)
            
        else:
            data = uploadVideo(file)
        
        if data:
            break
        else:
            time.sleep(random.randint(20,60))
    
    #TODO: usar service.get(id) para obtener todos los datos del archivo y meter los interesantes en mysql
        
    if file.endswith('.jpg'):
        query = 'update images set uid={}, link={}, width={}, height={} where id like \'{}\''.format(data['id'],
                                                                                                   data['webContentLink'],
                                                                                                   data['imageMediaMetadata.width'],
                                                                                                   data['imageMediaMetadata.height'],
                                                                                                   id )
        
    else:
        query = 'update videos set uid={}, link={}, width={}, height={} where id like \'{}\''.format(data['id'],
                                                                                                   data['webContentLink'],
                                                                                                   data['videoMediaMetadata.width'],
                                                                                                   data['videoMediaMetadata.height'],
                                                                                                   id )
        
    run_query(query)
        


     
        
        