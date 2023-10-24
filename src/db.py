import sqlite3
from .helper import send_logs

def query( db_action, db_command ):

    if db_action == "":
        send_logs('ERROR', 'DB call missing db_action variable')
        return 1

    #print('db_command: '+str(db_command))
    if db_command == "":
        send_logs('ERROR', 'DB call missing db_command variable')
        return 1

    # Connect to DB
    conn = sqlite3.connect('tagger.db')
    c = conn.cursor()

    if db_action == 'insert' or db_action == 'try':
        try:
            c.execute(db_command)
        except:
            if db_action != 'try':
                send_logs('ERROR', 'Faild to insert to DB with command: '+str(db_command))
    else:
        try:
            c.execute(db_command)
            results = c.fetchall()
            return results
        except:
            send_logs('ERROR', 'Faild to read from DB with command: '+str(db_command))
            

    conn.commit()
    conn.close()

if __name__ == '__main__':
    query()