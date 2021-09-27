#python2 only

from Tkinter import *
import Tkinter as tk
import ScrolledText as tkst
from time import ctime
import ln2sqlmodule
import time 
import threading
import re
import os

def test():
    t=ln2sqlmodule.getSql("What are the name of all emp","./emp.sql")
    label.config(text=t)
    
root = Tk()             
 
# Open window having dimension 100x100
root.geometry('300x200')
 
# Create a Button
btn = tk.Button(root, text = 'Click me !', bd = '5', command=test)
label = tk.Label(text="SQL")
# Set the position of button on the top of window.  
btn.pack(side = 'top')  
label.pack() 


    

root.mainloop()