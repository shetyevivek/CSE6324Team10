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
import mysql.connector

#**************************************************************************************************************************************************
# Global variable defined for global scope
Default_ln2SQL='ln2sql/'
Sql_dict = {}
db_dict={}
asql = []
att_values=[]
corrected_attrib = ""
where_clause = []
or_clause = []
and_clause = []
attribute1 = ""
attribute2 = ""

#**************************************************************************************************************************************************
# Database Connection for XAMPP
mydb = mysql.connector.connect(
  host = "localhost",
  user = "root",
  password = "",
  database = "team10"
)

mycursor = mydb.cursor()
myresult = ()

#**************************************************************************************************************************************************
# Entry point of the code
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

        # Input Question Textbox
        #self.un.insert(END, "Count how many city there are with the name <'blob'>")
        #self.un.insert(END, "Display the firstname of student whose age is between <21> and <25>")
        self.un.insert(END, "What is the average age of student whose name is <'Doe'> and age over <25>")
        
        self.con= ttk.Button(self.Input, text = "submit",command = self.submit)
        self.con.grid(column=2,row=1)
        #self.vo=ttk.Button(self.Input,text="Voice",command=self.voice)
        #self.vo.grid(column=3,row=1)
        
        self.labeld = ttk.Label(self.Input,text='Database Dump')
        self.labeld.grid(column = 0, row = 2)
        self.dbn= ttk.Entry(self.Input,width=40)
        self.dbn.grid(column=1,row=2)
        self.dbn.insert(END,'database_store/school.sql')
        #SQL
        self.SQL = ttk.LabelFrame(self, text = "Text-SQL")
        self.SQL.grid(column = 0, row = 2)
        self.lq=scrolledtext.ScrolledText(self.SQL,width=80,height=20)
        self.lq.grid(column=0,row=1)
        
        # Result from database
        self.result = ttk.LabelFrame(self, text = "Results")
        self.result.grid(column = 0, row = 3)
        self.plog=scrolledtext.ScrolledText(self.result,width=80,height=20)
        self.plog.grid(column=0,row=1)
    
    # After clicking submit button
    def submit(self):
        question= self.un.get()
        dumpf= self.dbn.get()

        dc = "<'>"
        m_question = question
        for c in dc:
            m_question = m_question.replace(c, "")
            print("Vivek's Question: " + m_question)
        
        print(question)
        print(dumpf)
        
        # To run on Linux, use python3 -m
        sqls = subprocess.check_output('python -m ln2sql.main -d '+ dumpf +' -l lang_store/english.csv -j output.json -i "'+ m_question +'"', stderr=subprocess.STDOUT,shell=True)
        sqls = sqls.decode()
        #clear the log
        self.lq.delete(1.0,'end')
        self.plog.delete(1.0,'end')
        #insert question
        self.lq.insert(INSERT,time.strftime('%Y-%m-%d %H:%M:%S')+": "+question+'\n')
        #insert ln2SQL output.
        self.lq.insert(INSERT,time.strftime('%Y-%m-%d %H:%M:%S')+": Ln2SQL Output:"+ sqls + '\n')
        
 #******************************************************************************************************************************************************************       
        # check the output of ln2SQL
        r = self.checkFailures(sqls,question,dumpf) #return value r[0] 0 pass(r[1] empty), -1 detected but cannot fix it(r[1] empty) , -2 can fix it(r[1] fixed result)
        if (r[0]==0):
            self.lq.insert(INSERT,time.strftime('%Y-%m-%d %H:%M:%S')+": The output passed the check --> (No SQL Syntax Errors)"+ '\n') 
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
        #att_values=[]
        word_split = question.split()
        print(word_split)

        for attrib in word_split:
            x = re.search("^<.*>$", attrib)
            if x:
                att_values.append(attrib[1:-1])
                print("Oye!")
                print(att_values)

#**********************************************************************************************************************************************
        # Calling the CheckValues Function
        z = self.checkValues(Sql_dict, att_values)
        print(z)
        if (z==0):
            self.lq.insert(INSERT,time.strftime('\n\n' + '%Y-%m-%d %H:%M:%S')+": No need replace the attribute values"+ '\n')

            mycursor.execute(sqls)
            myresult = mycursor.fetchall()

            for x in myresult:
                self.plog.insert(INSERT, x)
                self.plog.insert(INSERT, '\n')

        if(z==1):
            self.lq.insert(INSERT,time.strftime('\n\n' + '%Y-%m-%d %H:%M:%S')+": We need to replace the attribute values"+ '\n\n')
            self.lq.insert(INSERT,time.strftime('%Y-%m-%d %H:%M:%S')+": After replacing the attribute values:"+ '\n')
            
            # Calling the addValues Function
            var = self.addValues(question,word_split,db_dict,Sql_dict,r,sqls,att_values)
            cquery = ""
            for s in var[1]:
                self.lq.insert(INSERT, s+'\n')
                cquery = cquery + " "
                cquery = cquery + s

            mycursor.execute(cquery)
            myresult = mycursor.fetchall()

            for x in myresult:
                self.plog.insert(INSERT, x)
                self.plog.insert(INSERT, '\n')
        
