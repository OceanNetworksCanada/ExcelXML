# -*- coding: utf-8 -*-
"""
Created on Fri May  8 16:38:03 2020

Modifications of Joe's StationXML to make it more user friendly.

Version 1.2.0

-Major stability improvements
-Added delete channel or station
-Addressed response file generator
-Added buttons to address minor channel or station edits individually
-Added flat response generator

Version 1.2.1

-Addresses issue where user can't update a station if they weren't changing
the station name
-Minor fixes

Version 1.3.1

-Adds a change log that can be updated by the user. Will not automatically
update but needs a summary (entered as bullets without the bullets) into the
text field. Changes are logged in the ChangeLog.txt in the '_bin' folder.
    -outside of the user entered changes, log will capture:
        -Time/date of change (PST)
        -user making the change
        -name of starting file
        -name of new file
        -list of the bullets with a '-'
        -adds separator at the end


@author: Jacob Kukovica
"""
import matplotlib
matplotlib.use('TKAgg')

import os
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as tkm
import tkinter.filedialog as tkf
import tkinter.font as tkfont
import time

from obspy import read_inventory, UTCDateTime
from datetime import datetime
from obspy.clients.nrl import NRL

from obspy.core.inventory import Inventory, Network, Station, Channel, Site, Equipment
from obspy.core.inventory.util import ExternalReference

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

import numpy as np

from tkinter import scrolledtext as st

