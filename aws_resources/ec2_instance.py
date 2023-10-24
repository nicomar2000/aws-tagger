import boto3
from src import helper, processor, add_resource

def get_mapped_sources(resource_data):
    # <AWS module name> : <resource ID key> 
    mapped_sources = { 'vpc':resource_data['VpcId'],'image':resource_data['ImageId'],'subnet':resource_data['SubnetId'] }
    return mapped_sources

# This function would be use for 
def add_tag(job_information, this_region, resources_id,tags):

    session = boto3.Session(profile_name=job_information['aws_profile'])
    ec2_client = session.client('ec2', region_name = this_region )
    response = False
    try:
        response = ec2_client.create_tags(
            DryRun=False,
            Resources=[resources_id],
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
        ec2_client = session.client('ec2', region_name = this_region)
        
        # Itearate trough all EC2 instances
        resource_name = 'ec2_instance'
        for r in ec2_client.describe_instances()['Reservations']:
            for i in r['Instances']:
                
                if resource_id == 'none' or resource_id == i['InstanceId']:
                    
                    try:
                        this_tags = i['Tags']
                    except:
                        this_tags = []

                    add_resource.run( resource_name, i['InstanceId'], this_tags, this_region )

                    if resource_id != 'none':
                        return this_tags
                    else:
                    
                        # Get mapped_resources
                        mapped_sources = get_mapped_sources(i)

                        # Get description
                        description = ''

                        # Get display name
                        display_name = ''
                        
                        tag_suggestions = processor.hint_processor(
                                                job_information,
                                                this_region,
                                                this_tags, 
                                                i['InstanceId'], 
                                                job_information['hints_lists'],
                                                helper.send_mapped_resources(job_information, mapped_sources, resource_name), 
                                                description, 
                                                display_name
                                            )


if __name__ == '__main__':
    search()