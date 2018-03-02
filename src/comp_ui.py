#coding=utf-8
from Tkinter import *
from ttk import Combobox
import comp
import redis
import os


def get_path(ico):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    base_path=unicode(base_path,"gb2312")
    return os.path.join(base_path, ico)


class Application(Frame):

        def __init__(self,master):
            Frame.__init__(self,master)
            self.root = master
            self.root.title('company_info(Version:v1.0.3   Author:qing.guo)')
            self.root.geometry('720x460')
            self.root.resizable(0, 0)  # 禁止调整窗口大小
            self.root.protocol("WM_DELETE_WINDOW",self.close)
            self.root.iconbitmap(get_path('company.ico'))
        
        def creatWidgets(self):
            frame_left = Frame(self.root, width=360, height=460, bg='#C1CDCD')
            frame_right = Frame(self.root, width=360, height=460, bg='#C1CDCD')
            frame_left.grid_propagate(0)
            frame_right.propagate(0)
            frame_right.grid_propagate(0)
            frame_left.grid(row=0, column=0)
            frame_right.grid(row=0, column=1)
            
            self.v1 = StringVar()
            self.v2 = StringVar()
            
            
            Label(frame_left, text=u"选择数据类型:",bg='#C1CDCD').grid(row=0, column=0, pady=10, padx=5)
            self.cb1 = Combobox(frame_left,width=30,textvariable=self.v1)
            self.cb1.grid(row=0,column=1, columnspan=2,ipady=1, padx=5,pady=10,sticky=W)
            self.cb1['values']=[u'公司id',u'公司名称',u'机器人32位id或uid',u'服务器32位id或uid']
            self.cb1.current(0)
            
            Label(frame_left, text=u"输入查询数据 :", bg='#C1CDCD').grid(row=1, column=0, pady=10, padx=5)
            Entry(frame_left, width=33,textvariable=self.v2).grid(row=1,column=1,columnspan=2,padx=2,pady=10,ipady=2,sticky=W)
            self.b1=Button(frame_left, text=u"查询归属公司id",command=self.test1, bg='#C1CDCD')
            self.b1.grid(row=2,column=1,padx=5,pady=8)
            self.b2=Button(frame_left, text=u"查询公司服务器",command=self.test2, bg='#C1CDCD')
            self.b2.grid(row=3,column=1,padx=5,pady=8)

            self.b3=Button(frame_left, text=u"查询公司机器人",command=self.test3, bg='#C1CDCD')
            self.b3.grid(row=4,column=1,padx=5,pady=8)

            self.b4=Button(frame_left, text=u"查询公司人员信息",command=self.test4, bg='#C1CDCD')
            self.b4.grid(row=5,column=1,padx=5,pady=8)

            self.b5=Button(frame_left, text=u"查询部门人员信息",command=self.test5, bg='#C1CDCD')
            self.b5.grid(row=6,column=1,padx=5,pady=8)
            
            self.b6=Button(frame_left, text=u"查询剩余可用服务器",command=self.test6, bg='#C1CDCD')
            self.b6.grid(row=7,column=1,padx=5,pady=8)
            
            self.b7=Button(frame_left, text=u"查询剩余可用机器人",command=self.test7, bg='#C1CDCD')
            self.b7.grid(row=8,column=1,padx=5,pady=8)

            self.b8=Button(frame_left, text=u"删除当前公司所有信息",command=self.test8,bg='#C1CDCD')
            self.b8.grid(row=9,column=1,padx=5,pady=8)
            
            #Scrollbar
            scrollbar = Scrollbar(frame_right,bg='#C1CDCD')
            scrollbar.pack(side=RIGHT, fill=Y)
            self.text_msglist = Text(frame_right, yscrollcommand=scrollbar.set,bg='#C1CDCD')
            self.text_msglist.pack(side=RIGHT, fill=BOTH)
            scrollbar['command'] = self.text_msglist.yview
            self.text_msglist.tag_config('green', foreground='#008B00')
            self.text_msglist.tag_config('blue', foreground='#0000FF')
            self.text_msglist.tag_config('red', foreground='#FF3030')

            
        
                
        def test(self,flag):
            r=redis.StrictRedis(host='58.60.230.238',port=6278,db=0,password='qhkj_redis_987',encoding='utf-8',socket_timeout=5)
            self.com=comp.Company(flag,r,app)
            self.com.setDaemon(True)
            self.com.start()
            
        def check(self,flag):
            r=redis.StrictRedis(host='58.60.230.238',port=6278,db=0,password='qhkj_redis_987',encoding='utf-8',socket_timeout=5)
            self.v3 = StringVar()
            window = Toplevel(self,bg='#C1CDCD')
            window.title('check permission')
            window.geometry('400x100')
            window.resizable(0, 0)  # 禁止调整窗口大小
            Label(window,text=u'请输入操作密码:',bg='#C1CDCD').grid(row=0, column=0,pady=10, padx=5)
            e=Entry(window, width=30,textvariable=self.v3)
            e.grid(row=0,column=1,padx=5,pady=10,sticky=W)
            e.focus()
            self.v3.set('')
            r.set('comp_pwd','qhkj_987',nx=True)
            def check_pwd():
                input_pwd=self.v3.get()
                redis_pwd=r.get('comp_pwd')
                if input_pwd==redis_pwd:
                    if flag==6:
                        self.b6.config(state='disabled')
                        self.test(6)
                    elif flag==7:
                        self.b7.config(state='disabled')
                        self.test(7)
                    elif flag==8:
                        self.b8.config(state='disabled')
                        self.test(8)
                else:
                    self.text_msglist.insert(END,"输入密码错误\n",'red')
                window.destroy()

            Button(window, text=u"确定",width=20,command=check_pwd,bg='#C1CDCD').grid(row=1, column=1,pady=10, padx=5)
            window.protocol("WM_DELETE_WINDOW", window.destroy)
            
            
        def test1(self):
            self.b1.config(state='disabled')
            self.test(1)
        def test2(self):
            self.b2.config(state='disabled')
            self.test(2)
        def test3(self):
            self.b3.config(state='disabled')
            self.test(3)
        def test4(self):
            self.b4.config(state='disabled')
            self.test(4)
        def test5(self):
            self.b5.config(state='disabled')
            self.test(5)
        def test6(self):
            self.check(6)
        def test7(self):
            self.check(7)
        def test8(self):
            self.check(8)
        def close(self):
            self.root.quit()
            self.root.destroy()

    
if __name__ == "__main__":
    
    root=Tk()
    app=Application(root)
    app.creatWidgets()
    app.mainloop()
  

        
   

