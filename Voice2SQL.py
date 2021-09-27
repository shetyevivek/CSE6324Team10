from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
from socket import *
from time import ctime
import time 
import subprocess
import re
import os


class Root(Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.title("Voice-To-SQL")
        self.minsize(320, 240)
        #input
        self.Input = ttk.LabelFrame(self, text = "Input.Text")
        self.Input.grid(column = 0, row = 1)
        self.labelq = ttk.Label(self.Input,text='question')
        self.labelq.grid(column = 0, row = 1)
        self.un=ttk.Entry(self.Input,width=40)
        self.un.grid(column=1,row=1)
        self.un.insert(END,'how many city there are in which the employee name is similar to aman?')
        
        self.con= ttk.Button(self.Input, text = "submit",command = self.submit)
        self.con.grid(column=2,row=1)
        self.vo=ttk.Button(self.Input,text="Voice",command=self.voice)
        self.vo.grid(column=3,row=1)
        
        self.labeld = ttk.Label(self.Input,text='database dump')
        self.labeld.grid(column = 0, row = 2)
        self.dbn= ttk.Entry(self.Input,width=40)
        self.dbn.grid(column=1,row=2)
        self.dbn.insert(END,'database_store/city.sql')
        #SQL
        self.SQL = ttk.LabelFrame(self, text = "Text-SQL")
        self.SQL.grid(column = 0, row = 2)
        self.lq=scrolledtext.ScrolledText(self.SQL,width=80,height=20)
        self.lq.grid(column=0,row=1)
        
        #result
        self.result = ttk.LabelFrame(self, text = "result")
        self.result.grid(column = 0, row = 3)
        self.plog=scrolledtext.ScrolledText(self.result,width=80,height=20)
        self.plog.grid(column=0,row=1)
        
    def submit(self):
        question= self.un.get()

        dumpf= self.dbn.get()
        
        print (question)
        print(dumpf)
        
        sqls = subprocess.check_output('python3 -m ln2sql.main -d '+ dumpf+' -l lang_store/english.csv -j output.json -i "'+ question+'"'
,stderr=subprocess.STDOUT,shell=True)
        sqls = sqls.decode()
        self.lq.insert(INSERT,question+'\n')
        self.lq.insert(INSERT,sqls+'\n')
        return
    
    def voice(self):
        return
        
        
        
root=Root()
root.mainloop()    