import boto3
from src import helper, processor, add_resource

def get_mapped_sources():
    mapped_sources = {}
    return mapped_sources

# Very important!
from .ec2_instance import add_tag

def get_tag(job_information, this_region, resource_id):
    return process_resource( job_information, this_region, resource_id )


def search( job_information):
    for this_region in job_information['region_name']:
        process_resource( job_information, this_region, 'none' )


def process_resource( job_information, this_region, resource_id ):
        
        # Connect to AWS
        session = boto3.Session(profile_name=job_information['aws_profile'])
        ec2_client = session.client('ec2',
                            region_name = this_region,
                            )
        
        # Itearate trough all EC2 instances
        resource_name = 'vpc'
        for i in ec2_client.describe_vpcs()['Vpcs']:

            if resource_id == 'none' or resource_id == i['VpcId']:

                add_resource.run( resource_name, i['VpcId'], i['Tags'], this_region )

                if resource_id != 'none':
                    return i['Tags']
                else:

                    # Get mapped_resources
                    mapped_sources = get_mapped_sources()

                    # Get description
                    description = ''

                    # Get display name
                    display_name = ''
                    
                    tag_suggestions = processor.hint_processor(
                                            job_information,
                                            this_region,
                                            i['Tags'], 
                                            i['VpcId'], 
                                            job_information['hints_lists'],
                                            helper.send_mapped_resources(job_information, mapped_sources, resource_name), 
                                            description, 
                                            display_name
                                        )


if __name__ == '__main__':
    search()