from flask import Flask,  request, jsonify
from flask_cors import CORS
from jinja2 import Template
from onto import Onto
import os

scripts_dir = os.getenv('SCRIPTS_DIR', 'templates')
ont_folder = os.getenv('ONTOLOGIES_PATH', '../ontologies')
app = Flask(__name__)
CORS(app)

def get_dependencies_for_method(ont, method):
    method_node = ont.get_nodes_by_name(method)[0]
    while not ont.is_node_of_type(method_node, 'библиотека'):
        method_node = ont.get_nodes_linked_from(method_node, 'a_part_of')[0]
    return method_node['name']


@app.route('/get_script/<string:method>/')
def get_meth(method):
    if os.path.exists(os.path.join(scripts_dir, method)):
        with open(os.path.join(scripts_dir, method), 'r', encoding='utf-8') as f:
            return jsonify({'script': f.read()})
    else:
        ont = Onto.load_from_file(os.path.join(ont_folder, 'methods.ont'))
        base_lib = get_dependencies_for_method(ont, method)
        print(base_lib)
        if os.path.exists(os.path.join(scripts_dir, base_lib)):
            with open(os.path.join(scripts_dir, base_lib), 'r', encoding='utf-8') as f:
                tmp = f.read()
            prefix, method_name = method.rsplit('.', 1)
            template = Template(tmp)
            return jsonify({'script': template.render(prefix=prefix, method_name=method_name)})
        else:
            return jsonify({'script': 'Своими силами прочитайте данные из $(INPUT_FOLDER)/data \n и параметры из $(INPUT_FOLDER)/params.json'})


@app.route('/write_script/<string:method>/', methods=['POST'])
def write_script(method):
    code = request.json['script']
    with open(os.path.join(scripts_dir, method), 'w', encoding='utf-8') as f:
        f.write(code)
    return 'ok', 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)