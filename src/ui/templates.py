from ..db import query
from ..helper import open_file
from aws_resources import *
from ..loader import get_job_information
import os

def main():

    job_information = get_job_information()

    header = '''
<!DOCTYPE html>
<html>
    <script src="https://www.kryogenix.org/code/browser/sorttable/sorttable.js"></script>
    
    <style>
        table.sortable {
            overflow-y: auto; 
            height: 200px; 
        }
        table.sortable thead th {
            position: sticky; /* make the table heads sticky */
            top: 0px; /* table head will be placed from the top of the table and sticks to it */
        }
        table.sortable {
            border-collapse: collapse; /* make the table borders collapse to each other */
            width: 100%;
        }
        table.sortable th,
        table.sortable td {
            padding: 8px 16px;
            border: 1px solid #ccc;
        }
        table.sortable th {
            background: #395870;
        }
        
        table.missing_tag_details {
            height: 100px;
            width: 100%;
            border-radius: 0;
        }
        table.missing_tag_details td {
            border-bottom: 0px;
            border-right: 0px;
        }
        .reviewd_tag {
            font-weight: bold;
        }
        .list_item {
            text-align: start;
        }
        table.sortable {
        border-collapse: separate;
        border-spacing: 0;
        color: #4a4a4d;
        font: 14px/1.4 "Helvetica Neue", Helvetica, Arial, sans-serif;
        }
        th,
        table.sortable td {
        padding: 10px 15px;
        vertical-align: middle;
        }
        table.sortable thead {
        background: #395870;
        background: linear-gradient(#49708f, #293f50);
        color: #fff;
        font-size: 11px;
        text-transform: uppercase;
        cursor: default;
        }
        th:first-child {
        border-top-left-radius: 5px;
        text-align: left;
        }
        th:last-child {
        border-top-right-radius: 5px;
        }
        tbody tr:nth-child(even) {
        background: #f0f0f2;
        }
        td.td_big {
            min-width: 200px;
        }
        td.td_xbig {
            min-width: 405px;
        }
        td.td_small {
            min-width: 140px;
        }
        td.td_xsmall {
            min-width: 65px;
        }
        table.sortable td {
        border-bottom: 1px solid #cecfd5;
        border-right: 1px solid #cecfd5;
        }
        table.sortable td:first-child {
        border-left: 1px solid #cecfd5;
        }
        .book-title {
        color: #395870;
        display: block;
        }
        .text-offset {
        color: #7c7c80;
        font-size: 12px;
        }
        .item-stock,
        .item-qty {
        text-align: center;
        }
        .item-price {
        text-align: right;
        }
        .item-multiple {
        display: block;
        }
        tfoot {
        text-align: right;
        }
        tfoot tr:last-child {
        background: #f0f0f2;
        color: #395870;
        font-weight: bold;
        }
        tfoot tr:last-child td:first-child {
        border-bottom-left-radius: 5px;
        }
        tfoot tr:last-child td:last-child {
        border-bottom-right-radius: 5px;
        }
        .set_regions {
            text-align: left;
        }
        .filter_table {
            height: 30px;
            width: 1100px;
        }
        .main_table {
            height: 650px;
            width: 1200px;
            overflow: auto;
        }
        .add_error {
            color: white;
            background-color: red;
        }
        [id^=level_depth_] {
            width: 35px;
        }
        .modal {
            display: none; /* Hidden by default */
            position: fixed; /* Stay in place */
            z-index: 1; /* Sit on top */
            padding-top: 100px; /* Location of the box */
            left: 0;
            top: 0;
            width: 100%; /* Full width */
            height: 100%; /* Full height */
            overflow: auto; /* Enable scroll if needed */
            background-color: rgb(0,0,0); /* Fallback color */
            background-color: rgba(0,0,0,0.4); /* Black w/ opacity */
        }

        .modal-content {
            background-color: #fefefe;
            margin: auto;
            padding: 20px;
            border: 1px solid #888;
            width: 50%;
            height: 50%;
        }
        .table_hint_list {
            overflow-y: auto; 
            height: 80%;         
        }
    </style>
    <body>

'''


    table = '''
    <div class="main_table" >
    <table style="width:100%" class="sortable">
        <thead>
            <tr>
                <th scope="col">Device type</th>
                <th scope="col">Resourcer ID</th>
                <th scope="col">Region</th>
                <th scope="col">Current tags</th>
                <th scope="col">Missing tags</th>
            </tr>
        </thead>
'''

    # Get the all data
    resources = query("read", "SELECT * FROM resources")
    current_tags = query("read", "SELECT * FROM current_tags")
    missing_tags = query("read", "SELECT * FROM missing_tags")

    # Get tags to review
    reviewd_tags = []

    # Get all tags
    all_tags = ''
    count_tags = 0
    
    for eac_tag in job_information['hints_lists']:
        reviewd_tags.append(eac_tag.lower())
        all_tags += '<div class="list_item" ><button id="hint_edit_'+eac_tag+'" data-hint="'+str(job_information['hints_lists'][eac_tag])+'" >Edit</button><button id="tagkey_delete_'+eac_tag+'" >Delete</button>' + eac_tag.capitalize()  + '</div>'
        count_tags = count_tags + 1

    # Get the selected resources
    all_resources = ''
    count_resources = 0
    path = os.path.realpath(__file__)
    dir = os.path.dirname(path)
    dir2 = dir.replace('src/ui', 'aws_resources')

    for each_file in os.listdir(dir2):
        if '.py' in each_file:
            aws_module =each_file.split('.py')[0]
            if aws_module in job_information['aws_resources']:
                dl = job_information['aws_resources'][aws_module]['depth_level']
                set_Action = 'remove'
                count_resources = count_resources + 1
            else:
                dl = 0
                set_Action = 'add'

            all_resources += '''
<div class="list_item" >
    <button id="awsresource_'''+set_Action+'''_'''+aws_module+'''" >'''+set_Action.capitalize()+'''</button>
    <select id="level_depth_'''+aws_module+'''" value="'''+str(dl)+'''">
'''
            # Add depth levels
            for i in range(0, 4):
                if str(i) == dl:
                    is_selected = 'selected'
                else:
                    is_selected = ''
                all_resources += '<option value="'+str(i)+'" '+is_selected+' >'+str(i)+'</option>'

            all_resources += '''
    </select> ''' + aws_module.capitalize()  + '''
</div>'''
            
    # Get regions count
    count_aws = len(job_information['region_name'])
    set_aws_regions = ''
    for e_posible_region in ['us-east-1','us-east-2','us-west-1','us-west-2']:
        region_selected = ''
        if e_posible_region in job_information['region_name']:
            region_selected = 'checked'
        set_aws_regions += '<input type="checkbox" id="set_region_'+str(e_posible_region)+'"  value="'+str(e_posible_region)+'" '+str(region_selected)+'>'
        set_aws_regions += '<label for="set_region_'+str(e_posible_region)+'" >'+str(e_posible_region)+'</label><br>'
    
    banner =''' 
<table id="control" >
    <thead>
        <tr>
            <th>
                <div id="togg_tag" > <a id="togg_tag_action" >+</a>  Check <span id="togg_tag_count">''' + str(count_tags) + '''</span> tag keys: </div>
            </th>
            <th>
                <div id="togg_resource" > <a id="togg_resource_action" >+</a>  ''' + str(count_resources) + ''' AWS resources type: </div>
            </th>
            <th>
                <div id="togg_aws" > <a id="togg_aws_action" >+</a> ''' + str(count_aws) + ''' AWS regions: </div>
            </th>            
            <th>
                <div id="togg_profile" > <a id="togg_profile_action" >+</a> Profile: <span id="used_profile">'''+job_information['aws_profile']+'''</span>
            </th>            
            <th>
                <button id="run_loockup">Run lookup</button><span id="suggest_lookup" style="display:none;"><-- You might whant to click this now</span>
            </th>
        </tr>                
    </thead>
    <tr>
        <th>
            <div id="togg_tag_content" style="display:none;">
            <button id="add_tag_key" >Add tag key</button>
            <input id="add_tag_key_input" >
            ''' + all_tags +'''
            </div>
        </th>
        <th>
            <div id="togg_resource_content" style="display:none;">
            ''' + all_resources +'''
            </div>
        </th>
        <th>
            <div id="togg_aws_content" style="display:none;">
            <div class="set_regions">''' + set_aws_regions +'''</div>
            </div>
        </th>
        <th>
            <div id="togg_profile_content" style="display:none;">
                <button id="change_profile">Change profile</button><input id="set_profile" value="'''+job_information['aws_profile']+'''" >
            </div>
        </th>
    </tr>
</table>'''

    # Iterate on resources
    device_type = []
    regions = []
    
    try:
        for id,type,aws_id,region in resources:

            # To sort by type in UI
            regions.append(region)
            device_type.append(type)

            this_current_tags = ''
            # Get missing tags for this resources
            for id,t_aws_id,key,value in current_tags:
                if t_aws_id == aws_id:
                    t_key = key.lower()
                    if t_key in reviewd_tags:
                        key = '<span class="reviewd_tag">' + key + '</span>'
                    this_current_tags += "<br>"+key+'='+value
            this_current_tags = this_current_tags[4:]

        
            # Get missing tags for this resources
            set_tag_key = ''
            control_missing_tags = False
            for id,resource_id,hint_source,tag_key,possible_value,found_in,hint,match_string in missing_tags:
                if resource_id == aws_id:
                    control_missing_tags = True
                    if hint_source == "same":
                        hint_source = "From this resource"

                    set_tag_key += '''
<table class="missing_tag_details">
    <tr>
        <td><b>Tag: </b>'''+tag_key+'''</td>
    </tr>
    <tr>
        <td><b>Possible value:</b> '''+possible_value+'''</td>
        <td> 
            <button class="td_possible_value_add" id="'''+str(id)+'''" >Add</button>
            <button class="td_possible_value_view" data-hs="'''+str(hint_source)+'''" data-fi="'''+str(found_in)+'''" data-ms="'''+str(match_string)+'''" data-tg="'''+str(tag_key)+'''" data-hi="'''+str(hint)+'''"  >
                Details
            </button>
        </td>
    </tr>
</table></div>'''
                
            if control_missing_tags:
                set_display = 'missing_tags'
            else:
                set_display = ''

            table += '''
        <tr class="tr_view '''+type+''' '''+set_display+''' '''+region+'''">
            <td class="td_xsmall" >'''+type+'''</td>
            <td class="td_small" >'''+aws_id+'''</td>
            <td class="td_xsmall" >'''+region+'''</td>
            <td class="td_big" >'''+this_current_tags+'''</td>
            <td class="td_xbig" >'''+set_tag_key+'''</td>
        </tr>
'''
    except:
        pass

    table += '''
        </table>
'''

    # Sorting buttons
    device_types = list(set(device_type))
    regions = list(set(regions))
    banner += '''
<div class="filter_table" >
    <table style="width:70%" class="filter_options">
        <tr>
            <td>
                <select class="set_filter" id="resource_type">
                    <option value="all" selected>All resources</option>
'''
    for this_type in device_types:
        banner += '<option value="'+this_type+'">'+this_type.capitalize()+'</option>'
    
    banner += '''
                </select>
            </td>
            <td>
                <select class="set_filter" id="display">
                    <option value="completed" selected>All tags</option>
                    <option value="missing">Missing tags</option>
                </select>
            </td>
            <td>
                <select class="set_filter" id="regions">
                    <option value="all" selected>All regions</option>
'''
    for region in regions:
        banner += '<option value="'+region+'">'+region+'</option>'
    
    banner += '''
                </select>
            </td>
            <td>
                <button class="tag_handler" id="add_tags" disabled>
                    Add Tags
                </button>

                <button class="tag_handler" id="rm_tags" disabled>
                    Remove all tags
                </button>
            </td>
            <td>
                <button id="reload_data" >
                    Data reload
                </button>            
            </td>
            <td>
                Entry counts: <span id="entry_count"><span>
            </td>
        </tr>
    </table>
</div>

<!-- The Modal -->
<div id="myModal" class="modal">

  <!-- Modal content -->
  <div id="myModalContent" class="modal-content">
    <span class="close">&times;</span>
    <p>Some text in the Modal..</p>
  </div>

</div>

'''

    footer = '''
    </body>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <script>

    var modal = document.getElementById("myModal");

    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[0];

    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
    modal.style.display = "none";
    }



    $(document).ready(function() {

        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = "none";
                reload_data();
            }
        }        

        $('body').on('click', '#change_profile, [id^=set_region_]', function() {
            // Get all regions
            var all_regions = [];
            $('[id^=set_region_]:checked').each(function() {
                all_regions.push($(this).val());
            });
            // Get profile name
            var new_profile = $('#set_profile').val();
            // Update profile name
            $('#used_profile').text(new_profile);
            // Save data
            $.ajax({
                url: '/api',
                type: 'POST',
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify({ "action": "update_aws" ,"new_profile": new_profile, "all_regions":all_regions }),
                success: function(response) {

                    if ( response.status == 'True' ) {
                        $('#suggest_lookup').show();
                    } 
                },
                error: function(error) {
                    console.log(error);
                }
            });            
        });

        set_count_entry();
        $('body').on('click', 'button[id^=hint_edit_]', function() {
            var tagkey_name = $(this).attr("id").split('hint_edit_')[1];
            open_modal(tagkey_name);
        });
        
        $('body').on('click', 'button[id^=alter_hint_add_]', function() {
            var tagkey_name = $(this).attr("id").split('alter_hint_add_')[1];
            var hint_name = $('#alter_hint_list').val();
            var alter_hitn_name = $('#new_alt_hint_name').val();
            $('#new_alt_hint_name').val("");
            // Add table element
            $('table[data-hintname="'+hint_name+'"]').append(add_alterhint(tagkey_name, hint_name, alter_hitn_name));
            update_job('alter_hint_add', alter_hitn_name, hint_name, tagkey_name);
        });

        $('body').on('click', 'button[id^=alt_hint_del_]', function() {
            var alt_hint_name = $(this).attr("id").split('alt_hint_del_')[1];
            var tagkey_name = $(this).data('key');
            var hint_name = $(this).data('hint');
            $(this).parent().parent().remove();
            update_job('alt_hint_del', alt_hint_name, hint_name, tagkey_name);
        });

        $('body').on('click', 'button[id^=hint_del_]', function() {
            var hint_name = $(this).attr("id").split('hint_del_')[1];
            var tagkey_name = $('#this_tag_key').text();
            // Remove option from dropdown
            $("#alter_hint_list option[value='"+hint_name+"']").remove();
            // Delete entry in table
            $(this).parent().parent().remove();
            update_job('hint_del', hint_name, tagkey_name);
        });

        $('body').on('click', 'button[id^=hint_add_]', function() {
            var tagkey_name = $(this).attr("id").split('hint_add_')[1];
            var value = $('#new_hint_name').val();
            $('#new_hint_name').val("");
            var alternative_hint_table = '<table data-hintname="'+value+'" class="alternative_hints_table"></table>';
            // Add value to dropdown
            $('#alter_hint_list').append('<option value="'+value+'" >'+value+'</option>');
            // Add hint to table
            $('#hint_list').append(add_hint(tagkey_name, value, alternative_hint_table));
            update_job('hint_add', value, tagkey_name);
        });

        $('body').on('click', 'button[id^=tagkey_delete_]', function() {
            var tagkey_name = $(this).attr("id").split('tagkey_delete_')[1];
            $(this).parent().remove();
            update_job('delete_tag_key', tagkey_name);
        });

        $('#add_tag_key').click(function() {
            var togg_tag_count = parseInt($('#togg_tag_count').text());
            var new_togg_tag_count = togg_tag_count + 1;
            var new_hint_word = $('#add_tag_key_input').val();
            $('#add_tag_key_input').val("");
            $('#togg_tag_count').text(new_togg_tag_count);
            $('#togg_tag_content').append('<div class="list_item" ><button id="hint_edit_'+new_hint_word+'" data-hint="{}">Edit</button><button id="tagkey_delete_'+new_hint_word+'">Delete</button>'+new_hint_word+'</div>');
            open_modal(new_hint_word);
        });

        $('button[id^=awsresource_]').click(function() {
            var action_details_array = $(this).attr("id").split('_', 2);
            var action = action_details_array[1];
            var action_details = action_details_array[0] + '_' + action_details_array[1]
            var resource_name = $(this).attr("id").split(action_details+'_')[1];
            var level = $("#level_depth_"+resource_name).val();
            if (action == 'add'){
                $('#'+$(this).attr("id")).text('Remove');
                $('#'+$(this).attr("id")).attr('id','awsresource_remove_'+resource_name);
            } else {
                $('#'+$(this).attr("id")).text('Add');
                $('#'+$(this).attr("id")).attr('id','awsresource_add_'+resource_name);
            }
            update_job(action+'_awsresource', resource_name, level);
        });

        $("[id^=level_depth_]").change(function() {
            var resource_name = $(this).attr("id").split('level_depth_')[1];
            var level = $(this).val();
            update_job('level_depth', resource_name, level);
        });

        $('div[id^=togg_]').click(function() {
            var this_id = this.id
            $("#"+this_id+"_content").toggle( function(){
                if($("#"+this_id+"_content").is(":visible")){
                    $("#"+this_id+"_action").text("-");
                } else {
                    $("#"+this_id+"_action").text("+");
                }
            });
        });

        $("#run_loockup").click(function() {
            if ($(this).hasClass('loading')){
                console.log('aborted')
                return;
            }
            run_loockup();
        });

        $(".td_possible_value_view").click(function() {
            var hint_source = $(this).data('hs');
            var found_in = $(this).data('fi');
            var match_string = $(this).data('ms');
            var tag_key = $(this).data('tg');
            var hint = $(this).data('hi');
            alert('Tag key: '+tag_key+'\\nHint source: '+hint_source+'\\nFound in: '+found_in+'\\nMatch string: '+match_string+'\\nHint: '+hint)
        });

        $(".set_filter").change(function() {
            
            var change_region = $('#regions').val();
            var change_display = $('#display').val();
            var change_to_type = $('#resource_type').val();
            
            if ( change_region == 'all' ){
                var set_region = '';
            } else {
                var set_region = '.'+change_region;
            }

            if ( change_display == 'missing' ){
                var set_display = '.'+'missing_tags';
            } else {
                var set_display = '';
            }
           
            if ( change_to_type == 'all' ){
                var set_type = '';
            } else {
                var set_type = '.'+change_to_type;
            }

            $('.tr_view').show();
            if ( change_display != 'completed' || change_to_type != 'all' || change_region != 'all'  ){
                var for_element = '.tr_view:not( '+set_display+set_type+set_region+')';
            } else {
                var for_element = '';
            }

            $(for_element).hide();

            set_count_entry();
                        
        });

        $(".td_possible_value_add").click(function() {

            if ($(this).hasClass('loading')){
                return;
            }

            add_suggestion_toggle('#'+this.id)

            count_add_suggestion()
        });

        $("#rm_tags").click(function() {
            $('.td_possible_value_add.add_suggestion').each(function() {
                add_suggestion_toggle('#'+this.id)
                $(this).removeClass('add_suggestion');
            });
            count_add_suggestion()
        });

        $("#reload_data").click(function() {

            if ($(this).hasClass('loading')){
                return;
            }
            
            $(this).html('<i class="fa fa-circle-o-notch fa-spin"></i> Loading');
            $(this).addClass('loading');

            reload_data();

        });

        $("#add_tags").click(function() {
        
            if ($(this).hasClass('loading')){
                return;
            }

            var ids = [];
            $('.td_possible_value_add.add_suggestion').each(function() {
                ids.push(this.id);
            });

            $("#add_tags, .td_possible_value_add.add_suggestion").html('<i class="fa fa-circle-o-notch fa-spin"></i> Loading');
            $("#add_tags, .td_possible_value_add.add_suggestion").addClass('loading');
            $("#rm_tags").prop("disabled", true);

            $.ajax({
                url: '/api',
                type: 'POST',
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify({ "action": "add_suggestion" ,"suggestion": ids }),
                success: function(response) {

                    var t_control = JSON.parse(response.control.replace(/'/g, '"'));
                    
                    $("#add_tags, .td_possible_value_add.add_suggestion").prop("disabled", true);
                    $("#add_tags, .td_possible_value_add.add_suggestion").removeClass('loading');
                    $("#rm_tags").prop("disabled", true);
                    $('#rm_tags').text( 'Remove all tags'); 

                    
                    if ( response.status == 'True' ) {
                        $("#add_tags, .td_possible_value_add.add_suggestion").html('Added');
                    } else {
                        $("#add_tags").html('Error');
                        $("#add_tags").addClass('add_error');

                        $.each(t_control, function(t_id, status) {

                            if ( status == 'True' ) {
                                var set_status = 'Added';
                            } else {
                                var set_status = 'Error';
                                 $(" #"+t_id+".td_possible_value_add").addClass('add_error')
                            }
                            
                            $(" #"+t_id+".td_possible_value_add").html(set_status);
                        });
                    }
                },
                error: function(error) {
                    console.log(error);
                }
            });
        });

        function open_modal(tagkey_name) {
        
            try {
                var hint_list = $('#hint_edit_'+tagkey_name).data("hint").replace(/'/g, '"');
            }
            catch(err) {
                var hint_list = '{}'
            }
            var hint_list_obj = JSON.parse(hint_list);
            var hint_name_list = ""
            var current_hint = '<div class="table_hint_list"><table id="hint_list">';
            $.each ( hint_list_obj, function (hint_name, alternative_hints){
                
                hint_name_list += '<option value="'+hint_name+'">'+hint_name+'</option>'

                var alternative_hint_table = '<table data-hintname="'+hint_name+'" class="alternative_hints_table">';
                $.each ( alternative_hints, function (key, alternative_hint){
                    alternative_hint_table += add_alterhint(tagkey_name, hint_name, alternative_hint);
                });
                alternative_hint_table += '</table>';
                
                current_hint += add_hint(tagkey_name, hint_name, alternative_hint_table);

            });
            current_hint += '</table></div>';

            var title = '<div> Tag Key: <span id="this_tag_key">'+tagkey_name+'</span></div>';
            title += '<div><button id="hint_add_'+tagkey_name+'">Add value</button> <input id="new_hint_name"> </div>';
            title += '<div><button id="alter_hint_add_'+tagkey_name+'">Add hint to </button> <select id="alter_hint_list" >'+hint_name_list+'</select> <input id="new_alt_hint_name"> </div>';

            $('#myModalContent').html(title+current_hint);
            modal.style.display = "block";

        }

        function reload_data() {

            // Requet server to re build the page from DB
            $.ajax({
                url: '/api',
                type: 'POST',
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify({ "action": "reload_data" }),
                success: function(response) {
                    $("#reload_data").html('Reload');
                    $("#reload_data").removeClass('loading');
                    location.reload();
                },
                error: function(error) {
                    console.log(error);
                }
            });        
        }

        function add_alterhint(tagkey_name, hint_name, alternative_hint) {
            var alternative_hint_table = '<tr>';
            alternative_hint_table += '<th> <button data-key="'+tagkey_name+'" data-hint="'+hint_name+'" id="alt_hint_del_'+alternative_hint+'"> Delete </button></th>';
            alternative_hint_table += '<th>'+alternative_hint+'</th>';
            alternative_hint_table += '</tr>';
            return alternative_hint_table;  
        }

        function add_hint(tagkey_name, hint_name, alternative_hint_table) {
            var current_hint = '<tr>';
            current_hint += '<th><button data-key="'+tagkey_name+'" id="hint_del_'+hint_name+'" >Delete</button></th>';
            current_hint += '<th>'+hint_name+'</th>';
            current_hint += '<th>'+alternative_hint_table+'</th>';
            current_hint += '</tr>';        

            return current_hint;
        }

        function add_suggestion_toggle(this_id) { 
            var current_text = $(this_id).text();
            if (current_text == 'Add'){
                set_text = 'Remove';
                $(this_id).addClass('add_suggestion');
            } else {
                $(this_id).removeClass('add_suggestion');
                set_text = 'Add';
            }
            $(this_id).text(set_text);
        }

        function count_add_suggestion() { 
            var to_add_count = $('.add_suggestion').length;
            if ( to_add_count == 0 ) {
                $(".tag_handler").prop("disabled", true);
                var text_to_add_count = ''
            } else {
                $(".tag_handler").prop("disabled", false);
                var text_to_add_count = '('+to_add_count+')'
            }
            $('#rm_tags').text( 'Remove all tags '+text_to_add_count);
        }

        function update_job(type, value1='', value2='', value3='') { 
            
            if ( type == 'run_loockup' ) {
                $('#suggest_lookup').hide();
            } else {
                $('#suggest_lookup').show();
            }
            $.ajax({
                url: '/api',
                type: 'POST',
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify({ "action": type, "value1": value1, "value2": value2, "value3": value3  }),
                success: function(response) {
                    if ( type == 'run_loockup' ) {
                        location.reload();
                    }
                },                
                error: function(error) {
                    console.log(error);
                }
            });

        }

        function run_loockup() { 
            $("#run_loockup").html('<i class="fa fa-circle-o-notch fa-spin"></i> Loading');
            $("#run_loockup").addClass('loading');
            update_job('run_loockup')
        }
        
        function set_count_entry() { 
            var count = $('tr.tr_view:visible').length;
            $('#entry_count').text(count);
        }
    });
    </script>
</html>
'''
    # Write page content
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    ui_file_path = os.path.join(__location__, "tagger.html")
    with open(ui_file_path, "w") as filetowrite:
        filetowrite.write(header+banner+table+footer)




if __name__ == '__main__':
    main()