# app/admin/views.py

from flask import current_app, abort, request, flash, redirect, render_template, url_for, session, jsonify
from flask_login import current_user, login_required
from flask_modals import render_template_modal, response
from werkzeug.utils import secure_filename
from datetime import datetime
from PIL import Image
import discogs_client
from thefuzz import fuzz

import uuid
import os
from . import admin
from .forms import ItemTypeForm, VinylForm
from .. import db
from ..models import item_type, item_info, item, tblVinyls, item_images
import sys

def allowed_file(filename):
    return '.' in filename and \
           os.path.splitext(filename)[1].replace('.','') in current_app.config['ALLOWED_EXTENSIONS']

def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.is_admin:
        abort(403)

def check_mod():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.is_mod:
        abort(403)

@admin.route('/itemtypes', methods=['GET', 'POST'])
@login_required
def add_item_type(id=None):
    """
    Add a item_type to the database
    """
    check_admin()
    #TODO: !important Fix refresh after form submission
    #TODO: Make edit form a modal
    flag = session.pop('flag', False)
    add_item_type = True
    form = ItemTypeForm()
    if form.validate_on_submit() and id==None:
        itemtype = item_type(name=form.name.data)
        itemtype.user_id = current_user.get_id()
        itemtype.entry_date = datetime.now()
        try:
            # add item type to the database
            db.session.add(itemtype)
            db.session.commit()
            flash('You have successfully added a new item type.')
        except:
            # in case item type name already exists
            flash('Error: Item type already exists.')
        session['flag'] = True
        # redirect to item types page
        return redirect(url_for('admin.add_item_type'))

    # load item types template
    modal = None if flag else 'modal-form'
    return render_template_modal('admin/itemtypes/itemtypes.html', action="Add",
                           add_item_type=add_item_type, form=form,
                           title="Add Item Type", modal=modal)

