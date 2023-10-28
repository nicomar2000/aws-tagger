import boto3
from src import helper, processor, add_resource

def get_mapped_sources(resource_data):
    # <AWS module name> : <resource ID key> 
    mapped_sources = {}
    return mapped_sources

def add_tag(job_information, this_region, resource_id,add_tags):

    session = boto3.Session(profile_name=job_information['aws_profile'])
    s3_client = session.client('s3', region_name = this_region )
    response = False
    
    current_tags = get_tag(job_information, this_region, resource_id)

    new_tags = add_tags + current_tags
    try:
        set_output = s3_client.put_bucket_tagging(
            Bucket=resource_id,
            Tagging={
                'TagSet': new_tags
            }
        )
        response = True
    except:
        print('ERROR - Adding tags to: '+resource_id+' error:'+str(set_output))
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
        s3_client = session.client('s3', region_name = this_region)

        response = s3_client.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        
        # Itearate trough all S3 buckets
        resource_name = 's3'
        for bucket in buckets:            

            if resource_id == 'none' or resource_id == bucket:
                
                try:
                    this_tags = s3_client.get_bucket_tagging(Bucket=bucket)['TagSet']
                except:
                    this_tags = []

                add_resource.run( resource_name, bucket, this_tags, this_region )

                if resource_id != 'none':
                    return this_tags
                else:
                
                    # Get mapped_resources
                    mapped_sources = get_mapped_sources(bucket)

                    # Get description
                    description = ''

                    # Get display name
                    display_name = ''
                    
                    tag_suggestions = processor.hint_processor(
                                            job_information,
                                            this_region,
                                            this_tags, 
                                            bucket, 
                                            job_information['hints_lists'],
                                            helper.send_mapped_resources(job_information, mapped_sources, resource_name), 
                                            description, 
                                            display_name
                                        )


if __name__ == '__main__':
    search()