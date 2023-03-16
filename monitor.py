import requests
import csv
import time
import json
import os
from datetime import datetime

# Define the Prometheus URL
prometheus_url = "http://23.22.153.110:30387/api/v1/query"

# Define the Prometheus queries for each metric and metric name
cpu_query = 'sum(rate(container_cpu_usage_seconds_total{namespace=~".+"}[1m])) by (namespace, pod, container)'
cpu_metric_name = 'CPU usage'
memory_query = 'sum(container_memory_usage_bytes{namespace=~".+"}) by (namespace, pod, container)'
memory_metric_name = 'Memory usage'
disk_read_query = 'sum(rate(container_fs_reads_bytes_total{namespace=~".+"}[1m])) by (namespace, pod, container)'
disk_read_metric_name = 'Disk read'
disk_write_query = 'sum(rate(container_fs_writes_bytes_total{namespace=~".+"}[1m])) by (namespace, pod, container)'
disk_write_metric_name = 'Disk write'
network_in_query = 'sum(rate(container_network_receive_bytes_total{namespace=~".+"}[1m])) by (namespace, pod, container)'
network_in_metric_name = 'Network in'
network_out_query = 'sum(rate(container_network_transmit_bytes_total{namespace=~".+"}[1m])) by (namespace, pod, container)'
network_out_metric_name = 'Network out'

# Define headers for the CSV file
csv_headers = ['Namespace', 'Deployment', 'Container', 'CPU usage', 'Memory usage', 'Disk read', 'Disk write', 'Network in', 'Network out', 'Time']

# Define a function to query Prometheus and return the result as JSON
def query_prometheus(query):
    # proxy = {"http":"http://localhost:8080","https":"http://localhost:8080"}
    response = requests.get(prometheus_url, params={'query': query})
    data = json.loads(response.content)
    return data

def get_defaults(result,index):
    try:
        namespace = result[index]['metric']['namespace']
    except KeyError:
        namespace = "N/A"
    try:
        deployment = result[index]['metric']['deployment']
    except KeyError:
        deployment = "N/A"
    try:
        container = result[index]['metric']['container']
    except KeyError:
        container = "N/A"
    return namespace,deployment,container

def get_value(result,namespace,deployment,container):
    value = "N/A"
    for index in range(len(result)):
        _namespace,_deployment,_container = get_defaults(result,index)
        if _namespace == namespace and _deployment == deployment and _container == container:
            if len(result[index]['value']) > 0:
                value = result[index]['value'][-1]
                break
    return value

def write_csv_file(cpu_results, memory_results, disk_read_results, disk_write_results, network_in_results, network_out_results, headers, metric_name):
    #  Check if file exists
    file = 'metrics.csv'
    fileExists = False
    current_time = datetime.now()
    time_formatted = current_time.strftime("%H:%M:%S")
    if os.path.isfile(file):
        fileExists = True
    with open('metrics.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not fileExists:
            writer.writerow(csv_headers)
        for result in cpu_results:

            index = cpu_results.index(result)
            namespace,deployment,container = get_defaults(cpu_results,index)

            row = [namespace, deployment, container]

            cpu_value = get_value(cpu_results,namespace,deployment,container)
            memory_value = get_value(memory_results,namespace,deployment,container)
            dr_value = get_value(disk_read_results,namespace,deployment,container)
            dw_value = get_value(disk_write_results,namespace,deployment,container)
            net_in_value = get_value(network_in_results,namespace,deployment,container)
            net_out_value = get_value(network_out_results,namespace,deployment,container)

            row.append(cpu_value)
            row.append(memory_value)
            row.append(dr_value)
            row.append(dw_value)
            row.append(net_in_value)
            row.append(net_out_value)
            row.append(time_formatted)

            writer.writerow(row)
while True:
    cpu_data = query_prometheus(cpu_query)
    memory_data = query_prometheus(memory_query)
    disk_read_data = query_prometheus(disk_read_query)
    disk_write_data = query_prometheus(disk_write_query)
    network_in_data = query_prometheus(network_in_query)
    network_out_data = query_prometheus(network_out_query)

    # Extract the results from the Prometheus response
    cpu_results = cpu_data['data']['result']
    memory_results = memory_data['data']['result']
    disk_read_results = disk_read_data['data']['result']
    disk_write_results = disk_write_data['data']['result']
    network_in_results = network_in_data['data']['result']
    network_out_results = network_out_data['data']['result']

    # Write the results to a CSV file
    write_csv_file(cpu_results, memory_results, disk_read_results, disk_write_results, network_in_results, network_out_results, csv_headers, 'cpu usage')
    # write_csv_file(memory_results, csv_headers, 'memory usage')
    # write_csv_file(disk_read_results, csv_headers, 'disk read')
    # write_csv_file(disk_write_results, csv_headers, 'disk write')
    # write_csv_file(network_in_results, csv_headers, 'network in')
    # write_csv_file(network_out_results, csv_headers, 'network out')


    # Sleep for 5 minutes before running the script again
    time.sleep(60)
