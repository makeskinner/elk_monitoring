# Make Environment Monitoring System with Python and Docker

This project aims to provide detailed monitoring of any Make.com environment by collecting data from various sources, processing it, and sending it to Elasticsearch for centralized visualization and analysis. The Python script (newPoller.py) plays a crucial role in retrieving log data from the Make.com API and sending it to Logstash for further processing.

## Overview

1. **Data Collection:**
   The script utilizes the `requests` library to send HTTP GET requests to the Make.com API, retrieving log data in JSON format.

2. **Data Processing:**
   The script parses the JSON data, extracting relevant information such as timestamp, organizationId, scenarioId, teamId, and other metrics.

3. **Data Formatting:**
   The extracted data is formatted into a dictionary structure, ensuring consistent and structured data representation.

4. **Data Sending:**
   The formatted data is sent to Logstash using the asynchronous logging library asyncio and the AsynchronousLogstashHandler class.

## Logstash Processing

The processed data is received by Logstash, which performs further parsing, enrichment, and transformation using the logstash.conf file. The processed data is then stored in Elasticsearch, a centralized data store for indexing, querying, and analyzing the collected information.

## Visualization and Analysis

Elasticsearch is integrated with Kibana, a powerful data visualization tool, enabling users to create interactive dashboards and charts for analyzing system performance, application logs, and other metrics. Kibana provides a user-friendly interface for exploring and extracting insights from the data collected from various sources.

## Advantages

* **Centralized Data Collection and Storage:** All data from various sources is collected, processed, and stored in a centralized location, making it easier to analyze and correlate information.

* **Automated Data Collection:** The python script and Logstash pipeline automate the data collection process, minimizing manual intervention and ensuring continuous monitoring.

* **Data Processing and Transformation:** Logstash performs data parsing, enrichment, and transformation, ensuring that the data is in a suitable format for analysis and visualization.

* **Visualization and Analysis:** Kibana provides powerful tools for visualizing and analyzing the data collected from Elasticsearch, enabling users to gain insights into system performance, application logs, and other critical metrics.

* **Scalability:** The Docker Compose setup makes it easy to scale the monitoring system by adding or removing containers as needed to accommodate increasing data volumes or new sources of data.

## Conclusion

This project demonstrates a comprehensive approach to monitoring Make.com environments using Python, Docker, and Elasticsearch. The Python script plays a key role in retrieving log data from the Make.com API and sending it to Logstash for further processing and visualization using Kibana. This solution provides a centralized platform for tracking system performance, application logs, and critical metrics, empowering users to optimize their Make.com environments and troubleshoot issues effectively.
