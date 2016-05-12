# encoding: utf-8

import sys, os, traceback
import httplib2
from apiclient import discovery
from apiclient.http import MediaFileUpload
import oauth2client
import time
import datetime
import random
import MySQLdb



# If modifying these scopes, delete your previously saved credentials
SCOPES = 'https://www.googleapis.com/auth/drive.file'
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
        print u"[{}] {}: Subiendo imagen {} a google drive".format(datetime.datetime.now(), __file__, file)
        credentials     = get_credentials()
        http            = credentials.authorize(httplib2.Http())
        service         = discovery.build('drive', 'v3', http=http)
        file_metadata   = { 'name' : os.path.basename(file), 'parents' : ["0Bwse_WnehFNKT0d2Wmp4cGhKSWs"]}
        media           = MediaFileUpload(file,  mimetype='image/jpg')#, resumable=True)
        data            = service.files().create(body = file_metadata, 
                                                 media_body = media, 
                                                 fields = 'id, imageMediaMetadata(height,width), webContentLink').execute()#, 
                                                 #fields = ('id', 'webViewLink')).execute()
        data['metadata'] = data.pop('imageMediaMetadata')
        data['link'] = data.pop('webContentLink')
        return data
    
    except Exception as e:
        print u"[{}] {}: ERROR! Hubo un error inesperado al subir el archivo a google drive:".format(datetime.datetime.now(), __file__)
        traceback.print_exc()

    
def uploadVideo(file):
    try:
        print u"[{}] {}: Subiendo video {} a google drive".format(datetime.datetime.now(), __file__, file)
        credentials     = get_credentials()
        http            = credentials.authorize(httplib2.Http())
        service         = discovery.build('drive', 'v3', http=http)
        file_metadata   = { 'name' : os.path.basename(file), 'parents' : ["0Bwse_WnehFNKWERoYS1wYnMwVVk"]}
        media           = MediaFileUpload(file,  mimetype='video/mp4', resumable=True)
        request         = service.files().create(body = file_metadata,
                                                 media_body = media, 
                                                 fields = 'id,videoMediaMetadata(height,width),webViewLink')
                                                 
        data = None
        while data is None:
            status, data = request.next_chunk()                                               
        #print ('File ID: %s' % data.get('id'))
        data['metadata'] = data.pop('videoMediaMetadata')
        data['link'] = data.pop('webViewLink')
        return data
    
    except Exception as e:
        print u"[{}] {}: ERROR! Hubo un error inesperado al subir el archivo a google drive:".format(datetime.datetime.now(), __file__)
        traceback.print_exc()




def run_query(query=''): 
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
        


def main(file):    
    id   = os.path.basename(file).split(".")[0].strip()
        
    for i in range(20):
        if file.endswith('.jpg'):
            data = uploadImage(file)
            table = 'images'
            
        else:
            data = uploadVideo(file)
            table = 'videos'
        
        if data:
            break
        
        else:
            print >> sys.stderr, u"[{}] {}: ERROR! Hubo un problema al subir el archivo {} a google drive. Reintento: {}".format(datetime.datetime.now(), __file__, file, i)
            time.sleep(random.randint(20,60))
    
    query = "update {} set uid='{}', link='{}', width={}, height={} where id like '{}'".format(table,
                                                                                               data['id'],
                                                                                               data['link'],
                                                                                               data['metadata']['width'],
                                                                                               data['metadata']['height'],
                                                                                               id )
        
    run_query(query)
    return data['link']
      
         
         
if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))


     
        
        