# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin
from sqlalchemy import Column, Integer, String

from app import db, login_manager

from app.base.util import hash_pass

class User(db.Model, UserMixin):

    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass( value ) # we need bytes here (not plain str)
                
            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)
class Project(db.Model,UserMixin):
    __tablename__='Project'
    ProjectID=Column(String, primary_key=True)
    ProjectTitle=Column(String)
    PrincipalInvestigator=Column(String)
    Budget=Column(String)
    Area=Column(String)
    StartDate=Column(String)
    EndDate=Column(String)
    def __init__(self,ProjectID,ProjectTitle,PrincipalInvestigator,Budget,EndDate,StartDate,Area):
        self.ProjectID=ProjectID
        self.ProjectTitle=ProjectTitle
        self.PrincipalInvestigator=PrincipalInvestigator
        self.Budget=Budget
        self.EndDate=EndDate
        self.StartDate=StartDate
        self.Area=Area
        
class Employee(db.Model,UserMixin):
    __tablename__='Employee'
    ECNo=Column(String, primary_key=True)
    EmployeeName=Column(String)
    Gender=Column(String)
    Designation=Column(String)
    FunctionalDesignation=Column(String)
    Area=Column(String)
    Group=Column(String)
    Division=Column(String)
    Qualification=Column(String)
class Team(db.Model, UserMixin):
    __tablename__='Team'
    ProjectID=Column(String, primary_key=True)
    EmployeeName=Column(String,primary_key=True)
    def __init__(self,ProjectID,EmployeeName):
        self.ProjectID=ProjectID
        self.EmployeeName=EmployeeName
class MileStones(db.Model,UserMixin):
    __tablename__='MileStones'
    ProjectID=Column(String, primary_key=True)
    Milestone=Column(String, primary_key=True)
    MilestoneDate=Column(String)
    def __init__(self,ProjectID,MileStone,MilestoneDate):
        self.ProjectID=ProjectID
        self.Milestone=MileStone
        self.MilestoneDate=MilestoneDate
@login_manager.user_loader
def user_loader(id):
    return User.query.filter_by(id=id).first()

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    return user if user else None
