import os
import random
import string
from twilio.rest import Client
from flask import Flask, Response, redirect, render_template, request,Blueprint, session
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse, Gather
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_socketio import SocketIO, send
from .models import User, Family
from . import db
from datetime import datetime
import json
from difflib import SequenceMatcher
import requests
from flask_migrate import Migrate
from pytz import timezone


views = Blueprint("views", __name__)


account_sid =  ''
auth_token = ''
client = Client(account_sid,auth_token)


DEV_OPTIONS = [" Create default user\n"," Create test family\n"," View test family attribute\n"," Change test family attribute\n"," Delete test family\n"," Reset test family\n"," Add user to test family\n", " Remove user from test family\n", " Change user attribute\n", " View user attribute\n"]


aliases = {
    "create account": "Create an account",
    "create account ": "Create an account",
    "create account!": "Create an account",
    "create account.": "Create an account",
    "i would like to create an account": "Create an account",
    "how can i create an account": "Create an account",
    "how can i create an account?": "Create an account",
    "i would like to create an account!": "Create an account",
    "i would like to create an account.": "Create an account",
    "make me a account": "Create an account",
    "can i have an account": "Create an account",
    "can i have an account please": "Create an account",
    "can i have an account please?": "Create an account",
    "create family": "Create a family",
    "create family " : "Create a family",
    "create family!": "Create a family",
    "create family.": "Create a family",
    "i would like to create a family": "Create a family",
    "how can i create a family": "Create a family",
    "how can i create a family?": "Create a family",
    "i would like to create a family": "Create a family",
    "i would like to create a family!": "Create a family",
    "i would like to create a family.": "Create a family",
    "make me a family": "Create a family",
    "can i have a family": "Create a family",
    "can i have family please": "Create a family",
    "can i have a family please?": "Create a family",
    "view families": "View families",
    "view my families": "View families",
    "how to view families": "View families",
    "can i see the families i am in": "View families",
    "can i see my families": "View families",
    "how do i see my families": "View families",
    "what families i am in": "View families",
    "i forgot what families i am in": "View families",
    "can i see what families i am in": "View families",
    "what families i am in": "View families",
    "i need to login to a family": "Login to a family",
    "how can i login to a family": "Login to a family",
    "help i need to login to a family": "Login to a family",
    "join family": "Join a family",
    "join a family": "Join a family",
    "how to join family": "Join a family",
    "how can i join a family": "Join a family",
    "i need to join a family": "Join a family",
    "join my friends family": "Join a family",
    "join the family": "Join a family",
    "change my name": "Change account name",
    "change account name": "Change account name",
    "how can i change my account name": "Change account name",
    "how can i change my name": "Change account name",
    "change name of account": "Change account name",
    "new account name": "Change account name",
    "account name new": "Change account name",
    "new name": "Change account name",
    "view list": "View shopping list",
    "view shopping list": "View shopping list",
    "view my list": "View shopping list",
    "view the family list": "View shopping list",
    "view the shopping list": "View shopping list",
    "how can i see the list": "View shopping list",
    "how can i see the web editor": "View shopping list",
    "how can i see whats on the list": "View shopping list",
    "how can i see my shopping list": "View shopping list",
    "how to see the shopping list": "View shopping list",
    "logout of family": "Logout of family",
    "how to logout of a family": "Logout of family",
    "logout family": "Logout of family",
    "can i logout of family": "Logout of family",
    "logout please": "Logout of family",
    "logout help": "Logout of family",
    "view admins": "View family admins",
    "view family admins": "View family admins",
    "who are the admins of this family": "View family admins",
    "how can i see the admins of the family": "View family admins",
    "who are the admins": "View family admins",
    "show me the admins of the family": "View family admins",
    "can i see the admins of the family": "View family admins",
    "view members": "View family members",
    "view family members": "View family members",
    "who are the members of this family": "View family members",
    "how can i see the members of the family": "View family members",
    "who are the members": "View family members",
    "show me the members of the family": "View family members",
    "can i see the members of the family": "View family members",
    "view owner" : "View family owner",
    "who owns this family": "View family owner",
    "who is the family owner": "View family owner",
    "view the owner of the family": "View family owner",
    "can i see the owner of the family": "View family owner",
    "who owns this family": "View family owner",
    "i dont know who owns the family": "View family owner",
    "why cant i find the owner of the family": "View family owner",
    "i need the owner": "View family owner",
    "family edit": "Edit family details",
    "edit family": "Edit family details",
    "edit family details": "Edit family details",
    "change family details": "Edit family details",
    "make new family details": "Edit family details",
    "i need to change family details": "Edit family details",
    "change family name": "Edit family details",
    "make announcement": "Make an announcement",
    "i need to announce something": "Make an announcement",
    "i need to say something to this family": "Make an announcement",
    "tell this family a message": "Make an announcement",
    "i need you to announce a message to the family": "Make an announcement",
    "tell the family a message": "Make an announcement",
    "i have an idea": "Make an announcement",
    "view announcement": "View the most recent announcement",
    "whats the announcement": "View the most recent announcement",
    "can i see the family announcement": "View the most recent announcement",
    "can i see the announcement": "View the most recent announcement",
    "what did the admin announce": "View the most recent announcement",
    "what did the owner announce": "View the most recent announcement",
    "can i see what the family announcement is": "View the most recent announcement",
    "i dont know what the owner or admin announced": "View the most recent announcement",
    "i neeed to see the most recent announcement from the family": "View the most recent announcement",
    "join code": "View the family joincode",
    "view join code": "View the family joincode",
    "view joincode of family": "View the family joincode",
    "whats the joincode": "View the family joincode",
    "whats the joincode of the family": "View the family joincode",
    "i need the joincode": "View the family joincode",
    "how can i see the join code of the family": "View the family joincode",
    "how can i see the joincode of the family": "View the family joincode",
    "view all announcements": "View all family announcements",
    "what are the announcements of this family": "View all family announcements",
    "can i see the family announcements": "View all family announcements",
    "view the announcements of the family": "View all family announcements",
    "i want to see all the announcements": "View all family announcements",
    "let me see all the announcements": "View all family announcements",
    "announcements are the best": "View all family announcements",
    "kick a user": "Kick a user from the family",
    "i need to kick someone from the family": "Kick a user from the family",
    "kick somebody from my family": "Kick a user from the family",
    "kick user from family": "Kick a user from the family",
    "remove user": "Kick a user from the family",
    "remove user from family": "Kick a user from the family",
    "get rid of user": "Kick a user from the family",
    "i hate a user": "Kick a user from the family",
    "get this person out the family": "Kick a user from the family",
    "get out of my family": "Kick a user from the family",
    "bye get out of my family": "Kick a user from the family",
    "view audit log": "View audit log",
    "whats the audit log of this family": "View audit log",
    "whats the action log of this family": "View audit log",
    "can i see the audit log": "View audit log",
    "can i see the action log": "View audit log",
    "who did tihs": "View audit log",
    "i dont know who did that": "View audit log",
    "i dont know who added that": "View audit log",
    "i dont know who removed that": "View audit log",
    "i dont know who edited that": "View audit log",
    "add item": "Add an item to the shopping list",
    "add item to list": "Add an item to the shopping list",
    "add item to shopping list": "Add an item to the shopping list",
    "add an item to the list": "Add an item to the shopping list",
    "add an item to the shop list": "Add an item to the shopping list",
    "how do i add an item to the shopping list": "Add an item to the shopping list",
    "i need to add an item to the list": "Add an item to the shopping list",
    "need to add something to the list": "Add an item to the shopping list",
    "oh i need to add that": "Add an item to the shopping list",
    "i need to take that off the list": "Remove an item from the shopping list",
    "remove item": "Remove an item from the shopping list",
    "remove item from shopping list": "Remove an item from the shopping list",
    "remove item from list": "Remove an item from the shopping list",
    "i need to remove that from the list": "Remove an item from the shopping list",
    "thats stupid why is it on the list": "Remove an item from the shopping list",
    "get that off the list": "Remove an item from the shopping list",
    "how do i remove an item from the list": "Remove an item from the shopping list",
    "how can i remove an item from the list": "Remove an item from the shopping list",
    "i need to change that": "Edit an item in the shopping list",
    "i need to change that item": "Edit an item in the shopping list",
    "change item": "Edit an item in the shopping list",
    "edit item": "Edit an item in the shopping list",
    "edit item on list": "Edit an item in the shopping list",
    "how do i edit an item": "Edit an item in the shopping list",
    "how do i edit an item on the list": "Edit an item in the shopping list",
    "i need to change an item on the list": "Edit an item in the shopping list",
    "i need to change that item": "Edit an item in the shopping list",
    "i need to change the item to something else": "Edit an item in the shopping list",
}

