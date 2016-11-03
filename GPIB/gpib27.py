#!/usr/bin/env python
#gpib.py
#written by Kevin Ersoy in Python 2.7
import sys
import socket
import time
from Tkinter import *
import visa

filename = 'favicon2.ico'
#filename = 'C:\\python\\favicon2.ico'
if hasattr(sys, '_MEIPASS'):
    # PyInstaller >= 1.6
    os.chdir(sys._MEIPASS)
    #filename = 'C:\\python\\favicon2.ico'
    filename = os.path.join(sys._MEIPASS, filename)
    print filename

def quitMe():
	sys.exit()

def button1():
	T1.delete(1.0, END)
	my_instrument = rm.open_resource(Entry1.get())
	T1.insert(INSERT, "Connected to : " + my_instrument.ask("*IDN?"))

def queryGPIB():
	my_instrument = rm.open_resource(Entry1.get())
	T1.delete(1.0, END)
	T1.insert(INSERT,my_instrument.ask(Entry2.get()))
	
def writeGPIB():
	my_instrument = rm.open_resource(Entry1.get())
	T1.delete(1.0, END)
	my_instrument.write(Entry2.get())
	T1.insert(INSERT,"Sent: "+Entry2.get())
	
def readGPIB():
	my_instrument = rm.open_resource(Entry1.get())
	T1.delete(1.0, END)
	T1.insert(INSERT,my_instrument.read())
	
def resourcesGPIB():
	T1.delete(1.0, END)
	T1.insert(INSERT,rm.list_resources())
	
top = Tk()
top.title('Interactive GPIB')
top.iconbitmap(filename)
Entry1 = StringVar()
Entry2 = StringVar()

L1 = Label(top, text="Visa Resource").grid(row=0,column=0, sticky=E)
E1 = Entry(top, width=32, bd=4, textvariable=Entry1, justify=LEFT).grid(row=0, column=1, columnspan=2)
B1 = Button(top, text="Connect", command=button1, height=1).grid(row=0, column=3)
L2 = Label(top, text="Command").grid(row=1,column=0, sticky=E)
E2 = Entry(top, width=42, bd=4, textvariable=Entry2).grid(row=1, column=1, columnspan=3)
T1 = Text(top, bd=3, height=10, width=45)
T1.grid(row=3, column=0, columnspan=4)
Entry1.set('TCPIP0::172.28.36.19::inst0::INSTR')
Entry2.set('*IDN?')
B2 = Button(top, text="Query", command=queryGPIB, height=1).grid(row=2, column=0)
B3 = Button(top, text="Write", command=writeGPIB, height=1).grid(row=2, column=1)
B4 = Button(top, text="Read", command=readGPIB, height=1).grid(row=2, column=2)
B5 = Button(top, text="Resources?", command=resourcesGPIB, height=1).grid(row=2, column=3)
L3 = Label(top, text="by Kevin Ersoy 2016").grid(row=4,column=0, columnspan=4, sticky=E)

menubar = Menu(top)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Exit", command=quitMe)
menubar.add_cascade(label="File", menu=filemenu)

top.config(menu=menubar)

rm = visa.ResourceManager();


top.mainloop()
