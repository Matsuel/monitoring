"""
    Monit API est une API REST qui permet de récupérer
    les informations de monit et de les afficher.
"""
from argparse import ArgumentParser
from os import name as os_name
from flask import Flask, jsonify, redirect, abort
from swagger_ui import api_doc
from monit import (
    get_report,
    get_all_reports,
    get_last_report,
    get_avg_of_report,
    create_report,
    get_all_reports_content
)

app = Flask(__name__)
api_doc(app, config_path="./swagger.yml", url_prefix="/doc")
DIRECTORY  = "./monit" if os_name == "nt" else "/var/monit"
DIRECTORY_LOG = "./log" if os_name == "nt" else "/var/log/monit"
DIRECTORY_CONFIG = "." if os_name == "nt" else "/etc/monit"

class MissingArgumentsException(Exception):
    """
    Exception levée si des arguments sont manquants
    """

@app.route('/', methods=['GET'])
def doc():
    """
    Redirige vers la documentation
    """
    return redirect("/doc", code=302)

@app.route('/version', methods=['GET'])
def version():
    """
    Renvoie la version de l'API
    """
    return jsonify({"version": "1.0.0"}),200

@app.route('/reports/list', methods=['GET'])
def get_reports():
    """
    Renvoie la liste des rapports
    """
    return jsonify({"reports": get_all_reports(DIRECTORY)}),200

@app.route('/reports/last', methods=['GET'])
def get_last():
    """
    Renvoie le dernier rapport
    """
    return jsonify(get_last_report(DIRECTORY)),200

@app.route('/reports', methods=['GET'])
def get_content():
    """
    Renvoie le contenu de tous les rapports
    """
    return jsonify({"reports": get_all_reports_content(DIRECTORY)}),200

@app.route('/reports/<string:identifier>', methods=['GET'])
def get_report_by_name(identifier):
    """
    Renvoie un rapport en fonction de son nom
    """
    reports_names = get_all_reports(DIRECTORY)
    if identifier not in reports_names and f"{identifier}.json" not in reports_names:
        abort(404)
    if identifier.endswith(".json"):
        report = get_report(identifier, DIRECTORY)
    else:
        report = get_report(f"{identifier}.json", DIRECTORY)
    if not identifier:
        return jsonify({"error": "Report name required"}), 400
    return jsonify(report) if report is not None else abort(404)

@app.route('/reports/avg/<int:hours>', methods=['GET'])
def get_avg(hours):
    """
    Renvoie la moyenne des valeurs des rapports plus jeunes que X heures
    """
    report = get_avg_of_report(hours, DIRECTORY)
    if not hours:
        return jsonify({"error": "Hours required"}), 400
    return jsonify(report),200 if report is not None else abort(404)

@app.route('/check', methods=['GET'])
def check():
    """
    Renvoie le dernier rapport
    """
    return jsonify({"report": create_report()}),200

@app.errorhandler(404)
def not_found(error):
    """
    Renvoie une erreur 404 si la page n'existe pas
    """
    return jsonify({"error": f"Not found {error}"}), 404

if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("-p", "--port", help="Port to listen on", type=int, default=5000)
    argparser.add_argument("-a", "--address", help="Address to listen on")
    args = argparser.parse_args()
    if not args.address or not args.port:
        raise MissingArgumentsException("Missing arguments port or address")
    app.run(host=args.address, port=args.port, debug=True)