URL = "virtualshoppinglist.com"


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# ----------------- replying to a message ----------------- #



@views.route("/sms",methods=["POST"])
def sms_reply():
    sent = False
    external = False
    resp = MessagingResponse()
    users_number = request.values.get("From")
    content = request.values.get("Body")
    usr = User.query.filter_by(phone_number=users_number).first()
    rsp = ""

    if usr == None:
        rsp = "You currently do not have an account.\n\nTo create an account, please type create"
        sent = True

        if content.lower() == "create":
            if usr!= None:
                rsp = "You already have an account!"
                sent = True
            else:
                tz = timezone('EST')
                now = datetime.now(tz)
                month_num = now.strftime("%m")
                day = now.strftime("%d")
                year = now.strftime("%y")
                datetime_object = datetime.strptime(month_num, "%m")
                full_month_name = datetime_object.strftime("%B")
                usr = User(users_number,"",json.dumps([]),"creatingAccount",False,"None",json.dumps([]),f"{full_month_name}, {day}, {year}")
                db.session.add(usr)
                db.session.commit()
                rsp = "Please choose a name for your account!"
                sent = True
                usr.status = "chosenName"
                db.session.commit()
    else:

        # -------------- Functions for account not being created --------------
        if usr.status == "chosenName":
            createAccount(usr,content)
            external = True
        if usr.status == "confirmingName":
            createAccount(usr,content)
            external = True
        # -------------- Functions after account has been created --------------
        elif usr.fullAcc == True:

            if "Choosing a command" in usr.status:
                option_selected = content
                options_presented = usr.status.split("\n")
                op_found = False
                if option_selected == "0":
                    op_found = True
                    rsp = "Operation canceled."
                    sent = True
                    usr.status = ""
                    db.session.commit()
                for x in options_presented:
                    if f"Option #{option_selected}" in x:
                        op_found = True
                        index = options_presented.index(x)
                        operation = options_presented[index].split(": ")[1]
                        usr.status = ""
                        db.session.commit()
                        if operation == "Create a family":
                            content = "create"
                        elif operation == "View families":
                            content = "view"
                        elif operation == "Login to a family":
                            rsp = "Please enter the name of the family you would like to login to."
                            sent = True
                            usr.status = "chooseFamFromList"
                            db.session.commit()
                        elif operation == "Join a family":
                            content = "join"
                        elif operation == "Change account name":
                            content = "changename"
                        elif operation == "View shopping list":
                            content = "viewl"
                        elif operation == "Logout of family":
                            content = "logout"
                        elif operation == "View family admins":
                            content = "viewa"
                        elif operation == "View family members":
                            content = "viewm"
                        elif operation == "View family owner":
                            content = "viewo"
                        elif operation == "Edit family details":
                            content = "fedit"
                        elif operation == "Make an announcement":
                            content = "announce"
                        elif operation == "View the most recent announcement":
                            content = "viewann"
                        elif operation == "View the family joincode":
                            content = "joincode"
                        elif operation == "View all family announcements":
                            content = "viewannall"
                        elif operation == "Kick a user from the family":
                            rsp = "Please enter the phone number of the person you want to kick."
                            sent = True
                            usr.status = "kickingUser"
                            db.session.commit()
                        elif operation == "View audit log":
                            content = "viewaudit"
                        elif operation == "Add an item to the shopping list":
                            rsp = "Please enter the name of the item you would like to add to the shopping list."
                            sent = True
                            usr.status = "addingItemToList"
                            db.session.commit()
                        elif operation == "Remove an item from the shopping list":
                            rsp = "Please enter the name of the item you would like to remove from the shopping list."
                            sent = True
                            usr.status = "removingItemFromList"
                            db.session.commit()
                        elif operation == "Edit an item in the shopping list":
                            rsp = "Please enter the name of the item you would like to edit in the shopping list."
                            sent = True
                            usr.status = "listEditItem"
                            db.session.commit()
                if op_found == False:
                    rsp = "Sorry, that was not an option. Please try retyping the command you wished to execute."
                    sent = True
                    usr.status = ""
                    db.session.commit()

            elif usr.status == "addingItemToList":
                content = f"addi {content}"
           
            elif usr.status == "chooseFamFromList":
                content = f'login {content}'
            
            elif usr.status == "kickingUser":
                content = f"kick {content}"

            elif usr.status == "removingItemFromList":
                content = f"rmvi {content}"

            elif usr.status == "listEditItem":
                content = f"editi {content}"

            # ------------------- Creating a family -------------------
            if content.lower() == "create" or content.lower() ==  "createfamily" or content.lower() == "createfam" and usr.currentFam == "None":
                code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

                family = Family("TEMP",usr.phone_number,json.dumps([]),json.dumps([]),f"{code}",json.dumps([]),json.dumps([]),json.dumps([]),json.dumps([]))
                db.session.add(family)
                rsp = "Please choose a name for your new family!"
                sent = True
                usr.status = "choosingNameForFamily"
                db.session.commit()
                    
                    
            if usr.status == "choosingNameForFamily" and content.lower() != "create" and content.lower() !=  "createfamily" and content.lower() != "createfam" and content.lower()!="temp":
                createFamily(usr,content)
                external = True
            elif usr.status == "confirmingFamilyName" and content.lower() != "create" and content.lower() !=  "createfamily" and content.lower() != "createfam" and content.lower()!="temp":
                createFamily(usr,content)
                external = True
            
            # ------------------- Viewing a users famillies -------------------
            if content.lower() == "view" or content.lower() ==  "viewfamilies" or content.lower() == "viewFams" and usr.currentFam == "None":
                users_fams = json.loads(usr.families)

                built_str = "Your families: \n\n"
                i = 1
                for x in users_fams:
                    fam_name = x.split(":")[0]
                    built_str += f"{i}: {fam_name}\n"
                    i+=1
                rsp = built_str
                sent = True
                
            # ------------------- Logging into a family -------------------
            if content.split()[0].lower() == "login" :
                if usr.currentFam =="None":

                    loginToFam(usr,content)
                    external = True
                else:
                    rsp = "You cannot do this as you are currently already logged into a family."
                    sent = True
                    
                    
            elif usr.status == "loggingIntoFam":
                loginToFam(usr,content)
                external = True
            
            
            # ------------------- Joining into a family -------------------
            if content.split()[0].lower() == "join" or content.split()[0].lower() == "joinf" or content.split()[0].lower() == "joinfam" or content.split()[0].lower() == "joinfamily":
                rsp = "Please enter the joincode of the family you are trying to join. If you have already entered it, it could be incorrect please ensure it's correct and try again."
                sent = True
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
                        usrs_fams.append(f"{fam.name}")
                        usr.families = json.dumps(usrs_fams)
                        fam_member_list = json.loads(fam.members)
                        fam_member_list.append(usr.phone_number)
                        fam.members = json.dumps(fam_member_list)
                        usr.status = ""
                        rsp = f"You have now joined a family with the name {fam.name}!"
                        sent = True
                        db.session.commit()
                        famFound = True
                if famFound == False:
                    rsp = "Please enter the joincode of the family you are trying to join. If you have already entered it, it could be incorrect please ensure it's correct and try again."   
                    sent = True
            
            # ------------------- Family Commands -------------------
            if content.lower() == "cmds"  and usr.currentFam == "None":
                rsp = "View Families: Displays the families you are a part of\n\nCreate Family: Create a family\n\nJoin Family: Join a family\n\nChangename: Change the name of your account\n\nLogin (familyname): Logs your session into a specific family"
                sent = True
            elif content.lower() == "cmds" and usr.currentFam != "None":
                rsp = f"Commands of family: {usr.currentFam}\n\n View List (viewl): View the shopping list of this fmaily\n\nAdd Item (addi): Adds an item to the shopping list\n\nView Members (viewm): View the members of this family\n\nView Admins (viewa): View the admins of this family\n\nView owner (viewo): See who owns the family\n\nView Annoucements (viewann): View the announcements put out by admins and the owner.\n\nLogout: Logs out of this family.\n\nADMIN COMMMNANDS:\n\nRemove Item (rmvi): Removes an item from the shopping list\n\nEdit item (editi): Edit an item in the shopping list\n\n Kick: Kicks a member\n\nAnnounce: Create an announcement for the family\n\nAudit log (viewaudit): Views the audit log of administrative actions.\n\nOWNER COMMANDS:\n\nFamily edit (fedit): Edit things about the family such as the name, more features coming soon."  
                sent = True
            elif content.lower() == "changename":
                rsp = "Please reply with a new name for your account."
                sent = True
                usr.status = "changingName"
                db.session.commit()
            
            elif usr.status == "changingName":
                usr.name = content
                db.session.commit()
                rsp = f"You have changed your name to {content}!"
                sent = True
            
            if content.lower() == "viewl" or content.lower() == "viewlist":
                if usr.currentFam == "None":
                    rsp = "You must be logged into a family to execute this command."
                else:

                    for x in Family.query.all():
                            if x.name == usr.currentFam:
                                member_list = json.loads(x.members)
                                admin_list = json.loads(x.admins)
                                auth_list = json.loads(x.authed_members)
                                owner = x.owner
                                if usr.phone_number in auth_list:

                                    name = x.name.split(":")[0]
                                    rsp = f"You can view {name}'s list at the following link: http://{URL}/{x._id}/list"
                                    sent = True
                                else:
                                    if usr.phone_number in member_list or usr.phone_number in admin_list or usr.phone_number == owner:
                                        name = x.name.split(":")[0]
                                        rsp = f"You can view {name}'s list at the following link: http://{URL}/{x._id}/auth "
                                        sent = True

            elif content.lower() == "logout":
                if usr.currentFam == "None":
                    rsp = "You must be logged into a family to execute this command."
                else:         
                    rsp = f"You have succesfully logged out of your current family: {usr.currentFam}"
                    sent = True
                    usr.currentFam = "None"
                    db.session.commit()
                
            elif content.lower() == "viewm"  or content.lower() == "viewmembers":
                if usr.currentFam == "None":
                    rsp = "You must be logged into a family to execute this command."
                else:
                    fam_obj = Family.query.filter_by(name=usr.currentFam).first()
                    
                    fam_members = json.loads(fam_obj.members)
                    if len(fam_members) == 0:
                        rsp = "There are currently no members in the family."
                        sent = True
                    else:
                        built_str = f"Members of {fam_obj.name}\n\n"
                        for x in fam_members:
                            usr_obj = User.query.filter_by(phone_number=x).first()
                            built_str += f"{usr_obj.name}: {x}\n"
                            rsp = built_str
                            sent = True
            
            elif content.lower() == "viewa"  or content.lower() == "viewadmins":
                if usr.currentFam == "None":
                    rsp = "You must be logged into a family to execute this command."
                else:                
                    fam_obj = Family.query.filter_by(name=usr.currentFam).first()
                    
                    fam_members = json.loads(fam_obj.admins)
                    if len(fam_members) == 0:
                        rsp = "There are currently no admins in the family."
                        sent = True
                    else:
                        built_str = f"Members of {fam_obj.name}\n\n"
                        for x in fam_members:
                            usr_obj = User.query.filter_by(phone_number=x).first()
                            built_str += f"{usr_obj.name}: {x}\n"
                            rsp = built_str
                            sent = True
                        
            elif content.lower() == "viewo"  or content.lower() == "viewowner":
                if usr.currentFam == "None":
                    rsp = "You must be logged into a family to execute this command."
                else:             
                    fam_obj = Family.query.filter_by(name=usr.currentFam).first()
                    owner_obj = User.query.filter_by(phone_number=fam_obj.owner).first()
                    rsp = f"The owner of this is family is {owner_obj.name} ({fam_obj.owner})"
                    sent = True
            
            
            elif  content.lower() == "fedit":
                if usr.currentFam == "None":
                    rsp = "You must be logged into a family to execute this command."
                else:                 
                    fam_obj = Family.query.filter_by(name=usr.currentFam).first()
                    owner_obj = User.query.filter_by(phone_number=fam_obj.owner).first()
                    if usr.phone_number == owner_obj.phone_number:
                        rsp =  f"This feature is only available on the web editor. You can find the link to edit the family name here: {URL}/{fam_obj._id}/settings/change-name"
                        sent = True
                    else:
                        rsp = "You do not have permission to run this command."
                        sent = True
            


            
            elif content.lower() == "announce"  or content.lower() == "ann":
                if usr.currentFam == "None":
                    rsp = "You must be logged into a family to execute this command."
                else:             
                    fam_obj = Family.query.filter_by(name=usr.currentFam).first()
                    
                    admin_list = json.loads(fam_obj.admins)
                    
                    if usr.phone_number == fam_obj.owner or usr.phone_number in admin_list:
                        usr.status = "creatingAnn"
                        rsp = "Please reply with the message you wish to announce."
                        sent = True
                        db.session.commit()
                    else:
                        rsp = "You must be an admin or owner to announce something."
                        sent = True
            
            elif usr.status == "creatingAnn":
                fam_obj = Family.query.filter_by(name=usr.currentFam).first()
                ann = content
                ann_list = json.loads(fam_obj.announcements)
                tz = timezone('EST')
                now = datetime.now(tz)
                dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
                ann_list.insert(0,f"{dt_string}: {ann}")
                fam_obj.announcements = json.dumps(ann_list)
                usr.status = ""
                db.session.commit()
                rsp = f"Operation successful:\n\nUser: {usr.name}\n\nAction: Created announcement\n\nAnnouncement: {ann}"
                sent = True


            
            
            elif content.lower() == "viewann":
                if usr.currentFam == "None":
                    rsp = "You must be logged into a family to execute this command."
                else:              
                    fam_obj = Family.query.filter_by(name=usr.currentFam).first()
                    ann_list = json.loads(fam_obj.announcements)
                    rsp = f"Current annoucement:\n\n{ann_list[0]}\n\nIf you would like to view all announcements, please type viewannall"
                    sent = True
            
            
            elif content.lower() == "joincode":
                if usr.currentFam == "None":
                    rsp = "You must be logged into a family to execute this command."
                else:                 
                    fam_obj = Family.query.filter_by(name=usr.currentFam).first()
                    rsp = f"Joincode is {fam_obj.joincode}"
                    sent = True
            
            elif content.lower() == "viewannall":
                if usr.currentFam == "None":
                    rsp = "You must be logged into a family to execute this command."
                else:                
                    fam_obj = Family.query.filter_by(name=usr.currentFam).first()
                    ann_list = json.loads(fam_obj.announcements)
                    built_str = f"All announcements of {fam_obj.name}:\n\n"
                    for x in ann_list:
                        built_str +=f'{x}\n\n'
                    rsp = built_str
                    sent = True
            elif content.lower() == "announce changelog":
                if usr.phone_number == "+14075906008":
                    usr_count = 0
                    for user in User.query.all():
                        usr_count +=1
                        message = client.messages \
                        .create(
                            body=f"A new update for Virtual Shopping List has just come out! You can check it out at virtualshoppinglist.com/changelog",
                            from_="+13025642358",
                            to=user.phone_number
                        )
                    sent =True
                    rsp = f"Success! The update has been sent out to {usr_count} users."
                else:
                    sent = True
                    rsp = "You do not have permission to run this developer command."
            
            elif content.lower().split(" ")[0] == "kick":
                if usr.currentFam == "None":
                    rsp = "You must be logged into a family to execute this command."
                else:
                    
                    fam_obj = Family.query.filter_by(name=usr.currentFam).first()
                    admin_list = json.loads(fam_obj.admins)
                    member_list = json.loads(fam_obj.members)
                    item = content.lower().split("kick ")
                    item.pop(0)
                    usr_to_kick = item[0]
                    if usr.phone_number in admin_list or usr.phone_number == fam_obj.owner:
                        if usr_to_kick in member_list:
                            member_list.remove(usr_to_kick)
                            usr_to_kick_obj = User.query.filter_by(phone_number=usr_to_kick).first()
                            usrs_fams = json.loads(usr_to_kick_obj.families)
                            usrs_fams.remove(fam_obj.name)
                            if usr_to_kick_obj.currentFam == fam_obj.name:
                                usr_to_kick_obj.currentFam = "None"
                            usr_to_kick_obj.families = json.dumps(usrs_fams)
                            fam_obj.members = json.dumps(member_list)
                            db.session.commit()
                            rsp = f"Operation successful:\n\nUser: {usr.name}\n\nAction: Kicked a user\n\nUser kicked: {usr_to_kick_obj.name}"
                            sent = True
                        elif usr_to_kick in admin_list:
                            if usr.phone_number == fam_obj.owner:
                                admin_list.remove(usr_to_kick)
                                usr_to_kick_obj = User.query.filter_by(phone_number=usr_to_kick).first()
                                usrs_fams = json.loads(usr_to_kick_obj.families)
                                usrs_fams.remove(fam_obj.name)
                                if usr_to_kick_obj.currentFam == fam_obj.name:
                                    usr_to_kick_obj.currentFam = "None"
                                usr_to_kick_obj.families = json.dumps(usrs_fams)
                                fam_obj.admins = json.dumps(admin_list) 
                                db.session.commit()
                                rsp = f"Operation successful:\n\nUser: {usr.name}\n\nAction: Kicked a user\n\nUser kicked: {usr_to_kick_obj.name}"
                                sent = True
                            else:
                                rsp  = "You must be the owner to kick an admin."
                                sent = True
                        else:
                            rsp = "User not found."
                            sent = True
                    else:
                        rsp = "You do not have permission to kick someone from this family."
                        sent = True
            
            elif content.lower() == "viewaudit":
                if usr.currentFam == "None":
                    rsp = "You must be logged into a family to execute this command."
                else:            
                    fam_to_find = Family.query.filter_by(name=usr.currentFam).first()    
                    admin_list = json.loads(fam_to_find.admins)
                    auditLog = json.loads(fam_to_find.auditLog)
                    if usr.phone_number in admin_list or usr.phone_number == fam_to_find.owner:
                        built_str = f"Audit log of {fam_to_find.name}:\n\n"
                        for x in auditLog:
                            built_str += f"{x}\n\n"
                        rsp = built_str
                        sent = True
                    else:
                        rsp = "You do not have permission to run this command."
                        sent = True
            
            
            elif "editItem" in usr.status:
                new_name = content
                fam_to_find = usr.currentFam
                for x in json.loads(usr.families):
                    if x == fam_to_find:
                        fam_obj  =  Family.query.filter_by(name=x).first()
                        fam_list = json.loads(fam_obj.list)
                        item_id = usr.status.split("editItem")[1]
                        original_name = fam_list[int(item_id)-1].split(": ")[1]
                        audit_log = json.loads(fam_obj.auditLog)
                        tz = timezone('EST')
                        now = datetime.now(tz)
                        dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
                        audit_log.append(f"{dt_string}: {usr.name} edited {original_name}  to {new_name}")
                        fam_list[int(item_id)-1] = f"{item_id}: {new_name}: Previously edited by {usr.name} , they renamed this item to {new_name}. The previous name of this item was {original_name}: {dt_string}"
                        fam_obj.list = json.dumps(fam_list)
                        fam_obj.auditLog = json.dumps(audit_log)
                        usr.status = ""
                        db.session.commit()
                        sent = True
                        rsp = f"Operation Succesful\n\nUser: {usr.name}\n\nAction: Edited an item on the list: renamed {original_name} to {new_name} \n\nFamily: {fam_obj.name}"
                        

            if len(content.split(" ")) > 1:
                if content.lower().split(" ")[0] == "addi":

                    fam_to_find = usr.currentFam
                    if fam_to_find == "None":
                        rsp = "You must be logged in to a family to execute this command."
                        sent = True
                        usr.status = ""
                        db.session.commit()
                    else:
                        for x in json.loads(usr.families):

                            if x== fam_to_find:
                                
                                item = content.lower().split("addi ")
                                item.pop(0)

                                fam_obj = Family.query.filter_by(name=x).first()
                               
                                        
                                fam_list = json.loads(fam_obj.list)
                                audit_log = json.loads(fam_obj.auditLog)
                                tz = timezone('EST')
                                now = datetime.now(tz)
                                dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
                                fam_list.append(f"{len(fam_list) +1}: {item[0]}: Added by {usr.name}: {dt_string}")
                                audit_log.append(f"{dt_string}: {usr.name} added {item[0]} to the list")
                            

                                fam_name = x.split(":")[0]
                                rsp = f"Operation Succesful\n\nUser: {usr.name}\n\nAction: Added an item to the list: {item[0]} \n\nFamily: {fam_name}"
                                sent = True
                                fam_obj.list = json.dumps(fam_list)
                                fam_obj.auditLog = json.dumps(audit_log)
                                usr.status = ""
                                db.session.commit()

                elif content.lower().split(" ")[0] == "rmvi":
                    fam_to_find = usr.currentFam
                    if fam_to_find == "None":
                        rsp = "You must be logged in to a family to execute this command."
                        sent = True
                        usr.status = ""
                        db.session.commit()
                    else:
                        for x in json.loads(usr.families):
                            if x== fam_to_find:
                                item = content.lower().split("rmvi ")
                                item.pop(0)
                                fam_obj = Family.query.filter_by(name=x).first()
                                if usr.phone_number in json.loads(fam_obj.admins) or usr.phone_number == fam_obj.owner:
                                    fam_list = json.loads(fam_obj.list)
                                    audit_log = json.loads(fam_obj.auditLog)
                                    tz = timezone('EST')
                                    now = datetime.now(tz)
                                    fam_name = x.split(":")[0]
                                    
                                    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
                                    for x in fam_list:
                                        if x.split(": ")[1] == item[0]:
                                            fam_list.remove(x)
                                            audit_log.append(f"{dt_string}: {usr.name} removed {item[0]} from the list")
                                            fam_obj.list = json.dumps(fam_list)
                                            fam_obj.auditLog = json.dumps(audit_log)
                                            usr.status = ""
                                            db.session.commit()

                                            rsp = f"Operation Succesful\n\nUser: {usr.name}\n\nAction: Removed an item from the list: {item[0]} \n\nFamily: {fam_name}"
                                            sent = True
                                else:
                                    rsp = "You must be an admin or the owner of the family to run this command."
                                    sent = True
                
                elif content.lower().split(" ")[0] == "editi":                       
                    fam_to_find = usr.currentFam
                    if fam_to_find == "None":
                        rsp = "You must be logged in to a family to execute this command."
                        sent = True
                        usr.status = ""
                        db.session.commit()
                    else:
                        for x in json.loads(usr.families):
                            if x== fam_to_find:
                                item = content.lower().split("editi ")
                                item.pop(0)
                                fam_obj = Family.query.filter_by(name=x).first()
                                if usr.phone_number in json.loads(fam_obj.admins) or usr.phone_number == fam_obj.owner:
                                    fam_list = json.loads(fam_obj.list)
                                    audit_log = json.loads(fam_obj.auditLog)
                                    tz = timezone('EST')
                                    now = datetime.now(tz)
                                    fam_name = x.split(":")[0]
                                    
                                    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
                                    for x in fam_list:
                                        if x.split(": ")[1] == item[0]:
                                            usr.status = f"editItem{x.split(': ')[0]}"
                                            db.session.commit()
                                            rsp = "Please reply with the new name you would like this item to have."
                                            sent = True
     
                                else:
                                    rsp = "You must be an admin or the owner of the family to run this command."
                                    sent = True

    # ------------------------------- Cmd not found ---------------------------------------------
                else:
                    if usr.status == "" and sent == False and external == False:
                        i = 0
                        action_list = []
                        built_str = "Choosing a command :\n"
                        for x in aliases:
                            if similar(content.lower(),x) > 0.6:

                                action = aliases.get(x)
                                if action not in action_list:
                                    i+=1
                                    action_list.append(action)
                                    built_str += f"Option #{i}: {action}\n"

                        if len(action_list) == 0:
                            rsp = "Sorry, I don't understand what you are trying to say. Please try rephrasing your command or type cmds for help."
                        else:
                            usr.status = built_str
                            db.session.commit()
                            rsp = "Sorry, I didn't understand what you were trying to say. Please choose an option from below by replying with the number of the action you wish to do.\n\nOption #0: Cancel"
                            i=0
                            for y in action_list:
                                i+=1
                                rsp += f"\nOption #{i}: {y}"



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
                    usr.status = ""
            db.session.commit()
            
            
        elif content.lower() == "no":
            message = client.messages \
            .create(
                body=f"Okay, your family name has been reset to nothing, please respond to change your name.",
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
        entered_fam = content.lower().split("login ")
        if len(entered_fam) == 1:
            message = client.messages \
            .create(
                body=f"Please specify a family!",
                from_="+13025642358",
                to=usr.phone_number
            )
        else:
            entered_fam = content.lower().split("login ")[1]
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
def get_details(ip_address):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        js = response.json()
        return js
    except Exception as e:
        return e
    
@views.route('/')
def home():
    return render_template("home.html")

@views.route('/dashboard')
def dashboard():
    usr = User.query.filter_by(phone_number=session.get("phoneNumber")).first()
    if usr == None:
        return redirect("/")
    else:
        fam = "None"
        if usr.currentFam != "None":
            fam = Family.query.filter_by(name=usr.currentFam).first()
        ip_address = request.environ["HTTP_X_REAL_IP"]
        details = get_details(ip_address)
        country = details.get("country")
        region = details.get("regionName")
        city = details.get("city")
        timezone = details.get("timezone")
        num_of_fams = len(json.loads(usr.families))

        return render_template("dashboard.html",usr=usr,country=country,region=region,city=city,timezone=timezone,fam=fam,num_of_fams=num_of_fams)


@views.route('/switch-family')
def switchFamily():
    usr = User.query.filter_by(phone_number=session.get("phoneNumber")).first()
    if usr.currentFam == "None":
        return redirect("/dashboard")
    elif usr == None:
        return redirect("/")
    else:
        fam_list = []
        for x in json.loads(usr.families):
            fam_obj = Family.query.filter_by(name=x).first()
            fam_list.append(fam_obj)
        return render_template("switchFamily.html",usr=usr,fam_list=fam_list)

@views.route('/switch-family/<fam_id>')
def switchFamilyConfirm(fam_id):
    usr = User.query.filter_by(phone_number=session.get("phoneNumber")).first()
    fam = Family.query.filter_by(_id=fam_id).first()
    if fam == None or usr == None:
        return redirect("/")
    elif  usr.phone_number in json.loads(fam.admins) or usr.phone_number == fam.owner:
        usr.currentFam = fam.name
        db.session.commit()
        return redirect("/dashboard")
    else:
        return redirect("/dashboard")

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
                auth_list = json.loads(fam.authed_members)
                auth_list.append(usr.phone_number)
                fam.authed_members = json.dumps(auth_list)
                usr.currentFam = fam.name
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
        if  usr.phone_number in json.loads(fam.admins) or usr.phone_number == fam.owner:
           perms = True
           shoppingList = json.loads(fam.list)

           name = fam.name.split(":")[0]
           owner_details = User.query.filter_by(phone_number=fam.owner).first()
           return render_template("list.html",shopList=shoppingList,fam=fam,famName=name,owner=owner_details,perms=perms)
        
        if usr.phone_number in json.loads(fam.members): 
            perms = False
            owner_details = User.query.filter_by(phone_number=fam.owner).first()
            shoppingList = json.loads(fam.list)
            name = fam.name.split(":")[0]
            return render_template("list.html",perms=perms,fam=fam,owner=owner_details,shopList=shoppingList,famName=name)
        

 
        else:

            owner_details = User.query.filter_by(phone_number=fam.owner).first()
            return render_template("list.html",notValidated=True,owner=owner_details,fam=fam)


@views.route("/<id>/delete/<item_id>")
def delItem(id,item_id):
    fam = Family.query.filter_by(_id=id).first()
    usr = User.query.filter_by(phone_number=session.get("phoneNumber")).first()
    if fam == None or usr == None:
        return render_template("delItem.html",close=True)
    else:
        if  usr.phone_number in json.loads(fam.admins) or usr.phone_number == fam.owner:
            fam_list = json.loads(fam.list)
            audit_log = json.loads(fam.auditLog)
            tz = timezone('EST')
            now = datetime.now(tz)
            dt_string = now.strftime("%m/%d/%Y %H:%M:%S")

            index = int(item_id) -1
            audit_log.append(f"{dt_string}: {usr.name} removed {fam_list[index].split(': ')[1]} from the list")
            fam_list.remove(fam_list[index])

            temp_list = []
            for x in fam_list:
                i=0
                built_str = ""
                sep_string = x.split(": ")
                sep_string[0] = int(sep_string[0]) -1
                for word in sep_string:
                    if i == 3:
                        built_str += f"{word}"
                    else:
                        built_str += f"{word}: "
                        i+=1
                temp_list.append(built_str)
            fam.list = json.dumps(temp_list)
            fam.auditLog = json.dumps(audit_log)
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
        audit_log = json.loads(fam.auditLog)
        tz = timezone('EST')
        now = datetime.now(tz)
        dt_string = now.strftime("%m/%d/%Y %H:%M:%S")


        index = int(item_id) -1
        item = fam_list[index]
        split_item = item.split(": ")
        fam_list[index] = f"{item_id}: {new_name}: Previously edited by {usr.name} , they renamed this item to {new_name}. The previous name of this item was {split_item[1]} : {dt_string}"
        audit_log.append(f"{dt_string}: {usr.name} edited {split_item[1]} to {new_name}")
        fam.list = json.dumps(fam_list)
        fam.auditLog = json.dumps(audit_log)

        db.session.commit()
        return redirect(f"/{id}/list")


@views.route('/<id>/settings',methods=['POST','GET'])
def settings(id):
    fam = Family.query.filter_by(_id=id).first()
    usr = User.query.filter_by(phone_number=session.get("phoneNumber")).first()
    if request.method == "GET":
        if fam == None or usr == None:
            return redirect(f'/{fam._id}/list')
        else:
            owner = False
            admin = False
            if usr.phone_number == fam.owner:
                owner = True
            elif usr.phone_number in json.loads(fam.admins):
                admin = True
            return render_template("settings.html",fam=fam,owner=owner,admin=admin)
    elif request.method == "POST":
        for user in json.loads(fam.admins):
            usr_obj = User.query.filter_by(phone_number=user).first()
            fam_list = json.loads(usr_obj.families)
            for family in fam_list:
                if family == fam.name:
                    fam_list.remove(family)
                    usr_obj.families = json.dumps(fam_list)
                    usr_obj.currentFam = f"None"
                    db.session.commit()
                    
                    
        for user in json.loads(fam.members):
            usr_obj = User.query.filter_by(phone_number=user).first()
            fam_list = json.loads(usr_obj.families)
            for family in fam_list:
                if family == fam.name:
                    fam_list.remove(family)
                    usr_obj.families = json.dumps(fam_list)
                    usr_obj.currentFam = f"None"
                    db.session.commit()
                    
        owner_fam_list = json.loads(usr.families)
        for family in owner_fam_list:   
            if family == fam.name:
                owner_fam_list.remove(family)
                usr.families = json.dumps(owner_fam_list)
                usr.currentFam = f"None"
                db.session.commit()
        db.session.delete(fam)
        db.session.commit()
        return redirect('/')

@views.route('/<id>/settings/change-name',methods=["POST","GET"])
def change_name(id):
    fam = Family.query.filter_by(_id=id).first()
    usr = User.query.filter_by(phone_number=session.get("phoneNumber")).first()
    if request.method == "GET":
        if fam == None or usr == None:
            return redirect(f'/{fam._id}/list')
        else:
            if usr.phone_number == fam.owner:
                return render_template('changeName.html',fam=fam)
            else:
                return redirect(f'/{fam._id}/list')
    elif request.method == "POST":
        new_name = request.form.get("newname")
        name = fam.name.split(":")
        for user in json.loads(fam.admins):
            usr_obj = User.query.filter_by(phone_number=user).first()
            fam_list = json.loads(usr_obj.families)
            for family in fam_list:
                if family == fam.name:
                    index = fam_list.index(fam.name)
                    fam_list[index] = f"{new_name}:owned by {fam.owner}"
                    usr_obj.families = json.dumps(fam_list)
                    usr_obj.currentFam = f"{new_name}:owned by {fam.owner}"
                    db.session.commit()
                    
                    
        for user in json.loads(fam.members):
            usr_obj = User.query.filter_by(phone_number=user).first()
            fam_list = json.loads(usr_obj.families)
            for family in fam_list:
                if family == fam.name:
                    index = fam_list.index(fam.name)
                    fam_list[index] = f"{new_name}:owned by {fam.owner}"
                    usr_obj.families = json.dumps(fam_list)
                    usr_obj.currentFam = f"{new_name}:owned by {fam.owner}"
                    db.session.commit()
        
        owner_fam_list = json.loads(usr.families)
        for family in owner_fam_list:   
            if family == fam.name:
                
                index = owner_fam_list.index(fam.name)
                owner_fam_list[index] = f"{new_name}:owned by {fam.owner}"
                usr.families = json.dumps(owner_fam_list)
                usr.currentFam = f"{new_name}:owned by {fam.owner}"
                
                db.session.commit()

        
        name.pop(0)

        name.insert(0,new_name)
        built_str = f"{name[0]}:{name[1]}"
        fam.name = built_str

            
        db.session.commit()
        return redirect(f"/{id}/settings")

@views.route('/<id>/settings/manage-admins',methods=["POST","GET"])
def manageAdmins(id):
    fam = Family.query.filter_by(_id=id).first()
    usr = User.query.filter_by(phone_number=session.get("phoneNumber")).first()
    if request.method == "GET":
        if fam == None or usr == None:
            return redirect(f'/{fam._id}/list')
        else:
            if usr.phone_number == fam.owner:
                admin_list = json.loads(fam.admins)
                obj_list = []
                for x in admin_list:
                    admin  = User.query.filter_by(phone_number=x).first()
                    obj_list.append(admin)
                return render_template('manageAdmins.html',fam=fam,adminList=obj_list)
            else:
                return redirect(f'/{fam._id}/list')
    
    elif request.method == "POST":
        adminnumber = request.form.get("adminnumber")
        admin_list = json.loads(fam.admins)
        admin_list.remove(adminnumber)
        fam.admins = json.dumps(admin_list)
        db.session.commit()
        return redirect(f'/{fam._id}/settings/manage-admins')
    
@views.route('/<id>/settings/manage-admins/add',methods=["POST","GET"])
def addAdmin(id):
    fam = Family.query.filter_by(_id=id).first()
    usr = User.query.filter_by(phone_number=session.get("phoneNumber")).first()
    if request.method == "GET":
        if fam == None or usr == None:
            return redirect(f'/{fam._id}/list')
        else:
            if usr.phone_number == fam.owner:
                admin_list = json.loads(fam.admins)
                return render_template('addAdmin.html',fam=fam,adminList=admin_list)
            else:
                return redirect(f'/{fam._id}/list')

    elif request.method == "POST":
        new_admin = "+1" + request.form.get("newadmin")
        admin_list = json.loads(fam.admins)
        if new_admin in admin_list:
            pass
        else:
            admin_list.append(new_admin)
            fam.admins = json.dumps(admin_list)
            db.session.commit()
        return redirect(f'/{fam._id}/settings/manage-admins')



@views.route('/<id>/settings/manage-members',methods=["POST","GET"])
def manageMembers(id):
    
    fam = Family.query.filter_by(_id=id).first()

    usr = User.query.filter_by(phone_number=session.get("phoneNumber")).first()
    if request.method == "GET":
        if fam == None or usr == None:
            return redirect(f'/{fam._id}/list')
        else:
            if usr.phone_number == fam.owner or usr.phone_number in json.loads(fam.admins):
                member_list = json.loads(fam.members)
                obj_list = []
                for x in member_list:
                    member  = User.query.filter_by(phone_number=x).first()
                    obj_list.append(member)
                return render_template("manageMembers.html",fam=fam,memberList=obj_list)
    elif request.method == "POST":

        member = request.form.get("membernumber")

        member_list = json.loads(fam.members)
        usr_to_remove = User.query.filter_by(phone_number=member).first()
        usrs_families = json.loads(usr_to_remove.families)

        usrs_families.remove(fam.name)
        usr_to_remove.famiies  = json.dumps(usrs_families)
        usr_to_remove.currentFam = "None"
        member_list.remove(member)
        fam.members = json.dumps(member_list)
        db.session.commit()
        return redirect(f'/{fam._id}/settings/manage-members')
    
    
@views.route('/<id>/settings/logs',methods=["POST","GET"])
def viewLogs(id):
    
    fam = Family.query.filter_by(_id=id).first()

    usr = User.query.filter_by(phone_number=session.get("phoneNumber")).first()
    if request.method == "GET":
        if fam == None or usr == None:
            return redirect(f'/{fam._id}/list')
        else:
            if usr.phone_number == fam.owner or usr.phone_number in json.loads(fam.admins):
                audit_log = json.loads(fam.auditLog)
                return render_template("logs.html",auditLog=audit_log,fam=fam)
            
@views.route("/<id>/add",methods=['GET',"POST"])
def addItem(id):
    fam = Family.query.filter_by(_id=id).first()
    usr = User.query.filter_by(phone_number=session.get("phoneNumber")).first()
    if request.method == "GET":
        if fam == None or usr == None:
            return render_template("home.html")
        else:
            if usr.phone_number in json.loads(fam.members) or usr.phone_number in json.loads(fam.admins) or usr.phone_number == fam.owner:
                return render_template("addItem.html")
    elif request.method == "POST":
        item_name = request.form.get("newname")
        fam_list = json.loads(fam.list)
        audit_log = json.loads(fam.auditLog)     
        tz = timezone('EST')  
        now = datetime.now(tz)
        dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
        fam_list.append(f"{len(fam_list) +1}: {item_name}: Added by {usr.name}: {dt_string}")


        audit_log.append(f"{dt_string}: {usr.name} added {item_name} to the list") 
        fam.list = json.dumps(fam_list)
        fam.auditLog = json.dumps(audit_log)
        db.session.commit()
        return redirect(f'/{fam._id}/list')  
    
@views.route("/changelog",methods=["GET","POST"])
def changelog():
    if request.method == "GET":
        return render_template("changelog.html")
    
@views.route("/changelog/<id>",methods=["GET","POST"])
def viewChangelog(id):
    if request.method == "GET":
        return render_template(f"changelog{id}.html")
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
    tz = timezone('EST')
    now = datetime.now(tz)
    month_num = now.strftime("%m")
    day = now.strftime("%d")
    year = now.strftime("%y")
    datetime_object = datetime.strptime(month_num, "%m")
    full_month_name = datetime_object.strftime("%B")
    usr = User("+14075906008","Carter",json.dumps(["Carter's default family"]),"",True,"",json.dumps([]),f"{full_month_name}, {day}, {year}")
    db.session.add(usr)
    db.session.commit()
    return "default user has been created"

def createTestFam():
    code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    family = Family("TESTFAMILY","4071111111",json.dumps([]),json.dumps([]),f"{code}",json.dumps([]),json.dumps([]),json.dumps([]),json.dumps([]))
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
    family = Family("TESTFAMILY","4071111111",json.dumps([]),json.dumps([]),f"{code}",json.dumps([]),json.dumps([]),json.dumps([]))
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



# --------------------------------- END OF SMS FUNCTIONS ---------------------------------
