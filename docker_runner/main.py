import io
import docker
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from onto import Onto
import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

ont_folder = os.getenv('ONTOLOGIES_PATH', '../ontologies')
input_folder = os.getenv('INPUT_PATH', '../input')
ont = Onto.load_from_file(os.path.join(ont_folder, 'dependencies.ont'))
app = Flask(__name__)
CORS(app)
client = docker.from_env()





@app.route('/run', methods=['POST'])
def gen_image():
    img = request.json['img']
    code = request.json['code']
    data_loc = request.json['data']
    container = None
    app.logger.info(client.volumes.get('input'))
    with open(os.path.join(input_folder, 'script'), 'w', encoding='utf-8') as f:
        f.write(code)
    try:
        container = client.containers.run(img,
                                     command=['script'],
                                     volumes={'/input': {'bind': f'/input', 'mode': 'ro'}},
                                     working_dir=f'/input', stderr=True, detach=True)
        container.wait()
    except Exception as e:
        app.logger.info(e)
    try:
        app.logger.info(f"container: {container}")
        app.logger.info(container.logs())
        return jsonify({'result': container.logs()})
    except Exception as e:
        app.logger.info(e)
        return jsonify({'result': 'your script is wrong'})



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
