import MySQLdb
import json
from MySQLdb import cursors


class Mysqlbug():
    def __init__(self):
        with open('config.json') as config:    
            data = json.load(config)
            self.database = MySQLdb.connect(host = data['host'], user = data['user'], passwd = data['password'], db = data['db'], port = 3306)
        self.signtobug = {}
        self.setBugDict()

    def setBugDict(self):
        cursor = self.database.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute("""
                SELECT id, sign, url, create_time, last_modified, priority, severity, cc_count, comment_count, status, resolution, attachment_count, duplicate_of
                FROM bugs;
            """
            )
        results = cursor.fetchall()
        for result in results:
            self.signtobug[result['id']] = result
        cursor.close()

    def getBug(self, id):
        return self.signtobug.get(id)
