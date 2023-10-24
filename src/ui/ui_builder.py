import os, sys, logging
from flask import Flask, jsonify, request, render_template
from ..db import query
from ..helper import open_file
from ..suggestion import add
from .templates import main
from ..lookup import review
from ..loader import get_job_information

def load_ui_data():
    main()


def start_ui():

    job_information = get_job_information()

    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    template_dir = os.path.abspath(__location__)

    app = Flask(__name__, template_folder=template_dir)
    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None
    log = logging.getLogger('werkzeug')
    log.disabled = True
    print('###########################################################################')
    print('#                                                                         #')
    print('# Open your browser and navegate to the address http://127.0.0.1:8080     #')
    print('#                                                                         #')
    print('###########################################################################')
        
    @app.route('/')
    def home():
        return render_template('tagger.html')

    @app.route('/api', methods=['POST'])
    def api():
        data = request.get_json()  

        # Add suggestions
        control = {}
        status = True
        if str(data['action']) == 'add_suggestion':
            for suggestion_id in data['suggestion']:
                result = add(job_information, suggestion_id)
                if not result:
                    status = False
                control[suggestion_id] = str(result)
        
            # Re fresh UI content
            load_ui_data()


        if str(data['action']) == 'update_aws':
            query("insert", "DROP TABLE aws_details")
            query("try", "CREATE TABLE aws_details (aws_profile PRIMARY KEY, t_aws_regions)")
            query("insert", "INSERT INTO aws_details (aws_profile, t_aws_regions) VALUES ('"+str(data['new_profile'])+"', '"+str(','.join(data['all_regions']))+"')")

        if str(data['action']) == 'add_awsresource':
            query("insert", "INSERT INTO aws_module (resource_id, depth_level) VALUES ('"+str(data['value1'])+"', '"+str(data['value2'])+"')")

        elif str(data['action']) == 'remove_awsresource':
            query("insert", "DELETE FROM aws_module WHERE resource_id='"+data['value1']+"'")

        elif str(data['action']) == 'level_depth':
            query("insert", "UPDATE aws_module SET depth_level='"+str(data['value2'])+"' WHERE resource_id='"+str(data['value1'])+"'")

        elif str(data['action']) == 'hint_add':
            query("insert", "INSERT INTO hints_lists (tag_key, hint_name) VALUES ('"+data['value2']+"','"+data['value1']+"')")

        elif str(data['action']) == 'hint_del':
            print("hint_name: "+str(data['value1']))
            print("tagkey_name: "+str(data['value2']))
            query("insert", "DELETE FROM hints_lists WHERE tag_key='"+data['value2']+"' AND hint_name='"+data['value1']+"'")

        elif str(data['action']) == 'alter_hint_add':
            print("alter_hitn_name: "+str(data['value1']))
            print("hint_name: "+str(data['value2']))
            print("tagkey_name: "+str(data['value3']))
            query("insert", "INSERT INTO alternative_hint (tag_key, hint_name, alternative_hint_name) VALUES ('"+data['value3']+"','"+data['value2']+"','"+data['value1']+"')")

        elif str(data['action']) == 'alt_hint_del':
            print("alter_hitn_name: "+str(data['value1']))
            print("hint_name: "+str(data['value2']))
            print("tagkey_name: "+str(data['value3']))
            query("insert", "DELETE FROM alternative_hint WHERE tag_key='"+data['value3']+"' AND hint_name='"+data['value2']+"' AND alternative_hint_name='"+data['value1']+"' ")

        elif str(data['action']) == 'run_loockup':
            # Review resources and re-fresh UI content
            review()
            load_ui_data()

        elif str(data['action']) == 'reload_data':

            # Re fresh UI content
            load_ui_data()

        return jsonify({"status": str(status), 'control': str(control)})

    app.run(port=8080, debug=True)

    
if __name__ == '__main__':
    load_ui_data()