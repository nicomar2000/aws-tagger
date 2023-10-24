from aws_resources import *
from .db import query
import importlib
from src.helper import send_logs

def add(job_information, suggestion_id):

    missing_tags = query("read", "SELECT * FROM missing_tags WHERE id='"+suggestion_id+"'")

    response = False

    for id,resource_id,hint_source,tag_key,possible_value,found_in,hint,match_string in missing_tags:

        if suggestion_id == str(id):

            # Get suggestion
            tags = [{
                    'Key': tag_key,
                    'Value': possible_value
                }]
            
            # Get resource details
            resources = query("read", "SELECT * FROM resources WHERE aws_id='"+resource_id+"'")
            for r_id,type,aws_id,region in resources:

                # Send request to add tags
                #response = ec2_instance.add_tag(job_information, region, resource_id, tags)

                # Load aws resource module
                this_resource = importlib.import_module( f"aws_resources.{type}")
                try:
                    this_resource.add_tag(job_information, region, resource_id, tags)
                    response = True
                except ValueError:
                    send_logs('ERROR', '002 Failed to run module '+str(type)+' error:'+str(ValueError))

            # Remove suggestion from DB
            if response:
                query("insert", "DELETE FROM missing_tags WHERE id='"+suggestion_id+"'")

    return response


if __name__ == '__main__':
    add()