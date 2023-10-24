from .db import query

def get_job_information():


    job_information = { 
        'region_name': [],
        'aws_resources': {},
        'hints_lists': {},
        'aws_profile': 'default'
    } 

    # Get aws details
    aws_details = query("read", "SELECT * FROM aws_details")
    try:
        for aws_profile,t_aws_regions in aws_details:
            job_information['region_name'] = t_aws_regions.split(',')
            job_information['aws_profile'] = aws_profile
    except:
        pass

    # Get resources
    try:
        for id,resource_id, depth_level in query("get", "SELECT * FROM aws_module"):
            job_information['aws_resources'][resource_id] = { 'depth_level': depth_level}
    except:
        pass

    # Get hint list
    try:
        for id,tag_key, hint_name in query("get", "SELECT * FROM hints_lists"):
            alternate_hints_list = []

            # Add tag_keys
            if tag_key not in job_information['hints_lists']:
                job_information['hints_lists'][tag_key] = {}

            # Add hint and alternative hint
            for t_id,t_tag_key, t_hint_name, alternative_hint_name in query("get", "SELECT * FROM alternative_hint WHERE hint_name='"+hint_name+"'"):
                alternate_hints_list.append(alternative_hint_name)
            job_information['hints_lists'][tag_key][hint_name] = alternate_hints_list
    except:
        pass
    
    return job_information