#!/usr/bin/env python3
import sys
from src.helper import open_file
from src.ui import ui_builder
from src.lookup import review
from src.db import query

def main():

    # Create table if they dont exist
    try:
        query("try", "CREATE TABLE aws_details (aws_profile PRIMARY KEY, t_aws_regions)")
        query("try", "CREATE TABLE resources (id INTEGER PRIMARY KEY,type,aws_id TEXT UNIQUE,region)")
        query("try", "CREATE TABLE aws_module (id INTEGER PRIMARY KEY,resource_id, depth_level)")
        query("try", "CREATE TABLE current_tags (id INTEGER PRIMARY KEY,aws_id,key,value)")
        query("try", "CREATE TABLE missing_tags (id INTEGER PRIMARY KEY,resource_id,hint_source,tag_key,possible_value,found_in,hint,match_string)")
        query("try", "CREATE TABLE hints_lists (id INTEGER PRIMARY KEY,tag_key, hint_name)")
        query("try", "CREATE TABLE alternative_hint (id INTEGER PRIMARY KEY,tag_key, hint_name, alternative_hint_name)")
    except:
        pass
    
    ui_builder.load_ui_data()
    ui_builder.start_ui()

    


if __name__ == '__main__':
    main()