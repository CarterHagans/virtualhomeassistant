import os
import random
import string
from twilio.rest import Client
from dotenv import load_dotenv
from flask import Flask, Response, redirect, render_template, request,Blueprint, session
from twilio.twiml.messaging_response import MessagingResponse
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_socketio import SocketIO, send
from .models import User, Family
from . import db
from datetime import datetime
import json

import openai


openai.api_key = "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"

views = Blueprint("views", __name__)

load_dotenv()
account_sid = os.getenv("ACCOUNT_SID")
auth_token = os.getenv("AUTH_TOKEN")
client = Client(account_sid,auth_token)


DEV_OPTIONS = [" Create default user\n"," Create test family\n"," View test family attribute\n"," Change test family attribute\n"," Delete test family\n"," Reset test family\n"," Add user to test family\n", " Remove user from test family\n", " Change user attribute\n", " View user attribute\n"]



URL = "localhost:5000"

# ----------------- replying to a message ----------------- #



@views.route("/sms",methods=["POST"])
def sms_reply():
    
    resp = MessagingResponse()
    users_number = request.values.get("From")
    content = request.values.get("Body")
    usr = User.query.filter_by(phone_number=users_number).first()
    rsp = ""
    
    if usr == None:
        rsp = "You currently do not have an account.\n\nTo create an account, please type create"

        if content.lower() == "create":
            if usr!= None:
                rsp = "You already have an account!"
            else:
                usr = User(users_number,"",json.dumps([]),"creatingAccount",False,"None",json.dumps([]))
                db.session.add(usr)
                db.session.commit()
                rsp = "Please choose a name for your account!"
                usr.status = "chosenName"
                db.session.commit()
    else:

        # -------------- Functions for account not being created --------------
        if usr.status == "chosenName":
            createAccount(usr,content)
        if usr.status == "confirmingName":
            createAccount(usr,content)
        # -------------- Functions after account has been created --------------
        elif usr.fullAcc == True:
            if content.lower() == "cmds" or content.lower() == "commands" or content.lower() == "cmdlist" and usr.currentFam == "None":
                rsp = "View Families: Displays the families you are a part of\n\nCreate Family: Create a family\n\nJoin Family: Join a family\n\nChange name: Change the name of your account\n\nLogin (familyname): Logs your session into a specific family"
            
           

            # ------------------- Creating a family -------------------
            if content.lower() == "create" or content.lower() ==  "createfamily" or content.lower() == "createfam" and usr.currentFam == "None":
                code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

                family = Family("TEMP",usr.phone_number,json.dumps([]),json.dumps([]),f"{code}",json.dumps([]),json.dumps([]))
                db.session.add(family)
                rsp = "Please choose a name for your new family!"
                usr.status = "choosingNameForFamily"
                db.session.commit()
                    
                    
            if usr.status == "choosingNameForFamily" and content.lower() != "create" and content.lower() !=  "createfamily" and content.lower() != "createfam" and content.lower()!="temp":
                createFamily(usr,content)
            elif usr.status == "confirmingFamilyName" and content.lower() != "create" and content.lower() !=  "createfamily" and content.lower() != "createfam" and content.lower()!="temp":
                createFamily(usr,content)
            
            # ------------------- Viewing a users famillies -------------------
            if content.lower() == "view" or content.lower() ==  "viwefamilies" or content.lower() == "viewFams" and usr.currentFam == "None":
                users_fams = json.loads(usr.families)
                built_str = "Your families: \n\n"
                i = 1
                for x in users_fams:
                    fam_name = x.split(":")[0]
                    built_str += f"{i}: {fam_name}\n"
                    i+=1
                rsp = built_str
                
            # ------------------- Logging into a family -------------------
            if content.split()[0].lower() == "login":
                if usr.currentFam =="None":

                    loginToFam(usr,content)
                else:
                    rsp = "You cannot do this as you are currently already logged into a family."
                    
                    
            if usr.status == "loggingIntoFam":
                loginToFam(usr,content)
            
            
            # ------------------- Joining into a family -------------------
            if content.split()[0].lower() == "join" or content.split()[0].lower() == "joinf" or content.split()[0].lower() == "joinfam" or content.split()[0].lower() == "joinfamily":
                rsp = "Please enter the joincode of the family you are trying to join. If you have already entered it, it could be incorrect please ensure it's correct and try again."
                usr.status = "joiningNewFam"
                db.session.commit()


            if usr.status == "joiningNewFam":
                code = content
                famFound = False
                usrs_fams = json.loads(usr.families)
                fam_names = []
                
                for x in usrs_fams:
                    fam_names.append(x.split(":")[0])
                
                for fam in Family.query.all():
                    
                    if code == fam.joincode and users_number != fam.owner and fam.name not in fam_names:
                        usrs_fams.append(f"{fam.name}:owned by {fam.owner}")
                        usr.families = json.dumps(usrs_fams)
                        fam_member_list = json.loads(fam.members)
                        fam_member_list.append(usr.phone_number)
                        fam.members = json.dumps(fam_member_list)
                        usr.status = ""
                        rsp = f"You have now joined a family with the name {fam.name}!"
                        db.session.commit()
                        famFound = True
                if famFound == False:
                    rsp = "Please enter the joincode of the family you are trying to join. If you have already entered it, it could be incorrect please ensure it's correct and try again."   
            
            
            # ------------------- Family Commands -------------------
            if content.lower() == "cmds" or content.lower() == "commands" or content.lower() == "cmdlist" and usr.currentFam != "None":
                rsp = f"Commands of family: {usr.currentFam}\n\n View List (viewl): View the shopping list of this fmaily\n\Add Item (addi): Adds an item to the shopping list\n\nRemove Item (rmvi): Removes an item from the shopping list\n\nEdit item (editi): Edit an item in the shopping list\n\nView Members (viewm): View the members of this family\n\nView Admins (viewa): View the admins of this family\n\nView owner: See who owns the family\n\nView Annoucements (viewa): View the announcements put out by admins and the owner.\n\nLogout: Logs out of this family.\n\nADMIN COMMMNANDS: Kick: Kicks a member\n\nAnnounce: Create an announcement for the family\n\nAudit log: Views the audit log of administrative actions.\n\nOWNER COMMANDS:\n\nBan: Bans a user\n\nManage admins: Manage the roles of others\n\nFamily edit: Edit things about the family such as public, private family, name, and more."   
            
            if content.lower() == "viewl" or content.lower() == "viewlist" and usr.currentFam != "None":

                if " (auth)" in usr.currentFam:

                    for x in Family.query.all():
                        print(x.name,usr.currentFam)
                        if x.name +" (auth)" == usr.currentFam:
                            member_list = json.loads(x.members)
                            admin_list = json.loads(x.admins)
                            owner = x.owner
                            name = x.name.split(":")[0]
                            if usr.phone_number in member_list or usr.phone_number in admin_list or usr.phone_number == owner:
                                rsp = f"You can view {name}'s list at the following link: http://{URL}/{x._id}/list "
                else:
                    for x in Family.query.all():
                        if x.name == usr.currentFam:
                            member_list = json.loads(x.members)
                            admin_list = json.loads(x.admins)
                            owner = x.owner
                            name = x.name.split(":")[0]
                            if usr.phone_number in member_list or usr.phone_number in admin_list or usr.phone_number == owner:
                                rsp = f"You can view {name}'s list at the following link: http://{URL}/{x._id}/auth "

            if len(content.split(" ")) > 1:
                if content.split(" ")[0] == "addi":

                    fam_to_find = usr.currentFam
                    if fam_to_find == "None":
                        rsp = "You must be logged in to a family to execute this command."
                    else:
                        for x in json.loads(usr.families):

                            if x== fam_to_find:
       
                                item = content.split("addi ")
                                item.pop(0)
                                built_str = ""
                                if " (auth)" in x:
                                    name = x.split()
                                    name.pop()
                                    for word in name:
                                        built_str += f"{word} "
                                print(built_str)
                                fam_obj = Family.query.filter_by(name=built_str).first()
                                fam_list = json.loads(fam_obj.list)
                                audit_log = json.loads(fam_obj.auditLog)
                                now = datetime.now()
                                dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
                                fam_list.append(f"{len(fam_list) +1}: {item[0]}: Added by {usr.name}: {dt_string}")

                               

                                fam_name = x.split(":")[0]
                                rsp = f"Operation Succesful\n\nUser: {usr.name}\n\nAction: Added an item to the list: {item[0]} \n\nFamily: {fam_name}"
                                fam_obj.list = json.dumps(fam_list)
                                db.session.commit()
                                
     # ------------------------------- Dev commands ---------------------------------------------
        
            if content.lower() == "dcmds":
                
                if usr.phone_number == "+14075906008":
                    built_str = "Please choose an option from below: \n"
                    count = 1 
                    for x in DEV_OPTIONS:
                        built_str = built_str + f"\n{count}:{x}"
                        count+=1
                    rsp = built_str
                    usr.status = "selectingDevOption"
                    db.session.commit()
                else:
                    rsp = "You do not have permission to execute the dev commands!"
            elif usr.status == "selectingDevOption":
                selectDevCmd(usr,content)
            elif usr.status == 'selectingAttrToChange':
                selectDevCmd(usr,content)
            elif usr.status == "choosingUsrToAddForTestFam":
                selectDevCmd(usr,content)
            elif usr.status == "choosingUsrToRemoveForTestFam":
                selectDevCmd(usr,content)
            elif usr.status == "devChangingUsrAttr":
                selectDevCmd(usr,content)
               
                  
                     
    resp.message(f"{rsp}")
    return Response(str(resp),mimetype="application/xml")