@admin.route('/itemtypes/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_item_type(id):
    """
    Edit a item type
    """
    check_admin()

    add_item_type = False

    itemtype = item_type.query.get_or_404(id)
    form = ItemTypeForm(obj=itemtype)
    if form.validate_on_submit():
        itemtype.name = form.name.data
        itemtype.edit_date = datetime.now()
        itemtype.edit_user_id = current_user.get_id()
        db.session.commit()
        flash('You have successfully edited the item type.')

        # redirect to the item types page
        return redirect(url_for('admin.add_item_type'))

    form.name.data = itemtype.name
    return render_template_modal('admin/itemtypes/itemtype.html', action="Edit",
                           add_item_type=add_item_type, form2=form,
                           itemtype=itemtype, title="Edit Item Type")

#TODO: Add multi-delete from selection (take in args with request args and then iterate though and delete each)
@admin.route('/itemtypes/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_item_type(id):
    """
    Delete a itemtype from the database
    """
    check_admin()

    itemtype = item_type.query.get_or_404(id)
    db.session.delete(itemtype)
    db.session.commit()
    flash('You have successfully deleted the item type.')

    # redirect to the item types page
    return redirect(url_for('admin.add_item_type'))

    return render_template(title="Delete Item Type")


@admin.route('/items/vinyls', methods=['GET', 'POST'])
@login_required
def add_vinyls():
    check_admin()

    form = VinylForm()
 
    if form.validate_on_submit():
        submit_time = datetime.now()
        filenames = []
        i = 1
        for pic in form.Pictures.data:
            if allowed_file(pic.filename):
                ext = os.path.splitext(pic.filename)[1]
                filename = form.Catno.data + '-' + str(submit_time.strftime("%Y_%m_%d-%I_%M_%S_%p")) + '-' + str(i) + ext
                filename = filename.replace(" ","")
                file_location = os.path.join(current_app.config['IMAGE_UPLOAD_PATH'],filename)
                thumbnail = form.Catno.data + '-' + str(submit_time.strftime("%Y_%m_%d-%I_%M_%S_%p")) + '-' + str(i) + ext
                thumbnail = thumbnail.replace(" ","")
                thumbnail_location = os.path.join(current_app.config['THUMBNAIL_UPLOAD_PATH'],thumbnail)
                pic.save(file_location)
                pic = Image.open(file_location)
                pic.thumbnail((120,120), Image.ANTIALIAS)
                pic.save(thumbnail_location)
                filenames.append(filename)
                i=i+1
        items = item(item_type_id=141,user_id=current_user.get_id(),entry_time=submit_time)
        item_infos = item_info(Comments=form.Comments.data,Price=form.Price.data)
        vinyl = tblVinyls(Catno=form.Catno.data,Artist=form.Artist.data,Album=form.Album.data,Sleeve_Grade=form.Sleeve_Grade.data,Record_Grade=form.Record_Grade.data) 
        try:
            item_infos.vinyl_info = vinyl
            items.info = item_infos
            for filename in filenames:
                image = item_images(file_name = filename)
                items.images.append(image)
            print('Output:'+str(items.info), file=sys.stderr)
            db.session.add(items)
            db.session.commit()
            flash('You have successfully added the item.')
        except Exception as e:
            # in case item type name already exists
            print(e, file=sys.stderr)
        return redirect(url_for('admin.add_vinyls'))

    # load item types template
    return render_template_modal('admin/items/Vinyls/items.html', action="Add",
                           add_item_type=add_item_type, form=form,
                           title="Add Item Type", modal='modal-form')

@admin.route('/items/vinyls/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_item_vinyl(id):
    """
    Edit a vinyl entry type
    """
    check_admin()

    add_item_type = False

    form = VinylForm()
    entry = item.query.get_or_404(id)

    if request.method == 'GET':
        form.Catno.data = entry.info.vinyl_info.Catno
        form.Artist.data = entry.info.vinyl_info.Artist
        form.Album.data = entry.info.vinyl_info.Album
        form.Sleeve_Grade.data = entry.info.vinyl_info.Sleeve_Grade
        form.Record_Grade.data = entry.info.vinyl_info.Record_Grade
        form.Comments.data = entry.info.Comments
        form.Price.data = entry.info.Price
    if form.validate_on_submit():
        submit_time = datetime.now()
        filenames = []
        i = 1
        for pic in form.Pictures.data:
            if allowed_file(pic.filename):
                ext = os.path.splitext(pic.filename)[1]
                filename = form.Catno.data + '-' + str(submit_time.strftime("%Y_%m_%d-%I_%M_%S_%p")) + '-' + str(i) + ext
                filename = filename.replace(" ","")
                file_location = os.path.join(current_app.config['IMAGE_UPLOAD_PATH'],filename)
                thumbnail = form.Catno.data + '-' + str(submit_time.strftime("%Y_%m_%d-%I_%M_%S_%p")) + '-' + str(i) + ext
                thumbnail = thumbnail.replace(" ","")
                thumbnail_location = os.path.join(current_app.config['THUMBNAIL_UPLOAD_PATH'],thumbnail)
                pic.save(file_location)
                pic = Image.open(file_location)
                pic.thumbnail((120,120), Image.ANTIALIAS)
                pic.save(thumbnail_location)
                filenames.append(filename)
                i=i+1
        for filename in filenames:
                image = item_images(file_name = filename)
                entry.images.append(image)
        entry.info.vinyl_info.Catno = form.Catno.data
        entry.info.vinyl_info.Artist = form.Artist.data
        entry.info.vinyl_info.Album = form.Album.data
        entry.info.vinyl_info.Sleeve_Grade = form.Sleeve_Grade.data
        entry.info.vinyl_info.Record_Grade = form.Record_Grade.data
        entry.info.Comments = form.Comments.data
        entry.info.Price = form.Price.data
        entry.edit_date = submit_time
        entry.edit_user_id = current_user.get_id()
        db.session.commit()
        flash('You have successfully edited the item type.')

        # redirect to the item types page
        return redirect(url_for('admin.add_vinyls'))
    
    # form.name.data = itemtype.name
    return render_template_modal('admin/items/Vinyls/edit.html', action="Edit",
                           add_item_type=add_item_type, form=form,
                           entry=entry, title="Edit Vinyl")


@admin.route('/items/vinyls/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_vinyl(id):
    """
    Delete a vinyl from the database
    """
    check_admin()

    vinyl = item.query.get_or_404(id)
    if vinyl.images:
        for image in vinyl.images:
            image_location = os.path.join(current_app.config['IMAGE_UPLOAD_PATH'],image.file_name)
            thumbnail_location = os.path.join(current_app.config['THUMBNAIL_UPLOAD_PATH'],image.file_name)
            os.remove(image_location)
            os.remove(thumbnail_location)
    db.session.delete(vinyl)
    db.session.commit()
    flash('You have successfully deleted the item type.')

    # redirect to the item types page
    return redirect(url_for('admin.add_vinyls'))


@admin.route('/items/vinyls/delete/image/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_image_from_entry(id):
    """
    Delete an image from an entry from the database
    """
    check_admin()

    image = item_images.query.get_or_404(id)
    if image:
        image_location = os.path.join(current_app.config['IMAGE_UPLOAD_PATH'],image.file_name)
        thumbnail_location = os.path.join(current_app.config['THUMBNAIL_UPLOAD_PATH'],image.file_name)
        os.remove(image_location)
        os.remove(thumbnail_location)
    db.session.delete(image)
    db.session.commit()

    return jsonify('success')


@admin.route('/items/vinyls/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_vinyl(id):
    """
    Update a vinyl entry info from the discogs API
    """

    d = discogs_client.Client('Vinyl Info Grabber/0.1', user_token=current_app.config['DISCOGS_TKN'])
    vinyl = item.query.get_or_404(id)
    Catno = vinyl.info.vinyl_info.Catno
    Artist = vinyl.info.vinyl_info.Artist

    results = d.search(catno = Catno)
    wasFound = False
    for result in results.page(1)[0:10]:
        try:
            release = d.release(result.data['id'])
            print(Artist,file=sys.stderr)
            print(release.artists[0].data['name'],file=sys.stderr)
            if fuzz.partial_ratio(Catno,result.data['catno']) >= 60 and fuzz.ratio(Artist,release.artists[0].data['name']) >= 50:             
                release = d.release(result.data['id'])
                vinyl.info.vinyl_info.Catno = result.data['catno']
                if 'year' in result.data:
                    vinyl.info.vinyl_info.Release_Year = result.data['year']
                vinyl.info.vinyl_info.Artist = release.artists[0].data['name']
                vinyl.info.vinyl_info.Album = release.title
                vinyl.info.vinyl_info.Labels = result.data['label'][0]
                vinyl.info.vinyl_info.Genres = ', '.join(result.data['genre'])
                vinyl.info.vinyl_info.Styles = ', '.join(result.data['style'])
                vinyl.info.vinyl_info.needsManualReview = False
                wasFound = True
                flash('You have successfully updated the vinyl.')
                break
        except:
            continue
    if wasFound == False:
        vinyl.info.vinyl_info.needsManualReview = True
        flash('Error: No similar results were found.')
    vinyl.info.vinyl_info.wasScanned = True
    db.session.commit()
    return redirect(url_for('admin.add_vinyls'))

#TODO: work with ebay api?