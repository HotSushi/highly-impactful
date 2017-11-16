import MySQLdb
import json
from MySQLdb import cursors


class Mysql():
    def __init__(self):
        with open('config.json') as config:    
            data = json.load(config)
            self.database = MySQLdb.connect(host = data['host'], user = data['user'], passwd = data['password'], db = data['db'], port = 3306)
        self.signtobug = {}


    def generateCrash(self):
        self.setBugDict()
        cursor = self.database.cursor()
        limit = 1000
        offset = 0
        with open('meta.json') as metadata:
            data = json.load(metadata)
            if('offset' in data):offset=data["offset"]    

        while True:
            cursor.execute("""
                SELECT id, sign, url, crash_date, os_name, os_version, cpu_info, build, version, reason, opengldriver, opengldevice
                FROM crash
                LIMIT %s
                OFFSET %s;
            """%(str(limit), str(offset))
            )

            results = cursor.fetchall()
            if(len(results)==0):
                break
            for result in results:
                if(result[1] not in self.signtobug):                    
                    continue
                row = list(result)
                row.append(self.signtobug[result[1]])
                yield row
            offset += limit
            with open('meta.json', 'w') as outfile:
                data = {"offset": offset}
                json.dump(data, outfile)
        cursor.close()

    def setBugDict(self):
        cursor = self.database.cursor() 
        cursor.execute("""
                SELECT signature.sign, GROUP_CONCAT(bugs.id SEPARATOR ',') 
                FROM signature, bugs 
                WHERE signature.sign = bugs.sign 
                GROUP BY signature.sign;
            """
            )
        results = cursor.fetchall()
        for result in results:
            self.signtobug[result[0]] = result[1]
        cursor.close()

   