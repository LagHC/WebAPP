from flask import request, current_app, flash, redirect, render_template, url_for, jsonify
from flask_login import login_required, login_user, logout_user
import sys, urllib

import os
from . import auth
from .forms import LoginForm, RegistrationForm
from .. import db
from ..models import User
from datetime import datetime, timedelta

from oauthclient.oauth2api import oauth2api
from oauthclient.credentialutil import credentialutil
from oauthclient.model.model import environment

import app

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle requests to the /register route
    Add an employee to the database through the registration form
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,username=form.username.data,first_name=form.first_name.data,last_name=form.last_name.data,password=form.password.data)
        # add employee to the database
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered! You may now login.')

    # redirect to the login page
        return redirect(url_for('auth.login'))

    # load registration template
    return render_template('auth/register.html', form=form, title='Register')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle requests to the /login route
    Log an employee in through the login form
    """
    form = LoginForm()
    if form.validate_on_submit():

        # check whether employee exists in the database and whether
        # the password entered matches the password in the database
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(
                form.password.data):
            # log employee in
            login_user(user)

            # redirect to the dashboard page after login
            if user.is_admin:
                return redirect(url_for('home.admin_dashboard'))
            else:
                return redirect(url_for('home.dashboard'))

        # when login details are incorrect
        else:
            flash('Invalid email or password.')

    # load login template
    return render_template('auth/login.html', form=form, title='Login')

@auth.route('/logout')
@login_required
def logout():
    """
    Handle requests to the /logout route
    Log an employee out through the logout link
    """
    logout_user()
    flash('You have successfully been logged out.')

    # redirect to the login page
    return redirect(url_for('auth.login'))

@auth.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', title='Profile')

@auth.route('/ebay')
@login_required
def ebay():
    app_config_path = current_app.config['EBAY_CONFIG_LOC']
    credentialutil.load(app_config_path)
    oauth2api_inst = oauth2api()
    signin_url = oauth2api_inst.generate_user_authorization_url(environment.SANDBOX, current_app.config['EBAY_SCOPES'])
    return redirect(signin_url)

@auth.route('/authenticate')
@login_required
def authenticate():
    decoded_code=[]
    code = request.args.get('code')
    expires_in = request.args.get('expires_in')
    current_date = datetime.now()
    expire_time = datetime.now()+timedelta(seconds=int(expires_in))
    if code:
        decoded_code = urllib.parse.unquote(code)
    return {
        'code':str(code),
        'current date':current_date,
        'expire_date':expire_time
        }

    