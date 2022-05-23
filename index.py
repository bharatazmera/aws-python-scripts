import os
import boto3
import socket
import logging
logger = logging.getLogger()
logger.setLevel(logging.ERROR)

def lambda_handler(event, context):
    cloudwatch = boto3.client('cloudwatch')
    lambdah = boto3.client('lambda')
    protocol = os.environ['cfprotocol']
    healthcheckname = os.environ['cfstackname']
    host = os.environ['cfResourceIPaddress']
    port = int(os.environ['cfport'])
    
    threeway = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        threeway.settimeout(4)
        threeway.connect(("amazon.com", 80))
    
    except socket.error as e:
        if "timed out" in str(e):
            print("The Lambda function does not have internet access because it is not in a private subnet with internet access provided by a NAT Gateway or NAT instance. The TCP connection might be successful but Lambda will not be able to push metrics to Cloudwatch and the Route 53 health check will always be unhealthy.")
    
    threeway = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        threeway.settimeout(4)
        threeway.connect((host, port))
        metric = 1
    
        print ("The TCP connection was successful.")
        response = cloudwatch.put_metric_data(Namespace = 'Route53PrivateHealthCheck', MetricData = [{'MetricName': 'TCP: ' + healthcheckname + ' (Health Check for resource ' + host + ')', 'Dimensions': [{'Name': 'TCP Health Check','Value': 'TCP Health Check'}], 'Unit': 'None','Value': metric},])
    
    except socket.error as e:
        metric = 0
        response = cloudwatch.put_metric_data(Namespace = 'Route53PrivateHealthCheck', MetricData = [{'MetricName': 'TCP: ' + healthcheckname + ' (Health Check for resource ' + host + ')', 'Dimensions': [{'Name': 'TCP Health Check','Value': 'TCP Health Check'}], 'Unit': 'None','Value': metric},])
        
        if "timed out" in str(e):
            print ("The TCP connection timed out because " + host + " did not respond within the timeout period of 4 seconds.")
        elif "Name or service not known" in str(e):
            print ("The TCP connection was unsuccessful because " + host +  " did not resolve.")
        elif "refused" in str(e):
            print ("The TCP connection was unsuccessful because the connection was refused by " + host + ". Ensure the host is listening for TCP connections on the port number specified.")
        else:
            logger.error("Error: " + str(e))
    
    except:
        metric = 0
        response = cloudwatch.put_metric_data(Namespace = 'Route53PrivateHealthCheck', MetricData = [{'MetricName': 'TCP: ' + healthcheckname + ' (Health Check for resource ' + host + ')', 'Dimensions': [{'Name': 'TCP Health Check','Value': 'TCP Health Check'}], 'Unit': 'None','Value': metric},])
        print ("The TCP connection was unsuccessful.")
   
