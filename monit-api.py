from  flask import Flask, jsonify, request, redirect
import json
from monit import get_report, get_all_reports, get_last_report, get_avg_of_report, create_report
import argparse

app = Flask(__name__)
directory  = "./monit"

@app.route('/api/v1.0', methods=['GET'])
def index():
    return jsonify({"version": "1.0"})

@app.route('/api/v1.0/usage', methods=['GET'])
def usage():
    return jsonify({"usage": {
        "get_reports": "/api/v1.0/list",
        "get_last_report": "/api/v1.0/get/last",
        "get_report": "/api/v1.0/get/report/<string:name>",
        "get_avg": "/api/v1.0/get/avg/<int:hours>",
        "check": "/api/v1.0/check"
    }})

#Get all reports names
@app.route('/api/v1.0/list', methods=['GET'])
def get_reports():
    return jsonify({"reports": get_all_reports(directory)})

#Get last report content
@app.route('/api/v1.0/get/last', methods=['GET'])
def get_last():
    return jsonify(get_last_report(directory))

#Get report content by name if name is provided
@app.route('/api/v1.0/get/report/<string:name>', methods=['GET'])
def get_report_by_name(name):
    report = get_report(name, directory) if name.endswith(".json") else get_report(f"{name}.json", directory)
    if not name:
        return jsonify({"error": "Report name required"})
    if name.endswith(".json"):
        return jsonify({"error": "Report name without extension"}) if report is not None else jsonify({"error": "Report not found"})
    else:
        return jsonify(get_report(f"{name}.json", directory)) if report is not None else jsonify({"error": "Report not found"})

#Get reports younger than hours if hours is provided
@app.route('/api/v1.0/get/avg/<int:hours>', methods=['GET'])
def get_avg(hours):
    report = get_avg_of_report(hours, directory)
    if not hours:
        return jsonify({"error": "Hours required"})
    return jsonify(report) if report is not None else jsonify({"error": "No reports found for this period"})


@app.route('/api/v1.0/check', methods=['GET'])
def check():
    create_report()
    return jsonify({"report": get_last_report(directory)})

@app.route('/<path:dummy>')
def redirect_error(dummy):
    return redirect("/api/v1.0/usage", code=302)

@app.errorhandler(404)
def page_not_found(e):
    return redirect("/api/v1.0/usage", code=302)

if (__name__ == "__main__"):
    # app.run(debug=True, port=5000)

    argparser = argparse.ArgumentParser()
    argparser.add_argument("-p", "--port", help="Port to listen on", type=int, default=5000)
    argparser.add_argument("-a", "--address", help="Address to listen on")
    args = argparser.parse_args()
    if not args.address or not args.port:
        raise Exception("Address and port required")
    
    app.run(host=args.address, port=args.port, debug=True)