import boto3
from src import helper, processor, add_resource

def get_mapped_sources(resource_data):

    # <AWS module name> : <resource ID key> 
    if 'DBSubnetGroup' in resource_data:
        vpc = resource_data['DBSubnetGroup']['VpcId']
        try:
            subnets = resource_data['DBSubnetGroup']['Subnets'][0]['SubnetIdentifier']
        except:
            subnets = ''
    else:
        vpc = ''
        subnets = ''

    mapped_sources = { 
                        'vpc':vpc,
                        'subnets':subnets
                    }
    return mapped_sources

def add_tag(job_information, this_region, resource_id,add_tags):
    # Connect to AWS
    session = boto3.Session(profile_name=job_information['aws_profile'])
    rds_client = session.client('rds', region_name = this_region)

    # Get ARN
    rds_arn = rds_client.describe_db_instances(DBInstanceIdentifier=resource_id)['DBInstances'][0]['DBInstanceArn']

    response = rds_client.add_tags_to_resource(
        ResourceName=rds_arn,
        Tags=add_tags
    )

def get_tag(job_information, this_region, resource_id):
    return process_resource( job_information, this_region, resource_id )


def search(job_information):
    for this_region in job_information['region_name']:
        process_resource( job_information, this_region, 'none' )


def process_resource( job_information, this_region, resource_id ):
        
        # Connect to AWS
        session = boto3.Session(profile_name=job_information['aws_profile'])
        rds_client = session.client('rds', region_name = this_region)
        
        resource_name = 'rds'
        response = rds_client.describe_db_instances()
        for instance in response['DBInstances']:

            instance_arn = instance['DBInstanceArn']
            instance_id = instance['DBInstanceIdentifier']   

            all_tags = rds_client.list_tags_for_resource(ResourceName=instance_arn)['TagList']

            if resource_id == 'none' or resource_id == instance_id:

                add_resource.run( resource_name, instance_id, all_tags, this_region )

                if resource_id != 'none':
                    return all_tags
                else:
                
                    # Get mapped_resources
                    mapped_sources = get_mapped_sources(instance)

                    # Get description
                    description = ''

                    # Get display name
                    display_name = ''
                    
                    tag_suggestions = processor.hint_processor(
                                            job_information,
                                            this_region,
                                            all_tags, 
                                            instance_id, 
                                            job_information['hints_lists'],
                                            helper.send_mapped_resources(job_information, mapped_sources, resource_name), 
                                            description, 
                                            display_name
                                        )


if __name__ == '__main__':
    search()