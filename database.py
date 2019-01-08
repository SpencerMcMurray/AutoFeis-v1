import pymysql


class Database:
    def __init__(self):
        host = "127.0.0.1"
        port = 3306
        user = "root"
        password = ""
        db = "mydb"

        self.con = pymysql.connect(host=host, port=port, user=user, password=password, db=db,
                                   cursorclass=pymysql.cursors.DictCursor, autocommit=True)
        self.cur = self.con.cursor()
