from  flask import Flask, jsonify, request
import json
from monit import get_report, get_all_reports, get_last_report, get_avg_of_report, create_report
import argparse

app = Flask(__name__)
directory  = "/var/monit"

#Get all reports names
@app.route('/api/v1.0/list', methods=['GET'])
def get_reports():
    return jsonify({"reports": get_all_reports(directory)})

#Get last report content
@app.route('/api/v1.0/last', methods=['GET'])
def get_last():
    return jsonify(get_last_report(directory))

#Get report content by name if name is provided
@app.route('/api/v1.0/report', methods=['GET'])
def name_required():
    return jsonify({"error": "Name required"})

@app.route('/api/v1.0/report/<string:name>', methods=['GET'])
def get_report_by_name(name):
    if name.endswith(".json"):
        return jsonify(get_report(name, directory))
    else:
        return jsonify(get_report(f"{name}.json", directory))
    

#Get reports younger than hours if hours is provided
@app.route('/api/v1.0/avg', methods=['GET'])
def hours_required():
    return jsonify({"error": "Hours required"})

@app.route('/api/v1.0/avg/<int:hours>', methods=['GET'])
def get_avg(hours):
    return jsonify(get_avg_of_report(hours, directory))

@app.route('/api/v1.0/check', methods=['GET'])
def check():
    create_report()
    return jsonify({"report": get_last_report(directory)})


if (__name__ == "__main__"):
    # app.run(debug=True, port=5000)

    argparser = argparse.ArgumentParser()
    argparser.add_argument("-p", "--port", help="Port to listen on", type=int, default=5000)
    argparser.add_argument("-a", "--address", help="Address to listen on")
    args = argparser.parse_args()
    if not args.address or not args.port:
        raise Exception("Address and port required")
    
    app.run(host=args.address, port=args.port, debug=True)