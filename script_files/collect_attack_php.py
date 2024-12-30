import json
import time
from datetime import datetime

# Constants
NL = '\n'
TAB = '\t'
SPC = ' '

# Default globals dictionary
globals_dict = {}

# Usage text
usage_text = (
    TAB + '[-append] (Appends data to the output file)' + NL +
    TAB + '-lower="dd.mm.yyyy" -upper="dd.mm.yyyy" (Date range to collect, the' + NL +
    SPC + 'last day is excluded)' + NL +
    TAB + '-include="field:value[,field:value...]" (Fields to include in the' + NL +
    SPC + 'query - this option overrides -exclude)' + NL +
    TAB + '-exclude="field:value[,field:value...]" (Fields to exclude from the' + NL +
    SPC + 'query)' + NL +
    TAB + '-vision="<Vision IP>" -user="<Vision User>" -pass="<Vision Pass>"' + NL +
    TAB + '[-dps="dpIP[,dpIP...]"] (DP IPs to collect data from - default all)' + NL +
    TAB + '[-window=nnnn] (Time window in seconds for each query request - the' + NL +
    SPC + 'default is 3600)' + NL + NL
)

# Check for missing parameters
required_params = ['vision', 'user', 'pass', 'lower', 'upper']
for param in required_params:
    if param not in globals_dict:
        print(f"{param.capitalize()} parameter not found." + NL + NL + usage_text)
        exit(1)

# Convert date ranges to Unix epoch format (UTC)
def to_epoch(date_str, format='%d.%m.%Y'):
    return int(time.mktime(datetime.strptime(date_str, format).timetuple()))

globals_dict['lower'] = to_epoch(globals_dict['lower'])
globals_dict['upper'] = to_epoch(globals_dict['upper'])

# Set default parameters
globals_dict['window'] = globals_dict.get('window', 3600)  # 1 hour default

# Query creation function
def create_query(globals_dict):
    query = {
        "criteria": [],
        "pagination": {
            "page": 0,
            "size": 10000,
            "topHits": 10000
        }
    }

    # Create an "and" filter
    and_filters = {
        "type": "andFilter",
        "filters": []
    }

    # Date range filter
    time_filter = {
        "type": "timeFilter",
        "field": "endTime",
        "lower": "{lower}",
        "upper": "{upper}",
        "includeLower": True,
        "includeUpper": True
    }
    and_filters['filters'].append(time_filter)

    # Include or exclude filters
    if 'include' in globals_dict:
        include_array = globals_dict['include'].split(',')
        if len(include_array) == 1:
            field, value = globals_dict['include'].split(':')
            and_filters['filters'].append({
                "type": "termFilter",
                "field": field,
                "value": value
            })
        else:
            or_filter = {
                "type": "orFilter",
                "filters": []
            }
            for text in include_array:
                field, value = text.split(':')
                or_filter['filters'].append({
                    "type": "termFilter",
                    "field": field,
                    "value": value
                })
            and_filters['filters'].append(or_filter)
    elif 'exclude' in globals_dict:
        exclude_array = globals_dict['exclude'].split(',')
        for text in exclude_array:
            field, value = text.split(':')
            and_filters['filters'].append({
                "type": "termFilter",
                "field": field,
                "value": value,
                "inverseFilter": True
            })

    # Add "and" filters to query criteria
    query['criteria'].append(and_filters)

    # Create an "or" filter for DefensePro IPs
    or_filters = {
        "type": "orFilter",
        "filters": []
    }
    if 'dps' in globals_dict:
        dps_array = globals_dict['dps'].split(',')
        for dp in dps_array:
            or_filters['filters'].append({
                "type": "termFilter",
                "field": "deviceIp",
                "value": dp
            })
    else:
        or_filters['filters'].append({
            "type": "termFilter",
            "field": "deviceIp",
            "value": "0.0.0.0",
            "inverseFilter": True
        })

    # Add "or" filters to query criteria
    query['criteria'].append(or_filters)

    if globals_dict.get('debug'):
        print(json.dumps(query, indent=4))

    return query

# Data collection function
def collect_data(globals_dict, query):
    def vision_login(vision_ip, user, password):
        # Placeholder for Vision login function
        return "ok"

    vision_ip = globals_dict['vision']
    lower = globals_dict['lower']
    upper = globals_dict['upper']
    window = globals_dict['window']
    out_file = globals_dict['data']
    append = globals_dict.get('append', False)

    # Create output file
    mode = 'a' if append else 'w'
    with open(out_file, mode) as fh:
        while lower < upper:
            d1 = lower
            d2 = lower + window
            query['criteria'][0]['filters'][0]['lower'] = str(d1 * 1000)
            query['criteria'][0]['filters'][0]['upper'] = str(d2 * 1000)
            
            # Simulate REST API call
            res = {"data": {}, "metaData": {"totalHits": 0}}
            if 'data' not in res:
                continue
            
            lower += window
            if res['metaData']['totalHits'] > 0:
                fh.write(json.dumps(res) + NL)

    return True

# Example usage
query = create_query(globals_dict)
collect_data(globals_dict, query)
