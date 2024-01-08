import requests
import logging
from pythonjsonlogger import jsonlogger
from logstash_async.handler import AsynchronousLogstashHandler
import json
import time
import asyncio

host = 'logstash'
port = 50000

# Create a logger
logger = logging.getLogger('python-logstash-logger')
logger.setLevel(logging.DEBUG)
formatter = jsonlogger.JsonFormatter()
# Create an AsynchronousLogstashHandler and add it to the logger
async_handler = AsynchronousLogstashHandler(host, port, database_path=None)
async_handler.setFormatter(formatter)
logger.addHandler(async_handler)

# Set Authorization header
request_headers = {"Authorization": "Token 3416e930-c99d-4600-bb8e-034647afe95c",
                   "Content-Type": "application/json"}

# Define the base URL for API requests
euUrl = "https://eu1.make.celonis.com/api/v2/admin/scenarios/logs"

current_time = int(round(time.time() * 1000) - 60000)
print("Current timestamp is: ", current_time)
# Define initial parameters for the first request
parameters = {'showCheckRuns': 'true', 'pg[sortDir]': 'asc', 'from': current_time}

# Define a function to handle paginated responses
async def fetch_logs(parameters):
    global logger

    print("Using imtId: ", parameters.get('pg[last]') if 'pg[last]' in parameters else "None")
    connection_attempts = 0
    while connection_attempts < 5:
        try:
            response = requests.get(euUrl, headers=request_headers, params=parameters)
            if response.status_code == 200:
                print(response.url)
                break
            else:
                print(response.reason)
                print(response.text)
                return None
        except ConnectionRefusedError:
            # Connection is closed, wait for a short duration and retry
            time.sleep(1)
            connection_attempts += 1
            if connection_attempts == 5:
                raise Exception("Failed to connect to Logstash after 5 attempts")

    json_data = response.json()
    # print(json_data)
    # Check for scenario logs
    if not json_data['scenarioLogs']:
        logger.warning("No Scenario Logs")
        return 'Wait'

    # Extract pagination information
    try:
        pg_last = json_data['scenarioLogs'][-1]["imtId"]
    except:
        print("pg_last issue!")
    # Check if 'pg_last' is a string before formatting it
    if isinstance(pg_last, str):
        # Convert 'imtId' to a string if it is not already
        str_imtId = str(pg_last)
        # print(pg_last)
        # logger.debug("Pagination - imtId for next request: %s", str_imtId)
    else:
        raise TypeError("Expected 'pg_last' to be a string, but got %s", type(pg_last))
        logger.error("Expected 'pg_last' to be a string, but got %s", type(pg_last))
        sys.exit()


    # Process and format data
    # scenario_logs = []
    for scenario_log in json_data['scenarioLogs']:
        # print(scenario_log)
        # print("-----------")
        data = {
            "imtId": scenario_log['imtId'],
            "organizationId": scenario_log['organizationId'],
            "scenarioId": scenario_log['scenarioId'],
            "teamId": scenario_log['teamId'],
            "timestamp": scenario_log['timestamp'],
            "operations": scenario_log['operations'] if 'operations' in scenario_log else 0,
            "duration": scenario_log['duration'] if 'duration' in scenario_log else 0,
            "transfer": scenario_log['transfer'] if 'transfer' in scenario_log else 0,
            "status": scenario_log['status'] if 'status' in scenario_log else 0
        }
        # scenario_logs.append(data)
        # print(scenario_logs)
        # print("_____________")

    # Send data to Logstash asynchronously
    # for data in scenario_logs:
        try:
            print("Timestamp: ", data['timestamp'])
            logger.info('python-logstash: data', extra=data)
            # print(data)
        except:
            logger.error('Failed to log data: ', extra=data)
        # time.sleep(0.5)
    return str_imtId

# Continuously fetch logs and process them
async def main():
    pg_last = None
    print("Logger running...")
    while True:
        # If there is no pg_last value, make the initial request
        if pg_last is None:
            pg_last = await fetch_logs(parameters)
        elif pg_last == 'Wait':
            # Sleep for a few seconds before checking for new logs again
            print("Sleeping for 5 seconds...")
            await asyncio.sleep(10)
            pg_last = await fetch_logs(parameters)
        # Use the pg_last value for subsequent requests
        elif 'scenario' in pg_last:
            if 'from' in parameters:
                del parameters['from']
            parameters['pg[last]'] = pg_last
            print(f"pg[last] is: {pg_last}")
            logger.debug(f"Pagination - imtId for next request: {parameters['pg[last]']}")
            pg_last = await fetch_logs(parameters)
        else:
            print("Unknow pg_last value: ", str(pg_last))
            continue

# Create an event loop
loop = asyncio.new_event_loop()
try:
    loop.run_until_complete(main())
except Exception as e:
    print(e)
    logger.exception(e)
    loop.close()

