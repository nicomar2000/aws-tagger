import boto3
from src import helper, processor, add_resource

def get_mapped_sources(resource_data):
    # <AWS module name> : <resource ID key> 
    mapped_sources = { 'vpc':resource_data['VpcId'] }
    return mapped_sources

# This function would be use for 
def add_tag(job_information, this_region, resources_id,tags):

    session = boto3.Session(profile_name=job_information['aws_profile'])
    elbv2_client = session.client('elbv2', region_name = this_region )

    response = False
    
    try:
        for r in elbv2_client.describe_load_balancers()['LoadBalancers']:
            
            lb_arn = r['LoadBalancerArn']
            lb_name = r['LoadBalancerName']
                        
            if resources_id == lb_name:

                response = elbv2_client.add_tags(
                    ResourceArns=[lb_arn],
                    Tags=tags
                )
                response = True
    except:
        pass

    return response


def get_tag(job_information, this_region, resource_id):
    return process_resource( job_information, this_region, resource_id )


def search(job_information):
    for this_region in job_information['region_name']:
        process_resource( job_information, this_region, 'none' )


def process_resource( job_information, this_region, resource_id ):
        
        # Connect to AWS
        session = boto3.Session(profile_name=job_information['aws_profile'])
        elbv2_client = session.client('elbv2', region_name = this_region)
        
        # Itearate trough all elbv2 instances
        resource_name = 'elbv2'
        for r in elbv2_client.describe_load_balancers()['LoadBalancers']:

            lb_arn = r['LoadBalancerArn']
            lb_name = r['LoadBalancerName']
                        
            if resource_id == 'none' or resource_id == lb_name:
                
                try:
                    this_tags =  elbv2_client.describe_tags(ResourceArns=[lb_arn])['TagDescriptions'][0]['Tags']
                except:
                    this_tags = []
                    
                add_resource.run( resource_name, lb_name, this_tags, this_region )

                if resource_id != 'none':
                    return this_tags
                else:
                
                    # Get mapped_resources
                    mapped_sources = get_mapped_sources(r)

                    # Get description
                    description = ''

                    # Get display name
                    display_name = ''
                    
                    tag_suggestions = processor.hint_processor(
                                            job_information,
                                            this_region,
                                            this_tags, 
                                            lb_name, 
                                            job_information['hints_lists'],
                                            helper.send_mapped_resources(job_information, mapped_sources, resource_name), 
                                            description, 
                                            display_name
                                        )


if __name__ == '__main__':
    search()