import requests
import sys
from pathlib import Path
import argparse
import json
class swanms_submit:
    def __init__(self,notebook):
        self.notebook = notebook
        if not Path(self.notebook).is_file():
            print('Notebook %s not found.'%self.notebook,sys.stderr)
            sys.exit(1)
        self.code = None


    def load_code(self):
        with open(self.notebook,'r') as f:
            self.code = f.read()
            f.close()
        return self.code

    def send(self,url):
        # TODO: put an ID to the submit
        req=requests.post(url, data={'notebook': self.notebook, 'code': self.code})
        if req.status_code == 200:
            print('Status = ',req.status_code)
            print('Reason = ',req.reason)
            payload=json.loads(req.text)
            print('PID = ',payload['pid'])
            print(payload['stdout'])
            if payload['stderr'] != '':
                print('STDERR = ',payload['stderr'])
            print('SWAN Microservice Started.')            
        else:
            print('Status = ',req.status_code)
            print('Reason = ',req.reason)
            payload=json.loads(req.text)
            print('PID = ',payload['pid'])
            print(payload['stdout'])
            if payload['stderr'] != '':
                print('STDERR = ',payload['stderr'])
            print('SWAN Microservice Fail.')            


def submit():
    parser = argparse.ArgumentParser(description='swanms_submit help to send notebook code to microservices endpoint.',epilog='Use swamms_client to see the status of your micro service.')
    parser.add_argument('--notebook',help='Notebook file.',action="store", required=True)
    parser.add_argument('--server',help='Server endpoint',action="store", required=True)
    args = parser.parse_args()
    submitter=swanms_submit(notebook=args.notebook)
    submitter.load_code()
    submitter.send(args.server)


if __name__ == '__main__':
    submit()