def createAccount(user,content):

    if user.status == "chosenName":
        message = client.messages \
        .create(
            body=f"You chose {content} as your name, correct?\n\n",
            from_="+13025642358",
            to=user.phone_number
        )
        user.status = "confirmingName"
        user.name = content
        db.session.commit()
        
    elif user.status == "confirmingName":
        if content.lower() == "yes":
            message = client.messages \
            .create(
                body=f"Thank you, {user.name}! Your account has been created. Please type cmds to view the commands you can do.",
                from_="+13025642358",
                to=user.phone_number
            )
            user.status = ""
            user.fullAcc = True
            db.session.commit()
            
        elif content.lower() == "no":
            message = client.messages \
            .create(
                body=f"Okay, your name is not {user.name}, please respond to change your name.",
                from_="+13025642358",
                to=user.phone_number
            )
            user.status = "chosenName"
            user.name = ""
            db.session.commit()
        elif content.lower() != "no" and content.lower() != "yes":

            message = client.messages \
            .create(
                body=f"Please reply with yes or no.",
                from_="+13025642358",
                to=user.phone_number
            )



def createFamily(usr,content):
    if usr.status == "choosingNameForFamily":
        message = client.messages \
        .create(
            body=f"You chose {content} as your family name, correct?\n\nPlease reply with yes or no",
            from_="+13025642358",
            to=usr.phone_number
        )
    
        for fam in Family.query.all():
            if fam.name == "TEMP" and fam.owner == usr.phone_number:
                fam.name = f"TEMP:{content}"
        usr.status = "confirmingFamilyName"
        db.session.commit()
    elif usr.status == "confirmingFamilyName":
        if content.lower() == "yes":
            message = client.messages \
            .create(
                body=f"Thank you, {usr.name}! Your family has been created. You can view your families by typing the view command.",
                from_="+13025642358",
                to=usr.phone_number
            )
            for fam in Family.query.all():
                if "temp" in fam.name.lower() and fam.owner == usr.phone_number:
                    name = fam.name.split(":")[1]
                    fam.name = f"{name}:owned by {usr.phone_number}"
                    users_fams = json.loads(usr.families)
                    users_fams.append(fam.name)
                    usr.families = json.dumps(users_fams)
            db.session.commit()
            
            
        elif content.lower() == "no":
            message = client.messages \
            .create(
                body=f"Okay, your family name has been reset from {usr.name} to nothing, please respond to change your name.",
                from_="+13025642358",
                to=usr.phone_number
            )
            usr.status = "choosingNameForFamily"
            db.session.commit()
            
            
