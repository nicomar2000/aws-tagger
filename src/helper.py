import os, yaml

def main():
    pass

def open_file(file_path):
    if os.path.isfile(file_path):
        file_path_content_raw = open(file_path, 'r').read() 
        file_path_content = yaml.safe_load_all(file_path_content_raw)
        return list(file_path_content)[0]
    else:
        send_logs('ERROR', 'No deployment file found')

def send_logs(this_severity, this_message):
    print('~~ ' + this_severity + " - " + this_message)
    if this_severity == 'ERROR':
        print(this_message)
        return 1
    
def send_mapped_resources(job_information, mapped_sources, resource_name):
    
    # Here we control if the resource should be sent to review depending on the selected depth level 
    send_mapped_resources = {}
    limit_control = 0
    
    for mapped_resource_name in mapped_sources:

        if 'depth_level' in job_information['aws_resources'][resource_name]:
            if limit_control >= int(job_information['aws_resources'][resource_name]['depth_level']):
                break
        
        send_mapped_resources[mapped_resource_name] = mapped_sources[mapped_resource_name]
        limit_control = limit_control + 1

    return send_mapped_resources



if __name__ == '__main__':
    main()