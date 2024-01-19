from  flask import Flask, jsonify, redirect, abort
import json
from monit import get_report, get_all_reports, get_last_report, get_avg_of_report, create_report,get_all_reports_content
import argparse
import os

app = Flask(__name__)
directory  = "./monit" if os.name == "nt" else "/var/monit"
directory_log = "./log" if os.name == "nt" else "/var/log/monit"
directory_config = "." if os.name == "nt" else "/etc/monit"

@app.route('/', methods=['GET'])
def index():
    return jsonify({"version": "1.0"})

@app.route('/usage', methods=['GET'])
def usage():
    return jsonify({"usage": {
        "get": {
            "/reports": "Get all reports content",
            "/reports/<string:ID>": "Get report content by ID, ID is report name",
            "/reports/avg/<int:hours>": "Get average of reports younger than hours",
            "/reports/last": "Get last report",
            "reports/list": "Get all reports names",
        }
    }})

#Get all reports names
@app.route('/reports/list', methods=['GET'])
def get_reports():
    return jsonify({"reports": get_all_reports(directory)}),200

#Get last report content
@app.route('/reports/last', methods=['GET'])
def get_last():
    return jsonify(get_last_report(directory)),200

@app.route('/reports', methods=['GET'])
def get_content():
    return jsonify({"reports": get_all_reports_content(directory)}),200

#Get report content by name if name is provided
@app.route('/reports/<string:ID>', methods=['GET'])
def get_report_by_name(ID):
    reports_names = get_all_reports(directory)
    if ID not in reports_names:
        abort(404)
    report = get_report(ID, directory) if ID.endswith(".json") else get_report(f"{ID}.json", directory)
    if not ID:
        return jsonify({"error": "Report name required"}), 400
    return jsonify(report),200 if report is not None else jsonify({"error": "No report found"}), 404

#Get reports younger than hours if hours is provided
@app.route('/reports/avg/<int:hours>', methods=['GET'])
def get_avg(hours):
    report = get_avg_of_report(hours, directory)
    if not hours:
        return jsonify({"error": "Hours required"}), 400
    return jsonify(report,200) if report is not None else jsonify({"error": "No reports found for this period"}), 404


@app.route('/check', methods=['GET'])
def check():    
    return jsonify({"report": create_report()}),200

@app.route('/<path:dummy>')
def redirect_error(dummy):
    return redirect("/usage", code=302)

@app.errorhandler(404)
def page_not_found(e):
    return redirect("/usage", code=302)

if (__name__ == "__main__"):
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-p", "--port", help="Port to listen on", type=int, default=5000)
    argparser.add_argument("-a", "--address", help="Address to listen on")
    args = argparser.parse_args()
    if not args.address or not args.port:
        raise Exception("Address and port required")
    
    app.run(host=args.address, port=args.port, debug=True)