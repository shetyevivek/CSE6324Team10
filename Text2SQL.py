# Updated File
from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
from socket import *
from time import ctime
import time 
import subprocess
import re
import os
import openai
import json

Default_ln2SQL='ln2sql/'
Sql_dict = {}
db_dict={}


class Root(Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.title("Text-To-SQL")
        self.minsize(320, 240)
        #input
        self.Input = ttk.LabelFrame(self, text = "Input.Text")
        self.Input.grid(column = 0, row = 1)
        self.labelq = ttk.Label(self.Input,text='Question')
        self.labelq.grid(column = 0, row = 1)
        self.un=ttk.Entry(self.Input,width=40)
        self.un.grid(column=1,row=1)
        self.un.insert(END,"Count how many city there are with the name blob")
        #self.un.insert(END,"Display the firstname of student whose age is between 21 and 25")
        
        self.con= ttk.Button(self.Input, text = "submit",command = self.submit)
        self.con.grid(column=2,row=1)
        #self.vo=ttk.Button(self.Input,text="Voice",command=self.voice)
        #self.vo.grid(column=3,row=1)
        
        self.labeld = ttk.Label(self.Input,text='Database Dump')
        self.labeld.grid(column = 0, row = 2)
        self.dbn= ttk.Entry(self.Input,width=40)
        self.dbn.grid(column=1,row=2)
        self.dbn.insert(END,'database_store/city.sql')
        #SQL
        self.SQL = ttk.LabelFrame(self, text = "Text-SQL")
        self.SQL.grid(column = 0, row = 2)
        self.lq=scrolledtext.ScrolledText(self.SQL,width=80,height=40)
        self.lq.grid(column=0,row=1)
        
        #result
        #self.result = ttk.LabelFrame(self, text = "result")
        #self.result.grid(column = 0, row = 3)
        #self.plog=scrolledtext.ScrolledText(self.result,width=80,height=20)
        #self.plog.grid(column=0,row=1)
    
    
    def submit(self):
        question= self.un.get()

        dumpf= self.dbn.get()
        
        print (question)
        print(dumpf)
        
        sqls = subprocess.check_output('python -m ln2sql.main -d '+ dumpf +' -l lang_store/english.csv -j output.json -i "'+ question +'"', stderr=subprocess.STDOUT,shell=True)
        sqls = sqls.decode()
        #clear the log
        self.lq.delete(1.0,'end')
        #insert question
        self.lq.insert(INSERT,time.strftime('%Y-%m-%d %H:%M:%S')+": "+question+'\n')
        #insert ln2SQL output.
        self.lq.insert(INSERT,time.strftime('%Y-%m-%d %H:%M:%S')+": Ln2SQL output:"+ sqls + '\n')
        
        
        # check the output of ln2SQL
        r = self.checkFailures(sqls,question,dumpf) #return value r[0] 0 pass(r[1] empty), -1 detected but cannot fix it(r[1] empty) , -2 can fix it(r[1] fixed result)
        if (r[0]==0):
            self.lq.insert(INSERT,time.strftime('%Y-%m-%d %H:%M:%S')+": The output passed the check"+ '\n') 
        elif (r[0]==-1): 
            self.lq.insert(INSERT,time.strftime('%Y-%m-%d %H:%M:%S')+": Failure Case is detected, but we cannot fix it"+ '\n')
        elif(r[0]==-2):
            self.lq.insert(INSERT,time.strftime('%Y-%m-%d %H:%M:%S')+": Failure Case is detected and we can fixed it"+ '\n')
            for s in r[1]:
                self.lq.insert(INSERT, s+'\n')
                
        #Vivek        
        #r=addvalue(question,words,db_dict,Sql_dict,r) # < >      r[0]=0 
        #if (r[0] ==0):
        #    self.lq.insert(INSERT,time.strftime('%Y-%m-%d %H:%M:%S')+": do not need replace values"+ '\n') 
        #elif (r[0]==-1): 
        #    self.lq.insert(INSERT,time.strftime('%Y-%m-%d %H:%M:%S')+": replaced value for between and case"+ '\n')
        #elif(r[0]==-2):
        #    self.lq.insert(INSERT,time.strftime('%Y-%m-%d %H:%M:%S')+": replaced values"+ '\n')
        #    for s in r[1]:
        #        self.lq.insert(INSERT, s+'\n')

        #print("Vivek Vishwanath Shetye")
        att_values=[]
        word_split = question.split()
        print(word_split)

        for attrib in word_split:
            x = re.search("^<.*>$", attrib)
            if x:
                att_values.append(attrib[1:-1])
                print(att_values)

        # Function Call
        z = self.checkValues(Sql_dict, att_values)
        print(z)
        if (z==0):
            self.lq.insert(INSERT,time.strftime('\n\n' + '%Y-%m-%d %H:%M:%S')+": No need replace the attribute values"+ '\n')
        if(z==1):
            self.lq.insert(INSERT,time.strftime('\n\n' + '%Y-%m-%d %H:%M:%S')+": We need to replace the attribute values"+ '\n\n')
            self.lq.insert(INSERT,time.strftime('%Y-%m-%d %H:%M:%S')+": After replacing the attribute values"+ '\n')
            var = self.addValues(question,word_split,db_dict,Sql_dict)
            for s in var[1]:
                self.lq.insert(INSERT, s+'\n')
        
        # openAI api
        prom=self.buildprompt(sqls,question,dumpf)
        print(prom)
        openai.api_key = "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"
        
        response = openai.Completion.create(
        engine="davinci-codex",
        #prompt="### Postgres SQL tables, with their properties:\n#\n# Employee(id, name, department_id)\n# Department(id, name, address)\n# Salary_Payments(id, employee_id, amount, date)\n#\n### A query to list the names of the departments which employed more than 10 employees in the last 3 months\nSELECT",
        prompt= prom,
        temperature=0,
        max_tokens=150,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["#", ";"]
        )
        j=json.loads(json.dumps(response))
        self.lq.insert(INSERT,"\n")
        self.lq.insert(INSERT,"\n")
        self.lq.insert(INSERT,time.strftime('%Y-%m-%d %H:%M:%S')+":OPENAI API:"+  '\n')
        self.lq.insert(INSERT,"SELECT"+j["choices"][0]["text"]+  '\n')
           
    def checkFailures(self,sqls,question,dumpf):
        #scan sqldump file to create db_dict (key= tablename, value = the list of attributes).=======
        path = Default_ln2SQL + dumpf
        f = open(path,"r")
        # a new dict for database.key= tablename, value = the list of attributes.
        tableName=''
        #db_dict={}
        attributeList=[] 
        inTableFlag=0 #flag use for reading all attributes under a table.
        line= f.readline()
        while line:
            strs=line.split()  #split the line
            #print(strs) 
            #if first element is 'create', it is the defination of the table. 
            if (strs!=[]):
                if (inTableFlag==1):
                    #print('11')
                    if (strs[0]!=')'):
                        attributeList.append(strs[0])
                    else:
                        inTableFlag=0 #set flag to 0
                        #print(tableName)
                        #print(attributeList)
                        db_dict[tableName]=attributeList.copy() #must use copy or deepcopy
                        attributeList.clear()
                      
                if (strs[0]=='CREATE'):
                    tableName = strs[2]
                    inTableFlag=1 #set flag to 1
                    #print ('tableName'+tableName)            
            line= f.readline()
        print(db_dict)
        f.close()
        #===========================================================
        #scan the output of ln2SQL
        #Sql_dict = {}
        sqls=sqls.splitlines()
        for s in sqls:
            if (s!=''):
                ss=s.split()
                #print(ss)
                if (ss[0]=="SELECT"): 
                    Sql_dict["SELECT"]=ss.copy()
                if (ss[0]=="FROM"): 
                    Sql_dict["FROM"]=ss.copy()
                if (ss[0]=="INNER"): 
                    Sql_dict["INNER JOIN"]=ss.copy()
                if (ss[0]=='ON'):
                    Sql_dict["ON"]=ss.copy()
                if (ss[0]=='WHERE'):
                    Sql_dict["WHERE"]=ss.copy()
                    
        print(Sql_dict)                                    
        #====================
        #scan question=============================================
        words=question.split()
        #print(words)


        
        #start check cases        
        r=self.checkCase01(question,words,db_dict,Sql_dict)
        if (r[0]!=0):  
            return r
        
        
        
        #Aakreeti, you call your checkcase4 function here. should be similar with line 143-149.
        #r=self.checkCase04(question,words,db_dict,Sql_dict)
        #if (r[0]!=0):
        #    return r
        #=======
        
        return r
        
    
    def checkCase01(self,question,words,db_dict,Sql_dict): #return (0) pass: (-1) cannot fixed : (-2) can be fixed (Csql is the correct sql)
        #Case1, if the SQL statement inner join two tables(in the example, city join emp)
        # && the original question only mentioned one table's name(in the example, city) 
        # && From database definition, nomentioned table has the attribute which mentioned in question, we can safely conclude that the failure happens.
        Csql=[]
        if (("INNER JOIN" in Sql_dict) & ("FROM" in Sql_dict) & ("WHERE" in Sql_dict)):
            #get two table names.
            
            table1=Sql_dict['INNER JOIN'][2]
            table2=Sql_dict['FROM'][1]
            
            whereClause=Sql_dict['WHERE'][1].split('.') #"emp.name"
            #print(whereClause)
            whereTable = whereClause[0]
            whereAttribute= whereClause[1]
            print(table1+" "+table2+" "+whereTable+" "+whereAttribute)
            
            #only one table in the question.
            if (table1==whereTable and question.find(table2)!=-1 and question.find(table1)==-1 and question.find(whereAttribute)!=-1): 
                #self.lq.insert(INSERT,time.strftime('%Y-%m-%d %H:%M:%S')+": Faliure Case 1 is detected"+ '\n')
                #is fixable? if table2 has a similar attribute. for example "city.cityname" can be fixed.
                fixable=0 #flag
                for a in db_dict["`"+table2+"`"]:
                    #print(a.upper()+" "+ whereAttribute.upper())
                    #print(a.upper().find(whereAttribute.upper()))
                    if(a.upper().find(whereAttribute.upper())!=-1):
                        fixAttribute=a[1:-1]
                        fixable=1
                
                if (fixable==1): #if fixable
                    Csql.append('SELECT '+ Sql_dict["SELECT"][1]) #SELECT Clause
                    Csql.append( 'FROM ' + table2)
                    where="WHERE " + table2 + '.' + fixAttribute
                    for i in range(2,len(Sql_dict['WHERE'])):
                        where+=Sql_dict['WHERE'][i]
                    Csql.append (where)
                    print(Csql)
                    return -2,Csql #can be fixed
                else:
                    return -1,Csql #cannot be fixed
        return 0,Csql  
    
    def buildprompt(self,sqls,question,dumpf):
        #read dumpfile
        #scan sqldump file to create db_dict (key= tablename, value = the list of attributes).=======
        path = Default_ln2SQL + dumpf
        f = open(path,"r")
        # a new dict for database.key= tablename, value = the list of attributes.
        tableName=''
        db_dict={}
        attributeList=[] 
        inTableFlag=0 #flag use for reading all attributes under a table.
        line= f.readline()
        while line:
            strs=line.split()  #split the line
            #print(strs) 
            #if first element is 'create', it is the defination of the table. 
            if (strs!=[]):
                if (inTableFlag==1):
                    #print('11')
                    if (strs[0]!=')'):
                        attributeList.append(strs[0])
                    else:
                        inTableFlag=0 #set flag to 0
                        #print(tableName)
                        #print(attributeList)
                        db_dict[tableName]=attributeList.copy() #must use copy or deepcopy
                        attributeList.clear()
                      
                if (strs[0]=='CREATE'):
                    tableName = strs[2]
                    inTableFlag=1 #set flag to 1
                    #print ('tableName'+tableName)            
            line= f.readline()
        print(db_dict)
        f.close()
        
        #using db_dict build prompt
        p="### Postgres SQL tables, with their properties:\n#\n# "
        #add tables and attributes
        for key, value in db_dict.items():
            p=p+ key.replace("`","")+ "("
            for v in value:
                p=p+v.replace("`","")+","
            p=p+") \n# "
        p=p+"\n### "+ question + "\nSELECT"
        #"Employee(id, name, department_id)\n# Department(id, name, address)\n# Salary_Payments(id, employee_id, amount, date)\n#\n### A query to list the names of the departments which employed more than 10 employees in the last 3 months\nSELECT",
        return p
        
    #Vivek, Aakreeti. add your function here.
    # Check if attribute values are correctly substituted
    def checkValues(self,Sql_dict, att_values):
        if not att_values:
            return 0

        if("WHERE" in Sql_dict):
            if("BETWEEN" in Sql_dict.values()):
                value1 = Sql_dict["WHERE"][3]
                value2 = Sql_dict["WHERE"][5]

                if(value1 not in att_values) and (value2 not in att_values):
                    return 1
            else:
                value1 = Sql_dict["WHERE"][3]

                if(value1 not in att_values):
                    return 1
        else:
            print("Inside")
            return 0

    #Function to change attribute Values
    def addValues(self,question,word_split,db_dict,Sql_dict):
        if (("INNER JOIN" in Sql_dict) and ("FROM" in Sql_dict) and ("WHERE" in Sql_dict)):
            #get two table names.
            Csql=[]
            corrected_attrib = ""
            
            table1=Sql_dict['INNER JOIN'][2]
            table2=Sql_dict['FROM'][1]
            
            whereClause=Sql_dict['WHERE'][1].split('.') #"emp.name"
            #print(whereClause)
            whereTable = whereClause[0]
            whereAttribute= whereClause[1]
            print(table1+" "+table2+" "+whereTable+" "+whereAttribute)
            
            #only one table in the question.
            if (table1==whereTable and question.find(table2)!=-1 and question.find(table1)==-1 and question.find(whereAttribute)!=-1): 
                #self.lq.insert(INSERT,time.strftime('%Y-%m-%d %H:%M:%S')+": Faliure Case 1 is detected"+ '\n')
                #is fixable? if table2 has a similar attribute. for example "city.cityname" can be fixed.
                fixable=0 #flag

                print(word_split)
                for attrib in word_split:
                    x = re.search("^<.*>$", attrib)
                    if x:
                        corrected_attrib = attrib[1:-1]
                        print(corrected_attrib)

                for a in db_dict["`"+table2+"`"]:
                    #print(a.upper()+" "+ whereAttribute.upper())
                    #print(a.upper().find(whereAttribute.upper()))
                    if(a.upper().find(whereAttribute.upper())!=-1):
                        fixAttribute=a[1:-1]
                        fixable=1
                
                if (fixable==1): #if fixable
                    Csql.append('SELECT '+ Sql_dict["SELECT"][1]) #SELECT Clause
                    Csql.append( 'FROM ' + table2)
                    where="WHERE " + table2 + '.' + fixAttribute
                    for i in range(2,len(Sql_dict['WHERE'])-1):
                        where+=Sql_dict['WHERE'][i]
                        where+= corrected_attrib
                    Csql.append(where)
                    print("God")
                    print(Csql)
                    return -2,Csql #can be fixed
                else:
                    return -1,Csql #cannot be fixed

        if (("FROM" in Sql_dict) & ("WHERE" in Sql_dict)):
            #get two table names.
            Csql=[]
            corrected_attrib = []
            
            #table1=Sql_dict['INNER JOIN'][2]
            table1=Sql_dict['FROM'][1]
            
            whereClause=Sql_dict['WHERE'][1].split('.') #"emp.name"
            #print(whereClause)
            whereTable = whereClause[0]
            whereAttribute= whereClause[1]
            print(table1+" " +whereTable+ " " +whereAttribute)
            
            #only one table in the question.
            if (table1==whereTable and question.find(table1)!=-1 and question.find(whereAttribute)!=-1):
                #self.lq.insert(INSERT,time.strftime('%Y-%m-%d %H:%M:%S')+": Faliure Case 1 is detected"+ '\n')
                #is fixable? if table2 has a similar attribute. for example "city.cityname" can be fixed.
                fixable=0 #flag

                print(word_split)
                for attrib in word_split:
                    x = re.search("^<.*>$", attrib)
                    if x:
                        corrected_attrib.append(attrib[1:-1])
                        print(corrected_attrib)

                for a in db_dict["`"+table1+"`"]:
                    #print(a.upper()+" "+ whereAttribute.upper())
                    #print(a.upper().find(whereAttribute.upper()))
                    if(a.upper().find(whereAttribute.upper())!=-1):
                        fixAttribute=a[1:-1]
                        fixable=1
                        #print(fixAttribute)
                
                if (fixable==1): #if fixable
                    Csql.append('SELECT '+ Sql_dict["SELECT"][1]) #SELECT Clause
                    Csql.append( 'FROM ' + table1)
                    where="WHERE " + table1 + '.' + fixAttribute + " "
                    where+=Sql_dict['WHERE'][2]
                    where+= " " + corrected_attrib[0] + " AND " + corrected_attrib[1]
                    Csql.append (where)
                    print(Csql)
                    return -2,Csql #can be fixed
                else:
                    return -1,Csql #cannot be fixed
        return 0,Csql

root=Root()
root.mainloop()