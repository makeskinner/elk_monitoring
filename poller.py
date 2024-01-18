import asyncio
import datetime
import json
import logging
from logstash_async.handler import AsynchronousLogstashHandler
from pythonjsonlogger import jsonlogger
import requests
import sys
import time

host = 'logstash'
port = 50000

pyLogFmt = f"[python-logstash]:"

# Create a logger
logger = logging.getLogger('python-logstash-logger')
logger.setLevel(logging.DEBUG)
formatter = jsonlogger.JsonFormatter()
# Create an AsynchronousLogstashHandler and add it to the logger
async_handler = AsynchronousLogstashHandler(host, port, database_path=None)
async_handler.setFormatter(formatter)
logger.addHandler(async_handler)

## UPDATE ME ##
private_api_token = "<ADD_YOUR_API_TOKEN_HERE>"
env_domain = "https://eu1.make.celonis.com"
##############

# Set Authorization header
request_headers = {"Authorization": f"Token {private_api_token}",
                   "Content-Type": "application/json"}

# Define the base URL for API requests
euUrl = f"{env_domain}/api/v2/admin/scenarios/logs"

current_time = int(round(time.time() * 1000) - 60000)

# Define initial parameters for the first request
parameters = {'showCheckRuns': 'true', 'pg[sortDir]': 'asc', 'from': current_time}

logItems = [
    "imtId", 
    "organizationId", 
    "scenarioId", 
    "teamId", 
    "timestamp", 
    "operations", 
    "duration", 
    "transfer", 
    "status"
]


def get_current_timestamp():
    current_time = datetime.datetime.now()
    current_timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S')
    return current_timestamp


def log_message(message=None):
    current_timestamp = get_current_timestamp()
    return(f"{current_timestamp} - {pyLogFmt} {message}" if message else f"{current_timestamp} - {pyLogFmt}")


# Parse the Make Error Repsonse Schema
def parse_api_error_response(response_json):
    error_data = {}
    if response_json and 'detail' in response_json and 'message' in response_json:
        error_data['detail'] = response_json['detail']
        error_data['message'] = response_json['message']
    else:
        error_data['error'] = 'Invalid API error response'
    return error_data


def find_valid_imtId(scenarios_dict):
    if not scenarios_dict:
        # No scenarios found
        return None

    max_valid_index = 0
    for i, item in enumerate(scenarios_dict):
        # print(log_message(f"DEBUG: item is :\n{item}"))
        if not item['imtId'].startswith('NaN_scenario'):
            max_valid_index = i

    if max_valid_index > 0:
        print(log_message(f" INFO: Found last valid imtId: {scenarios_dict[max_valid_index]['imtId']}"))
        return scenarios_dict[max_valid_index]['imtId']
    else:
        print(log_message(f" ERROR: Failed to find valid imtId"))
        return None


