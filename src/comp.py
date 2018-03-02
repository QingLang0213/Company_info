#coding='utf-8'
import threading
import requests
from Tkinter import *
import json
import traceback
import redis
import time

import sys  
reload(sys)  
sys.setdefaultencoding('utf8')

class Company(threading.Thread):
    
    def __init__(self,flag,r,app):
        threading.Thread.__init__(self)
        self.flag=flag;
        self.r=r
        self.app=app
        self.cid='-1';
        
    
    def get_id_from_name(self,name):
        '根据公司名称查询cid'
        cid=self.r.get('company_name:'+name)
        if cid:
            self.cid=cid
        


    def get_id_from_robot(self,data):
        '查询机器人所属公司'
        if data.isdigit() and len(data)<32:
            uid=data
        else:
            uid=self.r.get('user_info:device_'+data)
            if uid==None:
                self.app.text_msglist.insert(END,u'设备'+data+'还未注册\n','red')
                return -1
        cid_list=list(self.r.smembers('robot_own_comp_info:'+uid))
        if not cid_list:
            self.app.text_msglist.insert(END,u'设备'+data+'还没有绑定公司\n','blue')
            return -1
        else:
            self.cid=cid_list[0]


    def get_id_from_server(self,data):
        '根据服务器查询公司信息'
        if data.isdigit() and len(data)<32:
            face_svr_id=data
        else:
            face_svr_id=self.r.get('user_info:face_svr_'+data)
            if face_svr_id==None:
                self.app.text_msglist.insert(END,u'服务器'+data+'还未注册\n','red')
                return -1
        cid_list=list(self.r.smembers('face_server_own_comp_info:'+face_svr_id))
        if not cid_list:
            self.app.text_msglist.insert(END,u'服务器'+data+'还没有绑定公司\n','blue')
            return -1
        else:
            self.cid=cid_list[0]
        

    def timestamp_datetime(self,value):
        data_format = '%Y-%m-%d %H:%M:%S'
        value = time.localtime(float(value))
        dt = time.strftime(data_format, value)
        return dt

    def get_company_server(self):
        '查询公司下面服务器信息'
        rent_status_dict={'0':u'空闲','1':u'租赁','2':u'锁定','3':u'解锁'}
        face_svr_id_list=self.r.smembers('comp_own_face_server_info:'+self.cid)
        self.app.text_msglist.insert(END,u'公司名下服务器:\n','blue')
        for face_svr_id in face_svr_id_list:
            face_svr_did=self.r.hget('comp_face_server_info:'+self.cid+':'+face_svr_id,'face_svr_did')
            self.app.text_msglist.insert(END,face_svr_id+'  :  '+face_svr_did+'\n','blue')
            face_svr_status=self.r.hget('user_info:'+face_svr_id,'status')
            face_svr_expire=self.r.hget('user_info:'+face_svr_id,'expire')
            if face_svr_status==None:
                rent_status='0'
            else:
                rent_status=face_svr_status
            if face_svr_expire==None:
                expire=''
            else:
                expire=self.timestamp_datetime(face_svr_expire)
            self.app.text_msglist.insert(END,u'服务器状态:'+rent_status_dict[rent_status]+'    失效时间:'+expire+'\n\n','blue')

            
        self.app.text_msglist.insert(END,'\n')
            
    def get_company_rebot(self):
        '查询公司名下机器人'
        rent_status_dict={'0':u'空闲','1':u'租赁','2':u'锁定','3':u'解锁'}
        did_list=self.r.smembers('comp_own_robot_info:'+self.cid)
        self.app.text_msglist.insert(END,u'公司名下机器人:\n','blue')
        for did in did_list:
            devid=self.r.hget('user_info:'+did,'account').split('_')[-1]
            self.app.text_msglist.insert(END,did+' : '+devid+'\n','blue')
            dev_status=self.r.hget('user_info:'+did,'status')
            dev_expire=self.r.hget('user_info:'+did,'expire')
            if dev_status==None:
                rent_status='0'
            else:
                rent_status=dev_status
            if dev_expire==None:
                expire=' '
            else:
                expire=self.timestamp_datetime(dev_expire) 
            self.app.text_msglist.insert(END,u'机器人状态:'+rent_status_dict[rent_status]+'    失效时间:'+expire+'\n\n','blue')
            
        self.app.text_msglist.insert(END,'\n')
       
    def get_company_info(self):
        
        mem_prem_list=[]
        mem_info=self.r.zrange('company_staff_id_info:'+self.cid, 0 ,-1,withscores=True)
        company_info=self.r.hgetall('company_info:'+self.cid)
        if not company_info:
            self.app.text_msglist.insert(END, u'未查询到公司\n\n','red')
            return -1
        name=company_info['name']
        size=company_info['size']
        comp_vers=company_info['comp_vers']
        for mem in mem_info:
            prem_lev=mem[1]
            uid=mem[0]
            if prem_lev==1.0:
                prem=u'主管理员'
                account=self.r.hget('user_info:'+uid,'account').split('_')[-1]
            elif prem_lev==2.0:
                prem=u'辅助管理员'
            else:
                prem=u'普通成员'
            mem_prem=uid+':'+prem
            mem_prem_list.append(mem_prem)
        self.app.text_msglist.insert(END,'\n公司名称:'+name+',公司规模:'+size+',公司版本号:'+comp_vers+',主管理员：'+account+'\n','blue')
        self.app.text_msglist.insert(END,u'公司成员:\n','blue')
        i=0
        for mem_prem in mem_prem_list:
            i=i+1
            self.app.text_msglist.insert(END, mem_prem+'\n','green')
            if(i%20==0):
                time.sleep(1)
                self.app.text_msglist.see(END)  
        self.app.text_msglist.insert(END,'\n')

    def get_company_dept(self):
        dept_id_list=self.r.zrange('company_dept_id_info:'+self.cid,0,-1)
        if not dept_id_list:
            self.app.text_msglist.insert(END,u'该公司下面没有部门\n\n','blue')
            return -1
        for dept_id in dept_id_list:
            dept_info=self.r.hgetall('company_dept_info:'+self.cid+':'+dept_id)
            dept_name=dept_info['name']
            dept_level=dept_info['level']
            if dept_info.has_key('dept_mgr'):
                dept_mgr=dept_info['dept_mgr']
            else:
                dept_mgr='0'
            self.app.text_msglist.insert(END,'\n部门名称：'+dept_name+'  部门级别:'+dept_level+'  部门管理员:'+dept_mgr+'\n','blue')
            members=list(self.r.smembers('comp_dept_own_user_info:'+self.cid+':'+dept_id))
            mem_str=', '.join(members)
            self.app.text_msglist.insert(END, u'部门成员:','blue')
            self.app.text_msglist.insert(END, mem_str+'\n','green')
            self.app.text_msglist.see(END)  
        self.app.text_msglist.insert(END,'\n')

    def get_face_server(self):
        '查询可用服务器'
        face_server_id_list=self.r.keys('user_info:face_svr_*')
        self.app.text_msglist.insert(END, u'\n可用服务器：\n','blue')
        for face_server_id in face_server_id_list:
            uid=self.r.get(face_server_id)
            cid_list=self.r.smembers('face_server_own_comp_info:'+uid)
            if not cid_list:
                face_svr_id=face_server_id.split('_')[-1]
                self.app.text_msglist.insert(END,uid+' : '+face_svr_id+'\n','green')
                self.app.text_msglist.see(END)  
                
        self.app.text_msglist.insert(END,'\n')
    def get_face_device(self):
        '查询可用sanbot_d'
        dev_id_list=self.r.keys('user_info:device_*')
        self.app.text_msglist.insert(END, u'\n可用机器人：\n','blue')
        for dev_id in dev_id_list:
            uid=self.r.get(dev_id)
            sub_type=self.r.hget('user_info:'+uid,'sub_type')
            if sub_type=='sanbot_d':
                cid_list=self.r.smembers('robot_own_comp_info:'+uid)
                if not cid_list:
                    devid=dev_id.split('_')[-1]
                    self.app.text_msglist.insert(END,uid+' : '+devid+'\n','green')
                    self.app.text_msglist.see(END)  
        self.app.text_msglist.insert(END,'\n')

    def delete_company(self):
        headers = {'content-type':'application/json'}
        url='http://58.60.230.238:11109/comp_del_req'
        if self.cid=='-1':
             self.app.text_msglist.insert(END,u'未查询到相关公司','red')
             return -1
        params={"uid":1,"comp_id":int(self.cid)}
        response = requests.post(url, data=json.dumps(params), headers=headers)
        res_text=response.text.encode('utf-8')
        self.app.text_msglist.insert(END,u'删除公司'+self.cid+'响应\n:'+res_text+'\n','blue')
        self.app.text_msglist.insert(END,'\n')
        
    def get_cid(self):
            
        data=self.app.v2.get().strip()
        item=self.app.v1.get()
        if item==u'公司id':
            cid=self.app.v2.get()
            if cid.isdigit():
                self.cid=cid
                
        elif item==u'公司名称':
            self.get_id_from_name(data)
        elif item==u'机器人32位id或uid':
            self.get_id_from_robot(data) 
        elif item==u'服务器32位id或uid':
            self.get_id_from_server(data)


        
    def run(self):
        
        try:
            if self.flag!=6 and self.flag!=7:
                self.get_cid()
            if self.flag==1:
                 if self.cid=='-1':
                     self.app.text_msglist.insert(END, u'未查询到公司\n\n','red')
                 else:
                     self.app.text_msglist.insert(END,u'查询到公司id为:'+self.cid+'\n\n','blue')
                 self.app.b1.config(state='normal')
            elif self.flag==2:
                self.get_company_server()
                self.app.b2.config(state='normal')
            elif self.flag==3:
                self.get_company_rebot()
                self.app.b3.config(state='normal')
            elif self.flag==4:
                self.get_company_info()
                self.app.b4.config(state='normal')
            elif self.flag==5:
                self.get_company_dept()
                self.app.b5.config(state='normal')
            elif self.flag==6:
                self.get_face_server()
                self.app.b6.config(state='normal')
            elif self.flag==7:
                self.get_face_device()
                self.app.b7.config(state='normal')
            elif self.flag==8:
                self.delete_company()
                self.app.b8.config(state='normal')
            self.app.text_msglist.see(END)
        except Exception,e:
            self.app.text_msglist.insert(END,traceback.format_exc(),'red')
            self.app.b1.config(state='normal')
            self.app.b2.config(state='normal')
            self.app.b3.config(state='normal')
            self.app.b4.config(state='normal')
            self.app.b5.config(state='normal')
            self.app.b6.config(state='normal')
            self.app.b7.config(state='normal')
            self.app.b8.config(state='normal')
            
        
        





    
