from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
import time
import os
from threading import Thread
import subprocess
from settings import DEFAULT_COMPOSER_LOG, HOST, PORT
from example_project_data import project_data

app = Flask(__name__)
app.debug = True
CORS(app)


def add_headers(response, http_code):
    response = jsonify(response), http_code
    response = make_response(response)
    response.headers['Access-Control-Allow-Origin'] = "*"
    response.headers['content-type'] = "application/json"
    return response


def check_expected_containers(ps_output, project):
    all_running = True
    for container_name in project_data[project]["expected_containers"]:
        if (str(ps_output).find(container_name)) == -1:
            all_running = False
    return all_running


def docker_log(log_file=DEFAULT_COMPOSER_LOG):
    subprocess.check_call('docker-compose logs -f -t >> ' + log_file, shell=True)


def docker_timer(location, timeout, log_file=DEFAULT_COMPOSER_LOG):
    os.chdir(location)
    docker_log_thread = Thread(target=docker_log, args=(log_file,))
    docker_log_thread.start()
    time.sleep(1)
    while time.time() - os.path.getmtime(log_file) < timeout:
        time.sleep(1)
    subprocess.call('docker-compose down', shell=True)
    return


@app.route("/", methods=['GET'])
def list_projects():
    return add_headers(project_data, 200)


@app.route("/start", methods=['POST'])
def start():
    try:
        project_name = request.json['project']
    except KeyError:
        return add_headers(response="'project' field missing from JSON", http_code=201)
    try:
        os.chdir(project_data[project_name]["location"])
    except KeyError:
        return add_headers(response="Project not found", http_code=201)
    try:
        subprocess.call('docker-compose up -d', shell=True)
        time.sleep(1)
        ps = subprocess.check_output('docker ps', shell=True)
        res = check_expected_containers(ps, "ocr")
    except:
        return add_headers(response="Error during docker-compose call.", http_code=500)
    if 'timeout' in request.json:
        timeout = request.json['timeout']
        log_file = request.json['log_file'] if 'log_file' in request.json else DEFAULT_COMPOSER_LOG
        docker_timer_thread = Thread(target=docker_timer, args=(project_data[project_name]["location"], timeout, log_file))
        docker_timer_thread.start()
    return add_headers(response=res, http_code=200)


@app.route("/stop", methods=['POST'])
def stop():
    if "project" in request.json:
        project = request.json['project']
    try:
        os.chdir(project_data[project]["location"])
    except KeyError:
        return add_headers(response="Project not found", http_code=201)
    try:
        subprocess.call('docker-compose down', shell=True)
    except:
        return add_headers(response="Error during docker-compose call.", http_code=500)
    return add_headers(response=True, http_code=200)


if __name__ == "__main__":
    app.run(host=HOST, port=PORT)