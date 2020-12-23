import io
import docker
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from onto import Onto

ont_folder = os.getenv('ONTOLOGIES_PATH', '../ontologies')
app = Flask(__name__)
CORS(app)
ont = Onto.load_from_file(os.path.join(ont_folder, 'dependencies.ont'))
client = docker.from_env()


def get_required_technologies(ont, deps):
    q = []
    visited = set()
    base_tech = []
    run_commands = []
    for d in deps:
        d = ont.get_nodes_by_name(d)[0]
        if len(ont.get_nodes_linked_to(d, 'requires')) == 0:
            q.insert(0, d)
        else:
            q.append(d)
    while len(q) > 0:
        tmp = q.pop(0)
        if tmp['id'] in visited:
            continue
        visited.add(tmp['id'])
        run_commands.append(tmp['attributes']['install_cmd'])
        reqs = ont.get_nodes_linked_from(tmp, 'requires')
        for r in reqs:
            if ont.is_node_of_type(r, 'base_technology'):
                if r not in base_tech:
                    base_tech.append(r)
            else:
                q.insert(0, r)
                # сделать нормальную топ сортировку через dfs и приоритеты
    return base_tech, run_commands[::-1]


def get_best_image(base_tech, ont):
    docker_image_node = ont.get_nodes_by_name('docker_image')[0]
    images = ont.get_nodes_linked_to(docker_image_node, 'is_a')
    best = None
    best_res = 1000000
    for image in images:
        ok_flag = True
        for tech in base_tech:
            if not ont.has_link(image['id'], tech['id'], 'provide'):
                ok_flag = False
                break
        if ok_flag:
            count = len(ont.get_nodes_linked_from(image, 'provide'))
            if count < best_res:
                best_res = count
                best = image
    return best


def get_dockerfile(deps):
    req_tech, run_commands = get_required_technologies(ont, deps)
    image = get_best_image(req_tech, ont)
    res = f"FROM {image['name']}\n"
    for cmd in run_commands:
        res = res + (f'RUN {cmd}\n')
    entrypoint_str = '","'.join(image['attributes']['entrypoint'].split())
    entrypoint_str = f'["{entrypoint_str}"]'
    res += 'ENTRYPOINT' + ' ' + entrypoint_str
    return res


@app.route('/gen_image_script', methods=['POST'])
def gen_image():
    deps = request.json
    dockerfile = get_dockerfile(deps)
    print(dockerfile)
    file_obj = io.BytesIO(str.encode(dockerfile))
    img, logs = client.images.build(fileobj=file_obj)
    return jsonify({'img_code': img.id.split(':')[1]})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