# Define a function to handle paginated responses
async def fetch_logs(parameters):
    global logger
    headerInfo = {}
    imtIdStr = parameters.get('pg[last]') if 'pg[last]' in parameters else "None"
    connection_attempts = 0
    # print(f"Parameters are: {parameters}")
    while connection_attempts < 5:
        try:
            logger.debug(log_message(f" DEBUG: Making API request using imtId: {imtIdStr}"))
            response = requests.get(euUrl, headers=request_headers, params=parameters)
            headerInfo["statusCode"] = response.status_code
            json_data = response.json()
            if response.status_code == 200:
                logger.debug(log_message(f" DEBUG: API response received"))
                # Save the relevant header info
                if 'X-RateLimit-Remaining' in response.headers:
                    headerInfo["rateLimitRemaining"] = int(response.headers['X-RateLimit-Remaining'])
                    headerInfo["rateLimitReset"] = datetime.datetime.fromtimestamp(int(response.headers['X-RateLimit-Reset']))
                break
            else:
                parsed_error_data = parse_api_error_response(json_data)
                logger.error(log_message(f" ERROR: Status Code: {response.status_code} & Message: {parsed_error_data}"))
                return 'Wait'
        except TimeoutError:
            logger.error(log_message(f" ERROR: Timeout error while fetching logs"))
            return 'Wait'
        except ConnectionRefusedError:
            # Connection is closed, wait for a short duration and retry
            logger.error(log_message(f" ERROR: Connection refused while fetching logs"))
            time.sleep(5)
            connection_attempts += 1
            if connection_attempts == 5:
                logger.error(log_message(f" ERROR: Failed to connect to Logstash after 5 attempts!"))
                raise Exception("Failed to connect to Logstash after 5 attempts")
                return "ConnectionRefusedError"

    try:
        # Process and format data
        scenario_logs = json_data['scenarioLogs']
    except KeyError:
        print(log_message(f" WARN: No scenario logs. Last response was:\n{json_data}"))
        logger.warning(log_message(f" WARN: No Scenario Logs"))
        return 'Wait'
    else:
        # Extract pagination information
        pg_last = find_valid_imtId(scenario_logs)
        if not pg_last:
            if imtIdStr == 'None':
                # Initial request, no more logs to fetch, set pg_last to 'Wait'
                pg_last = 'Wait'
            else:
                # Fetching subsequent logs failed, set pg_last to 'Stop'
                pg_last = 'Stop'
        else:
            # Check if 'pg_last' is a string before formatting it
            if not isinstance(pg_last, str):
                print(log_message(f" FATAL: Expected 'pg_last' to be a string, but got: {type(pg_last)}"))
                raise TypeError("Expected 'pg_last' to be a string, but got %s", type(pg_last))
                return 'TypeError'
            else:
                # Iterate through scenario logs and log each scenario separately
                for scenario in scenario_logs:
                    data = {}
                    # Log scenario details
                    for item in logItems:
                        if item in scenario.keys():
                            # Ensure the important metrics exist
                            try:
                                data[item] = scenario[item]
                                # print(f"{item}: {scenario[item]}")
                                # logger.info(f"{item}: {scenario[item]}")
                            except KeyError:
                                return 'KeyError'
                        elif item in ['operations', 'duration', 'transfer', 'status']:
                            # These are the only values we want to set to 0 if they don't exist
                            data[item] = 0
                        else:
                            # If we end up here then an important key is missing, such as 'teamId'. 
                            print(log_message(f" ERROR: missing key: {item}"))
                            print(log_message(f" ERROR: Last scenario object was:\n{scenario}"))
                            continue

                    # print(log_message(f" INFO: Logging DATA: {data}"))
                    # print(log_message(f" INFO: Logging RATELIMITS: {headerInfo}"))
                    # Log API response
                    logger.info(log_message(f" INFO: Logging"), extra=data)
                    logger.info(log_message(f" INFO: RateLimits"), extra=headerInfo)
    return pg_last

# Continuously fetch logs and process them
async def main():
    global parameters
    pg_last = None
    print(log_message(f" INFO: Logger running..."))
    while True:
        # If there is no pg_last value, make the initial request
        if pg_last is None:
            pg_last = await fetch_logs(parameters)
        elif pg_last == 'Wait':
            # Sleep for a few seconds before checking for new logs again
            print(log_message(f" INFO: Sleeping for 10 seconds..."))
            await asyncio.sleep(10)
            pg_last = await fetch_logs(parameters)
        elif pg_last == 'Stop':
            # Sleep for longer before checking for new logs again
            print(log_message(f" INFO: Sleeping for 30 seconds..."))
            await asyncio.sleep(30)
            pg_last = await fetch_logs(parameters)
        # Use the pg_last value for subsequent requests
        elif 'scenario' in pg_last:
            if 'from' in parameters:
                del parameters['from']
            parameters['pg[last]'] = pg_last
            # print(log_message(f" DEBUG: Pagination - imtId for next request: {parameters['pg[last]']}"))
            # logger.debug(log_message(f" DEBUG: Pagination - imtId for next request: {parameters['pg[last]']}"))
            pg_last = await fetch_logs(parameters)
        else:
            logger.error(log_message(f" ERROR: Unknown pg_last value: {str(pg_last)}"))
            break

# Create an event loop
loop = asyncio.new_event_loop()
print(log_message(f" INFO: Logging starting"))
logger.debug(log_message(f" INFO: Logging starting"))
try:
  loop.run_until_complete(main())
except Exception as e:
  # Extract the stack trace
  exc_info = asyncio.get_event_loop().get_exception_traceback()

  # Print the stack trace
  print("Stack Trace:")
  for frame, lineno, function, code in exc_info:
    print(f" File: {frame.filename}")
    print(f" Line: {lineno}")
    print(f" Function: {function}")
    print(f" Code:\n{code}")
    print("-" * 70)

  # Print the exception message
  print(f"FATAL Exception: {str(e)}")

  # Log the exception to the logger
  logger.exception(f"FATAL EXCEPTION: {str(e)}")

  # Gracefully close the event loop
  loop.close()