class ExcelXML(object):
    
    def __init__ (self, inventory_path):
        self.curdir = os.getcwd()
        
        self.root = tk.Tk()
        self.nrl = NRL()
        
        
        #   Get the size of the workplace to match maximum screen size
        w, h = self.root.maxsize()
        self.version = "1.3.1"
        self.root.title(string = "Inventory Manager {}".format(self.version))
        
        self.dw = w
        self.dh = h
        
        self.var1 = tk.IntVar()
        self.var1.set(0)
        
        fst = tkfont.Font(family = "Lucida Grande", size = 16, underline = 1)
        fsb = tkfont.Font(family = "Lucida Grande", size = 14)
        

        
        #   Create main app layout
        os.makedirs("_bin", exist_ok = True)
        os.makedirs("_Inventories", exist_ok = True)
        os.makedirs("_sensorRESP", exist_ok = True)
        os.makedirs("_dataloggerRESP", exist_ok = True)
        self.inventory_path = ""
        
        #   Empty Variables
        self.workingInv = None
        self.statWork = None
        self.chanWork = None
        self.workSelect = []
        self.treeTitle = tk.StringVar()
        self.treeTitle.set("No Inventory Selected")
        
        self.degS = u"\u00b0"
        
        self.InitialFile = None
        
        #   Empty Variables - Stat Widget
        
        self.respLab = tk.StringVar()
        self.respLab.set('None')
        self.sentv1 = tk.StringVar()
        self.sentv2 = tk.StringVar()              
        self.sentv3 = tk.StringVar()                
        self.sentv4 = tk.StringVar()
        self.sentv5 = tk.StringVar()                               
        self.sentv6 = tk.StringVar()
        
        self.sdentv1y = tk.StringVar()
        self.sdentv1m = tk.StringVar()
        self.sdentv1d = tk.StringVar()
        self.sdentv1H = tk.StringVar()
        self.sdentv1M = tk.StringVar()
        self.sdentv1S = tk.StringVar()
        
        self.sdentv2y = tk.StringVar()
        self.sdentv2m = tk.StringVar()
        self.sdentv2d = tk.StringVar()
        self.sdentv2H = tk.StringVar()
        self.sdentv2M = tk.StringVar()
        self.sdentv2S = tk.StringVar()
        
        self.sdentv3y = tk.StringVar()
        self.sdentv3m = tk.StringVar()
        self.sdentv3d = tk.StringVar()
        self.sdentv3H = tk.StringVar()
        self.sdentv3M = tk.StringVar()
        self.sdentv3S = tk.StringVar()
        
        self.centv1 = tk.StringVar()
        self.centv2 = tk.StringVar()
        self.centv3 = tk.StringVar()
        self.centv4 = tk.StringVar()
        self.centv5 = tk.StringVar()
        self.centv6 = tk.StringVar()
        self.centv7 = tk.StringVar()
        self.centv8 = tk.StringVar()
        self.centv9 = tk.StringVar()
        self.centv10 = tk.StringVar()
        self.centv11 = tk.StringVar()
        self.centv12 = tk.StringVar()
        self.centv13 = tk.StringVar()
        self.centv14 = tk.StringVar()
        self.centv15 = tk.StringVar()
        
        self.cdentv1y = tk.StringVar()
        self.cdentv1m = tk.StringVar()
        self.cdentv1d = tk.StringVar()
        self.cdentv1H = tk.StringVar()
        self.cdentv1M = tk.StringVar()
        self.cdentv1S = tk.StringVar()
        
        self.cdentv2y = tk.StringVar()
        self.cdentv2m = tk.StringVar()
        self.cdentv2d = tk.StringVar()
        self.cdentv2H = tk.StringVar()
        self.cdentv2M = tk.StringVar()
        self.cdentv2S = tk.StringVar()
        
        #   Get the main directory of the application
        self.create_menubar()
        
        
        #   Create the tree
        def channelSelect(event):
            try:
                r = availTree.item(availTree.identify("item",event.x, event.y))
                
                self.workSelect = [r['values'][3],r['values'][4]]

                if self.workingInv[0][self.workSelect[0]][self.workSelect[1]].response != 'None':
                    self.respLab.set('Response Present.')
                else:
                    self.respLab.set('NO RESPONSE!')

                print('here')
                self.sentv1.set(str(self.workingInv[0][self.workSelect[0]].code))
                self.sentv2.set(str(self.workingInv[0][self.workSelect[0]].latitude))                
                self.sentv3.set(str(self.workingInv[0][self.workSelect[0]].longitude))                
                self.sentv4.set(str(self.workingInv[0][self.workSelect[0]].elevation))
                self.sentv5.set(str(self.workingInv[0][self.workSelect[0]].site.name))                                
                self.sentv6.set(str(self.workingInv[0][self.workSelect[0]].description))
                
                #   Dates - Creation
                try: 
                    self.sdentv1y.set(UTCDateTime(self.workingInv[0][self.workSelect[0]].creation_date).year)
                    self.sdentv1m.set(UTCDateTime(self.workingInv[0][self.workSelect[0]].creation_date).month)
                    self.sdentv1d.set(UTCDateTime(self.workingInv[0][self.workSelect[0]].creation_date).day)
                    self.sdentv1H.set(UTCDateTime(self.workingInv[0][self.workSelect[0]].creation_date).hour)
                    self.sdentv1M.set(UTCDateTime(self.workingInv[0][self.workSelect[0]].creation_date).minute)
                    self.sdentv1S.set(UTCDateTime(self.workingInv[0][self.workSelect[0]].creation_date).second)
                except:
                    self.sdentv1y.set('2599')
                    self.sdentv1m.set('12')
                    self.sdentv1d.set('31')
                    self.sdentv1H.set('23')
                    self.sdentv1M.set('59')
                    self.sdentv1S.set('59')
                
                #   Dates - Start
                try:
                    self.sdentv2y.set(UTCDateTime(self.workingInv[0][self.workSelect[0]].start_date).year)
                    self.sdentv2m.set(UTCDateTime(self.workingInv[0][self.workSelect[0]].start_date).month)
                    self.sdentv2d.set(UTCDateTime(self.workingInv[0][self.workSelect[0]].start_date).day)
                    self.sdentv2H.set(UTCDateTime(self.workingInv[0][self.workSelect[0]].start_date).hour)
                    self.sdentv2M.set(UTCDateTime(self.workingInv[0][self.workSelect[0]].start_date).minute)
                    self.sdentv2S.set(UTCDateTime(self.workingInv[0][self.workSelect[0]].start_date).second)
                except:
                    self.sdentv2y.set('2599')
                    self.sdentv2m.set('12')
                    self.sdentv2d.set('31')
                    self.sdentv2H.set('23')
                    self.sdentv2M.set('59')
                    self.sdentv2S.set('59')
                
                #   Dates - end
                try:
                    self.sdentv3y.set(UTCDateTime(self.workingInv[0][self.workSelect[0]].end_date).year)
                    self.sdentv3m.set(UTCDateTime(self.workingInv[0][self.workSelect[0]].end_date).month)
                    self.sdentv3d.set(UTCDateTime(self.workingInv[0][self.workSelect[0]].end_date).day)
                    self.sdentv3H.set(UTCDateTime(self.workingInv[0][self.workSelect[0]].end_date).hour)
                    self.sdentv3M.set(UTCDateTime(self.workingInv[0][self.workSelect[0]].end_date).minute)
                    self.sdentv3S.set(UTCDateTime(self.workingInv[0][self.workSelect[0]].end_date).second)
                except:
                    self.sdentv3y.set('2599')
                    self.sdentv3m.set('12')
                    self.sdentv3d.set('31')
                    self.sdentv3H.set('23')
                    self.sdentv3M.set('59')
                    self.sdentv3S.set('59')
                
                
                self.centv1.set(self.workingInv[0][self.workSelect[0]][self.workSelect[1]].code)
                self.centv2.set(self.workingInv[0][self.workSelect[0]][self.workSelect[1]].location_code)
                self.centv3.set(self.workingInv[0][self.workSelect[0]][self.workSelect[1]].latitude)
                self.centv4.set(self.workingInv[0][self.workSelect[0]][self.workSelect[1]].longitude)
                self.centv5.set(self.workingInv[0][self.workSelect[0]][self.workSelect[1]].elevation)
                self.centv6.set(self.workingInv[0][self.workSelect[0]][self.workSelect[1]].depth)
                self.centv7.set(self.workingInv[0][self.workSelect[0]][self.workSelect[1]].azimuth)
                self.centv8.set(self.workingInv[0][self.workSelect[0]][self.workSelect[1]].dip)
                self.centv9.set(self.workingInv[0][self.workSelect[0]][self.workSelect[1]].types[0])
                self.centv10.set(self.workingInv[0][self.workSelect[0]][self.workSelect[1]].sample_rate)
                
                #   Channel description - sensor
                try:
                    chanD = self.workingInv[0][self.workSelect[0]][self.workSelect[1]].equipments[0].description
                    try:
                        chanD = self.workingInv[0][self.workSelect[0]][self.workSelect[1]].equipments[0].description.split('/',1)[0]
                    except:
                        chanD = self.workingInv[0][self.workSelect[0]][self.workSelect[1]].equipments[0].description
                except:
                    chanD = 'None'
                
                self.centv11.set(chanD)
                
                #   Channel description - datalogger
                try:
                    datD = self.workingInv[0][self.workSelect[0]][self.workSelect[1]].equipments[0].description
                    try:
                        datD = self.workingInv[0][self.workSelect[0]][self.workSelect[1]].equipments[0].description.split('/',1)[1]
                    except:
                        datD = self.workingInv[0][self.workSelect[0]][self.workSelect[1]].equipments[0].description
                except:
                    datD = 'None'
                self.centv12.set(datD)
                
                #   Equipment Serial - sensor
                try:
                    chanSerial = self.workingInv[0][self.workSelect[0]][self.workSelect[1]].equipments[0].serial_number
                    try:
                        chanSerial = self.workingInv[0][self.workSelect[0]][self.workSelect[1]].equipments[0].serial_number.split('/',1)[0]
                    except:
                        chanSerial = self.workingInv[0][self.workSelect[0]][self.workSelect[1]].equipments[0].serial_number
                except:
                    chanSerial = 'None'
                self.centv13.set(chanSerial)
                
                #   Equipment Serial - datalogger
                try:
                    datSerial = self.workingInv[0][self.workSelect[0]][self.workSelect[1]].equipments[0].serial_number
                    try:
                        datSerial = self.workingInv[0][self.workSelect[0]][self.workSelect[1]].equipments[0].serial_number.split('/',1)[1]
                    except:
                        datSerial = self.workingInv[0][self.workSelect[0]][self.workSelect[1]].equipments[0].serial_number
                except:
                    datSerial = 'None'
                self.centv14.set(datSerial)
                
                #   External reference/DeviceID
                try:
                    devID = self.workingInv[0][self.workSelect[0]][self.workSelect[1]].external_references[1].uri.split("=",1)[1]
                except:
                    devID = 'None'
                    
                #   separate datalogger/sensor serials
                try:
                    devID = self.workingInv[0][self.workSelect[0]][self.workSelect[1]].external_references[1].uri.split("=",1)[1]
                except:
                    devID = 'None'
                
                self.centv15.set(devID)
                
                #   Date - Channels
                #   Date Start
                try:
                    self.cdentv1y.set(UTCDateTime(self.workingInv[0][self.workSelect[0]][self.workSelect[1]].start_date).year)
                    self.cdentv1m.set(UTCDateTime(self.workingInv[0][self.workSelect[0]][self.workSelect[1]].start_date).month)
                    self.cdentv1d.set(UTCDateTime(self.workingInv[0][self.workSelect[0]][self.workSelect[1]].start_date).day)
                    self.cdentv1H.set(UTCDateTime(self.workingInv[0][self.workSelect[0]][self.workSelect[1]].start_date).hour)
                    self.cdentv1M.set(UTCDateTime(self.workingInv[0][self.workSelect[0]][self.workSelect[1]].start_date).minute)
                    self.cdentv1S.set(UTCDateTime(self.workingInv[0][self.workSelect[0]][self.workSelect[1]].start_date).second)
                except:
                    self.cdentv1y.set('2599')
                    self.cdentv1m.set('12')
                    self.cdentv1d.set('31')
                    self.cdentv1H.set('23')
                    self.cdentv1M.set('59')
                    self.cdentv1S.set('59')
               
                #   Date End
                try:
                    self.cdentv2y.set(UTCDateTime(self.workingInv[0][self.workSelect[0]][self.workSelect[1]].end_date).year)
                    self.cdentv2m.set(UTCDateTime(self.workingInv[0][self.workSelect[0]][self.workSelect[1]].end_date).month)
                    self.cdentv2d.set(UTCDateTime(self.workingInv[0][self.workSelect[0]][self.workSelect[1]].end_date).day)
                    self.cdentv2H.set(UTCDateTime(self.workingInv[0][self.workSelect[0]][self.workSelect[1]].end_date).hour)
                    self.cdentv2M.set(UTCDateTime(self.workingInv[0][self.workSelect[0]][self.workSelect[1]].end_date).minute)
                    self.cdentv2S.set(UTCDateTime(self.workingInv[0][self.workSelect[0]][self.workSelect[1]].end_date).second)
                except:
                    self.cdentv2y.set('2599')
                    self.cdentv2m.set('12')
                    self.cdentv2d.set('31')
                    self.cdentv2H.set('23')
                    self.cdentv2M.set('59')
                    self.cdentv2S.set('59')
                
                #   Generate Azimuth/dip plots
                plt.clf()
                ax1 = fig.add_subplot(121, projection = 'polar')
                ax1.plot(0,1)
                ax1.arrow(float(self.workingInv[0][self.workSelect[0]][self.workSelect[1]].azimuth)/180*np.pi,0,0,0.82, 
                          width = 0.05, edgecolor = 'black', facecolor = 'blue', lw = 2, zorder = 2)
                ax1.set_theta_zero_location("N")
                ax1.set_theta_direction(-1)
                ax1.set_yticklabels([])
                ax1.set_title("Azimuth", pad = 20, size = 18)
                
                ax2 = fig.add_subplot(122, projection = 'polar')
                ax2.plot(0,1)
                ax2.arrow(float(self.workingInv[0][self.workSelect[0]][self.workSelect[1]].dip)/180*np.pi,0,0,0.82,
                          width = 0.05, edgecolor = 'black', facecolor = 'blue', lw = 2, zorder = 2)
                ax2.set_theta_direction(-1)
                ax2.set_theta_zero_location("E")
                ax2.set_thetamin(-90)
                ax2.set_thetamax(90)
                ax2.set_xticks(np.linspace((-1*(np.pi))/2,(np.pi)/2, 13))
                ax2.set_yticklabels([])
                ax2.set_title("Dip", pad = 20, size = 18)
                ax2.set_xticklabels(['-90'+self.degS + '\n(Up)','-75'+self.degS,'-60'+self.degS,'-45'+self.degS,'-30'+self.degS,'-15'+self.degS,'0'+self.degS + "\n(Seafloor)",'15'+self.degS,'30'+self.degS,'45'+self.degS,'60'+self.degS,'75'+self.degS,'90'+self.degS +'\n(Down)'], size = 10)
                fig.canvas.draw()
            except:
                return
        
        #   Basic elements
        activeTree = tk.Frame(self.root, width = int(w*0.5), height = int(h*0.3))
        activeTree.grid(row = 0, column = 0, rowspan = 2, padx = 5, pady = 5, sticky = "w")
        activeTree.grid_propagate(0)        
        tk.Label(activeTree, textvariable = self.treeTitle, font = fst).grid(row = 0, column = 0, padx = 5, pady = 5, sticky = "w")
        
        availTree = ttk.Treeview(activeTree, selectmode = 'browse')
        availTree.grid(row = 1, column = 0, sticky = "nsew")
        
        #   Create scroll bars
        vsb = ttk.Scrollbar(activeTree, orient = "vertical", command = availTree.yview)
        vsb.grid(row = 1, column = 1, sticky = "nse")
        
        hsb = ttk.Scrollbar(activeTree, orient = "horizontal", command = availTree.xview)
        hsb.grid(row = 2, column = 0, sticky = "ews")
        
        availTree.configure(yscrollcommand = vsb.set)
        availTree.configure(xscrollcommand = hsb.set)
        
        #   Define treeview headers
        availTree["columns"] = ("1","2","3")
        availTree.column("#0", width = int(w*0.45)//4, minwidth = int(w*0.45)//4, stretch = tk.NO)
        availTree.column("1", width = int(w*0.45)//4, minwidth = int(w*0.45)//4, stretch = tk.NO)
        availTree.column("2", width = int(w*0.45)//4, minwidth = int(w*0.45)//4, stretch = tk.NO)
        availTree.column("3", width = int(w*0.45)//4, minwidth = int(w*0.45)//4, stretch = tk.NO)
        
        availTree.heading("#0", text = "Code", anchor = tk.CENTER)
        availTree.heading("1", text = "Location Code", anchor = tk.CENTER)
        availTree.heading("2", text = "Start Time (UTC)", anchor = tk.CENTER)
        availTree.heading("3", text = "End Time (UTC)", anchor = tk.CENTER)

        def change_tree(*args):
            if self.var1 != 0:
                for i in availTree.get_children():
                    availTree.delete(i)
                
                cd = self.workingInv.networks[0].code
                start = str(self.workingInv.networks[0].start_date)
                end = str(self.workingInv.networks[0].end_date)
                
                
                
                self.treeTitle.set("Inventory for: " + cd + ". From: " + start + " to " + end)
                stcnt = 0
                chcnt = 0
                
                for station in self.workingInv.networks[0].stations:
                    stat = availTree.insert("", stcnt, text = station.code, values = ("", str(station.start_date), str(station.end_date)))
                    chcnt = 0
                    for chan in station.channels:
                        availTree.insert(stat, "end",
                                         text = chan.code,
                                         values = (str(chan.location_code),
                                                   str(chan.start_date),
                                                   str(chan.end_date),
                                                   stcnt,
                                                   chcnt))
                        chcnt += 1
                        save.configure(state = 'normal')
                        save_c.configure(state = 'normal')
                        save_s.configure(state = 'normal')
                    stcnt += 1
        
        def saver(butt_Press):
            #   Get all values with update regarding the station
            if butt_Press == 2:
                #   Get all values with update regarding the channel
                tempCCo = self.centv1.get()
                tempLCo = self.centv2.get()
                tempCLa = self.centv3.get()
                tempCLo = self.centv4.get()
                tempCEl = self.centv5.get()
                tempCDe = self.centv6.get()
                tempCAz = self.centv7.get()
                tempCDi = self.centv8.get()
                tempCIT = self.centv9.get()
                tempCHz = self.centv10.get()
                tempCSD = self.centv11.get()
                tempCDD = self.centv12.get()
                tempCSN = self.centv13.get()
                tempCDN = self.centv14.get()
                tempDev = self.centv15.get()
                
                temp4y = self.cdentv1y.get()
                temp4m = self.cdentv1m.get()
                temp4d = self.cdentv1d.get()
                temp4H = self.cdentv1H.get()
                temp4M = self.cdentv1M.get()
                temp4S = self.cdentv1S.get()
                
                temp5y = self.cdentv2y.get()
                temp5m = self.cdentv2m.get()
                temp5d = self.cdentv2d.get()
                temp5H = self.cdentv2H.get()
                temp5M = self.cdentv2M.get()
                temp5S = self.cdentv2S.get()

                #   Checks channel information
                #   Channel code
                if (' ' in tempCCo) or (tempCCo == None) or len(tempCCo) > 3:
                    tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Station Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return
                        
                #   Azimuth/dip
                try:
                    az = float(tempCAz)
                    di = float(tempCDi)
                    if (0 <= az <= 360) != True:
                        tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Azimuth Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                        return
                    if (-90 <= di <= 90) != True:
                        tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Dip Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                        return
                except:
                    tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Azimuth or Dip Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return 
                
                #   Channel code naming check
                #   Get the end of the channel name
                charac = tempCCo[-1]
                
                if charac == 'N':
                    if (5 < az < 355) == True:
                        ask = tkm.askyesno(title = "Channel - Invalid Entry", message = "Azimuth Doesn't Match North Channel Name based on SEED Guidlines.\nDo you wish to continue?", parent = self.root, icon = "warning")
                        if ask == False:
                            return
                
                if charac == 'E':
                    if (85 < az < 95) == False:
                        ask = tkm.askyesno(title = "Channel - Invalid Entry", message = "Azimuth Doesn't Match East Channel Name based on SEED Guidlines.\nDo you wish to continue?", parent = self.root, icon = "warning")
                        if ask == False:
                            return
                        
                if charac == 'Z':
                    if (-85 < az < 85) == True:
                        ask = tkm.askyesno(title = "Channel - Invalid Entry", message = "Dip Doesn't Match Vertical Channel Name based on SEED Guidlines.\nDo you wish to continue?", parent = self.root, icon = "warning")
                        if ask == False:
                            return        
                    
                
                #   Location Code
                if (' ' in tempLCo) or len(tempLCo) > 2:
                    tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Station Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return
                
                #   Location
                try:
                    tempLat3 = float(tempCLa)
                    tempLon3 = float(tempCLo)
                    if (-90 <= tempLat3 <= 90) != True:
                        tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Latitude Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                        return
                    if (-180 <= tempLon3 <= 180) != True:
                        tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Longitude Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                        return
                except:
                    tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Location Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return 
                
                #   Elevation
                try:
                    tempEle3 = float(tempCEl)
                except:
                    tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Location Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return
                
                #   Depth
                try:
                    dep3 = float(tempCDe)
                except:
                    tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Location Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return
                
                #   Sample rate
                try:
                    samp = float(tempCHz)
                    if samp < 0:
                        tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Sample Rate Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                        return
                except:
                    tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Sample Rate Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                   
                #   Combine sensor/datalogger descriptions and serial numbers
                sendatDesc = tempCSD + '/' + tempCDD
                sendatNumb = tempCSN + '/' + tempCDN
                
                #   Generate the URL for the deviceID
                try:
                    devID = str(int(tempDev))
                    urlExt = 'https://data.oceannetworks.ca/DeviceListing?DeviceId=' + devID
                except:
                    tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Device ID Entry.\nPlease follow ONC Device ID Naming Scheme", parent = self.root, icon = "warning")
                    return
                
                #   Start Date
                try:
                    stadate4 = UTCDateTime(int(temp4y),int(temp4m),int(temp4d),int(temp4H),int(temp4M),int(temp4S))
                except:
                    tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Start Date Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return
                
                #   End Date
                try:
                    enddate5 = UTCDateTime(int(temp5y),int(temp5m),int(temp5d),int(temp5H),int(temp5M),int(temp5S))
                except:
                    tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid End Date Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return
                
                try:
                    upchan = Channel(
                                code = tempCCo.upper(),
                                location_code = tempLCo.upper(),
                                latitude = tempLat3,
                                longitude = tempLon3,
                                elevation = tempEle3,
                                depth = dep3,
                                start_date = stadate4,
                                end_date = enddate5,
                                azimuth = az,
                                dip = di,
                                sample_rate = samp,
                                types = [tempCIT.upper()],
                                equipments = Equipment(description = sendatDesc,
                                                       serial_number = sendatNumb),
                                sensor = Equipment(description = sendatDesc,
                                                   serial_number = sendatNumb),
                                external_references = [ExternalReference('https://data.oceannetworks.ca/DataSearch?location=' + self.workingInv[0][self.workSelect[0]].code, 'Data Search URL.'),
                                                       ExternalReference(urlExt, 'Device URL.')])
                    #   Get all of the channels that were within that station and update
                    self.workingInv[0][self.workSelect[0]].channels[self.workSelect[1]] = upchan
                    self.var1.set(self.var1.get()+1)
                except:
                    tkm.showwarning(title = "Invalid Channel", message = "Invalid Channel Creation.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return

            elif butt_Press == 1:
                tempSCo = self.sentv1.get()
                tempLat = self.sentv2.get()
                tempLon = self.sentv3.get()
                tempEle = self.sentv4.get()
                tempSit = self.sentv5.get()                               
                tempDec = self.sentv6.get()
                
                temp1y = self.sdentv1y.get()
                temp1m = self.sdentv1m.get()
                temp1d = self.sdentv1d.get()
                temp1H = self.sdentv1H.get()
                temp1M = self.sdentv1M.get()
                temp1S = self.sdentv1S.get()
                
                temp2y = self.sdentv2y.get()
                temp2m = self.sdentv2m.get()
                temp2d = self.sdentv2d.get()
                temp2H = self.sdentv2H.get()
                temp2M = self.sdentv2M.get()
                temp2S = self.sdentv2S.get()
                
                temp3y = self.sdentv3y.get()
                temp3m = self.sdentv3m.get()
                temp3d = self.sdentv3d.get()
                temp3H = self.sdentv3H.get()
                temp3M = self.sdentv3M.get()
                temp3S = self.sdentv3S.get()
                
                stat_check = ''
                
                print(tempSCo)
                
                for stat in self.workingInv[0].stations:
                    stat_check += str(stat.code) + '\t' 
                
                print('here1')
                #   Checks the station entries
                #   Station Code
                if (' ' in tempSCo) or (tempSCo == None) or len(tempSCo) > 5:
                    print('here2')
                    tkm.showwarning(title = "Station - Invalid Entry", message = "Invalid Station Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "error")
                    return
                
                elif tempSCo in stat_check:
                    print('here3')
                    tkm.showwarning(title = "Station Overwrite", message = "You are about to overwrite station " + tempSCo + ".\nDo you wish to continue?", parent = self.root, icon = "warning")
                
                #   Location
                try:
                    tempLat2 = float(tempLat)
                    tempLon2 = float(tempLon)
                    if (-90 <= tempLat2 <= 90) != True:
                        tkm.showwarning(title = "Station - Invalid Entry", message = "Invalid Latitude Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                        return
                    if (-180 <= tempLat2 <= 180) != True:
                        tkm.showwarning(title = "Station - Invalid Entry", message = "Invalid Longitude Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                        return
                except:
                    tkm.showwarning(title = "Station - Invalid Entry", message = "Invalid Location Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return
                
                #   Elevation
                try:
                    tempEle2 = float(tempEle)
                except:
                    tkm.showwarning(title = "Station - Invalid Entry", message = "Invalid Location Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return
                
                #   Creation Date
                try:
                    credate = UTCDateTime(int(temp1y),int(temp1m),int(temp1d),int(temp1H),int(temp1M),int(temp1S))
                except:
                    tkm.showwarning(title = "Station - Invalid Entry", message = "Invalid Creation Date Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return
                
                #   Start Date
                try:
                    stadate = UTCDateTime(int(temp2y),int(temp2m),int(temp2d),int(temp2H),int(temp2M),int(temp2S))
                except:
                    tkm.showwarning(title = "Station - Invalid Entry", message = "Invalid Start Date Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return
                
                #   End Date
                try:
                    enddate = UTCDateTime(int(temp3y),int(temp3m),int(temp3d),int(temp3H),int(temp3M),int(temp3S))
                except:
                    tkm.showwarning(title = "Station - Invalid Entry", message = "Invalid End Date Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return
                
                #   Generates a temporary station based on info update
                try:
                    upstat = Station(
                            code = tempSCo.upper(),
                            latitude = tempLat2,
                            longitude = tempLon2,
                            elevation = tempEle2,
                            description = tempDec,
                            creation_date = credate,
                            site = Site(name = tempSit),
                            start_date = stadate,
                            end_date = enddate)
                    
                    #   Get all of the channels that were within that station and update
                    
                    for chan in self.workingInv[0][self.workSelect[0]].channels:
                        upstat.channels.append(chan)
                        
                    
                    self.workingInv[0].stations[self.workSelect[0]] = upstat
                    self.var1.set(self.var1.get()+1)
                    
                except:
                    tkm.showwarning(title = "Invalid Station", message = "Invalid Station Creation.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return
                
            elif butt_Press == 3:
                #   Get all values with update regarding the channel
                tempCCo = self.centv1.get()
                tempLCo = self.centv2.get()
                tempCLa = self.centv3.get()
                tempCLo = self.centv4.get()
                tempCEl = self.centv5.get()
                tempCDe = self.centv6.get()
                tempCAz = self.centv7.get()
                tempCDi = self.centv8.get()
                tempCIT = self.centv9.get()
                tempCHz = self.centv10.get()
                tempCSD = self.centv11.get()
                tempCDD = self.centv12.get()
                tempCSN = self.centv13.get()
                tempCDN = self.centv14.get()
                tempDev = self.centv15.get()
                
                temp4y = self.cdentv1y.get()
                temp4m = self.cdentv1m.get()
                temp4d = self.cdentv1d.get()
                temp4H = self.cdentv1H.get()
                temp4M = self.cdentv1M.get()
                temp4S = self.cdentv1S.get()
                
                temp5y = self.cdentv2y.get()
                temp5m = self.cdentv2m.get()
                temp5d = self.cdentv2d.get()
                temp5H = self.cdentv2H.get()
                temp5M = self.cdentv2M.get()
                temp5S = self.cdentv2S.get()

                #   Checks channel information
                #   Channel code
                if (' ' in tempCCo) or (tempCCo == None) or len(tempCCo) > 3:
                    tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Station Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return
                        
                #   Azimuth/dip
                try:
                    az = float(tempCAz)
                    di = float(tempCDi)
                    if (0 <= az <= 360) != True:
                        tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Azimuth Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                        return
                    if (-90 <= di <= 90) != True:
                        tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Dip Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                        return
                except:
                    tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Azimuth or Dip Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return 
                
                #   Channel code naming check
                #   Get the end of the channel name
                charac = tempCCo[-1]
                
                if charac == 'N':
                    if (5 < az < 355) == True:
                        ask = tkm.askyesno(title = "Channel - Invalid Entry", message = "Azimuth Doesn't Match North Channel Name based on SEED Guidlines.\nDo you wish to continue?", parent = self.root, icon = "warning")
                        if ask == False:
                            return
                
                if charac == 'E':
                    if (85 < az < 95) == False:
                        ask = tkm.askyesno(title = "Channel - Invalid Entry", message = "Azimuth Doesn't Match East Channel Name based on SEED Guidlines.\nDo you wish to continue?", parent = self.root, icon = "warning")
                        if ask == False:
                            return
                        
                if charac == 'Z':
                    if (-85 < az < 85) == True:
                        ask = tkm.askyesno(title = "Channel - Invalid Entry", message = "Dip Doesn't Match Vertical Channel Name based on SEED Guidlines.\nDo you wish to continue?", parent = self.root, icon = "warning")
                        if ask == False:
                            return        
                    
                
                #   Location Code
                if (' ' in tempLCo) or (tempLCo == None) or len(tempLCo) > 2:
                    tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Station Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return
                
                #   Location
                try:
                    tempLat3 = float(tempCLa)
                    tempLon3 = float(tempCLo)
                    if (-90 <= tempLat3 <= 90) != True:
                        tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Latitude Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                        return
                    if (-180 <= tempLon3 <= 180) != True:
                        tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Longitude Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                        return
                except:
                    tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Location Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return 
                
                #   Elevation
                try:
                    tempEle3 = float(tempCEl)
                except:
                    tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Location Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return
                
                #   Depth
                try:
                    dep3 = float(tempCDe)
                except:
                    tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Location Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return
                
                #   Sample rate
                try:
                    samp = float(tempCHz)
                    if samp < 0:
                        tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Sample Rate Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                        return
                except:
                    tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Sample Rate Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                   
                #   Combine sensor/datalogger descriptions and serial numbers
                sendatDesc = tempCSD + '/' + tempCDD
                sendatNumb = tempCSN + '/' + tempCDN
                
                #   Generate the URL for the deviceID
                try:
                    devID = str(int(tempDev))
                    urlExt = 'https://data.oceannetworks.ca/DeviceListing?DeviceId=' + devID
                except:
                    tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Device ID Entry.\nPlease follow ONC Device ID Naming Scheme", parent = self.root, icon = "warning")
                    return
                
                #   Start Date
                try:
                    stadate4 = UTCDateTime(int(temp4y),int(temp4m),int(temp4d),int(temp4H),int(temp4M),int(temp4S))
                except:
                    tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid Start Date Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return
                
                #   End Date
                try:
                    enddate5 = UTCDateTime(int(temp5y),int(temp5m),int(temp5d),int(temp5H),int(temp5M),int(temp5S))
                except:
                    tkm.showwarning(title = "Channel - Invalid Entry", message = "Invalid End Date Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return
                
                try:
                    upchan = Channel(
                                code = tempCCo.upper(),
                                location_code = tempLCo.upper(),
                                latitude = tempLat3,
                                longitude = tempLon3,
                                elevation = tempEle3,
                                depth = dep3,
                                start_date = stadate4,
                                end_date = enddate5,
                                azimuth = az,
                                dip = di,
                                sample_rate = samp,
                                types = [tempCIT.upper()],
                                equipments = Equipment(description = sendatDesc,
                                                       serial_number = sendatNumb),
                                sensor = Equipment(description = sendatDesc,
                                                   serial_number = sendatNumb),
                                external_references = [ExternalReference('https://data.oceannetworks.ca/DataSearch?location=' + self.workingInv[0][self.workSelect[0]].code, 'Data Search URL.'),
                                                       ExternalReference(urlExt, 'Device URL.')])
                    #   Get all of the channels that were within that station and update
                    self.workingInv[0][self.workSelect[0]].channels[self.workSelect[1]] = upchan
                    self.var1.set(self.var1.get()+1)
                except:
                    tkm.showwarning(title = "Invalid Channel", message = "Invalid Channel Creation.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return

                tempSCo = self.sentv1.get()
                tempLat = self.sentv2.get()
                tempLon = self.sentv3.get()
                tempEle = self.sentv4.get()
                tempSit = self.sentv5.get()                               
                tempDec = self.sentv6.get()
                
                temp1y = self.sdentv1y.get()
                temp1m = self.sdentv1m.get()
                temp1d = self.sdentv1d.get()
                temp1H = self.sdentv1H.get()
                temp1M = self.sdentv1M.get()
                temp1S = self.sdentv1S.get()
                
                temp2y = self.sdentv2y.get()
                temp2m = self.sdentv2m.get()
                temp2d = self.sdentv2d.get()
                temp2H = self.sdentv2H.get()
                temp2M = self.sdentv2M.get()
                temp2S = self.sdentv2S.get()
                
                temp3y = self.sdentv3y.get()
                temp3m = self.sdentv3m.get()
                temp3d = self.sdentv3d.get()
                temp3H = self.sdentv3H.get()
                temp3M = self.sdentv3M.get()
                temp3S = self.sdentv3S.get()
                
                stat_check = ''
                
                print(tempSCo)
                
                for stat in self.workingInv[0].stations:
                    stat_check += str(stat.code) + '\t' 
                
                print('here1_1')
                #   Checks the station entries
                #   Station Code
                if (' ' in tempSCo) or (tempSCo == None) or len(tempSCo) > 5:
                    print('here2')
                    tkm.showwarning(title = "Station - Invalid Entry", message = "Invalid Station Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return
                
                elif tempSCo in stat_check:
                    print('here3')
                    tkm.showwarning(title = "Station - Invalid Entry", message = "Invalid Station Entry.\nStation code already exists!", parent = self.root, icon = "error")
                    return
                
                #   Location
                try:
                    tempLat2 = float(tempLat)
                    tempLon2 = float(tempLon)
                    if (-90 <= tempLat2 <= 90) != True:
                        tkm.showwarning(title = "Station - Invalid Entry", message = "Invalid Latitude Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                        return
                    if (-180 <= tempLat2 <= 180) != True:
                        tkm.showwarning(title = "Station - Invalid Entry", message = "Invalid Longitude Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                        return
                except:
                    tkm.showwarning(title = "Station - Invalid Entry", message = "Invalid Location Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return
                
                #   Elevation
                try:
                    tempEle2 = float(tempEle)
                except:
                    tkm.showwarning(title = "Station - Invalid Entry", message = "Invalid Location Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return
                
                #   Creation Date
                try:
                    credate = UTCDateTime(int(temp1y),int(temp1m),int(temp1d),int(temp1H),int(temp1M),int(temp1S))
                except:
                    tkm.showwarning(title = "Station - Invalid Entry", message = "Invalid Creation Date Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return
                
                #   Start Date
                try:
                    stadate = UTCDateTime(int(temp2y),int(temp2m),int(temp2d),int(temp2H),int(temp2M),int(temp2S))
                except:
                    tkm.showwarning(title = "Station - Invalid Entry", message = "Invalid Start Date Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return
                
                #   End Date
                try:
                    enddate = UTCDateTime(int(temp3y),int(temp3m),int(temp3d),int(temp3H),int(temp3M),int(temp3S))
                except:
                    tkm.showwarning(title = "Station - Invalid Entry", message = "Invalid End Date Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return
                
                #   Generates a temporary station based on info update
                try:
                    upstat = Station(
                            code = tempSCo.upper(),
                            latitude = tempLat2,
                            longitude = tempLon2,
                            elevation = tempEle2,
                            description = tempDec,
                            creation_date = credate,
                            site = Site(name = tempSit),
                            start_date = stadate,
                            end_date = enddate)
                    
                    #   Get all of the channels that were within that station and update
                    
                    for chan in self.workingInv[0][self.workSelect[0]].channels:
                        upstat.channels.append(chan)
                        
                    
                    self.workingInv[0].stations[self.workSelect[0]] = upstat
                    self.var1.set(self.var1.get()+1)
                    
                except:
                    tkm.showwarning(title = "Invalid Station", message = "Invalid Station Creation.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                    return

        #   Stats Frame
        availTree.bind('<1>', channelSelect)
        self.var1.trace('w', change_tree)
        
        stationInfo = tk.Frame(self.root)
        stationInfo.grid(row = 0, column = 1, padx = 5, pady = 5, sticky = "w")
        
        stationInfoDates = tk.Frame(self.root)
        stationInfoDates.grid(row = 1, column = 1, sticky = "w")
        
        channelInfo = tk.Frame(self.root)
        channelInfo.grid(row = 2, column = 1, padx = 5, pady = 5, sticky = "w")
        
        channelInfoDates = tk.Frame(self.root)
        channelInfoDates.grid(row = 3, column = 1, sticky = "w")
        
        #   Station/channels information labels
        ttk.Label(stationInfo, width = 12, text = "Station Info", font = fst).grid(row = 0, column = 0, padx = 5, sticky = "w")
        ttk.Label(stationInfo, width = 12, text = "Code: ", font = fsb).grid(row = 1, column = 0, padx = 5, sticky = "w")
        ttk.Label(stationInfo, width = 12, text = "Latitude ("+ self.degS + "): ", font = fsb).grid(row = 2, column = 0, padx = 5, sticky = "w")
        ttk.Label(stationInfo, width = 12, text = "Longitude ("+ self.degS + "): ", font = fsb).grid(row = 3, column = 0, padx = 5, sticky = "w")
        ttk.Label(stationInfo, width = 12, text = "Elevation (m): ", font = fsb).grid(row = 4, column = 0, padx = 5, sticky = "w")
        ttk.Label(stationInfo, width = 12, text = "Site: ", font = fsb).grid(row = 5, column = 0, padx = 5, sticky = "w")
        ttk.Label(stationInfo, width = 12, text = "Description: ", font = fsb).grid(row = 6, column = 0, padx = 5, sticky = "w")
        ttk.Label(stationInfoDates, width = 12, text = "Creation Date: ", font = fsb).grid(row = 7, column = 0, padx = 5, sticky = "w")
        ttk.Label(stationInfoDates, width = 12, text = "Start Date: ", font = fsb).grid(row = 8, column = 0, padx = 5, sticky = "w")
        ttk.Label(stationInfoDates, width = 12, text = "End Date: ", font = fsb).grid(row = 9, column = 0, padx = 5, sticky = "w")
   
        ttk.Label(channelInfo, width = 20, text = "Channel Info", font = fst).grid(row = 0, column = 0, padx = 5, sticky = "w")
        ttk.Label(channelInfo, width = 20, text = "Code: ", font = fsb).grid(row = 1, column = 0, padx = 5, sticky = "w")
        ttk.Label(channelInfo, width = 20, text = "Location Code: ", font = fsb).grid(row = 2, column = 0, padx = 5, sticky = "w")
        ttk.Label(channelInfo, width = 20, text = "Latitude  ("+ self.degS + "): ", font = fsb).grid(row = 3, column = 0, padx = 5, sticky = "w")
        ttk.Label(channelInfo, width = 20, text = "Longitude ("+ self.degS + "): ", font = fsb).grid(row = 4, column = 0, padx = 5, sticky = "w")
        ttk.Label(channelInfo, width = 20, text = "Elevation (m): ", font = fsb).grid(row = 5, column = 0, padx = 5, sticky = "w")
        ttk.Label(channelInfo, width = 20, text = "Depth (m): ", font = fsb).grid(row = 6, column = 0, padx = 5, sticky = "w")
        ttk.Label(channelInfo, width = 20, text = "Azimuth ("+ self.degS + "): ", font = fsb).grid(row = 7, column = 0, padx = 5, sticky = "w")
        ttk.Label(channelInfo, width = 20, text = "Dip ("+ self.degS + "): ", font = fsb).grid(row = 8, column = 0, padx = 5, sticky = "w")
        ttk.Label(channelInfo, width = 20, text = "Instrument Type\n(e.g., Geophysical): ", font = fsb).grid(row = 9, column = 0, padx = 5, sticky = "w")
        ttk.Label(channelInfo, width = 20, text = "Sample Rate (Hz): ", font = fsb).grid(row = 10, column = 0, padx = 5, sticky = "w")
        ttk.Label(channelInfo, width = 20, text = "Sensor Description: ", font = fsb).grid(row = 11, column = 0, padx = 5, sticky = "w")
        ttk.Label(channelInfo, width = 20, text = "Datalogger Description: ", font = fsb).grid(row = 12, column = 0, padx = 5, sticky = "w")
        ttk.Label(channelInfo, width = 20, text = "Sensor Serial Number: ", font = fsb).grid(row = 13, column = 0, padx = 5, sticky = "w")
        ttk.Label(channelInfo, width = 20, text = "Datalogger Serial Number: ", font = fsb).grid(row = 14, column = 0, padx = 5, sticky = "w")
        ttk.Label(channelInfo, width = 20, text = "Device ID: ", font = fsb).grid(row = 15, column = 0, padx = 5, sticky = "w")
        ttk.Label(channelInfo, width = 20, text = "Attached Response File? ", font = fsb).grid(row = 16, column = 0, padx = 5, sticky = "w")
        ttk.Label(channelInfoDates, text = "Start Date:", font = fsb).grid(row = 17, column = 0, padx = 5, sticky = "w")
        ttk.Label(channelInfoDates, text = "End Date:", font = fsb).grid(row = 18, column = 0, padx = 5, sticky = "w")
       
        labs = 'Year:','Month:','Day:','Hour:','Minute:','Second:'
        cnt = 0
        
        #   Entry boxes - station
        self.sent1 = tk.Entry(stationInfo, textvariable = self.sentv1, width = 20, font = 14)
        self.sent1.grid(row = 1, column = 1, sticky = 'w')
        self.sent2 = tk.Entry(stationInfo, textvariable = self.sentv2, width = 20, font = 14)
        self.sent2.grid(row = 2, column = 1, sticky = 'w')
        self.sent3 = tk.Entry(stationInfo, textvariable = self.sentv3, width = 20, font = 14)
        self.sent3.grid(row = 3, column = 1, sticky = 'w')
        self.sent4 = tk.Entry(stationInfo, textvariable = self.sentv4, width = 20, font = 14)
        self.sent4.grid(row = 4, column = 1, sticky = 'w')
        self.sent5 = tk.Entry(stationInfo, textvariable = self.sentv5, width = 75, font = 14)
        self.sent5.grid(row = 5, column = 1, sticky = 'w')
        self.sent6 = tk.Entry(stationInfo, textvariable = self.sentv6, width = 75, font = 14)
        self.sent6.grid(row = 6, column = 1, sticky = 'w')
        
            
        #   start/end/creation dates
        for i in range(1,13,2):
            if cnt < 6:
                lab1 = tk.Label(stationInfoDates, width = 6, text = labs[cnt], font = 14)
                lab1.grid(row = 7, column = i, padx = 5, sticky = 'w')
                lab2 = tk.Label(stationInfoDates, width = 6, text = labs[cnt], font = 14)
                lab2.grid(row = 8, column = i, padx = 5, sticky = 'w')
                lab3 = tk.Label(stationInfoDates, width = 6, text = labs[cnt], font = 14)
                lab3.grid(row = 9, column = i, padx = 5, sticky = 'w')
            cnt += 1
            
        self.sdent1y = tk.Entry(stationInfoDates, textvariable = self.sdentv1y, width = 6, font = 14)
        self.sdent1y.grid(row = 7, column = 2, padx = 2, sticky = 'w')
        self.sdent1m = tk.Entry(stationInfoDates, textvariable = self.sdentv1m, width = 6, font = 14)
        self.sdent1m.grid(row = 7, column = 4, padx = 2, sticky = 'w')
        self.sdent1d = tk.Entry(stationInfoDates, textvariable = self.sdentv1d, width = 6, font = 14)
        self.sdent1d.grid(row = 7, column = 6, padx = 2, sticky = 'w')
        self.sdent1H = tk.Entry(stationInfoDates, textvariable = self.sdentv1H, width = 6, font = 14)
        self.sdent1H.grid(row = 7, column = 8, padx = 2, sticky = 'w')
        self.sdent1M = tk.Entry(stationInfoDates, textvariable = self.sdentv1M, width = 6, font = 14)
        self.sdent1M.grid(row = 7, column = 10, padx = 2, sticky = 'w')
        self.sdent1S = tk.Entry(stationInfoDates, textvariable = self.sdentv1S, width = 6, font = 14)
        self.sdent1S.grid(row = 7, column = 12, padx = 2, sticky = 'w')
        
        self.sdent2y = tk.Entry(stationInfoDates, textvariable = self.sdentv2y, width = 6, font = 14)
        self.sdent2y.grid(row = 8, column = 2, padx = 2, sticky = 'w')
        self.sdent2m = tk.Entry(stationInfoDates, textvariable = self.sdentv2m, width = 6, font = 14)
        self.sdent2m.grid(row = 8, column = 4, padx = 2, sticky = 'w')
        self.sdent2d = tk.Entry(stationInfoDates, textvariable = self.sdentv2d, width = 6, font = 14)
        self.sdent2d.grid(row = 8, column = 6, padx = 2, sticky = 'w')
        self.sdent2H = tk.Entry(stationInfoDates, textvariable = self.sdentv2H, width = 6, font = 14)
        self.sdent2H.grid(row = 8, column = 8, padx = 2, sticky = 'w')
        self.sdent2M = tk.Entry(stationInfoDates, textvariable = self.sdentv2M, width = 6, font = 14)
        self.sdent2M.grid(row = 8, column = 10, padx = 2, sticky = 'w')
        self.sdent2S = tk.Entry(stationInfoDates, textvariable = self.sdentv2S, width = 6, font = 14)
        self.sdent2S.grid(row = 8, column = 12, padx = 2, sticky = 'w')
        
        self.sdent3y = tk.Entry(stationInfoDates, textvariable = self.sdentv3y, width = 6, font = 14)
        self.sdent3y.grid(row = 9, column = 2, padx = 2, sticky = 'w')
        self.sdent3m = tk.Entry(stationInfoDates, textvariable = self.sdentv3m, width = 6, font = 14)
        self.sdent3m.grid(row = 9, column = 4, padx = 2, sticky = 'w')
        self.sdent3d = tk.Entry(stationInfoDates, textvariable = self.sdentv3d, width = 6, font = 14)
        self.sdent3d.grid(row = 9, column = 6, padx = 2, sticky = 'w')
        self.sdent3H = tk.Entry(stationInfoDates, textvariable = self.sdentv3H, width = 6, font = 14)
        self.sdent3H.grid(row = 9, column = 8, padx = 2, sticky = 'w')
        self.sdent3M = tk.Entry(stationInfoDates, textvariable = self.sdentv3M, width = 6, font = 14)
        self.sdent3M.grid(row = 9, column = 10, padx = 2, sticky = 'w')
        self.sdent3S = tk.Entry(stationInfoDates, textvariable = self.sdentv3S, width = 6, font = 14)
        self.sdent3S.grid(row = 9, column = 12, padx = 2, sticky = 'w')
     
#        #   Entery boxes - channel        
        self.cent1 = tk.Entry(channelInfo, textvariable = self.centv1, width = 20, font = 14)
        self.cent1.grid(row = 1, column = 1, sticky = 'w')
        self.cent2 = tk.Entry(channelInfo, textvariable = self.centv2, width = 20, font = 14)
        self.cent2.grid(row = 2, column = 1, sticky = 'w')
        self.cent3 = tk.Entry(channelInfo, textvariable = self.centv3, width = 20, font = 14)
        self.cent3.grid(row = 3, column = 1, sticky = 'w')
        self.cent4 = tk.Entry(channelInfo, textvariable = self.centv4, width = 20, font = 14)
        self.cent4.grid(row = 4, column = 1, sticky = 'w')
        self.cent5 = tk.Entry(channelInfo, textvariable = self.centv5, width = 20, font = 14)
        self.cent5.grid(row = 5, column = 1, sticky = 'w')
        self.cent6 = tk.Entry(channelInfo, textvariable = self.centv6, width = 20, font = 14)
        self.cent6.grid(row = 6, column = 1, sticky = 'w')
        self.cent7 = tk.Entry(channelInfo, textvariable = self.centv7, width = 20, font = 14)
        self.cent7.grid(row = 7, column = 1, sticky = 'w')
        self.cent8 = tk.Entry(channelInfo, textvariable = self.centv8, width = 20, font = 14)
        self.cent8.grid(row = 8, column = 1, sticky = 'w')
        self.cent9 = tk.Entry(channelInfo, textvariable = self.centv9, width = 20, font = 14)
        self.cent9.grid(row = 9, column = 1, sticky = 'w')
        self.cent10 = tk.Entry(channelInfo, textvariable = self.centv10, width = 20, font = 14)
        self.cent10.grid(row = 10, column = 1, sticky = 'w')
        self.cent11 = tk.Entry(channelInfo, textvariable = self.centv11, width = 75, font = 14)
        self.cent11.grid(row = 11, column = 1, sticky = 'w')
        self.cent12 = tk.Entry(channelInfo, textvariable = self.centv12, width = 75, font = 14)
        self.cent12.grid(row = 12, column = 1, sticky = 'w')
        self.cent13 = tk.Entry(channelInfo, textvariable = self.centv13, width = 20, font = 14)
        self.cent13.grid(row = 13, column = 1, sticky = 'w')
        self.cent14 = tk.Entry(channelInfo, textvariable = self.centv14, width = 20, font = 14)
        self.cent14.grid(row = 14, column = 1, sticky = 'w')
        self.cent15 = tk.Entry(channelInfo, textvariable = self.centv15, width = 20, font = 14)
        self.cent15.grid(row = 15, column = 1, sticky = 'w')
        self.responseLab = tk.Label(channelInfo, textvariable = self.respLab, width = 40, font = fsb)
        self.responseLab.grid(row = 16, column = 1, padx = 5, sticky = 'w')
               
        #   start/end/creation dates
        cnt = 0
        for i in range(1,13,2):
            if cnt < 6:
                lab1 = tk.Label(channelInfoDates, width = 6, text = labs[cnt], font = 14)
                lab1.grid(row = 17, column = i, padx = 5, sticky = 'w')
                lab2 = tk.Label(channelInfoDates, width = 6, text = labs[cnt], font = 14)
                lab2.grid(row = 18, column = i, padx = 5, sticky = 'w')
            cnt += 1
        
        self.cdent1y = tk.Entry(channelInfoDates, textvariable = self.cdentv1y, width = 6, font = 14)
        self.cdent1y.grid(row = 17, column = 2, padx = 2, sticky = 'w')
        self.cdent1m = tk.Entry(channelInfoDates, textvariable = self.cdentv1m, width = 6, font = 14)
        self.cdent1m.grid(row = 17, column = 4, padx = 2, sticky = 'w')
        self.cdent1d = tk.Entry(channelInfoDates, textvariable = self.cdentv1d, width = 6, font = 14)
        self.cdent1d.grid(row = 17, column = 6, padx = 2, sticky = 'w')
        self.cdent1H = tk.Entry(channelInfoDates, textvariable = self.cdentv1H, width = 6, font = 14)
        self.cdent1H.grid(row = 17, column = 8, padx = 2, sticky = 'w')
        self.cdent1M = tk.Entry(channelInfoDates, textvariable = self.cdentv1M, width = 6, font = 14)
        self.cdent1M.grid(row = 17, column = 10, padx = 2, sticky = 'w')
        self.cdent1S = tk.Entry(channelInfoDates, textvariable = self.cdentv1S, width = 6, font = 14)
        self.cdent1S.grid(row = 17, column = 12, padx = 2, sticky = 'w')
        
        self.cdent2y = tk.Entry(channelInfoDates, textvariable = self.cdentv2y, width = 6, font = 14)
        self.cdent2y.grid(row = 18, column = 2, padx = 2, sticky = 'w')
        self.cdent2m = tk.Entry(channelInfoDates, textvariable = self.cdentv2m, width = 6, font = 14)
        self.cdent2m.grid(row = 18, column = 4, padx = 2, sticky = 'w')
        self.cdent2d = tk.Entry(channelInfoDates, textvariable = self.cdentv2d, width = 6, font = 14)
        self.cdent2d.grid(row = 18, column = 6, padx = 2, sticky = 'w')
        self.cdent2H = tk.Entry(channelInfoDates, textvariable = self.cdentv2H, width = 6, font = 14)
        self.cdent2H.grid(row = 18, column = 8, padx = 2, sticky = 'w')
        self.cdent2M = tk.Entry(channelInfoDates, textvariable = self.cdentv2M, width = 6, font = 14)
        self.cdent2M.grid(row = 18, column = 10, padx = 2, sticky = 'w')
        self.cdent2S = tk.Entry(channelInfoDates, textvariable = self.cdentv2S, width = 6, font = 14)
        self.cdent2S.grid(row = 18, column = 12, padx = 2, sticky = 'w')        
        
        
        #   Polar Plots
        fig = plt.figure(figsize = (int(w*0.4/96),int(h*0.6/96)))
        ax1 = fig.add_subplot(121, projection = 'polar')
        ax1.plot(0,1)
        ax1.set_theta_zero_location("N")
        ax1.set_theta_direction(-1)
        ax1.set_yticklabels([])
        ax1.set_title("Azimuth", pad = 20, size = 18)
        
        ax2 = fig.add_subplot(122, projection = 'polar')
        ax2.plot(0,1)
        ax2.set_theta_direction(-1)
        ax2.set_theta_zero_location("E")
        ax2.set_thetamin(-90)
        ax2.set_thetamax(90)
        ax2.set_xticks(np.linspace((-1*(np.pi))/2,(np.pi)/2, 13))
        ax2.set_yticklabels([])
        ax2.set_title("Dip", pad = 20, size = 18)
        ax2.set_xticklabels(['-90'+self.degS + '\n(Up)','-75'+self.degS,'-60'+self.degS,'-45'+self.degS,'-30'+self.degS,'-15'+self.degS,'0'+self.degS + "\n(Seafloor)",'15'+self.degS,'30'+self.degS,'45'+self.degS,'60'+self.degS,'75'+self.degS,'90'+self.degS +'\n(Down)'], size = 10)
        
        #   Plot Canvas
        canvas = FigureCanvasTkAgg(fig, master = self.root)
        plot_widget = canvas.get_tk_widget()
        plot_widget.grid(row = 1, column = 0, rowspan = 3)
        
        #   Upload Save Channel button
        save_c = tk.Button(channelInfoDates, text = "Update Channel", command = lambda: saver(2))
        save_c['font'] = tkfont.Font(family = "Lucida Grande", size = 18)
        save_c.configure(state = 'disabled')
        save_c.grid(row = 19, column = 4, columnspan = 6, padx = 5, pady = 8)
        
        #   Upload Save Station Button
        save_s = tk.Button(channelInfoDates, text = "Update Station", command = lambda: saver(1))
        save_s['font'] = tkfont.Font(family = "Lucida Grande", size = 18)
        save_s.configure(state = 'disabled')
        save_s.grid(row = 19, column = 0, columnspan = 6, padx = 5, pady = 8)
        
        #   Upload Save All Button
        save = tk.Button(channelInfoDates, text = "Update All", command = lambda: saver(3))
        save['font'] = tkfont.Font(family = "Lucida Grande", size = 18)
        save.configure(state = 'disabled')
        save.grid(row = 19, column = 8, columnspan = 6, padx = 5, pady = 8)
                
        
        
        
#%% Creates the menubar
    def create_menubar(self):
        """
        Create the menubar for the canvas
        """
        
        self.menubar = tk.Menu(self.root)
        
        self.filemenu = tk.Menu(self.menubar, tearoff = 0)
        self.filemenu.add_command(label = "New Inventory", command = self.new_inventory)
        self.filemenu.add_command(label = "Open Inventory", command = self.open_inventory)
        self.filemenu.add_separator()
        self.filemenu.add_command(label = "Export All", command = self.export_all)
        self.filemenu.add_command(label = "Selective Export", command = self.export_select)
        self.filemenu.add_separator()
        self.filemenu.add_command(label = "Quit", command = self.root.destroy)
        
        self.editmenu = tk.Menu(self.menubar, tearoff = 0)
        self.editmenu.add_command(label = "Edit Current Channel Response", command = lambda: self.change_resp())
        self.editmenu.add_command(label = "Assign Flat Channel Response", command = lambda: self.assignFlat())
        self.editmenu.add_separator()
        self.editmenu.add_command(label = "Add New Station to Network", command = lambda: self.edit_adds())
        self.editmenu.add_command(label = "Add New Channel to Station", command = lambda: self.edit_addc())
        self.editmenu.add_separator()
        self.editmenu.add_command(label = "Duplicate Current Channel", command = lambda: self.duplicateChan())
        self.editmenu.add_separator()
        self.editmenu.add_command(label = "Delete Station", command = lambda: self.deleteStation())
        self.editmenu.add_command(label = "Delete Current Channel", command = lambda: self.deleteChan())

        

        self.menubar.add_cascade(label = "File", menu = self.filemenu)
        self.menubar.add_cascade(label = "Edit", menu = self.editmenu)
        self.menubar.entryconfig("Edit", state = "disabled")
        self.root.config(menu = self.menubar)

#%% Create New Inventory
    def new_inventory(self):
        """
        Creates a new inventory either by starting folder or importing XML
        """
        def NewInventory():
            user = creater.get()
            inv = invCode.get()
            
            now = datetime.now()
            
            sta = Station(
                    code = "NEW",
                    latitude = 1,
                    longitude = 2,
                    elevation = 999,
                    creation_date = UTCDateTime(now),
                    site = Site(name = "Brand New Station"))
            
            cha = Channel(
                    code = "ABC",
                    location_code = "",
                    latitude = 1,
                    longitude = 2,
                    elevation = 999,
                    depth = 999,
                    start_date = UTCDateTime(now),
                    azimuth = 0,
                    dip = -90,
                    sample_rate = 999,
                    types = ['NEW INSTRUMENT'],
                    equipments = Equipment(description = 'Description',
                                       serial_number = 'Num123'),
                    sensor = Equipment(description = 'Description',
                                       serial_number = 'Num123'))
            
            newInv = Inventory(
                    networks = [],
                    source = user + ", Ocean Netowrks Canada",
                    created = UTCDateTime(datetime.today()))
            net = Network(
                    code = inv,
                    stations = [])
            
            sta.channels.append(cha)
            newInv.networks.append(net)
            newInv[0].stations.append(sta)
            
            #   Check if there is a folder for this network
            folds = []
            wrote = False
            for root, dirs, files in os.walk(self.curdir + "/_Inventories"):
                folds += dirs
                
                if inv == dirs:
                    newInv.write(self.curdir + "/_Inventories/" + dirs + "/" + str(inv) + ".xml", format = "STATIONXML")
                    wrote = True
            
            if wrote == False:
                os.makedirs(self.curdir + "/_Inventories/" + str(inv))
                newInv.write(self.curdir + "/_Inventories/" + str(inv) + "/" + str(inv) + ".xml", format = "STATIONXML")
            self.workingInv = newInv
            self.var1.set(self.var1.get()+1)
            self.menubar.entryconfig("Edit", state = "normal")
            newEntry.destroy()
            
        
        #   Gets entry for new network and makes directory
        #   Defines pop up
        newEntry = tk.Toplevel()
        newEntry.geometry("250x175")
        
        titFrame = ttk.Frame(newEntry)
        titFrame.grid(row = 1, column = 1, sticky = "w", padx = 5, pady = 5)
        ttk.Label(titFrame, text = "Enter Base Inventory Information").grid(row = 1, column = 1, sticky = "w", padx = 5, pady = 5)
        
        nameFrame = ttk.Frame(newEntry)
        nameFrame.grid(row = 2, column = 1, sticky = "e", padx = 5, pady = 5)
        ttk.Label(nameFrame, text = 'Creator Name: ').grid(row = 1, column = 1, sticky = "w", padx = 5, pady = 5)
        creater = ttk.Entry(nameFrame, width = 15)
        creater.grid(row = 1, column = 2, sticky = "e")
        
        invFrame = ttk.Frame(newEntry)
        invFrame.grid(row = 3, column = 1, sticky = "e", padx = 5, pady = 5)
        ttk.Label(invFrame, text = 'New Inventory Code: ').grid(row = 1, column = 1, sticky = "w", padx = 5, pady = 5)   
        invCode = ttk.Entry(invFrame, width = 15)
        invCode.grid(row = 1, column = 2, sticky = "e")       
        
        getButt = ttk.Frame(newEntry)
        getButt.grid(row = 4, column = 1, sticky = "e", padx = 5, pady = 5)
        
        ttk.Button(getButt, text = "Create", command = NewInventory, width = 15).pack()
        
#%% Open Inventory
    def open_inventory(self):
        #   Define progress bar
        #   Create download bar
        downPop = tk.Toplevel()
        downPop.attributes('-topmost', 'true')
        downPop.geometry('300x100')
        downPop.geometry('+%d+%d' % (((self.dw/2)-(250)),((self.dh/2) - (75)))) 
        downPop.withdraw()
        
        downProg = ttk.Progressbar(downPop, orient = tk.HORIZONTAL, length = 250, mode = 'determinate')
        downProg.pack(side = tk.TOP, padx = 5, pady = 10)
        
        downLabel = tk.Label(downPop, text = "Opening Inventory File")
        downLabel.pack(side = tk.TOP, padx = 5, pady = 10)
        downPop.update_idletasks()
        
        XML_inv = tkf.askopenfilename(
                initialdir = self.curdir + "/_Inventories", 
                title="Select Station Inventory", 
                filetypes=(("XML Files", ".xml"), ("All Files", "*.*")))
        downPop.deiconify()
        downProg['value'] = 0
        downLabel.configure(text = "...")
        downPop.update_idletasks()
        self.InitialFile = str(XML_inv)
        time.sleep(0.1)
        
        downProg['value'] = 5
        downLabel.configure(text = "Reading In Inventory")
        downPop.update_idletasks()
        
        obsRead = read_inventory(XML_inv)
        
        downProg['value'] = 100
        downLabel.configure(text = "Done!")
        downPop.update_idletasks()
        downPop.destroy()

        self.workingInv = obsRead
        self.menubar.entryconfig("Edit", state = "normal")
        self.var1.set(self.var1.get()+1)
  
#%% Edit Channel
    def edit_addc(self):
        def saver():
            statwrk = availstats.get()
            statlist = self.workingInv[0].get_contents()
            
            tcon = [i for i, s in enumerate(statlist['stations']) if statwrk in s]
            
            now = datetime.now()
            
            cha = Channel(
                    code = "ABC",
                    location_code = "",
                    latitude = 1,
                    longitude = 2,
                    elevation = 999,
                    depth = 999,
                    start_date = UTCDateTime(now),
                    azimuth = 0,
                    dip = -90,
                    sample_rate = 999,
                    types = ['NEW INSTRUMENT'],
                    equipments = Equipment(description = 'Description',
                                       serial_number = 'Num123'),
                    sensor = Equipment(description = 'Description',
                                       serial_number = 'Num123'))
            
            self.workingInv[0][tcon[0]].channels.append(cha)
            self.var1.set(self.var1.get()+1)
            oneAdd.destroy()
            
            
        #   Define the window 

        oneAdd = tk.Toplevel()
        oneAdd.resizable()
        
        statlist = self.workingInv[0].get_contents()
        
        editFrame = tk.LabelFrame(oneAdd, font = 14, text = 'Choose a Station To Add to:', relief = tk.RIDGE)
        editFrame.pack(side = tk.TOP, padx = 5, pady = 5)
        
        availstats = ttk.Combobox(editFrame, values = statlist['stations'], font = 14)
        availstats.current(0)
        availstats.pack(side = tk.LEFT, padx = 5, pady = 5)
        
        adder = tk.Button(editFrame, text = 'Add To Station', command = lambda: saver())
        adder['font'] = tkfont.Font(family = 'Lucinda Grande', size = 12)
        adder.pack(side = tk.RIGHT, padx = 5, pady = 5)
        
#%% Assign Flat Response
    def assignFlat(self):
        def saver():
            t = self.curdir + '/_bin/FlatResponseXML.xml'
            flatresp = read_inventory(t, format='STATIONXML')[0][0][0].response
            try:
                flatresp.response_stages[0].stage_gain = abs(float(e1.get()))
            except:
                tkm.showerror(title = 'Invalid Instrument Sensitivity', text = 'Instrument sensitivity is not a valid entry', icon = 'error')
                return
            
            flatresp.response_stages[0].input_units = str(e2.get())
            flatresp.response_stages[0].output_units = str(e3.get())
            try:
                flatresp.response_stages[0].decimation_input_sample_rate = self.workingInv[0][self.workSelect[0]][self.workSelect[1]].sample_rate
            except:
                tkm.showerror(title = 'Invalid Sample Rate', text = 'No Sample Rate is defined', icon = 'error')
                return
            
            self.workingInv[0][self.workSelect[0]][self.workSelect[1]].response = flatresp
            self.var1.set(self.var1.get()+1)
            assignFlat.destroy()
            
            
            
            
        #   Define the pop up window
        assignFlat = tk.Toplevel()
        assignFlat.resizable()
    
        editFrame = tk.LabelFrame(assignFlat, font = 14, text = 'Define Flat Response:', relief = tk.RIDGE)
        editFrame.pack(side = tk.TOP, padx = 5, pady = 5)
        
        r1 = tk.Frame(editFrame)
        r1.pack(side = tk.TOP, padx = 5, pady = 5)
        
        l1 = tk.Label(r1, text = 'Instrument Senstivity (keep as 1 to get counts return): ', font = 11)
        l1.pack(side = tk.LEFT, padx = 5, pady = 5)
        
        e1 = tk.Entry(r1, width = 20)
        e1.insert(tk.END, '1')
        e1.pack(side = tk.RIGHT, padx = 5, pady = 5)
        
        r2 = tk.Frame(editFrame)
        r2.pack(side = tk.TOP, padx = 5, pady = 5)
        
        l2 = tk.Label(r2, text = 'Input Units: ', font = 11)
        l2.pack(side = tk.LEFT, padx = 5, pady = 5)
        
        e2 = tk.Entry(r2, width = 20)
        e2.insert(tk.END, 'COUNTS')
        e2.pack(side = tk.RIGHT, padx = 5, pady = 5)
        
        r3 = tk.Frame(editFrame)
        r3.pack(side = tk.TOP, padx = 5, pady = 5)
        
        l3 = tk.Label(r3, text = 'Output Units: ', font = 11)
        l3.pack(side = tk.LEFT, padx = 5, pady = 5)
        
        e3 = tk.Entry(r3, width = 20)
        e3.insert(tk.END, 'COUNTS')
        e3.pack(side = tk.RIGHT, padx = 5, pady = 5)
        
        adder = tk.Button(editFrame, text = 'Generate Flat Response', command = lambda: saver())
        adder['font'] = tkfont.Font(family = 'Lucinda Grande', size = 12)
        adder.pack(side = tk.TOP, padx = 5, pady = 5)
        
                

        
#%% Change the Response for a Channel  
    def change_resp(self):
        def get_response(file):
            if file == 1:
                temp_Sens = tkf.askopenfilename( 
                                title="Select Response File", 
                                filetypes=(("XML Files", ".xml"), ("Text Files", ".txt"), ("All Files", "*.*")))
                
                labFile1.set(temp_Sens)
                try:
                    dl_resp = read_inventory(temp_Sens, format='RESP')[0][0][0].response
                    ent_label1.configure(textvariable = labFile1)
                except:
                    try:
                        dl_resp = read_inventory(temp_Sens, format='STATIONXML')[0][0][0].response
                        ent_label1.configure(textvariable = labFile1)
                    except:
                        tkm.showerror(title = "Response File Error", message = "Invalid File Selection", icon = "error")
                        respStatusFile.set('Could not build a response from the selected file')
                        return
                
                self.tempResp_File = dl_resp
                respStatusFile.set('Successfully built a response with the selected file')
                self.sav1.set(True)
                self.sav2.set(True)
                
            
            elif file == 2:
                temp_Sens = tkf.askopenfilename(
                                title="Select Response File", 
                                filetypes=(("XML Files", ".xml"), ("Text Files", ".txt"), ("All Files", "*.*")))
                
                labFile2.set(temp_Sens)
                try:
                    dl_resp = read_inventory(temp_Sens, format='RESP')[0][0][0].response
                    ent_label2.configure(textvariable = labFile2)
                except:
                    try:
                        dl_resp = read_inventory(temp_Sens, format='STATIONXML')[0][0][0].response
                        ent_label2.configure(textvariable = labFile2)
                    except:
                        tkm.showerror(title = "Response File Error", message = "Invalid File Selection", icon = "error")
                        return
                    
                self.TempSensResp = dl_resp
                respStatusFile.set('Successfully obtained the sensor response')
                self.sav1.set(True)

                
            elif file == 3:
                temp_Sens = tkf.askopenfilename(
                                title="Select Response File", 
                                filetypes=(("XML Files", ".xml"), ("Text Files", ".txt"), ("All Files", "*.*")))
                
                labFile3.set(temp_Sens)
                try:
                    dl_resp = read_inventory(temp_Sens, format='RESP')[0][0][0].response
                    ent_label3.configure(textvariable = labFile3)
                except:
                    try:
                        dl_resp = read_inventory(temp_Sens, format='STATIONXML')[0][0][0].response
                        ent_label3.configure(textvariable = labFile3)
                    except:
                        tkm.showerror(title = "Response File Error", message = "Invalid File Selection", icon = "error")
                        return
                    
                self.TempDatResp = dl_resp
                respStatusFile.set('Successfully obtained the datalogger response')
                self.sav2.set(True)
                
            if file == 2 or file == 3:
                if self.sav1.get() == True and self.sav2.get() == True:
                    try:
                        self.TempDatResp.response_stages.pop(0)
                        self.TempDatResp.response_stages.insert(0, self.TempSensResp.response_stages[0])
                        self.TempDatResp.instrument_sensitivity.input_units = self.TempSensResp.instrument_sensitivity.input_units
                        self.TempDatResp.instrument_sensitivity.input_units_description = self.TempSensResp.instrument_sensitivity.input_units_description
                        _response = self.TempDatResp
                        
                        if _response.instrument_sensitivity.output_units=="COUNTS" or _response.instrument_sensitivity.output_units == "COUNT":
                            _response.instrument_sensitivity.output_units = _response.instrument_sensitivity.output_units.lower()
                        if _response.instrument_sensitivity.input_units=="COUNTS" or _response.instrument_sensitivity.input_units == "COUNT":
                            _response.instrument_sensitivity.input_units = _response.instrument_sensitivity.input_units.lower()
                            
                        for stage in _response.response_stages:
                            #correct for COUNTS units name
                            if stage.output_units=="COUNTS" or stage.output_units=="COUNT":
                                stage.output_units = stage.output_units.lower()
                                stage.output_units_description = "Digital Counts"
                            if stage.input_units=="COUNTS" or stage.output_units=="COUNT":
                                stage.input_units = stage.input_units.lower()
                                stage.input_units_description = "Digital Counts"
                            #correct for Celsius (C) units name
                            if stage.output_units=="C":
                                stage.output_units = "degC"
                            if stage.input_units=="C":
                                stage.input_units = "degC"
                            
                        self.tempResp_File = _response
                        respStatusFile.set('Successfully built a response with the sensor/datalogger files')
                    except:
                        respStatusFile.set('Could not build a response!')
                        return
            
        
        def get_combo(self, event, log, t1, lab):

            if log == 1:
                if self.lastS.get() == False:
                    newV = sensCombo.get()
                    self.sensChoice.append(newV)

                try:
                    t2 = t1[newV]
                    self.nrlSensDict = t2
                    if type(t2) != tuple:
                        sensCombo['values'] = list(self.nrlSensDict)
                        sensCombo.current(0)
                    else:
                        self.lastS.set(True)
                        self.sav1.set(True)
    
                    lab.set(lab.get() + '\n' + newV)
                    lab1.configure(textvariable = lab)
                except:
                    print(self.sensChoice)
                    tkm.showwarning(title = "NRL Sensor Selection", message = "All fields of the selection filled!", icon = 'info')
                
                
            else:
                
                if self.lastD.get() == False:
                    newV = datCombo.get()
                    self.datChoice.append(newV)
                try:
                    t2 = t1[newV]
                    self.nrlDatDict = t2
                    
                    if type(t2) != tuple:
                        datCombo['values'] = list(self.nrlDatDict)
                        datCombo.current(0)
                    else:
                        self.lastD.set(True)
                        self.sav2.set(True)
                    lab.set(lab.get() + '\n' + newV)
                    lab2.configure(text = lab)
                except:
                    print(self.datChoice)
                    tkm.showwarning(title = "NRL Datalogger Selection", message = "All fields of the selection filled!", icon = 'info')
                
            
        def redo(inst, lab):
           if inst ==1:
               self.sensChoice = []
               self.nrlSensDict = self.nrl.sensors
               sensCombo['values'] = list(self.nrlSensDict)
               sensCombo.config(state = tk.NORMAL)
               sensCombo.current(0)
               lab.set("Your Current Sensor Selection is:")
               self.sav1.set(False)
               self.lastS.set(False)
               respStatusNRL.set('No NRL Response File')
               return
           else:
               self.datChoice = []
               self.nrlDatDict = self.nrl.dataloggers
               datCombo['values'] = list(self.nrlDatDict)
               datCombo.config(state = tk.NORMAL)
               datCombo.current(0)
               lab.set("Your Current Datalogger Selection is:")
               self.sav2.set(False)
               self.lastD.set(False)
               respStatusNRL.set('No NRL Response File')
               return
         
        def activeCheck(*args):
            if self.val1.get() == 0:
                for child in r0.winfo_children():
                    child.configure(state = 'normal')
                for child in sensFrame.winfo_children():
                    child.configure(state = 'disabled')
                for child in datFrame.winfo_children():
                    child.configure(state = 'disabled')
                for child in datFrame.winfo_children():
                    child.configure(state = 'disabled')
                acceptButt.configure(state = 'disabled')
                respStat.configure(state = 'normal')
                respNRL.configure(state = 'disabled')
                willBuild.set('Will try to buld response based on: Selected Response Files')

            if self.val2.get() == 0 and self.val1.get() == 0:
                for child in r1.winfo_children():
                    child.configure(state = 'normal')
                for child in r2.winfo_children():
                    child.configure(state = 'disabled')
                for child in r3.winfo_children():
                    child.configure(state = 'disabled')
                    
            elif self.val2.get() == 1 and self.val1.get() == 0:
                for child in r1.winfo_children():
                    child.configure(state = 'disabled')
                for child in r2.winfo_children():
                    child.configure(state = 'normal')
                for child in r3.winfo_children():
                    child.configure(state = 'normal')
                    
            elif self.val1.get() == 1:
                for child in r0.winfo_children():
                    child.configure(state = 'disabled')
                for child in r1.winfo_children():
                    child.configure(state = 'disabled')
                for child in r2.winfo_children():
                    child.configure(state = 'disabled')
                for child in r3.winfo_children():
                    child.configure(state = 'disabled')    
                for child in sensFrame.winfo_children():
                    child.configure(state = 'normal')
                for child in datFrame.winfo_children():
                    child.configure(state = 'normal')
                for child in datFrame.winfo_children():
                    child.configure(state = 'normal')
                acceptButt.configure(state = 'normal')
                respStat.configure(state = 'disabled')
                respNRL.configure(state = 'normal')
                willBuild.set('Will try to buld response based on: NRL Selections')

 
            if self.sav1.get() == True and self.sav2.get() == True:
                saveButt.configure(state = 'normal')
                C1.configure(state = 'normal')
                C2.configure(state = 'normal')
                
                if self.checkVarS.get() == 1:
                    ent1.configure(state = 'disabled')
                else:
                    ent1.configure(state = 'normal')
                    
                if self.checkVarD.get() == 1:
                    ent2.configure(state = 'disabled')
                else:
                    ent2.configure(state = 'normal')
                    
            elif self.sav1.get() == False or self.sav2.get() == False:
                saveButt.configure(state = 'disabled')
                C1.configure(state = 'disabled')
                C2.configure(state = 'disabled')
                ent1.configure(state = 'disabled')
                ent2.configure(state = 'disabled')

        def accepter(self):
            try:
                self.tempResp_NRL = self.nrl.get_response(sensor_keys = self.sensChoice, datalogger_keys = self.datChoice)
                respStatusNRL.set('Successfully built a response file with the above selections')
            except:
                tkm.showerror(title = "Sensor Coefficient Error", message = "Invalid or incomplete NRL keyword entry", icon = "error")
                
                
        def saver(self):
            
            tempChan = self.workingInv[0][self.workSelect[0]][self.workSelect[1]].copy()
            print(tempChan)
            
            if self.val1.get() == 0:
                self.tempFinalResp = self.tempResp_File
                
            elif self.val1.get() == 1:
                self.tempFinalResp = self.tempResp_NRL

             #   Make exception for silicon audio recorders at 40Vpg
            try: 
                if '_40Vpg' in tempChan.equipments[0].serial_number:
                    for stage in self.tempFinalResp.response_stages:
                        if stage.stage_gain == 1 and stage.input_units == 'counts' and stage.output_units == 'counts':
                            stage.stage_gain = stage.stage_gain * float(2/3)
                            break
            except:
                pass
            
            
            if self.checkVarS.get() == 0:
                try:
                    self.tempFinalResp.response_stages[0].stage_gain = float(ent1.get())
                except:
                    tkm.showerror(title = 'Invalid Stage Gain', text = 'The stage gain entered is invalid!', icon = 'error')
                    return
            if self.checkVarD.get() == 0:
                try:
                    for stage in self.tempFinalResp.response_stages:
                        if stage.input_units == 'V' and stage.output_units == 'COUNTS':
                            self.tempFinalResp.response_stages[2].stage_gain = 1/float(ent2.get())
                except:
                    tkm.showerror(title = 'Invalid Stage Gain', text = 'The stage gain entered is invalid!', icon = 'error')
                    return
                
            try:
                self.tempFinalResp.recalculate_overall_sensitivity()
            except:
                tkm.showerror(title = 'Sensitivity Recalculation', text = 'Unable to "recalculate_overall_sensitivity" for responses with input units different than ["DEF, "VEL", "ACC"]./nMoving on', icon = 'warning')
                pass
            
            tempChan.response = self.tempFinalResp
            self.workingInv[0][self.workSelect[0]].channels[self.workSelect[1]] = tempChan
            self.var1.set(self.var1.get()+1)
            respEdit.destroy()


        #   Define all management variables
        self.sensChoice = []
        self.datChoice = []
        
        self.nrlSensDict = self.nrl.sensors
        self.nrlDatDict = self.nrl.dataloggers
        
        self.TempSensResp = []
        self.TempDatResp = []
        
        self.tempFinalResp = []
        self.tempResp_File = []
        self.tempResp_NRL = []

        labts = tk.StringVar()
        labts.set("Your Current Sensor Selection is:")
        
        labtd = tk.StringVar()
        labtd.set("Your Current Datalogger Selection is:")
        
        labFile1 = tk.StringVar()
        labFile1.set("No File Chosen")
        
        labFile2 = tk.StringVar()
        labFile2.set("No File Chosen")
        
        labFile3 = tk.StringVar()
        labFile3.set("No File Chosen")
        
        sensOverText = tk.StringVar()
        sensOverText.set('No senor')
        
        datsOverText = tk.StringVar()
        datsOverText.set('No datalogger')
        
        self.checkVarS = tk.IntVar()
        self.checkVarS.set(1)
        self.checkVarD = tk.IntVar()
        self.checkVarD.set(1)
        
        respStatusFile = tk.StringVar()
        respStatusFile.set('No Response File')
        respStatusNRL = tk.StringVar()
        respStatusNRL.set('No NRL Response File')
        
        willBuild = tk.StringVar()
        willBuild.set('Will try to buld response based on: Selected Response Files')
            
        respEdit = tk.Toplevel()
        respEdit.resizable()
        respEdit.attributes('-topmost', True)
        
        self.val1 = tk.IntVar()
        self.val2 = tk.IntVar()
        self.sav1 = tk.BooleanVar()
        self.sav2 = tk.BooleanVar()
        self.sav1.set(False)
        self.sav2.set(False)
        
        self.lastS = tk.BooleanVar()
        self.lastS.set(False)
        self.lastD = tk.BooleanVar()
        self.lastD.set(False)
        
        e1 = tk.Frame(respEdit)
        ttk.Radiobutton(e1, text = 'Choose from File', variable = self.val1, value = 0).pack(side = tk.LEFT, padx = 5, pady = 5, anchor = 'w')
        ttk.Radiobutton(e1, text = 'Manually Generate Response', variable = self.val1, value = 1).pack(side = tk.RIGHT, padx = 5, pady = 5, anchor = 'w')
        e1.pack(side = tk.TOP, padx = 5, pady = 5)
        
        #   File method
        fileFrame = tk.LabelFrame(respEdit, font = 14, text = "Choose Response from File", relief = tk.RIDGE)
        fileFrame.pack(side = tk.TOP, padx = 5, pady = 5)
        
        r0 = tk.Frame(fileFrame)
        ttk.Radiobutton(r0, text = 'Sensor and Datalogger Responses Match', variable = self.val2, value = 0).pack(side = tk.TOP, padx = 5, pady = 5, anchor = 'w')
        ttk.Radiobutton(r0, text = 'Sensor and Datalogger Responses Differ', variable = self.val2, value = 1).pack(side = tk.TOP, padx = 5, pady = 5, anchor = 'w')

        r0.pack(side = tk.TOP, padx = 5, pady = 5)
        
        r1 = tk.Frame(fileFrame)
        tk.Label(r1, text = "Choose Sensor/Datalogger File: ", font = 11, anchor = 'w').pack(side = tk.LEFT, padx = 5, pady = 5, anchor = 'w')
        entR_Match = tk.Button(r1, text = "Choose File...", command = lambda: get_response(1))
        ent_label1 = tk.Label(r1, width = 20, textvariable = labFile1, font = 11, anchor = 'w')
        entR_Match.pack(side = tk.LEFT, padx = 5, pady = 5, anchor = 'w')
        ent_label1.pack(side = tk.LEFT, padx = 5, pady = 5, anchor = 'w')
        r1.pack(side = tk.TOP, padx = 5, pady = 5)
        
        r2 = tk.Frame(fileFrame)
        tk.Label(r2, text = "Choose Sensor Response File: ", font = 11, anchor = 'w').pack(side = tk.LEFT, padx = 5, pady = 5, anchor = 'w')
        entR_Match = tk.Button(r2, text = "Choose File...", state = 'disabled', command = lambda: get_response(2))
        ent_label2 = tk.Label(r2, width = 20, textvariable = labFile2, font = 11, anchor = 'w')
        entR_Match.pack(side = tk.LEFT, padx = 5, pady = 5)
        ent_label2.pack(side = tk.LEFT, padx = 5, pady = 5)
        r2.pack(side = tk.TOP, padx = 5, pady = 5)
        
        r3 = tk.Frame(fileFrame)
        tk.Label(r3, text = "Choose Datalogger Response File: ", font = 11, anchor = 'w').pack(side = tk.LEFT, padx = 5, pady = 5, anchor = 'w')
        entR_Match = tk.Button(r3, text = "Choose File...", state = 'disabled', command = lambda: get_response(3))
        ent_label3 = tk.Label(r3, width = 20, textvariable = labFile3, font = 11, anchor = 'w')
        entR_Match.pack(side = tk.LEFT, padx = 5, pady = 5)
        ent_label3.pack(side = tk.LEFT, padx = 5, pady = 5)
        r3.pack(side = tk.TOP, padx = 5, pady = 5)
        
        respStat = tk.Label(fileFrame, textvariable = respStatusFile, font = 11, anchor = 'w')
        respStat.pack(side = tk.TOP, padx = 5, pady = 5)

        manFrame = tk.LabelFrame(respEdit, font = 14, text = "Manually Enter Using National Response Library (NRL)", relief = tk.RIDGE)
        manFrame.pack(side = tk.TOP, padx = 5, pady = 5)
        
        sensFrame = tk.LabelFrame(manFrame, font = 14, text = "Sensor", relief = tk.RIDGE)
        sensFrame.pack(side = tk.TOP, padx = 5, pady = 5, fill = tk.X)
        
        sensCombo = ttk.Combobox(sensFrame, values = list(self.nrlSensDict), state = 'disabled')
        sensCombo.bind("<<ComboboxSelected>>", lambda event: get_combo(self, event, 1, self.nrlSensDict, labts))
        sensCombo.current(0)
        sensCombo.pack(side = tk.LEFT, padx = 5, pady = 5)
        
        lab1 = tk.Label(sensFrame, textvariable = labts, font = 11, anchor = 'w')
        lab1.pack(side = tk.LEFT, padx = 5, pady = 5)
        
        restButt1 = tk.Button(sensFrame, text = 'Reset', command = lambda: redo(1, labts), state = 'disabled')
        restButt1.pack(side = tk.RIGHT, padx = 5, pady = 5)
        
        datFrame = tk.LabelFrame(manFrame, font = 14, text = "Datalogger", relief = tk.RIDGE)
        datFrame.pack(side = tk.TOP, padx = 5, pady = 5, fill = tk.X)
        
        datCombo = ttk.Combobox(datFrame, values = list(self.nrlDatDict), state = 'disabled')
        datCombo.bind("<<ComboboxSelected>>", lambda event: get_combo(self, event, 2, self.nrlDatDict, labtd))
        datCombo.current(0)
        datCombo.pack(side = tk.LEFT, padx = 5, pady = 5)
        
        lab2 = tk.Label(datFrame, textvariable = labtd, font = 11, anchor = 'w')
        lab2.pack(side = tk.LEFT, padx = 5, pady = 5)
        
        restButt2 = tk.Button(datFrame, text = 'Reset', command = lambda: redo(2, labtd), state = 'disabled')
        restButt2.pack(side = tk.RIGHT, padx = 5, pady = 5)
        
        respNRL = tk.Label(manFrame, textvariable = respStatusNRL, font = 11, anchor = 'w')
        respNRL.pack(side = tk.TOP, padx = 5, pady = 5)
        respNRL.configure(state = 'disabled')
        
        calCheck = tk.Frame(manFrame)
        calCheck.pack(side = tk.TOP, padx = 5, pady = 5, fill = tk.X)
        
        calFrame = tk.LabelFrame(respEdit, font = 14, text = 'Calibrations', relief = tk.RIDGE)
        calFrame.pack(side = tk.TOP, padx = 5, pady = 5, fill = tk.X)
        
        
        sencal = tk.LabelFrame(calFrame, font = 13, text = 'Sensor')
        sencal.pack(side = tk.LEFT, padx = 5, pady = 5)
        
        sensTit = tk.Label(sencal, font = 11, text = 'Overall Sensor Sensitivity:', justify = 'left')
        sensTit.pack(side = tk.TOP, padx = 5, pady = 5)
        
        
        datcal = tk.LabelFrame(calFrame, font = 13, text = 'Datalogger')
        datcal.pack(side = tk.RIGHT, padx = 5, pady = 5)
        
        datTit = tk.Label(datcal, font = 11, text = 'Overall Datalogger Sensitivity:', justify = 'left')
        datTit.pack(side = tk.TOP, padx = 5, pady = 5)
        
        C1 = tk.Checkbutton(sencal, text = "Already Calibrated", variable = self.checkVarS, command = lambda: activeCheck())
        C1.pack(side = tk.TOP, padx = 5, pady = 5)
        C1.configure(state = 'disabled')

        C2 = tk.Checkbutton(datcal,  text = "Already Calibrated", variable = self.checkVarD, command = lambda: activeCheck())
        C2.pack(side = tk.TOP, padx = 5, pady = 5)
        C2.configure(state = 'disabled')

        ent1 = tk.Entry(sencal, width = 20, font = 11)
        ent1.configure(state = 'disabled')
        ent1.pack(side = tk.TOP, expand = tk.YES, padx = 5, pady = 5)

        ent2 = tk.Entry(datcal, width = 20, font = 11)
        ent2.configure(state = 'disabled')
        ent2.pack(side = tk.TOP, expand = tk.YES, padx = 5, pady = 5)
        
        buildLab = tk.Label(respEdit, textvariable = willBuild, font = 11, anchor = 'w')
        buildLab.pack(side = tk.TOP, padx = 5, pady = 5)
        
        acceptButt = tk.Button(respEdit, text = 'Accept Manual Selections', command = lambda: accepter(self))
        acceptButt['font'] = tkfont.Font(family = "Lucida Grande", size = 18)
        acceptButt.configure(state = 'disabled')
        acceptButt.pack(side = tk.TOP, padx = 5, pady = 5)

        saveButt = tk.Button(respEdit, text = 'Save', command = lambda: saver(self))
        saveButt['font'] = tkfont.Font(family = "Lucida Grande", size = 18)
        saveButt.configure(state = 'disabled')
        saveButt.pack(side = tk.TOP, padx = 5, pady = 5)
        


        self.val1.trace('w', activeCheck)
        self.val2.trace('w', activeCheck)
        self.sav1.trace('w', activeCheck)
        self.sav2.trace('w', activeCheck)
 
#%% Add Station        
    def edit_adds(self):
        def NewStatSave():
            lstr = self.workingInv[0].get_contents()
            newStat = name.get()
            
            if (' ' in newStat) or (newStat == None) or len(newStat) > 5:
                tkm.showwarning(title = "Station - Invalid Entry", message = "Invalid Station Entry.\nPlease follow SEED Guidlines", parent = self.root, icon = "warning")
                return
            
            if any(newStat.upper() in name for name in lstr['stations']):
                tkm.showwarning(title = "Station - Invalid Entry", message = "Station Already Exists.\nPlease Choose a Different Code", parent = self.root, icon = "warning")
                return
            
            now = datetime.now()
            
            sta = Station(
                    code = newStat.upper(),
                    latitude = 1,
                    longitude = 2,
                    elevation = 999,
                    creation_date = UTCDateTime(now),
                    site = Site(name = "Brand New Station"))
            
            cha = Channel(
                    code = "ABC",
                    location_code = "",
                    latitude = 1,
                    longitude = 2,
                    elevation = 999,
                    depth = 999,
                    start_date = UTCDateTime(now),
                    azimuth = 0,
                    dip = -90,
                    sample_rate = 999,
                    types = ['NEW INSTRUMENT'],
                    equipments = Equipment(description = 'Description',
                                       serial_number = 'Num123'),
                    sensor = Equipment(description = 'Description',
                                       serial_number = 'Num123'))
            
            sta.channels.append(cha)           
            self.workingInv[0].stations.append(sta)
            self.var1.set(self.var1.get()+1)
            addstat.destroy()

        
        addstat = tk.Toplevel()
        addstat.resizable()
        
        statFrame = tk.LabelFrame(addstat, font = 12, text = "Enter New Station Code", relief = tk.RIDGE)
        statFrame.pack(side = tk.TOP, padx = 5, pady = 5)
        
        name = tk.Entry(statFrame, width = 10, font = 12)
        name.pack(side = tk.LEFT, padx = 5, pady = 5)
        
        ent = tk.Button(statFrame, text = 'Add', command = lambda : NewStatSave())
        ent['font'] = tkfont.Font(family = 'Lucinda Grande', size = 12)
        ent.pack(side = tk.RIGHT, padx = 5, pady = 5)
        
#%% Delete station
    def deleteStation(self):
        def saver():
            ask = tkm.askyesno(title = "Station - Delete Selection", message = "Do you wish to delete the currently selected station " + str(availstats.get()) + '?', icon = "warning")
        
            if ask == True:
                del self.workingInv[0].stations[availstats.current()]
                self.var1.set(self.var1.get()+1)    
            else:
                return  
            
        #   Define the window 

        oneAdd = tk.Toplevel()
        oneAdd.resizable()
        
        statlist = self.workingInv[0].get_contents()
        
        editFrame = tk.LabelFrame(oneAdd, font = 14, text = 'Choose a Station To Delete:', relief = tk.RIDGE)
        editFrame.pack(side = tk.TOP, padx = 5, pady = 5)
        
        availstats = ttk.Combobox(editFrame, values = statlist['stations'], font = 14)
        availstats.current(0)
        availstats.pack(side = tk.LEFT, padx = 5, pady = 5)
        
        adder = tk.Button(editFrame, text = 'Delete Station', command = lambda: saver())
        adder['font'] = tkfont.Font(family = 'Lucinda Grande', size = 12)
        adder.pack(side = tk.RIGHT, padx = 5, pady = 5)

#%% Delete channel        
    def deleteChan(self):
        
        ask = tkm.askyesno(title = "Channel - Delete Selection", message = "Do you wish to delete the currently selected channel?", icon = "warning")
        
        if ask == True:
            del self.workingInv[0].stations[self.workSelect[0]].channels[self.workSelect[1]]
            self.var1.set(self.var1.get()+1)    
        else:
            return          


#%% Duplicate Channel        
    def duplicateChan(self):
        
        ask = tkm.askyesno(title = "Channel - Duplicate Selection", message = "Do you wish to duplicate the currently selected channel?", icon = "warning")
        
        if ask == True:
            temp = self.workingInv[0][self.workSelect[0]][self.workSelect[1]].copy()
            temp.code = temp.code + '2'
            self.workingInv[0].stations[self.workSelect[0]].channels.append(temp)
            self.var1.set(self.var1.get()+1)    
        else:
            return  
         
#%% Export All
    def export_all(self):
        def saveEx():
            sv = tkf.asksaveasfilename(defaultextension = '.xml',
                                        title="Save as", 
                                        filetypes=(("XML Files", ".xml"), ("all files", "*.*")))
            
            
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            
            t = text_area.get("1.0", tk.END)
            s = t.splitlines()
            
            if self.checkVarS.get() == 1:
                with open(self.curdir + '/_bin/ChangeLog.txt', 'a') as f:
                    f.write('Change Made at: ' + dt_string + '\n')
                    f.write('Change Made by: ' + str(name.get()) + '\n')
                    f.write('Initial File: ' + self.InitialFile + '\n')
                    f.write('Changed to File: ' + str(sv) + '\n')
                    f.write('THE FOLLOWING CHANGES WERE MADE:' + '\n')
                    for nl in s:
                        f.write('   -' + nl + '\n')
                    f.write('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
                    f.write('\n')
                
            if sv is None:
                return
            
            self.workingInv.created = UTCDateTime(datetime.now())
            self.workingInv.source = str(name.get()) + ', Ocean Networks Canada'
            self.workingInv.write(sv, format = "STATIONXML")
            exAll.destroy()

        def activeCheck(*args):
            if self.checkVarS.get() == 0:
                text_area.configure(state = 'disabled')
            if self.checkVarS.get() == 1:
                text_area.configure(state = 'normal')
                
        self.checkVarS = tk.IntVar()
        self.checkVarS.set(0)  
        
        exAll = tk.Toplevel()
        exAll.resizable()
        
        exFrame = tk.LabelFrame(exAll, font = 12, text = 'Export all', relief = tk.RIDGE)
        exFrame.grid(row = 0, column = 0, padx = 5, pady = 5)
        
        namelab = tk.Label(exFrame, text = 'Creator: ')
        namelab.grid(row = 0, column = 0, padx = 5, pady = 5)
        
        name = tk.Entry(exFrame, width = 10, font = 12)
        name.grid(row = 0, column = 1, padx = 5, pady = 5)
        
        C1 = tk.Checkbutton(exFrame, text = "Update Change Log", variable = self.checkVarS, command = lambda: activeCheck())
        C1.grid(row = 1, column = 0, padx = 5, pady = 5)
        
        lab1 = tk.Label(exFrame, text = "(Press 'Enter' to have each change in a new line)")
        lab1.grid(row = 1, column = 1, padx = 5, pady = 5)
        
        text_area = st.ScrolledText(exFrame, wrap = tk.WORD, width = 50, height = 25, font = ('Arial',12))
        text_area.grid(row = 3, column = 0, columnspan = 2, padx = 5, pady = 5)
        
        exBut = tk.Button(exFrame, text = 'Save', command = lambda: saveEx())
        exBut.grid(row = 4, column = 0, columnspan = 2, padx = 5, pady = 5)
        

#%% Selective Export      
    def export_select(self):
        def selective_saveas(station, location, channel, starttime, endtime, creator):
            
            if endtime != "*":
                try:
                    endtime = UTCDateTime(endtime)
                except:
                    tkm.showinfo(title="Invalid End Time", 
                                        message="Invalid end time provided. Must at least provide the year-month-day (e.g., 2010-01-01).")
                    return
                
            if starttime != "*":
                try:
                    starttime = UTCDateTime(starttime)
                except:
                    tkm.showinfo(title="Invalid Start Time", 
                                        message="Invalid start time provided. Must at least provide the year-month-day (e.g., 2010-01-01).")
                    return
                    
            sel_inv = self.workingInv.select(station=station, 
                                      location=location, 
                                      channel=channel, 
                                      starttime=starttime, 
                                      endtime=endtime)
            
            sel_inv = sel_inv.copy()
            
            if sel_inv.networks == []: #empty
                tkm.showinfo(title="Empty Inventory", 
                                    message="Parameter selection resulted in empty Inventory! \n\n{}\nStation: {}\nLocation: {}\nChannel: {}\nStart Time: {}\nEnd Time: {}\n\nFile NOT saved.".format(self.workingInv[0].code, station, location, channel, starttime, endtime))
                return
            else:
                filename = tkf.asksaveasfilename(
                        title="Save as", 
                        filetypes=(("XML Files", ".xml"), ("All Files", "*.*")))
                if filename is None:
                    return
                else:
                    sel_inv.created = UTCDateTime(datetime.now())
                    sel_inv.source = str(creator) + ', Ocean Networks Canada'
                    sel_inv.write(filename + '.xml', format="STATIONXML")
                    popup.destroy()

            
        if self.workingInv == "":
            return
        
        else:
            popup = tk.Toplevel()
            popup.grab_set()
            popup.title("Append to Inventory")
            
            lf = tk.LabelFrame(master=popup, text="Parameter Selection")
            lf.pack()
            
            tk.Label(lf, text="Station: ", justify="right").grid(row=1, column=1, sticky="e", padx=2, pady=5)
            stationEntry = tk.Entry(master=lf)
            stationEntry.grid(row=1, column=2, sticky="w")
            stationEntry.insert(tk.END, "*")
            
            tk.Label(lf, text="Location: ", justify="right").grid(row=2, column=1, sticky="e", padx=2, pady=5)
            locationEntry = tk.Entry(master=lf)
            locationEntry.grid(row=2, column=2, sticky="w")
            locationEntry.insert(tk.END, "*")
            
            tk.Label(lf, text="Channel: ", justify="right").grid(row=3, column=1, sticky="e", padx=2, pady=5)
            channelEntry = tk.Entry(master=lf)
            channelEntry.grid(row=3, column=2, sticky="w")
            channelEntry.insert(tk.END, "*")
            
            tk.Label(lf, text="Start Time: ", justify="right").grid(row=4, column=1, sticky="e", padx=2, pady=5)
            starttimeEntry = tk.Entry(master=lf)
            starttimeEntry.grid(row=4, column=2, sticky="w")
            starttimeEntry.insert(tk.END, "*")
        
            tk.Label(lf, text="End Time: ", justify="right").grid(row=5, column=1, sticky="e", padx=2, pady=5)
            endtimeEntry = tk.Entry(master=lf)
            endtimeEntry.grid(row=5, column=2, sticky="w")
            endtimeEntry.insert(tk.END, "*")
            
            tk.Label(lf, text="Creator: ", justify="right").grid(row=6, column=1, sticky="e", padx=2, pady=5)
            createEntry = tk.Entry(master=lf)
            createEntry.grid(row=6, column=2, sticky="w")
            createEntry.insert(tk.END, "*")
            
            b = tk.Button(master=lf, text="Save As", command=lambda: selective_saveas(station=stationEntry.get(), 
                                                                              location=locationEntry.get(), 
                                                                              channel=channelEntry.get(), 
                                                                              starttime=starttimeEntry.get(), 
                                                                              endtime=endtimeEntry.get(),
                                                                              creator=createEntry.get()))
            b.grid(row=7, column=1, sticky="w", padx=2, pady=5)
    
def main():
    app = ExcelXML("")
    app.root.mainloop()
    
if __name__ == '__main__':
    main()            
        
        