#********************************************************************************************************************************************************
        # OpenAI API
        prom=self.buildprompt(sqls,question,dumpf)
        print(prom)
        openai.api_key = "Our OpenAI API Key"
        
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
        self.lq.insert(INSERT,"SELECT"+j["choices"][0]["text"]+  '\n\n')
        
        #split text to a list of SQL by \n
        openAIoutput= "SELECT" + j["choices"][0]["text"]
        # check the output of OpenAI API
        r = self.checkOpenAIFailures(openAIoutput,question,dumpf) #return value r[0] 0 pass(r[1] empty), -1 detected but cannot fix it(r[1] empty) , -2 can fix it(r[1] fixed result)
        if (r[0]==0):
            self.lq.insert(INSERT,time.strftime('%Y-%m-%d %H:%M:%S')+": The output of SQL translate passed the check"+ '\n') 
        elif (r[0]==-1): 
            self.lq.insert(INSERT,time.strftime('%Y-%m-%d %H:%M:%S')+": SQL translate: Failure Case is detected, but we cannot fix it"+ '\n\n')
        elif(r[0]==-2):
            self.lq.insert(INSERT,time.strftime('%Y-%m-%d %H:%M:%S')+": SQL translate: Failure Case is detected and we can fixed it"+ '\n\n')
            for s in r[1]:
                self.lq.insert(INSERT, s+'\n')
        
        
    #===== the end of submit()     
    
#**********************************************************************************************************************************************************
    # Check OpenAI Failure Case
    def checkOpenAIFailures(self,sqls,question,dumpf):
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
        #scan the output of openAI api
        #Sql_dict = {}
        sqls=sqls.splitlines()
                                            
        #====================
        #scan question=============================================
        words=question.split()
        #print(words)


        
        #start check cases        
        r=self.OpenAIcase1(question,words,db_dict,sqls) #must using a list of SQL instead of SQL_dict since two join(key conflict)
        if (r[0]!=0):  
            return r
        
        return r   
    
#**********************************************************************************************************************************************************
    # Check Ln2SQL Failure Case
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
                if (ss[0]=='AND'):
                    Sql_dict["AND"]=ss.copy()
                if (ss[0]=='OR'):
                    Sql_dict["OR"]=ss.copy()
                    
        print("Hola!")
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
        
#****************************************************************************************************************************************************************
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
                        where+=" "+Sql_dict['WHERE'][i]
                    Csql.append (where)
                    print(Csql)
                    return -2,Csql #can be fixed
                else:
                    return -1,Csql #cannot be fixed
        return 0,Csql  
    
    def checkCase04(self,question,words,db_dict,Sql_dict): #return (0) pass: (-1) cannot fixed : (-2) can be fixed (Csql is the correct sql)
        #Case4, if the SQL statement doesnot have between and and keywords
        # && the original question has the between and and keyword like questions
        # && From database definition, nomentioned table has the attribute which mentioned in question, we can safely conclude that the failure happens.
        Csql=[]
        if (("between" in words) & ("and" in words)):
            #get between and and keyword.
             table1=Sql_dict['FROM'][1]
             attribute = Sql_dict['WHERE'][1]
        if(("BETWEEN") not in Sql_dict["WHERE"] and ("AND") not in Sql_dict["WHERE"]):
            #is fixable? if table has datatype.
            fixable=1 #flag
            if (fixable==1): #if fixable
                Csql.append('SELECT '+ Sql_dict["SELECT"][1]) #SELECT Clause
                Csql.append( 'FROM ' + table1)
                where="WHERE " + attribute + " BETWEEN "+ (Sql_dict['WHERE'][3]).replace(";","") +" AND " + Sql_dict["WHERE"][3]
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
        
#*****************************************************************************************************************************************************************************   
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
                    return 0

            else:
                value1 = Sql_dict["WHERE"][3]

                if(value1 not in att_values):
                    return 1
                else:
                    return 0

        if("OR" in Sql_dict):
            value2 = Sql_dict["OR"][3]

            if(value2 not in att_values):
                return 1
            else:
                return 0

        if("AND" in Sql_dict):
            value2 = Sql_dict["AND"][3]

            if(value2 not in att_values):
                return 1
            else:
                return 0

        else:
            print("Inside")
            return 0

