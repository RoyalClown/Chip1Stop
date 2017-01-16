import time
from pymongo import MongoClient

from Lib.DBConnection.Constant import Mongo_Url


class MongoConnection:
    def __init__(self, data=None):
        conn = MongoClient(*Mongo_Url)
        self.db = conn.local
        self.col = self.db.product
        self.data = data

    def db_create(self):
        print(self.data)
        self.col.insert(self.data)
        return

    def db_retrieve_all(self):
        try:
            data = self.col.find()
            return data
        except:
            print("查询全部数据失败")

    def db_retrieve(self):
        try:
            data = self.col.find(self.data)
            return data
        except:
            print("查询数据失败")

    def db_update(self, new_data):
        try:
            self.col.update({self.data}, {'$set': {new_data}})
        except:
            print("更新数据失败")
        return new_data

    def db_delete(self):
        try:
            self.col.remove({self.data})
        except:
            print("删除数据失败")

        return


if __name__ == "__main__":
    connection = MongoConnection({"label": "TECHCODE"})
    data_list = connection.db_retrieve()
    for i in data_list:
        time.sleep(0.01)
        print(i)
