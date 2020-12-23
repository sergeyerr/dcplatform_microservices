from onto import Onto
import os
from shutil import copyfile

ontologies_folder = os.getenv('ONTOLOGIES_PATH', '../ontologies')

upload_folder = os.getenv('UPLOADS_PATH', 'uploads')

def get_methods(ont):
    methods_ids = set()
    for rel in ont.links():
        if rel['name'] == 'use':
            methods_ids.add(rel['source_node_id'])
    res = []
    for node in ont.nodes():
        if node['id'] in methods_ids:
            res.append(node)
    return [x['name'] for x in res]

def get_params(method):
    filename = method + '.ont'
    ont = Onto.load_from_file(os.path.join(ontologies_folder, filename))
    method_node = ont.get_nodes_by_name(method)[0]
    params_nodes = []
    for param in ont.get_nodes_linked_from(method_node, 'has'):
        params_nodes.append(param)
    res = []
    for param in params_nodes:
        tmp = {'name': param['name']}
        tmp['type'] = ont.get_nodes_linked_from(param, 'type')[0]['name']
        tmp['domain'] = ont.get_nodes_linked_from(param, 'domain')[0]['name']
        tmp['value'] = ont.get_nodes_linked_from(param, 'default')[0]['name']
        tmp['class'] = ont.get_nodes_linked_from(param, 'is_a')[0]['name']
        res.append(tmp)
    return res


def get_dependencies_for_method(ont, method):
    method_node = ont.get_nodes_by_name(method)[0]
    while not ont.is_node_of_type(method_node, 'библиотека'):
        method_node = ont.get_nodes_linked_from(method_node, 'a_part_of')[0]
    return [method_node['name']]



from flask import Flask, jsonify, request
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

@app.route('/get_methods')
def get_meth():
    ont = Onto.load_from_file(os.path.join(ontologies_folder, 'methods.ont'))
    return jsonify(get_methods(ont))


@app.route('/get_params/<string:method>/')
def get_parms(method):
    return jsonify(get_params(method))


@app.route('/get_libraries/<string:method>/')
def get_libraries(method):
    ont = Onto.load_from_file(os.path.join(ontologies_folder, 'methods.ont'))
    return jsonify(get_dependencies_for_method(ont, method))


@app.route('/upload_methods_ontology', methods=['POST'])
def upload_methods_ontology():
    file = request.files['file']
    file.save(os.path.join(upload_folder, file.filename))
    Onto.load_from_file(os.path.join(upload_folder, file.filename))
    os.remove(os.path.join(ontologies_folder, 'methods.ont'))
    copyfile(os.path.join(upload_folder, file.filename), os.path.join(ontologies_folder, 'methods.ont'))
    return 'ok', 200


@app.route('/upload_params_ontology/<string:method>/', methods=['POST'])
def upload_params_ontology(method):
    file = request.files['file']
    file.save(os.path.join(upload_folder, file.filename))
    Onto.load_from_file(os.path.join(upload_folder, file.filename))
    os.remove(os.path.join(ontologies_folder, method + '.ont'))
    copyfile(os.path.join(upload_folder, file.filename), os.path.join(ontologies_folder, method + '.ont'))
    return 'ok', 200


@app.route('/upload_dependencies_ontology', methods=['POST'])
def upload_dependencies_ontology():
    file = request.files['file']
    file.save(os.path.join(upload_folder, file.filename))
    Onto.load_from_file(os.path.join(upload_folder, file.filename))
    os.remove(os.path.join(ontologies_folder, 'dependencies.ont'))
    copyfile(os.path.join(upload_folder, file.filename), os.path.join(ontologies_folder, 'dependencies.ont'))
    return 'ok', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)