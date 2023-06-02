from operator import inv

from . import db
from sqlalchemy.sql import func


class User(db.Model):
    _id =  db.Column(db.Integer,primary_key = True)
    phone_number = db.Column(db.String(500))
    name = db.Column(db.String(500))
    families = db.Column(db.String(5000))
    status = db.Column(db.String(500))
    fullAcc = db.Column(db.Boolean, default=False, nullable=False)
    inCmd = db.Column(db.Boolean, default=False, nullable=False)
    currentFam = db.Column(db.String(500))
    selfSearchResults = db.Column(db.String(5000))
    created_on = db.Column(db.String(500))
    
    def __init__(self,phone_number,name,families,status,fullAcc,currentFam,selfSearchResults,created_on):
        self.phone_number = phone_number
        self.name = name
        self.families = families
        self.status = status
        self.fullAcc =fullAcc
        self.currentFam = currentFam
        self.famSearchResults = selfSearchResults
        self.created_on = created_on



class Family(db.Model):
    _id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(500))
    owner = db.Column(db.String(100))
    admins = db.Column(db.String(5000))
    members = db.Column(db.String(5000))
    joincode = db.Column(db.String(100))
    list = db.Column(db.String(10000))
    auditLog = db.Column(db.String(10000))
    authed_members = db.Column(db.String(10000))
    announcements = db.Column(db.String(10000))


    
    def __init__(self,name,owner,admins,members,joincode,list,auditLog,authed_members,announcements):
        self.name = name
        self.owner = owner
        self.admins = admins
        self.members = members
        self.joincode = joincode
        self.list = list
        self.auditLog = auditLog
        self.authed_members = authed_members
        self.announcements = announcements