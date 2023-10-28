from .db import query
from .loader import get_job_information
from src.helper import send_logs
import os, importlib

def review():

    # Truncate tables
    query("insert", "DROP TABLE resources")
    query("insert", "DROP TABLE missing_tags")
    query("insert", "DROP TABLE current_tags")
    try:
        query("try", "CREATE TABLE resources (id INTEGER PRIMARY KEY,type,aws_id TEXT UNIQUE,region)")
        query("try", "CREATE TABLE current_tags (id INTEGER PRIMARY KEY,aws_id,key,value)")
        query("try", "CREATE TABLE missing_tags (id INTEGER PRIMARY KEY,resource_id,hint_source,tag_key,possible_value,found_in,hint,match_string)")
    except:
        # Not a very elegant way to check if table already exist
        pass

    # Check for job file
    job_information = get_job_information()


    send_logs('INFO', 'Lookup process started')

    # List all AWS resource available modules 
    aws_resources_modules = []
    for each_resource in os.listdir('aws_resources'):
        if '.py' in each_resource:
            aws_resources_modules.append( each_resource.split('.py')[0] )

    # Iterate in all requested aws resources
    if 'aws_resources' in job_information:
        for each_aws_resource in job_information['aws_resources']:
            
            # Make sure there is a module for this resource
            if each_aws_resource in aws_resources_modules:

                # Load aws resource module
                this_resource = importlib.import_module( f"aws_resources.{each_aws_resource}")
                try:
                    this_resource.search(job_information)
                except ValueError:
                    send_logs('ERROR', 'Failed to run module '+str(each_aws_resource)+' error:'+str(ValueError))
            else:
                send_logs('ERROR', 'AWS resource module missing: '+str(each_aws_resource))

    send_logs('INFO', 'Lookup process ended')

if __name__ == '__main__':
    review()