def loginToFam(usr,content):
    usrs_fams = json.loads(usr.families)
    if usr.status == "loggingIntoFam":
        fams_to_choose = json.loads(usr.selfSearchResults)
        chosen_fam = fams_to_choose[int(content)-1]
        message = client.messages \
        .create(
            body=f"You have succesfully logged in to the family with the name {chosen_fam}",
            from_="+13025642358",
            to=usr.phone_number
        )
        usr.selfSearchResults = json.dumps([])
        for x in json.loads(usr.families):

            if x.split(":")[0] == chosen_fam:
                    usr.currentFam = x

        usr.status = ""
        db.session.commit()
    else:
        entered_fam = content.split("login ")
        if len(entered_fam) == 1:
            message = client.messages \
            .create(
                body=f"Please specify a family!",
                from_="+13025642358",
                to=usr.phone_number
            )
        else:
            entered_fam = content.split("login ")[1]
            results = []
            for fam in usrs_fams:
                fam_name = fam.split(':')[0]
                if entered_fam.lower() in fam_name.lower():
                    results.append(fam_name)
                    
            
            if len(results) == 0:
                message = client.messages \
                .create(
                    body=f"You are currently in no families that match this name, please make sure you typed the name correctly and try again.",
                    from_="+13025642358",
                    to=usr.phone_number
                )
            elif len(results) == 1:
                message = client.messages \
                .create(
                    body=f"You have succesfully logged in to the family with the name {results[0]}",
                    from_="+13025642358",
                    to=usr.phone_number
                )
                for x in json.loads(usr.families):

                    if x.split(":")[0] == results[0]:
                            usr.currentFam = x
                usr.status = ""
                db.session.commit()
            elif len(results) > 1:
                built_str = "With the argument that you passed, there were multiple of your families that came up as the result. Please choose the family you were trying to login to from the list below, type the number that corresponds with that family.\n\n"
                count = 1
                for x in results:
                    built_str += f"{count}: {x}\n"
                    count+=1
                message = client.messages \
                .create(
                    body=built_str,
                    from_="+13025642358",
                    to=usr.phone_number
                )
                usr.status = "loggingIntoFam"
                usr.selfSearchResults = json.dumps(results)
                db.session.commit()
                
                
