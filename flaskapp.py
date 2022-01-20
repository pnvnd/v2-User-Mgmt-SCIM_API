import os, requests, tabulate
from flask import Flask, render_template, request

url = 'https://scim-provisioning.service.newrelic.com/scim/v2/{}'
usr = 'Users'
grp = 'Groups'


Flask_App = Flask(__name__) # Creating our Flask Instance

@Flask_App.route('/', methods=['GET'])
def index():
    """ Displays the index page accessible at '/' """

    return render_template('index.html')

@Flask_App.route('/result/', methods=['POST'])
def getUsers():

    # request.form looks for:
    # html tags with matching "name= "
    TOKEN = request.form['token']

    headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {TOKEN}",}

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

    # hds = ['Email', 'First Name', 'Last Name', 'User Type', 'ID', 'Group']
    # pretty = tabulate(list, headers=hds)

    return render_template("index.html", user=user, token=TOKEN)



if __name__ == '__main__':
    Flask_App.debug = True
    Flask_App.run()