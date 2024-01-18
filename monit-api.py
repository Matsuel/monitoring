from  flask import Flask, jsonify, request
import json
from monit import get_report, get_all_reports, get_last_report, get_reports_younger_than, get_avg_of_report, create_report_directory, create_config_directory, log

app = Flask(__name__)
directory  = "./monit"

@app.route('/api/v1.0/list', methods=['GET'])
def get_reports():
    return jsonify({"reports": get_all_reports(directory)})

@app.route('/api/v1.0/last', methods=['GET'])
def get_last():
    return jsonify(get_last_report(directory))

@app.route('/api/v1.0/report', methods=['GET'])
def name_required():
    return jsonify({"error": "Name required"})

@app.route('/api/v1.0/report/<string:name>', methods=['GET'])
def get_report_by_name(name):
    if name.endswith(".json"):
        return jsonify(get_report(name, directory))
    else:
        return jsonify(get_report(f"{name}.json", directory))
    


if (__name__ == "__main__"):
    app.run(debug=True, port=5000)