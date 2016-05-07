# encoding: utf-8

import sys, os
import httplib2
from apiclient import discovery
from apiclient.http import MediaFileUpload
import oauth2client
import json
import time



# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = os.environ['CONFIG_DIR'] + 'google_drive_client_secret.json'
APPLICATION_NAME = 'SVVPA'


        
        
def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """    
    credential_path = os.path.join(os.environ['CONFIG_DIR'], 'google-drive-credentials.json')
    store           = oauth2client.file.Storage(credential_path)
    credentials     = store.get()
    if not credentials or credentials.invalid:
        flow            = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME        
        credentials     = oauth2client.tools.run(flow, store)
        print u"[{}] {}: Guardando credenciales en {}".format(datetime.datetime.now(), __file__, credential_path)
    return credentials
        
        
   
def uploadFile(file, mimeType):
    try:
        credentials     = get_credentials()
        http            = credentials.authorize(httplib2.Http())
        service         = discovery.build('drive', 'v3', http=http)
        file_metadata   = { 'name' : os.path.basename(file)}
        media           = MediaFileUpload(file,  mimetype=mimeType)#, resumable=True)
        data            = service.files().create(body = file_metadata,        #TODO: CHECK: en principio solo hace falta la URL
                                                 media_body = media, 
                                                 fields = ('webContentLink')).execute()
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
    file = sys.argv[1]
    
    mimeType = 'image/jpg' if file.endswith('jpg') else 'video/mp4'
    id       = os.path.basename(file).split(".")[0].strip() 
    
    for i in range(20):
        data = uploadFile(sys.argv[1], mimeType)
        
        if data:
            run_query('insert into security(weblink) values({}) where id like \'{}\')
            
            
        else:
            time.sleep(random.randint(20,60))


     
        
      