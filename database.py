import pymysql


class Database:
    def __init__(self):
        host = "hostname"
        port = 3306
        user = "user"
        password = "password"
        db = "db"

        self.con = pymysql.connect(host=host, port=port, user=user, password=password, db=db,
                                   cursorclass=pymysql.cursors.DictCursor, autocommit=True)
        self.cur = self.con.cursor()
