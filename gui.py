# pyinstaller --onefile --noconsole --icon favicon.ico main.py
# pip install requests tabulate

## NOT READY FOR USE! ##

import os
import json
import requests

from tkinter import *
from tkinter import filedialog
import tkinter.messagebox as box

import webbrowser

TOKEN = os.getenv('TOKEN')
url = 'https://scim-provisioning.service.newrelic.com/scim/v2/{}'
usr = 'Users'
grp = 'Groups'
headers = {
    'Content-Type': 'application/json',
    'Authorization': f"Bearer {TOKEN}",
}

userId = "0"
groupId = "0"

### Functions Here ###

def getUsers():
    userResponse = requests.get(url=url.format(usr), headers=headers)
    userJsonData = userResponse.json()
    groupResponse = requests.get(url=url.format(grp), headers=headers)
    groupJsonData = groupResponse.json()
    list = []
    
    for userName in userJsonData['Resources']:
        groupList = []
        for groupName in groupJsonData['Resources']:
            if len(groupName['members']) != 0:
                 for grpName in groupName['members']:
                    if userName['id'] == grpName['value']:
                        groupList.append(groupName['displayName'])
        user = userName['userName'], userName['name']['givenName'], userName['name']['familyName'],  userName[
            'urn:ietf:params:scim:schemas:extension:newrelic:2.0:User']['nrUserType'], userName['id'],groupList
        list.append(user)

    hds = ['Email', 'First Name', 'Last Name', 'User Type', 'ID', 'Group']
    pretty = tabulate(list, headers=hds)
    print(pretty)
    print()

def getGroups():
    response = requests.get(url=url.format(grp), headers=headers)
    jsonData = response.json()
    list = []
    for groupName in jsonData['Resources']:
        user = groupName['displayName'], groupName['id']
        list.append(user)

    hds = ['Group', 'Group Id']
    pretty = tabulate(list, headers=hds)
    print(pretty)
    print()

def createUsers(fName,lName,email,userType):
    with open("util/users.json", "r") as jsonFile:
        data = json.load(jsonFile)
    data['userName'] = email
    data['emails'][0]['value'] = email 
    data['name']['givenName'] = fName
    data['name']['familyName'] = lName
    data['urn:ietf:params:scim:schemas:extension:newrelic:2.0:User']['nrUserType'] = userType + ' User'
    
    with open("util/users.json", "w") as jsonFile:
        json.dump(data, jsonFile)

    jsonFile = open('util/users.json','rb')
    users=jsonFile.read()
    response = requests.post(url=url.format(usr), headers=headers, data=users)
    jsonData = response.json()
    print(jsonData)
    jsonFile.close()
    print()

def createGroups(groupName):
    with open("util/groups.json", "r") as jsonFile:
        data = json.load(jsonFile)
    data['displayName'] = groupName
    with open("util/groups.json", "w") as jsonFile:
        json.dump(data, jsonFile)    
    jsonFile = open('util/groups.json','rb')
    users=jsonFile.read()
    response = requests.post(url=url.format(grp), headers=headers, data=users)
    jsonData = response.json()
    print(jsonData)
    jsonFile.close()
    print() 

def usersGroups(userId,groupId):
    with open("util/usersGroup.json", "r") as jsonFile:
        data = json.load(jsonFile)
    data['Operations'][0]['op'] = 'Add'
    data['Operations'][0]['value'][0]['value'] = userId
    with open("util/usersGroup.json", "w") as jsonFile:
        json.dump(data, jsonFile)    
    jsonFile = open('util/usersGroup.json','rb')
    users=jsonFile.read()
    response = requests.patch(url=url.format(grp+'/'+groupId), headers=headers, data=users)
    jsonData = response.json()
    print(jsonData)
    jsonFile.close()
    print()

def deleteUser(userId):
    response = requests.delete(url=url.format(usr+'/'+userId), headers=headers)
    print(response)
    print()

