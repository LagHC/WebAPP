from flask import request, current_app, render_template, abort, jsonify, send_from_directory
from flask_login import login_required, current_user
import sys
from operator import attrgetter

from ..models import ItemSchema, ItemTypeSchema, item_type, tblVinyls, item, item_info, item_images
from . import home
from .. import db

def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.is_admin:
        abort(403)

@home.route('/')
def homepage():
    """
    Render the homepage template on the / route
    """
    return render_template('home/index.html', title="Inventory Project")

@home.route('/dashboard')
@login_required
def dashboard():
    """
    Render the dashboard template on the /dashboard route
    """
    return render_template('home/dashboard.html', title="Dashboard")

@home.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # prevent non-admins from accessing the page
    if not current_user.is_admin:
        abort(403)

    return render_template('home/admin_dashboard.html', title="Dashboard")

@home.route('/api/item_types')
def item_type_data():
    # statement=item_type.query.all()
    # item_type_schema = ItemTypeSchema()
    # output = item_type_schema.dump(statement, many=True)
    # return jsonify(output)
    query = item_type.query
    item_type_schema = ItemTypeSchema()

    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            item_type.id.like(f'%{search}%'),
            item_type.name.like(f'%{search}%'),
            item_type.entry_date.like(f'%{search}%'),
            item_type.user_id.like(f'%{search}%'),
            item_type.edit_date.like(f'%{search}%'),
            item_type.edit_user_id.like(f'%{search}%')
        ))
    total_filtered = query.count()

    i=0
    while True:
        if i > 7:
            break
        col_name = request.args.get(f'columns[{i}][data]')
        if col_name not in ['id','name','entry_date','user_id','edit_date','edit_user_id']:
            col_name = 'name'
        col_search = request.args.get(f'columns[{i}][search][value]')
        if col_search:
            query = query.filter(db.or_(
                getattr(item_type,col_name).like(f'%{col_search}%')
            ))
        i += 1

    #Sorting
    order = []
    i = 0
    while True:
        col_idx = request.args.get(f'order[{i}][column]')
        if col_idx is None:
            break
        col_name = request.args.get(f'columns[{col_idx}][data]')
        if col_name not in ['id','name','entry_date','user_id','edit_date','edit_user_id']:
            col_name = 'name'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(item_type, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)
    
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    output = item_type_schema.dump(query,many=True)
    return {
        'data':output,
        'recordsFiltered':total_filtered,
        'recordsTotal':item_type.query.count(),
        'draw':request.args.get('draw',type=int)
    }

@home.route('/api/vinyl_info')
def item_info_data():
    # statement = item.query.filter_by(item_type_id = 141).all()
    # schema = ItemSchema()
    # result=schema.dump(statement, many=True)
    # return jsonify(result)
    query = item.query.filter_by(item_type_id = 141).outerjoin(item.info).outerjoin(item_info.vinyl_info)
    schema = ItemSchema()

    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            item.id.like(f'%{search}%'),
            item.user_id.like(f'%{search}%'),
            item.entry_time.like(f'%{search}%'),
            item.edit_date.like(f'%{search}%'),
            item_info.Comments.like(f'%{search}%'),
            item_info.Price.like(f'%{search}%'),
            tblVinyls.Catno.like(f'%{search}%'),
            tblVinyls.Artist.like(f'%{search}%'),
            tblVinyls.Album.like(f'%{search}%'),
            tblVinyls.Sleeve_Grade.like(f'%{search}%'),
            tblVinyls.Record_Grade.like(f'%{search}%'),
            tblVinyls.Release_Year.like(f'%{search}%'),
            tblVinyls.Styles.like(f'%{search}%'),
            tblVinyls.Genres.like(f'%{search}%'),
            tblVinyls.Labels.like(f'%{search}%'),
            item.edit_user_id.like(f'%{search}%')
        ))
    total_filtered = query.count()

    #Column Search
    i=0
    while True:
        if i > 14:
            break
        col_name = request.args.get(f'columns[{i}][data]')
        if col_name not in ['id','info.vinyl_info.Catno','info.vinyl_info.Artist','info.vinyl_info.Album','info.vinyl_info.Sleeve_Grade','info.vinyl_info.Record_Grade','info.vinyl_info.Release_Year','info.vinyl_info.Styles','info.vinyl_info.Genres','info.vinyl_info.Labels', 'info.Comments', 'info.Price']:
            col_name = 'id'
        col_search = request.args.get(f'columns[{i}][search][value]')
        if col_search:
            if 'info.vinyl_info' in col_name:
                col_name = col_name.replace('info.vinyl_info.','')
                query = query.filter(db.or_(
                getattr(tblVinyls,col_name).like(f'%{col_search}%')
                ))
            elif 'info':
                col_name = col_name.replace('info.','')
                query = query.filter(db.or_(
                getattr(item_info,col_name).like(f'%{col_search}%')
                ))
            else:
                query = query.filter(db.or_(
                getattr(item,col_name).like(f'%{col_search}%')
                ))
        i += 1

    #Sorting
    order = []
    i = 0
    while True:
        col_idx = request.args.get(f'order[{i}][column]')
        if col_idx is None:
            break
        col_name = request.args.get(f'columns[{col_idx}][data]')
        if col_name not in ['id','info.Price','info.vinyl_info.Sleeve_Grade','info.vinyl_info.Record_Grade','info.vinyl_info.Release_Year']:
            col_name = 'id'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        if col_name == 'id':
            col = getattr(item, col_name)
        elif col_name == 'info.Price':
            col_name = col_name.replace('info.','')
            col = getattr(item_info, col_name)
        else:
            col_name = col_name.replace('info.vinyl_info.','')
            col = getattr(tblVinyls, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    output=schema.dump(query, many=True)
    return {
        'data':output,
        'recordsFiltered':total_filtered,
        'recordsTotal':item.query.count(),
        'draw':request.args.get('draw',type=int)
    }


#TODO: ADD file limits and filesize limits on upload
@home.route('/uploads/images/<filename>')
def images(filename):
    return send_from_directory(current_app.config['IMAGE_UPLOAD_PATH'],
                               filename)

@home.route('/uploads/images/thumbnails/<filename>')
def thumbnails(filename):
    return send_from_directory(current_app.config['THUMBNAIL_UPLOAD_PATH'],
                               filename)