# --------------------------- VIEW FUNCTIONS ---------------------------       
    
@views.route("/<id>/auth",methods=["POST","GET"])    
def auth(id):

    fam = Family.query.filter_by(_id=id).first()
    if fam == None:
        return render_template("auth.html",close=True)
    if request.method == "GET":
        session.clear()
        return render_template("auth.html")
    elif request.method == "POST":
        if session.get("status") == None or session.get("status") != "waitingForAuth":
            number_to_search = "+1"
            entered_number = request.form.get("phonenumber")
            number_to_search +=entered_number
            acc = User.query.filter_by(phone_number=number_to_search).first()
            fam = Family.query.filter_by(_id=id).first()
            member_list = json.loads(fam.members)
            admin_list = json.loads(fam.admins)
            owner = fam.owner
            if acc.phone_number in member_list or acc.phone_number in admin_list or acc.phone_number == owner:
                code = ''.join(random.choice(string.digits) for _ in range(6))
                message = client.messages \
                .create(
                    body=f"Your authentication code is {code}",
                    from_="+13025642358",
                    to=acc.phone_number
                )
                fam_list  = json.loads(acc.families)
                acc.families = json.dumps(fam_list)
                session['status'] = "waitingForAuth"
                session['phoneNumber'] = acc.phone_number
                session['code'] = code
                db.session.commit()
            return render_template("auth.html",auth=True,phone_number=acc.phone_number,code=code)
        elif session.get('status') == "waitingForAuth":
            entered_code = request.form.get("entered_code")
            if entered_code == session.get("code"):
                usr = User.query.filter_by(phone_number=session.get("phoneNumber")).first()
                fam = Family.query.filter_by(_id=id).first()
                fam_list = json.loads(usr.families)
                for x in fam_list:
                    if x == fam.name:
                        fam_list.remove(x)
                        if " (auth)" not in x: 
                            new_name = x + " (auth)"
                        else:
                            new_name = x
                        fam_list.append(new_name)
                        usr.families = json.dumps(fam_list)
                        if " (auth)" not in x:
                            
                            usr.currentFam = usr.currentFam + " (auth)"
                        else:
                            usr.currentFam = x
                        db.session.commit()

                return redirect(f"/{id}/list")
                
            else:   
                return render_template("auth.html",authFailed=True)

          
