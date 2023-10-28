import boto3
from src import helper, processor, add_resource

def get_mapped_sources(resource_data):
    # <AWS module name> : <resource ID key> 
    try:
        mapped_sources = { 'vpc':resource_data['endpointConfiguration']['vpcEndpointIds'][0] }
    except:
        mapped_sources = {}

    return mapped_sources

# This function would be use for 
def add_tag(job_information, this_region, resources_id,tags):

    session = boto3.Session(profile_name=job_information['aws_profile'])
    apigateway_client = session.client('apigateway', region_name = this_region )

    response = False
    
    send_tags = {}

    for e_tag in tags:
        send_tags[e_tag['Key']] = e_tag['Value']
    try:
        response = apigateway_client.tag_resource(
            resourceArn=f'arn:aws:apigateway:{this_region}::/restapis/{resources_id}',
            tags=send_tags
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
        apigateway_client = session.client('apigateway', region_name = this_region)
        
        # Itearate trough all apigateway instances
        resource_name = 'apigateway'
        for r in apigateway_client.get_rest_apis()['items']:

            api_name = r['id']
                        
            if resource_id == 'none' or resource_id == api_name:
                

                this_tags = [] 
                response = apigateway_client.get_tags(
                    resourceArn=f'arn:aws:apigateway:{this_region}::/restapis/{api_name}'
                )
                for key in response['tags']:
                    this_tags.append( {'Key':key, 'Value':response['tags'][key]} )

                add_resource.run( resource_name, api_name, this_tags, this_region )

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
                                            api_name, 
                                            job_information['hints_lists'],
                                            helper.send_mapped_resources(job_information, mapped_sources, resource_name), 
                                            description, 
                                            display_name
                                        )


if __name__ == '__main__':
    search()