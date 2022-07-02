import requests
import xml.etree.ElementTree as ET
import json

class LBB_SEND():
        _defaults_ = {
                        "login_post_url":"",
                        "login_post_data": {
                                                        "login_id": '',
                                                        "password": "",
                                                        "access_token": ""
                                                },
                        "order_get_url":"",
                        "order_get_parameters":{
                                                        "login_id": '',
                                                        "access_token": ""
                                                }
                        }

        def __init__(self, **kwargs):
                
                self.__dict__.update(self._defaults_)
                self.__dict__.update(kwargs)
                self.login_post_url=self._defaults_["login_post_url"]
                self.login_post_data=self._defaults_["login_post_data"]
                self.login_check = requests.post(url=self.login_post_url, data=self.login_post_data)
                # print(self.login_check.text)
        
        
        def get_orders(self):

                self.order_get_url = self._defaults_["order_get_url"]
                for parameters in self._defaults_["order_get_parameters"].keys():
                        self.order_get_url = self.order_get_url+parameters+"="+self._defaults_["order_get_parameters"][parameters]+"&"
                self.order_get_url = self.order_get_url[0:-1]
                orders = requests.get(self.order_get_url)  
                string_xml = orders.content
                doc = ET.fromstring(string_xml)
                tree=ET.ElementTree(doc)
                item_list=[]   
                for veins in tree.iter("item_name"):
                        item_list.append(veins.text) 
                print(item_list)

response = requests.post(url = "http://192.168.2.47:30005/addorder", data = "Hello")