@views.route('/<id>/list',methods=["POST","GET"])
def shop_list(id):
    
    fam = Family.query.filter_by(_id=id).first()
    usr = User.query.filter_by(phone_number=session.get("phoneNumber")).first()

    if fam == None or usr == None:
        return render_template("list.html",close=True,fam=fam)
    
    else:
        for x in Family.query.all():
            
            if x.name + " (auth)" in json.loads(usr.families):

                if usr.phone_number in json.loads(fam.members) or usr.phone_number in json.loads(fam.admins) or usr.phone_number == fam.owner: 
                    perms = False
                if  usr.phone_number in json.loads(fam.admins) or usr.phone_number == fam.owner:
                    perms = True
                    shoppingList = json.loads(fam.list)
                    
                    name = fam.name.split(":")[0]
                    owner_details = User.query.filter_by(phone_number=fam.owner).first()

                    return render_template("list.html",shopList=shoppingList,fam=fam,famName=name,owner=owner_details,perms=perms)
                else:
                    return render_template("list.html",notValidated=True)
            else:
                return redirect(f"/{id}/auth")

@views.route("/<id>/delete/<item_id>")
def delItem(id,item_id):
    fam = Family.query.filter_by(_id=id).first()
    usr = User.query.filter_by(phone_number=session.get("phoneNumber")).first()
    if fam == None or usr == None:
        return render_template("delItem.html",close=True)
    else:
        if  usr.phone_number in json.loads(fam.admins) or usr.phone_number == fam.owner:
            fam_list = json.loads(fam.list)
            index = int(item_id) -1
            fam_list.remove(fam_list[index])
            fam.list = json.dumps(fam_list)
            db.session.commit()
            return render_template("delItem.html",perms=True,fam=fam)
        elif usr.phone_number in json.loads(fam.members):
            return render_template("delItem.html",perms=False)
        else:
            return render_template("delItem.html",notInFam=True)
        
@views.route("/<id>/edit/<item_id>",methods=['GET',"POST"])
def editItem(id,item_id):
    fam = Family.query.filter_by(_id=id).first()
    usr = User.query.filter_by(phone_number=session.get("phoneNumber")).first()
    if request.method == "GET":
        if fam == None or usr == None:
            return render_template("editItem.html",close=True)
        else:
            if  usr.phone_number in json.loads(fam.admins) or usr.phone_number == fam.owner:
                fam_list = json.loads(fam.list)
                index = int(item_id) -1
                item = fam_list[index]
                return render_template("editItem.html",perms=True,fam=fam,item=item)
            elif usr.phone_number in json.loads(fam.members):
                return render_template("editItem.html",perms=False)
            else:
                return render_template("editItem.html",notInFam=True)
            
    elif request.method == "POST":
        new_name = request.form.get("newname")
        fam_list = json.loads(fam.list)
        index = int(item_id) -1
        item = fam_list[index]
        split_item = item.split(": ")
        fam_list[index] = f"{item_id}: {new_name}: Previously edited by {usr.name} , they renamed this item to {new_name}. The previous name of this item was {split_item[1]} : {split_item[3]}"
        fam.list = json.dumps(fam_list)
        db.session.commit()
        return redirect(f"/{id}/list")

# --------------------------- TEST FUNCTIONS ---------------------------

