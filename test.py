#!/usr/bin/python
# -*- coding:utf-8 -*-

import requests
import json
import uuid



class Base(object):
    user={
        "username": "admin",
        "password": "root123"
    }
    base_url='http://localhost:8080'
    category_name="默认分类"

    def __init__(self,table):
        self.table = table
        self.get_headers()
        self.get_column()
    
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
            'datasourceId':'3',
            'query': '{"sql":"'+self.sql+'"}',
            'reload': 'false'}
        response = requests.post(url,data=data,headers=self.headers)
        self.column = json.loads(response.text)["columns"]
        

class DataSet(Base):

    def __init__(self,table,dataset_name):
        self.table = table
        Base.__init__(self,self.table)
        self.dataset_name = dataset_name
        
    
    def create_dataset_json(self):
        query={"sql":self.sql}
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
        schema={"dimension":dimension_list,"measure":measure_list}
        data={
                "data":{
                    "expressions": [],
                    "filters": [],
                    "schema":schema,
                    "datasource": 3, 
                    "select":select,
                    "query":query
                    },
                "name": self.dataset_name, 
                "categoryName": self.category_name
            }
        _json = {
            'json':json.dumps(data)
        }
        return _json

    def create_dataset(self):
        url= self.base_url+'/dashboard/saveNewDataset.do'
        json=self.create_dataset_json()
        response = requests.post(url,data=json,headers=self.headers)

class Widget(DataSet):

    def __init__(self,table,widget_name,dataset_name):
        self.widget_name = widget_name
        self.table = table
        self.dataset_name = dataset_name
        Base.__init__(self,self.table,self.dataset_name)

    def create_pie_widget_json(self,keys,values,aggregate_type):
        config={
            "option": {
                "legendShow": True
            },
            "chart_type": "pie",
            "keys": [
                {
                    "col": keys,
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
                            "col": values,
                            "aggregate_type": aggregate_type
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
                    "datasource": 9, 
                    "config":config
                },
                "name": self.widget_name, 
                "categoryName": self.category_name
        }
        _json = {
            'json':json.dumps(data)
        }
        return _json

    def create_pie_widget(self):
        url= self.base_url+'/dashboard/saveNewWidget.do'
        json=self.create_pie_widget_json()
        response = requests.post(url,data=json,headers=self.headers)
        print(response.text)

# json: {"name":"OBS_MASTER_REC诊断类型人数所占比1","categoryName":"默认分类","data":{"config":{"option":{"legendShow":true},"chart_type":"pie","keys":[{"col":"VISIT_TYPE","type":"eq","values":[],"sort":"asc","id":"219e0fda-1f74-4761-92a3-66d82f961d76"}],"groups":[],"values":[{"name":"","cols":[{"col":"CASE_OBJECT_ID","aggregate_type":"count"},{"col":"CASE_OBJECT_ID","aggregate_type":"distinct"}],"series_type":"pie","type":"value"}],"filters":[]},"datasetId":9,"expressions":[],"filterGroups":[]}}
# son: {"name":"OBS_MASTER_REC诊断类型人数所占比","categoryName":"默认分类","data":{"config":{"option":{"legendShow":true},"chart_type":"pie","keys":[{"col":"VISIT_TYPE","type":"eq","values":[],"sort":"asc","id":"219e0fda-1f74-4761-92a3-66d82f961d76"}],"groups":[],"values":[{"name":"","cols":[{"col":"CASE_OBJECT_ID","aggregate_type":"count"}],"series_type":"pie","type":"value"}],"filters":[]},"datasetId":9,"expressions":[],"filterGroups":[]}}
# json2={
#     'json':'{"name":"visit_type3","categoryName":"默认分类","data":{"config":{"option":{"legendShow":true},"chart_type":"line","keys":[{"col":"VISIT_TYPE","type":"eq","values":[],"sort":"asc","id":"607e63c1-4ae6-4dee-b6c5-1bfe962c5bb5"}],"groups":[],"values":[{"name":"","cols":[{"col":"VISIT_TYPE","aggregate_type":"distinct"}],"series_type":"pie","type":"value"}],"filters":[]},"datasetId":2,"expressions":[],"filterGroups":[]}}'
# }
# json3={'json':'{"layout":{"rows":[{"type":"widget","widgets":[{"name":"图表名称3","width":12,"widgetId":1}]}]},"categoryId":null,"name":"visit_type2"}'}

# 对于我们工作中的自己人,我们一般会使用别的验证,而不是csrf_token验证
# response = requests.post('http://localhost:8080/dashboard/saveNewDataset.do',data=json,headers=header)
# response2 = requests.post('http://localhost:8080/dashboard/saveNewWidget.do',data=json2,headers=header)
# response = requests.post('http://localhost:8080/login',data=user, allow_redirects=False)
# print(response.headers)
#response = requests.post('http://localhost:8080/dashboard/saveNewBoard.do',data=json3,headers=header)
# 通过get请求返回的文本值

if __name__ == '__main__':
    wg=Widget('OBS_MASTER_REC','OBS_MASTER_REC','OBS_MASTER_REC')
    wg.create_pie_widget()
