import os
import subprocess
from multiprocessing import Process, Queue
from flask import Flask, render_template
from flask_restful import Resource, Api, reqparse
import time
import socket

try:
    from swanms_apidoc import swanms_apidoc
    from nbstreamreader import NonBlockingStreamReader
except:
    from .swanms_apidoc import swanms_apidoc
    from .nbstreamreader import NonBlockingStreamReader

app = Flask(__name__, static_folder=os.getcwd()+'/static',  template_folder=os.getcwd()+'/templates')
api = Api(app)

print(' * Static Dir = '+os.getcwd()+'/static')
print(' * Templates Dir = '+os.getcwd()+'/templates')

parsersubmit = reqparse.RequestParser()
parsersubmit.add_argument('notebook')
parsersubmit.add_argument('code')

class swanms_server:
    services={}
    microservicedir = './microservices/'
    submit_timeout = 20
    apidocs_paths = []
    def __init__(self):
        try:
            os.mkdir(self.microservicedir)
            print(" * Directory " , os.getcwd()+'/'+self.microservicedir ,  " created ") 
        except FileExistsError:
            #Is this is happening then restart the microservices in the folder
            print(" * Warning! Directory " , os.getcwd()+'/'+self.microservicedir ,  " already exists")

    def launcher(self,notebook):
        process = subprocess.Popen(['jupyter', 'kernelgateway','--ip=%s'%socket.gethostbyname_ex(socket.gethostname())[2][0] ,'--KernelGatewayApp.api="kernel_gateway.notebook_http"','--KernelGatewayApp.seed_uri="%s"'%(swanms_server.microservicedir+notebook)], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT)
        swanms_server.services[notebook]={'process':process}
        return process
    
    class submit(Resource):
        def post(self):
            args = parsersubmit.parse_args()
            with open(swanms_server.microservicedir + args.notebook,'wt', encoding='utf-8') as f:
                f.write(args.code)
                f.close()
            print(' * Sumitting '+args.notebook)
            process=swanms_server.launcher(self,notebook=args.notebook)
            stdout_nbsr=NonBlockingStreamReader(process.stdout)
            stdout=''
            time.sleep(swanms_server.submit_timeout)
            chunk=stdout_nbsr.readline(swanms_server.submit_timeout)
            while chunk != None:
                stdout=stdout+chunk.decode("utf-8")
                chunk=stdout_nbsr.readline(0.5)
            # stderr_nbsr=NonBlockingStreamReader(process.stderr)
            stderr=''
            # chunk=stderr_nbsr.readline(swanms_server.submit_timeout)
            # while chunk != None:
            #     stderr=stderr+chunk.decode("utf-8")
            #     chunk=stderr_nbsr.readline(0.5)
            
            #if process.poll() is None: #the process is alive
            apidoc = swanms_apidoc(swanms_server.microservicedir + args.notebook)
            apidoc.gendoc()
            docdir=apidoc.get_docdir().split('/')[-1]
            swanms_server.apidocs_paths.append(docdir)

            return {'pid':process.pid,'stdout':stdout,'stderr':stderr}
            

@app.route('/apidocs/')
def apidocs():
    #cleaning the list of repeated in case was sent the same notebook again
    apidocs_paths = []
    for path in set(swanms_server.apidocs_paths):
        apidocs_paths.append(path+'/index.html')
    return render_template('apidocs.html', apidocs=apidocs_paths)

@app.route('/models/')
def models():
    #cleaning the list of repeated in case was sent the same notebook again
    swanms_server.models_paths = ["models/model.h5"]
    return render_template('models.html', models=swanms_server.models_paths)

api.add_resource(swanms_server.submit, '/submit')

def start_server():
    server=swanms_server()
    app.run(host=socket.gethostname(),port=8888,debug=True)

if __name__ == '__main__':
    start_server()