def selectDevCmd(usr,content):
    if usr.status == "selectingAttrToChange":
        val = content.split(" ")[1]

        if content.split(" ")[0] == "1":

            attr = "Owner"
            rsp = changeTestFamAttr(attr,val)
            message = client.messages \
            .create(
                body=f"{rsp}",
                from_="+13025642358",
                to=usr.phone_number
            )
        elif content.split(" ")[0] == "2":
            attr = "admins"
            rsp = changeTestFamAttr(attr,val)
            message = client.messages \
            .create(
                body=f"{rsp}",
                from_="+13025642358",
                to=usr.phone_number
            )
        elif content.split(" ")[0] == "3":
            attr = "members"
            rsp = changeTestFamAttr(attr,val)
            message = client.messages \
            .create(
                body=f"{rsp}",
                from_="+13025642358",
                to=usr.phone_number
            )
        elif content.split(" ")[0] == "4":
            attr = "joincode"
            rsp = changeTestFamAttr(attr,val)
            message = client.messages \
            .create(
                body=f"{rsp}",
                from_="+13025642358",
                to=usr.phone_number
            )
        usr.status = ""
        db.session.commit()
    elif usr.status == "choosingUsrToAddForTestFam":
        rsp = addUserToTestfam(content)
        message = client.messages \
        .create(
            body=f"{rsp}",
            from_="+13025642358",
            to=usr.phone_number
        )
        usr.status = ""
        db.session.commit()
    elif usr.status == "choosingUsrToRemoveForTestFam":
        rsp = removeUserFromTestFam(content)
        message = client.messages \
        .create(
            body=f"{rsp}",
            from_="+13025642358",
            to=usr.phone_number
        )
        usr.status = ""
        db.session.commit()
    elif usr.status == "devChangingUsrAttr":
        attr = None
        val = content.split(" ")[1]
        if content.split(" ")[0] == "1":
            attr = "status"
            rsp = changeUserAttr(attr,val)
            message = client.messages \
            .create(
                body=f"{rsp}",
                from_="+13025642358",
                to=usr.phone_number
            )
        elif content.split(" ")[0] == "2":
            attr = "name"
            rsp = changeUserAttr(attr,val)
            message = client.messages \
            .create(
                body=f"{rsp}",
                from_="+13025642358",
                to=usr.phone_number
            )
        elif content.split(" ")[0] == "3":
            attr = "families"
            rsp = changeUserAttr(attr,val)
            message = client.messages \
            .create(
                body=f"{rsp}",
                from_="+13025642358",
                to=usr.phone_number
            )
        elif content.split(" ")[0] == '4':
            attr = "currentFam"
            rsp = changeUserAttr(attr,val)
            message = client.messages \
            .create(
                body=f"{rsp}",
                from_="+13025642358",
                to=usr.phone_number
            )
        elif content.split(" ")[0] == "5":
            attr = "sessionStatus"
            rsp = changeUserAttr(attr,val)
            message = client.messages \
            .create(
                body=f"{rsp}",
                from_="+13025642358",
                to=usr.phone_number
            )
    else:
        
        if content == '1':
            rsp = createDefaultUser()
            message = client.messages \
            .create(
                body=f"{rsp}",
                from_="+13025642358",
                to=usr.phone_number
            )
        elif content == '2':
            rsp = createTestFam()
            message = client.messages \
            .create(
                body=f"{rsp}",
                from_="+13025642358",
                to=usr.phone_number
            )
        elif content == '3':
            rsp = getTestFamInfo()
            message = client.messages \
            .create(
                body=f"{rsp}",
                from_="+13025642358",
                to=usr.phone_number
            )
        elif content == '4':
            message = client.messages \
            .create(
                body=f"Please choose an option to change from below and the new value (sepereated by a space):\n1. Owner\n2. Admins\n3. Members\n4. Joincode",
                from_="+13025642358",
                to=usr.phone_number
            )
            usr.status = "selectingAttrToChange"
            db.session.commit()
        elif content == '5':
            rsp = deleteTestFam()
            message = client.messages \
            .create(
                body=f"{rsp}",
                from_="+13025642358",
                to=usr.phone_number
            )
        elif content == '6':
            rsp = resetTestFam()
            message = client.messages \
            .create(
                body=f"{rsp}",
                from_="+13025642358",
                to=usr.phone_number
            )
        elif content == '7':
            message = client.messages \
            .create(
                body=f"Please reply with the phone number you want to add to the test family.",
                from_="+13025642358",
                to=usr.phone_number
            )
            usr.status = "choosingUsrToAddForTestFam"
            db.session.commit()
        elif content == '8':
            message = client.messages \
            .create(
                body=f"Please reply with the phone number you want to remove to the test family.",
                from_="+13025642358",
                to=usr.phone_number
            )
            usr.status = "choosingUsrToRemoveForTestFam"
            db.session.commit()
        elif content == '9':
            message = client.messages \
            .create(
                body=f"Please choose an option from below. Also seperate the value with a space with what you want the new value to be.\n1. Status\n2. Name\n3. Families\n4. currentFam\n5. Session Status",
                from_="+13025642358",
                to=usr.phone_number
            )
            usr.status = "devChangingUsrAttr"
            db.session.commit()
        elif content == "10":
            rsp = viewUserAttr()
            message = client.messages \
            .create(
                body=f"{rsp}",
                from_="+13025642358",
                to=usr.phone_number
            )
        

