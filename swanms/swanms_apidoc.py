import json
import ast
import inspect
import os
import subprocess
import time

class swanms_apidoc:
    def __init__(self,notebook):
        self.notebook = notebook
        self.docdir = os.getcwd() + '/static/'+self.notebook.replace('.ipynb','doc').split('/')[-1]
        self.pyfile = self.notebook.replace('ipynb','py')
        with open(notebook) as json_file:  
            data = json.load(json_file)
            docstrings=[]
            for cell in data['cells']:
                source = ''
                source = source.join(cell['source'])
                source = inspect.cleandoc(source)
                try:
                    cell_node = ast.parse(source)
                    docstring = ast.get_docstring(cell_node)
                    if docstring is not None:
                        docstrings.append(docstring)
                except:
                    pass #no docstrings found on the cell
            with open(self.pyfile,'wt', encoding='utf-8') as outputfile:
                for docstring in docstrings:
                    outputfile.write("\"\"\"\n"+docstring+"\"\"\"\n")
                outputfile.close()

    def gendoc(self,timeout=1,maxtries=5):
        try:
            os.mkdir('static')
            print(" * Static Directory " , self.docdir ,  " created ") 
        except FileExistsError:
            #Is this is happening then restart the microservices in the folder
            print(" * Warning! Static Directory " , self.docdir ,  " already exists")
            
        process = subprocess.Popen(['apidoc', '-f',self.pyfile,'-o', self.docdir ], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT)
        counter=0
        while process.poll() is None:
            time.sleep(timeout)
            counter = counter+1
            if counter == maxtries:
                process.kill()
                break

    def get_docdir(self):
        return self.docdir






    
