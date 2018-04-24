#!/usr/bin/python
# -*- coding:utf-8 -*-

import requests
import json
import uuid
import pymysql


datasourceId=3

class Base(object):
    user={
        "username": "admin",
        "password": "root123"
    }
    base_url='http://localhost:8080'
    category_name="默认分类"
    db = pymysql.connect("localhost","root","111111","cboard",charset='utf8' )

    def __init__(self,table):
        self.table = table
        self.get_headers()
        self.get_column()
        self.con = self.db
    
    def get_headers(self):
        response = requests.post(self.base_url+'/login',data=self.user, allow_redirects=False)
        self.headers = {
        "Accept":"application/json, text/plain, */*",
        "Cookie":response.headers['Set-Cookie']
        }


    def get_column(self):
        url=self.base_url+"/dashboard/getColumns.do"
        self.sql='select * from {}'.format(self.table)
        data={
            'datasourceId':str(datasourceId), #jdbc存放的id 
            'query': '{"sql":"'+self.sql+'"}',
            'reload': 'false'}
        response = requests.post(url,data=data,headers=self.headers)
        self.column = json.loads(response.text)["columns"]
        

class DataSet(Base):

    def __init__(self,table,dataset_name=None):
        self.table = table
        self.dataset_name =dataset_name if dataset_name else table 
        Base.__init__(self,self.table)
    
    def create_dataset_json(self):
        self.query={"sql":self.sql}
        select=self.column
        dimension_list=[]
        measure_list=[]
        for l in select:
            tmp = {
                "type":"column",
                "column":l,
                "id":str(uuid.uuid4())
            }
            dimension_list.append(tmp)
            measure_list.append(tmp)
        self.schema={"dimension":dimension_list,"measure":measure_list}
        data={
                "data":{
                    "expressions": [],
                    "filters": [],
                    "schema":self.schema,
                    "datasource": datasourceId, 
                    "select":select,
                    "query":self.query
                    },
                "name": self.dataset_name, 
                "categoryName": self.category_name
            }
        _json = {
            'json':json.dumps(data)
        }
        return _json

    def create_dataset_db(self):
        self.create_dataset_json()
        data = {"schema":self.schema,"datasource":datasourceId,"query":self.query,"filters":[],"expressions":[]}
        sql = "INSERT INTO `cboard`.`dashboard_dataset` (`user_id`, `category_name`, `dataset_name`, `data_json`) VALUES ('1', '{}','{}','{}');".format(self.category_name,self.dataset_name,json.dumps(data))
        cursor = self.con.cursor()
        cursor.execute(sql)
        rs = cursor.fetchall()
        self.con.commit()
        return cursor.lastrowid

    def create_dataset(self):
        url= self.base_url+'/dashboard/saveNewDataset.do'
        json=self.create_dataset_json()
        response = requests.post(url,data=json,headers=self.headers)
        print(response.text)

class Widget(DataSet):

    def __init__(self,table,widget_name,
        dataset_name,keys,values,aggregate_type):
        self.widget_name = widget_name
        self.table = table
        self.dataset_name = dataset_name
        self.keys = keys
        self.values = values
        self.aggregate_type = aggregate_type
        DataSet.__init__(self,self.table,self.dataset_name)

    def create_pie_widget_json(self):
        config={
            "option": {
                "legendShow": True
            },
            "chart_type": "pie",
            "keys": [
                {
                    "col": self.keys,
                    "type": "eq",
                    "values": [],
                    "sort": "asc",
                    "id": str(uuid.uuid4())
                }
            ],
            "groups": [],
            "values": [
                {
                    "name": "",
                    "cols": [
                        {
                            "col": self.values,
                            "aggregate_type": self.aggregate_type
                        }
                    ],
                    "series_type": "pie",
                    "type": "value"
                }
            ],
            "filters": []
        }
        data={
            "data":{
                    "expressions": [],
                    "filters": [],
                    "datasetId": 4,
                    "config":config
                },
                "name": self.widget_name, 
                "categoryName": self.category_name
        }
        _json = {
            'json':json.dumps(data)
        }
        return _json

    def create_line_widget_json(self):
        pass
    
    def create_table_widget(self):
        pass

    def create_pie_widget(self):
        url = self.base_url+'/dashboard/saveNewWidget.do'
        json = self.create_pie_widget_json()
        response = requests.post(url,data=json,headers=self.headers)
        print(response.text)


class Board(Base):
    
    def __init__(self,table,board_name,widget_id_list):
        self.table = table
        self.board_name = board_name
        self.widget_id_list = widget_id_list
        Base.__init__(self,self.table)

    def create_board_json(self):
        widgets_list = list()
        for x in self.widget_id_list:
            tmp = {
                "name": "图表"+str(x),
                "width": 12,
                "widgetId": x
            }
            widgets_list.append(tmp)

        data={
            "layout":{
                    "rows": [{
                        "type":"widget",
                        "widgets":widgets_list
                    }],
                    
                },
                "name": self.board_name, 
                "categoryId": 'null'
        }
        _json = {
            'json':json.dumps(data)
        }
        return _json
    
    def create_board(self):
        url = self.base_url+'/dashboard/saveNewBoard.do'
        json = self.create_board_json()
        response = requests.post(url,data=json,headers=self.headers)
        print(response.text)


if __name__ == '__main__':
    ds=DataSet('PRESCRIPTION_RECORD')
    ds.create_dataset_db()
    # wg=Widget('OBS_MASTER_REC','OBS_MASTER_REC','OBS_MASTER_REC','VISIT_TYPE','CASE_OBJECT_ID','count')
    # wg.create_pie_widget()
    # bd=Board('OBS_MASTER_REC','medical_test',[6,7])
    # bd.create_board()
