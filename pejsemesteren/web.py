from flask import Flask, render_template, request, session, redirect, send_file, abort
#from flask_paginate import Pagination, get_page_args
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from paginate import Pagination, get_page_args
import pymongo
from glob import glob
from pdf import *
from bson.json_util import loads
import os
UPLOAD_FOLDER = '/home/ubuntu/stoves/pejsemesteren/static/'

db = MongoClient("mongodb://localhost:27017").pejem

offset = 0
app = Flask(__name__, static_url_path='/static')
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def get_users(arr, offset=0, per_page=9):
    return arr[offset: offset + per_page]


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form['eemail'] == "admin" and request.form['passwd'] == "YxM89mMk":
            session["admin"] = True
            return redirect("/add_stove_admin")
        else:
            return render_template('admin_login.html', wrong=True)
    return render_template('admin_login.html')


@app.route('/add_stove_admin', methods=['GET', 'POST'])
def admin_stove():
    try:
        print(session["admin"])
        if request.method == 'POST':
            if 'file2' not in request.files:
                print(request.files)
                return render_template('admin_actions.html', stove=True, nofile=True)
            file = request.files['file2']
            if file.filename == '':
                return render_template('admin_actions.html', stove=True, nofile=True)

            path = app.config['UPLOAD_FOLDER']+request.form["cat"]+"/"+request.form["manufacturer"]+"/"+request.form["name"].replace(" ","_")
            os.makedirs(path)
            file.save(path+"/1.jpg")

            db.stoves.insert_one({"name": request.form["name"], "description": request.form["descr"],
                                "category": request.form["cat"], "manufacturer": request.form["manufacturer"],
                                "energ": request.form["energy"], "eff": "", "out": request.form["output"],
                                "heat": request.form["heat"], "vol": "", "pic": "1.jpg"})
            return render_template('admin_actions.html', stove=True, success=True)
        return render_template('admin_actions.html', stove=True)
    except Exception as e:
        print(e)
        abort(403)


@app.route('/change_banner_admin')
def admin_banner():
    try:
        print(session["admin"])
        return render_template('admin_actions.html', banner=True)
    except:
        abort(403)


@app.route('/change_1', methods=['POST'])
def admin_banner_1():
    if session["admin"]:
        if 'file' not in request.files:
            return render_template('admin_actions.html', banner=True, nofile=True)
        file = request.files['file']

        if file.filename == '':
            return render_template('admin_actions.html', banner=True, nofile=True)

        file.save("/home/artyem/Documents/stoves/pejsemesteren/static/sources/img/sl1.jpg")
        return render_template("/admin_actions.html",banner=True,success=True)
    else:
        abort(403)

@app.route('/change_2', methods=['POST'])
def admin_banner_2():
    if session["admin"]:
        if 'file' not in request.files:
            return render_template('admin_actions.html', banner=True, nofile=True)
        file = request.files['file']

        if file.filename == '':
            return render_template('admin_actions.html', banner=True, nofile=True)

        file.save("/home/artyem/Documents/stoves/pejsemesteren/static/sources/img/sl2.jpg")
        return render_template("/admin_actions.html",banner=True,success=True)
    else:
        abort(403)

@app.route('/')
def index():
    return render_template('Home page.html')


@app.route('/remove/<stove>')
def remove(stove):
    arr = session["cart"]
    session.pop("cart")
    arr.remove(stove)
    session["cart"] = arr
    return redirect("/cart")


@app.route('/cart')
def cart():
    cart = []
    try:
        for i in session['cart']:
            cart.append(db.stoves.find_one({"name": i}))
    except Exception as e:
        pass
    return render_template("cart.html", cart=cart)


@app.route('/add_stove/<stove>')
def add(stove):
    try:
        cart_list = session['cart']
    except:
        cart_list = []
        session['cart'] = []
    cart_list.append(stove)
    session['cart'] = cart_list
    return redirect("/cart")


@app.route('/carttopdf')
def topdf():
    arr = []
    for i in session['cart']:
        a = db.stoves.find_one({"name": i})
        arr.append(a["manufacturer"])
        arr.append(a["name"])
    createpdf(arr)
    return send_file('demo.pdf', attachment_filename='ohhey.pdf')


@app.route('/choose')
def choose():
    return render_template("choose.html")


@app.route('/howto')
def howto():
    return render_template("howto.html")


@app.route('/financing')
def financing():
    return render_template("finance.html")


@app.route('/contacts')
def contacts():
    return render_template("contacts.html")


@app.route('/protection')
def protection():
    return render_template("protect.html")


@app.route('/<category>')
def categories(category):
    mans = []
    for i in db.stoves.find({"category": category}):
        mans.append(i["manufacturer"])
    return render_template('customer.html', category=category.replace("_", " "), mans=set(mans))


@app.route('/<category>/<manufacturer>')
def manufacturer_page(category, manufacturer):
    temp = db.stoves.find({"category": category, "manufacturer": manufacturer})
    page = int(request.args.get('page', 1))
    per_page = 9
    offset = (page - 1) * per_page
    pagination_users = get_users(temp, offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, offset=offset,
                            total=temp.count(), css_framework='bootstrap4')
    return render_template('product.html', category=category, manufacturer=manufacturer, stoves=temp, goods=pagination_users, pagination=pagination)


@app.route('/<category>/<manufacturer>/<product>')
def product_info(category, manufacturer, product):
    p = db.stoves.find_one({"name": product})
    print(product.replace(" ", "_"))
    pics = glob("static/%s/%s/%s/*.png" %
                (category, manufacturer, product.replace(" ", "_")))
    pics.extend(glob("static/%s/%s/%s/*.jpg" %
                     (category, manufacturer, product.replace(" ", "_"))))
    return render_template('product-info.html', category=category, manufacturer=manufacturer, product=p, pics=pics)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port="5000", debug=True)
