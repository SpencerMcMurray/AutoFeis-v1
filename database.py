import pymysql


class Database:
    def __init__(self):
        host = "den1.mysql5.gear.host"
        port = 3306
        user = "autofeistesting"
        password = "password1@"
        db = "autofeistesting"

        self.con = pymysql.connect(host=host, port=port, user=user, password=password, db=db,
                                   cursorclass=pymysql.cursors.DictCursor, autocommit=True)
        self.cur = self.con.cursor()