def createDefaultUser():
    usr = User("+14075906008","Carter",json.dumps(["Carter's default family"]),"",True,"",json.dumps([]))
    db.session.add(usr)
    db.session.commit()
    return "default user has been created"

def createTestFam():
    code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    family = Family("TESTFAMILY","4071111111",json.dumps([]),json.dumps([]),f"{code}",json.dumps([]),json.dumps([]))
    db.session.add(family)
    db.session.commit()
    return "test family has been created"


def getTestFamInfo():
    testfam = Family.query.filter_by(name="TESTFAMILY").first()
    return [testfam.owner,json.loads(testfam.admins),json.loads(testfam.members),testfam.joincode]

    

def changeTestFamAttr(attr,value):
    
    testfam = Family.query.filter_by(name="TESTFAMILY").first()
    if attr.lower() == "owner":
        testfam.owner = value
        return f"test family owner has been changed to {value}"
    elif attr.lower() == "admins":
        testfam.admins = json.dumps(value)
        return f"test family admin list has been changed to {value}"
    elif attr.lower() == "members":
        testfam.members = json.dumps(value)
        return f"test family member list has been changed to {value}"
    elif attr.lower() == "joincode":
        testfam.joincode = value
        return f"test family joincode has been changed to {value}"
        
    db.session.commit()

def deleteTestFam():
    testfam = Family.query.filter_by(name="TESTFAMILY").first()
    db.session.delete(testfam)
    db.session.commit()
    return "Test family deleted"

def resetTestFam():
    testfam = Family.query.filter_by(name="TESTFAMILY").first()
    db.session.delete(testfam)
    db.session.commit()
    code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    family = Family("TESTFAMILY","4071111111",json.dumps([]),json.dumps([]),f"{code}",json.dumps([]),json.dumps([]))
    db.session.add(family)
    db.session.commit()
    return "test family has been reset"


def addUserToTestfam(phone_number):
    testfam = Family.query.filter_by(name="TESTFAMILY").first()
    member_list = json.loads(testfam.members)
    member_list.append(phone_number)
    testfam.members = json.dumps(member_list)
    db.session.commit()
    return f"added {phone_number} to member list"

    
def removeUserFromTestFam(phone_number):
    testfam = Family.query.filter_by(name="TESTFAMILY").first()
    member_list = json.loads(testfam.members)
    member_list.remove(phone_number)
    testfam.members = json.dumps(member_list)
    db.session.commit()
    return f"removed {phone_number} from member list"




def changeUserAttr(attr,value):
    usr = User.query.filter_by(phone_number="+14075906008").first()
    if attr.lower() == "status":
        usr.status = f"{value}"
    elif attr.lower() == "name":
        usr.name =  f"{value}"
    elif attr.lower() == "families":
        usr.families = json.dumps(value)
    elif attr.lower() == "currentfam":
        usr.currentFam = f"{value}"
    elif attr.lower() == "sessionStatus":
        session['sessionStatus'] = value  
    
    db.session.commit()
    return f"{attr} has been changed to {value}"


def viewUserAttr():
    usr = User.query.filter_by(phone_number="+14075906008").first()
    return (usr.name,json.loads(usr.families),usr.status,usr.currentFam)