def deleteGroup(groupId):
    response = requests.delete(url=url.format(grp+'/'+groupId), headers=headers)
    print(response)
    print()

### Functions END ###

def callback(url):
    webbrowser.open_new(url)

"""
Menu Bar Start
"""
def work_dir():
    pwd = filedialog.askdirectory()
    os.chdir(pwd)
    cwd.config(text="Current Working Directory: " + pwd)

def about():
   about_win = Toplevel(window)

   about_win.title("About")
   
   frame0 = LabelFrame(about_win, text="New Relic V2 User Management SCIM API", padx=5, pady=5)
   frame0.pack(padx=10, pady=10)
   
   about_label = Label(frame0, text = "The New Relic V2 User Management SCIM API is an open-source tool that helps migrate V1 users to V2 using the SCIM API.")
   about_label.pack()

   link1 = Label(frame0, text="GitHub Repository for GUI by Peter Nguyen", fg="blue", cursor="hand2")
   link1.pack(anchor=W)
   link1.bind("<Button-1>", lambda e: callback("https://github.com/pnvnd/v2-User-Mgmt-SCIM_API"))

   link2 = Label(frame0, text="Original GitHub Project by Dan Kairu", fg="blue", cursor="hand2")
   link2.pack(anchor=W)
   link2.bind("<Button-1>", lambda e: callback("https://github.com/Dkairu/v2-User-Mgmt-SCIM_API"))

   close_button = Button(about_win, text="Close", command = about_win.destroy)
   close_button.pack(padx=10, pady=10)


"""
Graphical Interface Start
"""

#from main import *

window = Tk()
#window.iconbitmap("favicon.ico")
window.title("New Relic v2 User Management SCIM API")

menubar = Menu(window)

filemenu = Menu(menubar, tearoff=0)

menubar.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="Change TOKEN", command= work_dir)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=window.destroy)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="About", command=about)
menubar.add_cascade(label="Help", menu=helpmenu)

window.config(menu=menubar)

label = Label(window, text = "New Relic v2 User Management SCIM API - CRUD Operations")
label.grid(row=0, column=0, columnspan=4)

frame1 = LabelFrame(window, text="Create", padx=5, pady=5)
frame1.grid(row=1, column=0, padx=10, pady=10)

btn_createUsers = Button(frame1, text="Create User", command = createUsers)
btn_createUsers.grid(row=0, column=0, sticky='news')

btn_createGroups = Button(frame1, text="Create Group", command = createGroups)
btn_createGroups.grid(row=1, column=0, sticky='news')

frame2 = LabelFrame(window, text="Read", padx=5, pady=5)
frame2.grid(row=1, column=1, padx=10, pady=10)

btn_getUsers = Button(frame2, text="View Users", command = getUsers)
btn_getUsers.grid(row=0, column=0, sticky='news')

btn_getGroups = Button(frame2, text="View Users", command = getGroups)
btn_getGroups.grid(row=1, column=0, sticky='news')

frame3 = LabelFrame(window, text="Update", padx=5, pady=5)
frame3.grid(row=1, column=2, padx=10, pady=10)

btn_update = Button(frame3, text="Add User to Group", command = usersGroups(userId,groupId))
btn_update.grid(row=0, column=0, sticky='news')

frame4 = LabelFrame(window, text="Delete", padx=5, pady=5)
frame4.grid(row=1, column=3, padx=10, pady=10)

btn_deleteUser = Button(frame4, text="Delete User", command = deleteUser(userId))
btn_deleteUser.grid(row=0, column=0, sticky='news')

btn_deleteGroup = Button(frame4, text="Delete User", command = deleteGroup(groupId))
btn_deleteGroup.grid(row=1, column=0, sticky='news')

"""
Status Bar Start
"""
cwd = Label(window, text = "Current TOKEN: " + os.getenv("TOKEN"), bd=1, relief=SUNKEN, anchor=W)
cwd.grid(row=5, column=0, columnspan=4, sticky='news')

window.mainloop()