import requests
import time

reports=[]

for i in range(50):
    report_avg=None
    datas=requests.get("http://localhost:8090/check")
    report_avg=datas.json() if report_avg is None else report_avg
    reports.append(datas.json())
    print(datas.json())
    for report in reports:
        report_avg["report"]["cpu"] += report["report"]["cpu"]
        report_avg["report"]["memory"] += report["report"]["memory"]
    report_avg["report"]["cpu"] /= len(reports)
    report_avg["report"]["memory"] /= len(reports)
    report_avg["report"]["id"] = "avg"
    report_avg["report"]["cpu"] = round(report_avg["report"]["cpu"], 2)
    report_avg["report"]["memory"] = round(report_avg["report"]["memory"], 2)
    # print(report)
    print(f"Averrage: \n {report_avg}")
    time.sleep(3)