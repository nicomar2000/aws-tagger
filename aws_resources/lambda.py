import boto3
from src import helper, processor, add_resource

def get_mapped_sources(resource_data):

    # <AWS module name> : <resource ID key> 
    if 'VpcConfig' in resource_data['Configuration']:
        vpc = resource_data['Configuration']['VpcConfig']['VpcId']
        try:
            security_groups = resource_data['Configuration']['VpcConfig']['SecurityGroupIds'][0]
        except:
            security_groups = ''
        try:
            subnets = resource_data['Configuration']['VpcConfig']['SubnetIds'][0]
        except:
            subnets = ''
    else:
        vpc = ''
        security_groups = ''
        subnets = ''


    mapped_sources = { 
                        'vpc':vpc, 
                        'security_groups':security_groups, 
                        'subnets':subnets
                    }
    return mapped_sources

def add_tag(job_information, this_region, resource_id,add_tags):
    # Connect to AWS
    session = boto3.Session(profile_name=job_information['aws_profile'])
    lambda_client = session.client('lambda', region_name = this_region)

    # Get ARN
    lambda_arn = lambda_client.get_function(FunctionName=resource_id)['Configuration']['FunctionArn']
    
    # Format tags
    set_tags = {}
    for add_tag in add_tags:
        set_tags[add_tag['Key']] = add_tag['Value']


    response = lambda_client.tag_resource(
        Resource=lambda_arn,
        Tags=set_tags
    )

def get_tag(job_information, this_region, resource_id):
    return process_resource( job_information, this_region, resource_id )


def search(job_information):
    for this_region in job_information['region_name']:
        process_resource( job_information, this_region, 'none' )


def process_resource( job_information, this_region, resource_id ):
        
        # Connect to AWS
        session = boto3.Session(profile_name=job_information['aws_profile'])
        lambda_client = session.client('lambda', region_name = this_region)
        
        # Itearate trough all EC2 instances
        resource_name = 'lambda'
        paginator = lambda_client.get_paginator('list_functions')
        for page in paginator.paginate():
            for f in page['Functions']:
                
                r = lambda_client.get_function(FunctionName=f['FunctionName'])

                all_tags = []

                if "Tags" in r:
                    for key,value in r['Tags'].items():
                        all_tags.append( { "Key":key, "Value":value } )
                
                if resource_id == 'none' or resource_id == r['Configuration']['FunctionName']:

                    add_resource.run( resource_name, r['Configuration']['FunctionName'], all_tags, this_region )

                    if resource_id != 'none':
                        return all_tags
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
                                                all_tags, 
                                                r['Configuration']['FunctionName'], 
                                                job_information['hints_lists'],
                                                helper.send_mapped_resources(job_information, mapped_sources, resource_name), 
                                                r['Configuration']['Description'], 
                                                r['Configuration']['FunctionName']
                                            )


if __name__ == '__main__':
    search()