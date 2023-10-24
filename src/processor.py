from .db import query
from .helper import send_logs
import importlib

def get_tag_suggestion(existing_tags, resource_id, hints_lists, this_tag_key, description, display_name):

    set_output = {}
    set_output['tags'] = {}
    set_output['tags'][this_tag_key] = {}

    for hint in hints_lists[this_tag_key]:

        # Set to lower cases
        hint_orginal = hint
        hint = hint.lower()

        # Keep record of the status of the suggestion for this tag
        suggestion_status = 'missing'

        # Check hint in resource display_name
        if display_name != "":
            if hint in display_name:
                set_output['tags'][this_tag_key]['suggestion'] = { 'possible_value':hint_orginal, 'found_in': 'display_name', 'hint': hint, 'match_string': display_name }
                suggestion_status = 'found'

        # Check hint in resource description
        if description != "":
            if hint in description:
                set_output['tags'][this_tag_key]['suggestion'] = { 'possible_value':hint_orginal, 'found_in': 'description', 'hint': hint, 'match_string': description }
                suggestion_status = 'found'

        # Check hint in resource id
        if hint in resource_id.lower():
            set_output['tags'][this_tag_key]['suggestion'] = { 'possible_value':hint_orginal, 'found_in': 'resource_id', 'hint': hint, 'match_string': resource_id }
            suggestion_status = 'found'
    
        # Check if hint match any tag
        if suggestion_status == 'missing':
            search_output = search_in(existing_tags, hint)
            if search_output['found']:              
                set_output['tags'][this_tag_key]['suggestion'] = { 'possible_value':hint_orginal, 'found_in': 'tag', 'hint': hint, 'match_string': search_output['suggestion'] }
                suggestion_status = 'found'

        # Check if main entry match any alternative name tag
        if suggestion_status == 'missing':
            
            for alternative_hint in hints_lists[this_tag_key][hint_orginal]:

                alternative_hint = alternative_hint.lower()

                # Catch all alternative hint
                if alternative_hint == "*":
                    set_output['tags'][this_tag_key]['suggestion'] = { 'possible_value':hint_orginal, 'found_in': 'resource_id', 'hint': alternative_hint, 'match_string': resource_id }
                    suggestion_status = 'found'

                # Check hint in resource display_name
                if display_name != "":
                    if alternative_hint in display_name:
                        set_output['tags'][this_tag_key]['suggestion'] = { 'possible_value':hint_orginal, 'found_in': 'display_name', 'hint': alternative_hint, 'match_string': display_name }
                        suggestion_status = 'found'

                # Check hint in resource description
                if description != "":
                    if alternative_hint in description:
                        set_output['tags'][this_tag_key]['suggestion'] = { 'possible_value':hint_orginal, 'found_in': 'description', 'hint': alternative_hint, 'match_string': description }
                        suggestion_status = 'found'
                                        
                # Check alternative_hint in resource id
                if suggestion_status == 'missing':
                    if alternative_hint in resource_id.lower():
                        set_output['tags'][this_tag_key]['suggestion'] = { 'possible_value':hint_orginal, 'found_in': 'resource_id', 'hint': alternative_hint, 'match_string': resource_id }
                        suggestion_status = 'found'

                # Check alternative_hint in existing_tags:
                if suggestion_status == 'missing':
                    search_output = search_in(existing_tags, alternative_hint)
                    if search_output['found']:
                        set_output['tags'][this_tag_key]['suggestion'] = { 'possible_value':hint_orginal, 'found_in': 'tag', 'hint': alternative_hint, 'match_string': search_output['suggestion'] }
                        suggestion_status = 'found'

        set_output['tags'][this_tag_key]['suggestion_status'] = suggestion_status
        
        # Stop checking since we had found a match
        if suggestion_status != 'missing':
            break

    return set_output['tags']


