from .db import query
from .helper import send_logs

def run( device_type, aws_id, current_tags, aws_region ):

    # Avoid resource duplication
    result = query("read", "SELECT * FROM resources WHERE aws_id='"+aws_id+"'")

    if not result:

        query("try", "INSERT INTO resources (type,aws_id,region) VALUES ('"+device_type+"','"+aws_id+"','"+aws_region+"')")
        
        # Prepare present_tags
        for each_tag in current_tags:

            # Avoid tags with empty values
            if each_tag['Value'] != "":
                query("insert", "INSERT INTO current_tags (aws_id,key,value) VALUES ('"+aws_id+"','"+str(each_tag['Key'])+"','"+str(each_tag['Value'])+"')")
            else:
                send_logs('WARNING', 'Failed to add current tags on '+str(aws_id))


if __name__ == '__main__':
    run()