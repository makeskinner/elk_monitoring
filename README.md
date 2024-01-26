![image](https://github.com/makeskinner/elk_monitoring/assets/147710503/fb14b2e0-fe4c-4ae0-8bbd-63e67d7c2bca)

# Make Environment Monitoring System with Python and Docker

This project aims to provide detailed monitoring of any Make environment by collecting data from various sources, processing it, and sending it to Elasticsearch for centralized visualization and analysis. The Python script (newPoller.py) plays a crucial role in retrieving log data from the Make API and sending it to Logstash for further processing.

## Overview

1. **Data Collection:**
   The Python script retrieves log data from the [Make API](https://www.make.com/en/api-documentation/scenarios-scenarioId-logs-get), processes it by extracting relevant information and formatting it, and then sends it to Logstash for further processing and storage in Elasticsearch.
   The script utilizes the `requests` library to send HTTP GET requests to the Make API, retrieving log data in JSON format.

   > ***IMPORTANT:***
   >    The script uses an authentication token with the Make API. Ensure you have created this and defined it in the script. 
   >    Look for the comment marked `## UPDATE ME ##`
   >
   >    1. Base Domain for your API
   >        - By default the script is looking at the Enterprise EU1 environment "https://eu1.make.celonis.com"
   >        - Ensure you update this to one relevant to your environment
   >    2. Add your API Token by updating:
   >        - `private_api_token = "<ADD_YOUR_API_TOKEN_HERE>"`
3. **Data Processing:**
   The script parses the JSON data, extracting relevant information such as `timestamp`, `organizationId`, `scenarioId`, `teamId`, and other metrics.

4. **Data Formatting:**
   The extracted data is formatted into a dictionary structure, ensuring consistent and structured data representation.

5. **Data Sending:**
   The formatted data is sent to Logstash using the asynchronous logging library `asyncio` and the `AsynchronousLogstashHandler` class.

## Logstash Processing

The processed data is received by Logstash, which performs further parsing, enrichment, and transformation using the `logstash.conf` file. The processed data is then stored in Elasticsearch, a centralized data store for indexing, querying, and analyzing the collected information.

## Visualization and Analysis

Elasticsearch is integrated with Kibana, a powerful data visualization tool, enabling users to create interactive dashboards and charts for analyzing system performance, application logs, and other metrics. Kibana provides a user-friendly interface for exploring and extracting insights from the data collected from various sources.
The GitHub repository contains a dashboard that can be imported, providing you with a good starting point.

![image-20240118-114321](https://github.com/makeskinner/elk_monitoring/assets/147710503/c94b9e09-6bba-40f7-bb41-b0ed6f6065e1)

## Implementation
The project leverages Docker to manage and orchestrate the various components of the monitoring system. The gitHub repo contains all the necessary files and information you will require in order to get up and running.

# Pre-requisites
1. Create your own Make API Key
   - You will need this for authentication
3. Ensure you are aware of any VPN requirements and have it connected while running the tool

# Key Components and Their Roles
| Component | Role |
| --------- | ---- |
| Python Script (poller.py) | Collects log data from the Make API |
| [Logstash](https://www.elastic.co/logstash) | Receives data from Python script, Metricbeat, and Filebeat; parses, transforms, and sends data to Elasticsearch |
| [Elasticsearch](https://www.elastic.co/elasticsearch) | A centralized data store for indexing, querying, and analyzing the collected information |
| [Metricbeat](https://www.elastic.co/guide/en/beats/metricbeat/current/metricbeat-module-kibana.html) | Collects system metrics and sends them to Elasticsearch |
| [Filebeat](https://www.elastic.co/guide/en/beats/filebeat/current/filebeat-module-kibana.html) | Collects log files from the host system and sends them to Elasticsearch |
| [Kibana](https://www.elastic.co/kibana) | Visualizes and analyzes the data stored in Elasticsearch |


<details>
   
   <summary>EXPAND for Installation instructions</summary>
   
   ### Installing Docker Desktop
   To install Docker Desktop, follow these steps:

   1. **Download Docker Desktop:** Visit the [Docker Desktop](https://www.docker.com/products/docker-desktop) website and download the installer for your operating system.
      - You can always use CLI Docker instead if you wish!
   3. **Run the Installer:** Run the downloaded installer and follow the on-screen instructions. The installer will guide you through the setup process, including granting Docker Desktop administrative privileges.
   4. **Restart Your System:** After completing the installation, restart your computer. This ensures that Docker Desktop is fully initialized and running.
   5. **Verify Installation:** Open the Docker Desktop application and check if it's running. You should see the Docker Desktop icon in your system tray.
   
   ### Clone the GitHub repository
   To get started with the provided Docker Compose file, you'll need to acquire the necessary files from the GitHub repository:
   
   1. **Clone the GitHub Repository:** Clone the GitHub repository using the following command:
   
   ```
   git clone https://github.com/makeskinner/elk_monitoring.git
   ```
   This will create a copy of the repository in your local directory.
   
   2. **Navigate to the Directory:** Navigate to the cloned repository directory using the following command:
   ```
   cd elk_monitoring
   ```
   This will change your working directory to the repository directory.
   
   3. **Copy the Necessary Files:** Copy the everything to a suitable location in your local environment. These files will be used to configure and start the Docker services.
   
   ### Using the Docker Compose File
   > [!IMPORTANT]
   > The containers you’re about to install are comprised of the ELK stack from Elasticsearch.
   >
   > It’s important to NOTE that the configuration defines the Elasticsearch license as ‘basic’.
   >
   > The Basic license for Elastic Stack is free forever. It includes core functionality for searching, analyzing, and visualizing data. However, it has some limitations compared to paid licenses. Here's a summary:
   > 
   > Free forever, but limited:
   > 
   > Single node deployment: You can only have one node in your cluster with the Basic license. This can be sufficient for small projects or personal use, but may not be enough for larger deployments or demanding workloads.
   > 
   > Basic security features: You get basic role-based access control (RBAC) but lack advanced features like token authentication and audit logging.
   > 
   > No machine learning: The Basic license excludes access to machine learning capabilities like anomaly detection and outlier analysis.
   > 
   > Limited data retention: Data retention with the Basic license is shorter than with paid options. You might need to configure manual retention if you need to keep data for longer.
   > 
   > No official support: Basic license users are limited to community forums and documentation for support.
   > 
   > If you need more features or capabilities, you can upgrade to a paid license at any time. Paid licenses offer various options with increasing functionality and resources, including:
   > 
   > Gold: Adds machine learning, security features, and higher node limits.
   > 
   > Platinum: Includes all Gold features plus advanced security, data lifecycle management, and support.
   > 
   > Enterprise: The most comprehensive option, offering everything in Platinum plus customizability and dedicated support.
   > 
   > Ultimately, the choice depends on your specific needs and budget. The Basic license can be a great starting point for personal projects or small deployments, and it's free forever. But if you need more advanced features or scalability, paid licenses may be a better fit.
   
   To use the provided Docker Compose file, follow these steps:
   
   1. **Set Environment Variables:** Set the appropriate environment variables in the .env file:
      - You can leave everything as it is, but i’d suggest understanding memory requirements.
   > [!TIP]
   > Pay attention to the memory defined in the elasticsearch.yml file. You will need to tailor this to your specific needs. You may start with what's here and monitor your elastic container so understand whether or not you need to modify.
   ```Dockerfile
   # Project namespace (defaults to the current folder name if not set)
   #COMPOSE_PROJECT_NAME=myproject
   
   # Password for the 'elastic' user (at least 6 characters)
   ELASTIC_PASSWORD=changeme
   
   # Password for the 'kibana_system' user (at least 6 characters)
   KIBANA_PASSWORD=changeme
   
   # Version of Elastic products to use across all containers
   # It's best to keep everything running the same version
   # Update if available
   STACK_VERSION=8.11.3
   
   # Set the cluster name
   CLUSTER_NAME=docker-cluster
   
   # Set to 'basic' or 'trial' to automatically start the 30-day trial
   LICENSE=basic
   #LICENSE=trial
   
   # Port to expose Elasticsearch HTTP API to the host
   ES_PORT=9200
   
   # Port to expose Kibana to the host
   KIBANA_PORT=5601
   
   # Port to expose Logstash to the host
   LOGSTASH_PORT=50000
   
   # Increase or decrease based on the available host memory (in bytes)
   ES_MEM_LIMIT=1073741824
   KB_MEM_LIMIT=1073741824
   LS_MEM_LIMIT=1073741824
   
   # SAMPLE Predefined Key only to be used in POC environments
   ENCRYPTION_KEY=c34d38b3a14956121ff2170e5030b471551370178f43e5626eec58b04a30fae2
   ```
   3. **Build the Docker Images:** Build the Docker images for the services using the following command:
   ```   
   docker-compose build -f <path/to/docker-compose.yml>
   ```
   4. **Start the Services:** Start the Docker services using the following command:
   ```
   docker-compose up -d
   ```
   5. **Access Kibana:** Open your web browser and navigate to http://localhost:5601
      - Use the credentials elastic and <your_kibana_password> to access Kibana.
      - If you haven’t changed the values defined within the ```.env``` file then the password will be ```changeme```.
   
   6. **Add a Data View:** This will need to match the index name defined in ```logstash.yml```
      - For the default index enter make into the Index Pattern field
      - You should see the index name created by Logstash in the right hand area of the screen:
         - image-20240118-111643.png
         **NB:** This screenshot shows ent-scenario-logs: Ignore, just use a pattern that matches what you see here, so long as it’s an Index, not a Data stream
         Once the pattern matches the index the Timestamp field will be populated with the default value ```@timestamp```. Keep this as it is.
   
   7. **Import the Dashboard:** Use Stack Management from the hamburger menu
      - View Saved Objects within the Kibana menu items
      - Click the Import button and select ```exampleDashboard.ndjson``` from your local environment
   
   > [!TIP]
   > To stop and remove the services, use the following command:
   > ```
   > docker-compose down
   > ```
   > This will stop all running containers, remove any dangling containers, and remove all volumes created by Docker Compose.
   
   By following these steps, you'll have successfully installed Docker Desktop and used the provided Docker Compose file to create and manage a distributed Elasticsearch, Kibana, and Logstash stack.
</details>

## Advantages

* **Centralized Data Collection and Storage:** All data from various sources is collected, processed, and stored in a centralized location, making it easier to analyze and correlate information.

* **Automated Data Collection:** The python script and Logstash pipeline automate the data collection process, minimizing manual intervention and ensuring continuous monitoring.

* **Data Processing and Transformation:** Logstash performs data parsing, enrichment, and transformation, ensuring that the data is in a suitable format for analysis and visualization.

* **Visualization and Analysis:** Kibana provides powerful tools for visualizing and analyzing the data collected from Elasticsearch, enabling users to gain insights into system performance, application logs, and other critical metrics.

* **Scalability:** The Docker Compose setup makes it easy to scale the monitoring system by adding or removing containers as needed to accommodate increasing data volumes or new sources of data.

## Conclusion

This project demonstrates a comprehensive approach to monitoring Make environments using Python, Docker, and Elasticsearch. The Python script plays a key role in retrieving log data from the Make API and sending it to Logstash for further processing and visualization using Kibana. This solution provides a centralized platform for tracking system performance, application logs, and critical metrics, empowering users to optimize their Make environments and troubleshoot issues effectively.