def save_tag_suggestion(all_tags, resource_id, hint_source):
    for e_tag_key, e_tag_data in all_tags.items():
        if 'suggestion_status' in e_tag_data: 
            if e_tag_data['suggestion_status'] == 'found' or e_tag_data['suggestion_status'] == 'notfound':
                if e_tag_data['suggestion_status'] == 'found' :
                    possible_value = e_tag_data['suggestion']['possible_value']
                    found_in = e_tag_data['suggestion']['found_in']
                    hint = e_tag_data['suggestion']['hint']
                    match_string = e_tag_data['suggestion']['match_string']

                elif e_tag_data['suggestion_status'] == 'notfound':
                    possible_value = 'none'
                    found_in = 'none'
                    hint = 'none'
                    match_string = 'none'
                query("insert", "INSERT INTO missing_tags (resource_id,hint_source,tag_key,possible_value,found_in,hint,match_string) VALUES ('"+resource_id+"','"+hint_source+"','"+e_tag_key+"','"+possible_value+"','"+found_in+"','"+hint+"','"+match_string+"')")


def hint_processor(job_information, this_region, existing_tags, resource_id, hints_lists, mapped_resources, description, display_name):

    # Set the output
    
    for this_tag_key in hints_lists:

        set_output = {}
        set_output['tags'] = {}
        set_output['tags'][this_tag_key] = {}
        
        # Is this tag missing?
        search_needed = True
        for existing_tag in existing_tags:
            # Get key for this tag in lower case
            if existing_tag['Key'].lower() == this_tag_key.lower():
                # Avoid tags with empty values
                if existing_tag['Value'] != "":
                    search_needed = False

        # Add current tags to DB
        set_output['tags'][this_tag_key]['tag_present'] = not search_needed
        set_output['tags'][this_tag_key]['suggestion'] = {}
        
        # We need to find suggestions for missing tag
        if search_needed:
            
            set_output['tags'] = get_tag_suggestion(existing_tags, resource_id, hints_lists, this_tag_key, description, display_name)
            
            save_tag_suggestion(set_output['tags'], resource_id, 'same')

            for e_tag_key, e_tag_data in  set_output['tags'].items():
                if e_tag_data['suggestion_status'] == 'missing':
                    # Since resources is not present in DB, get data from AWS
                    missing_suggestion = True
                    for resource_name, mapped_resource_id in mapped_resources.items():
                        
                        # Store this mapped resoruces tags
                        mapped_resource_existing_tags = []

                        # Try to get resources data from DB
                        result = query("read", "SELECT * FROM current_tags WHERE aws_id='"+mapped_resource_id+"'")

                        if result:
                            
                            # Process existing tags from mapped resource
                            for id,aws_id,key,value in result:
                                mapped_resource_existing_tags.append( {'Key':key, 'Value':value} )

                        else: 

                            # Get the mapped resources module to retirve the current tags
                            try:
                                this_resource = importlib.import_module( f"aws_resources.{resource_name}")
                                mapped_resource_existing_tags = this_resource.get_tag(job_information, this_region, mapped_resource_id)
                            except:
                                send_logs('ERRrOR', 'Failed to run module '+str(resource_name) )

                        # Get tag suggestion from this mapped resources present tags                                
                        mapped_resource_tag_result = get_tag_suggestion(mapped_resource_existing_tags, mapped_resource_id, hints_lists, this_tag_key, description, display_name)
                        if e_tag_key in mapped_resource_tag_result and  mapped_resource_tag_result[e_tag_key]['suggestion_status'] == 'found':                       
                            save_tag_suggestion(mapped_resource_tag_result, resource_id, resource_name)
                            missing_suggestion = False
                            break


                    if missing_suggestion:
                        mapped_resource_tag_result = {}
                        mapped_resource_tag_result[e_tag_key] = {}
                        mapped_resource_tag_result[e_tag_key]['suggestion_status'] = 'notfound'
                        mapped_resource_tag_result[e_tag_key]['suggestion'] = {}
                        save_tag_suggestion(mapped_resource_tag_result, resource_id, 'none')


def search_in(current_tags, search_value):

    send_data=""
    found=False
    search_value = str(search_value).lower()
    try:
        for current_tag in current_tags:
            tag_value = str(current_tag['Value'])
            tag_value_lowercase = tag_value.lower()
            if search_value in tag_value_lowercase:
                send_data = tag_value
                found=True

    except:
        pass

    return { 'found': found, 'suggestion': send_data }

if __name__ == '__main__':
    hint_processor()