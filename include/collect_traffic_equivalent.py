import datetime
import json
import requests
import time

# Global configuration
VERSION = '5.4'
NL = '\n'
TAB = '\t'
SPC = ' '

# Usage text
usage_text = (
    f"{TAB}[-append] (Appends data to the output file){NL}"
    f"{TAB}-lower=\"dd.mm.yyyy\" -upper=\"dd.mm.yyyy\" (Date range to collect, the{NL}"
    f"{SPC}last day is excluded){NL}"
    f"{TAB}-vision=\"<Vision IP>\" -user=\"<Vision User>\" -pass=\"<Vision Pass>\"{NL}"
    f"{TAB}[-dps=\"dpIP[,dpIP...]\"] (DP IPs to collect data from - default all){NL}{NL}"
)

# Check for missing parameters
def check_globals(globals_dict):
    required_params = ["vision", "user", "pass", "lower", "upper"]
    for param in required_params:
        if param not in globals_dict:
            print(f"{param.capitalize()} parameter not found.{NL}{usage_text}")
            exit(1)

# Convert date to Unix timestamp
def to_unix_epoch(date_str):
    return int(time.mktime(datetime.datetime.strptime(date_str, "%d.%m.%Y").timetuple()))

# Create the query function
def create_query(globals_dict):
    query = {
        "aggregation": {
            "criteria": [
                {
                    "type": "timeFilter",
                    "field": "timeStamp",
                    "lower": "{lower}",
                    "upper": "{upper}",
                    "includeLower": True,
                    "includeUpper": True
                },
                {
                    "type": "termFilter",
                    "field": "monitoringProtocol",
                    "value": "all"
                },
                {
                    "type": "termFilter",
                    "field": "unit",
                    "value": "bps"
                },
                {
                    "type": "termFilter",
                    "field": "direction",
                    "value": "Inbound"
                },
                {
                    "type": "orFilter",
                    "filters": [
                        {"type": "termFilter", "field": "deviceIp", "value": dp_ip}
                        for dp_ip in globals_dict["dps"].split(",")
                    ]
                }
            ],
            "type": "dateHistogram",
            "aggField": "timeStamp",
            "aggName": "timeStamp",
            "aggregation": {
                "type": "calculation",
                "metrices": [
                    {"type": "sumMetric", "aggName": "trafficValue", "aggField": "trafficValue"},
                    {"type": "sumMetric", "aggName": "excluded", "aggField": "excluded"},
                    {"type": "sumMetric", "aggName": "discards", "aggField": "discards"}
                ]
            },
            "timeInterval": {
                "dateFraction": "HOUR",
                "amount": 1
            }
        },
        "order": [
            {
                "type": "Order",
                "order": "ASC",
                "field": "timeStamp",
                "sortingType": "LONG"
            }
        ]
    }
    return query

# Data collection function
def collect_data(globals_dict, query):
    vision_ip = globals_dict["vision"]
    output_file = globals_dict["data"]
    append = globals_dict.get("append", False)
    mode = 'a' if append else 'w'

    try:
        with open(output_file, mode) as fh:
            lower, upper = globals_dict["lower"], globals_dict["upper"]
            retries = globals_dict.get("maxRetry", 3)
            time_retry = globals_dict.get("timeRetry", 5)
            calls, events, exceed, lost = 0, 0, 0, 0

            while lower < upper:
                query["aggregation"]["criteria"][0]["lower"] = str(lower * 1000)
                query["aggregation"]["criteria"][0]["upper"] = str((upper - 1) * 1000)

                # Execute REST API call
                json_data = json.dumps(query)
                response = requests.post(f"https://{vision_ip}/mgmt/monitor/reporter/reports-ext/DP_TRAFFIC_UTILIZATION_RAW_REPORTS", data=json_data)
                res = response.json()

                if "data" not in res:
                    retries -= 1
                    if retries > 0:
                        print("Retrying...")
                        time.sleep(time_retry)
                        continue
                    else:
                        print("ERROR: Exceeded number of retries.")
                        break

                calls += 1
                if "metaData" in res and res["metaData"].get("totalHits", 0) > 0:
                    events += res["metaData"]["totalHits"]
                    if res["metaData"]["totalHits"] > globals_dict["recLimit"]:
                        exceed += 1
                        lost += res["metaData"]["totalHits"] - globals_dict["recLimit"]
                        print('!')
                    else:
                        print('-')
                else:
                    print('.')

                fh.write(json.dumps(res) + "\n")
            
            print(f"{calls} calls executed.")
            print(f"{events} events collected.")
            if exceed:
                print(f"WARNING: {exceed} calls exceeded {globals_dict['recLimit']} records.")
                print(f"WARNING: {lost} records lost.")
            print("Data collection complete.")

    except IOError as e:
        print(f"ERROR: Cannot create output file: {e}")

# Example usage
globals_dict = {
    "vision": "192.168.1.1",
    "user": "admin",
    "pass": "password",
    "lower": to_unix_epoch("01.01.2021"),
    "upper": to_unix_epoch("31.12.2021"),
    "data": "output.json",
    "dps": "192.168.1.2,192.168.1.3",
    "recLimit": 1000,
    "maxRetry": 3,
    "timeRetry": 5,
    "append": False
}

check_globals(globals_dict)
query = create_query(globals_dict)
collect_data(globals_dict, query)