#******************************************************************************************************************************************************
    #Function to change attribute Values
    def addValues(self,question,word_split,db_dict,Sql_dict,r,sqls, att_values):
        # check the output of ln2SQL
        if (r[0]==0 or r[0]==-1):
            print("Hello VVVS")
            asql=sqls.splitlines()
            asql = asql[1:-1]
            print(asql)
        elif(r[0]==-2):
            asql=r[1]
            print(asql)
            print("Hello VVS")
        #at this moment. we deal with asql. a sql statement.
        # find where 
                
        i=0
        j=0
        for s in asql:
            ss=s.split()
            print(ss)
            if (ss[0]=="WHERE"):
                print("Foxing")
                j=i
                where_clause = asql[j].split()
                print(asql[j].split())
                print("Fox")
            i+=1
        #asql[j] is the where clause.
        
        #if between condition,change the values in the between
        if('WHERE' in where_clause and 'BETWEEN' in where_clause and 'AND' in where_clause):
            where_clause[3] = att_values[0]
            where_clause[5] = att_values[1]

        if('WHERE' in where_clause and ('=' in where_clause or '>' in where_clause or '>=' in where_clause or '<' in where_clause or '<=' in where_clause)):
            where_clause[3] = att_values[0]

        asql[j] = ' '.join(where_clause)
        print(asql)

        x=0
        y=0
        for s in asql:
            ss=s.split()
            #print("Chocolate")
            #print(att_values[1])
            print(ss)
            if (ss[0]=="OR"):
                print("Foxing")
                y=x
                or_clause = asql[y].split()
                print(asql[y].split())
                print("Fox")
                if('OR' in or_clause and ('=' in or_clause or '>' in or_clause or '>=' in or_clause or '<' in or_clause or '<=' in or_clause)):
                    or_clause[3] = att_values[1]
                asql[y] = ' '.join(or_clause)
            x+=1

        p=0
        q=0
        for s in asql:
            ss=s.split()
            #print("Chocolate")
            #print(att_values[1])
            print(ss)
            if (ss[0]=="AND"):
                print("Foxing")
                q=p
                and_clause = asql[q].split()
                print(asql[q].split())
                print("Fox")
                if('AND' in and_clause and ('=' in and_clause or '>' in and_clause or '>=' in and_clause or '<' in and_clause or '<=' in and_clause)):
                    and_clause[3] = att_values[1]
                asql[q] = ' '.join(and_clause)
            p+=1

        return 0, asql
    
#************************************************************************************************************************************************
    # Check Case 2 function
    def checkCase02(self,question,words,db_dict,Sql_dict): #return (0) pass: (-1) cannot fixed : (-2) can be fixed (Csql is the correct sql)
        #Case2, if the Question has two or more table names. 
        # && the output does't has a inner join. we can safely conclude that the failure 2 happens.
        # cannot be fixed since no attr. if has attr, ln2SQL will give a correct answer. aggraisive approch. scan data. 
        
        Csql=[] 
        # count tables name in question.
        count=0
        for w in words:
            if ("`"+w+"`" in db_dict):
                count+=1
                
        #if count more than 2 and inner join not in. happens.         
        if ((count>=2) and ("INNER JOIN" not in Sql_dict)):
            return -1,Csql
        else:    
            return 0,Csql

#*****************************************************************************************************************************************************8
    # OpenAI Case 1 function
    def OpenAIcase1(self,question,words,db_dict,Sqls): #must using a list of SQL instead of SQL_dict since two join(key conflict)
        # has two join clauses and on join table isn't mentioned in question.
        Csql=[]
        Jtables=[]
        #count join clause
        count =0
        for s in Sqls:
            s=s.split()
            if (s[0]=="JOIN"):
                count+=1
                Jtables.append(s[1])
                
        #if
        if (count==2):
            if (Jtables[0] not in words and Jtables[1] in words):
                for i in range(len(Sqls)):
                    s=Sqls[i].split()
                    if (s[1]!= Jtables[0]):
                        Csql.append(Sqls[i])
                return -2,Csql
            
            if (Jtables[0] in words and Jtables[1] not in words):
                for i in range(len(Sqls)):
                    s=Sqls[i].split()
                    if (s[1]!= Jtables[1]):
                        Csql.append(Sqls[i])
                return -2,Csql    
        return 0,Csql
        
root=Root()
root.mainloop()