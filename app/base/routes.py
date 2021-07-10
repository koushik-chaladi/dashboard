# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import jsonify, render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)

from app import db, login_manager
from app.base import blueprint
from app.base.forms import LoginForm, CreateAccountForm
from app.base.models import User
from app.base.models import Project
from app.base.models import Team
from app.base.models import Employee
from app.base.models import MileStones
from app.base.util import verify_pass
from sqlalchemy import create_engine
from sqlalchemy import desc
import time
from flask_mail import Mail,Message
from sqlalchemy import and_


engine = create_engine('sqlite:///db.sqlite3')
@blueprint.route('/')
def route_default():
    return redirect(url_for('base_blueprint.login'))

## Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:
        
        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = User.query.filter_by(username=username).first()
        
        # Check the password
        if user and verify_pass( password, user.password):

            login_user(user)
            return redirect(url_for('base_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template( 'accounts/login.html', msg='Wrong user or password', form=login_form)

    if not current_user.is_authenticated:
        return render_template( 'accounts/login.html',
                                form=login_form)
    return redirect(url_for('home_blueprint.index'))

@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    login_form = LoginForm(request.form)
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username  = request.form['username']
        email     = request.form['email'   ]

        # Check usename exists
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template( 'accounts/register.html', 
                                    msg='Username already registered',
                                    success=False,
                                    form=create_account_form)

        # Check email exists
        user = User.query.filter_by(email=email).first()
        if user:
            return render_template( 'accounts/register.html', 
                                    msg='Email already registered', 
                                    success=False,
                                    form=create_account_form)

        # else we can create the user
        user = User(**request.form)
        db.session.add(user)
        db.session.commit()

        return render_template( 'accounts/register.html', 
                                msg='User created please <a href="/login">login</a>', 
                                success=True,
                                form=create_account_form)

    else:
        return render_template( 'accounts/register.html', form=create_account_form)

@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('base_blueprint.login'))

@blueprint.route('/empPopulate', methods=['GET', 'POST'])
def empPopulate():
    conn=engine.connect()
    employee=conn.execute("Select *from Employee")
    return render_template("project_2.html", employee=employee)
@blueprint.route('/addproject',methods=['GET', 'POST'])
def addproject():
    ProjectID=time.time()
    ProjectTitle=request.form['Project Title']
    ProjectInvestigator=request.form['Principal Investigator']
    ProjectTeam=[]
    ProjectTeam.append(request.form['mem1'])
    ProjectTeam.append(request.form['mem2'])
    ProjectTeam.append(request.form['mem3'])
    Milestone1=request.form['Milestone1']
    Miledate1=request.form['Miledate1']
    Budget=request.form['budget']
    EndDate=request.form['end']
    project=Project(ProjectID, ProjectTitle, ProjectInvestigator, Budget, EndDate)
    db.session.add(project)
    db.session.commit()
    for i in ProjectTeam:
        team=Team(ProjectID, i)
        db.session.add(team)
        db.session.commit()
    print(ProjectTitle)
    return render_template('/profile.html')

@blueprint.route('/addnew',methods=['GET', 'POST'])
def addnew():
    ProjectID=time.time()
    ProjectTitle=request.form['Project Title']
    ProjectInvestigator=request.form['Principal Investigator']
    ProjectTeam=request.form.getlist('addmore[]')
    Budget=request.form['budget']
    EndDate=request.form['EndDate']
    StartDate=request.form['StartDate']
    Area=request.form['Area']
    project=Project(ProjectID, ProjectTitle, ProjectInvestigator, Budget, EndDate, StartDate, Area)
    db.session.add(project)
    db.session.commit()
    print(ProjectTeam)
    for i in ProjectTeam[:-1]:
        team=Team(ProjectID, i)
        db.session.add(team)
        db.session.commit()
    MileStone=request.form.getlist('addmile[]')
    print(MileStone)
    MileDate=request.form.getlist('adddate[]')
    for i in range(len(MileStone)-1):
        mile=MileStones(ProjectID,MileStone[i],MileDate[i])
        db.session.add(mile)
        db.session.commit()
    print(ProjectTitle)
    return render_template('/profile.html')

@blueprint.route('/email',methods=['GET', 'POST'])
def email():
	return render_template("email.html")

@blueprint.route('/emailconfirm',methods=["POST"])
def emailconfirm():
        #emailbody=request.form.get("emailbody")
        #msg = Message(emailsubject,sender ='sender',recipients = ['reciever'])  #sender and receiver email
        #msg.body = emailbody
        #mail.send(msg)
        return render_template('email.html',data="Mail Sent Sucessfully")
@blueprint.route('/queryReport',methods=["GET","POST"])
def queryReport():
    conn=engine.connect()
    report=Project.query.filter_by()
    team=list(conn.execute("select *from team"))
    milestone=list(conn.execute("select *from milestones"))
    return render_template('table_4.html',data=report,team=team,milestone=milestone)
@blueprint.route('sortReport',methods=["GET", "POST"])
def sortReport():
    k=request.form["column"]
    order=request.form["order"]
    upper=request.form["upper"]
    lower=request.form["lower"]
    dupper=request.form["udate"]
    dlower=request.form["ldate"]
    conn=engine.connect()
    if k=="Budget":
        if upper!="" and lower!="":
            if order=="Asc":
                report=Project.query.filter(and_(Project.Budget>=int(lower),Project.Budget<=int(upper))).order_by(k)
            else:
                report=Project.query.filter(and_(Project.Budget>=int(lower),Project.Budget<=int(upper))).order_by(desc(k))
        elif upper!="":
            if order=="Asc":
                report=Project.query.filter(Project.Budget<=int(upper)).order_by(k)
            else:
                report=Project.query.filter(Project.Budget<=int(upper)).order_by(desc(k))
        elif lower!="":
            if order=="Asc":
                report=Project.query.filter(Project.Budget>=int(lower)).order_by(k)
            else:
                report=Project.query.filter(Project.Budget>=int(lower)).order_by(desc(k))
        else:
            if order=="Asc":
                report=Project.query.filter_by().order_by(k)
            else:
                report=Project.query.filter_by().order_by(desc(k))
    elif k=="ProjectTitle":
        if order=="Asc":
            report=Project.query.filter_by().order_by(k)
        else:
            report=Project.query.filter_by().order_by(desc(k))
    elif k=="EndDate":
        if dupper!="" and dlower!="":
            if order=="Asc":
                report=Project.query.filter(and_(Project.EndDate>=(dlower),Project.EndDate<=(dlower))).order_by(k)
            else:
                report=Project.query.filter(and_(Project.EndDate>=(lower),Project.EndDate<=(upper))).order_by(desc(k))
        elif dupper!="":
            if order=="Asc":
                report=Project.query.filter(Project.EndDate<=(dupper)).order_by(k)
            else:
                report=Project.query.filter(Project.EndDate<=(dupper)).order_by(desc(k))
        elif dlower!="":
            if order=="Asc":
                report=Project.query.filter(Project.EndDate>=(dlower)).order_by(k)
            else:
                report=Project.query.filter(Project.EndDate>=(dlower)).order_by(desc(k))
        else:
            if order=="Asc":
                report=Project.query.filter_by().order_by(k)
            else:
                report=Project.query.filter_by().order_by(desc(k))
    team=list(conn.execute("select *from team"))
    milestone=list(conn.execute("select *from milestones"))
    return render_template("table_4.html", data=report, team=team, milestone=milestone,k=k,order=order,upper=upper,lower=lower)
@blueprint.route('/table')
def table():
    return render_template('/profile.html')
## Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('page-403.html'), 403

@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('page-403.html'), 403

@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('page-404.html'), 404

@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('page-500.html'), 500
