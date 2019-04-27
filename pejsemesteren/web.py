from flask import Flask, render_template, request, session, redirect, send_file
#from flask_paginate import Pagination, get_page_args
from pymongo import MongoClient
from paginate import Pagination, get_page_args
import pymongo
from glob import glob
from bson.json_util import loads

db = MongoClient("mongodb://localhost:27017").pejem

offset = 0
app = Flask(__name__,static_url_path='/static')
app.secret_key = 'super secret key'

def get_users(arr,offset=0, per_page=9):
    return arr[offset: offset + per_page]

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
            cart.append(db.stoves.find_one({"name":i}))
    except Exception as e:
        pass
    return render_template("cart.html",cart=cart)

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
        a = db.stoves.find_one({"name":i})
        arr.append([a["manufacturer"],a["name"]])
    createpdf(arr)
    return send_file('demo.pdf', attachment_filename='ohhey.pdf')
)

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
    for i in db.stoves.find({"category":category}):
        mans.append(i["manufacturer"])
    return render_template('customer.html',category=category.replace("_"," "), mans = set(mans))

@app.route('/<category>/<manufacturer>')
def manufacturer_page(category,manufacturer):
    temp = db.stoves.find({"category":category,"manufacturer":manufacturer})
    page = int(request.args.get('page', 1))
    per_page = 9
    offset = (page - 1) * per_page
    pagination_users = get_users(temp,offset=offset,per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, offset=offset,total=temp.count(), css_framework='bootstrap4')
    return render_template('product.html',category=category,manufacturer=manufacturer,stoves=temp,goods=pagination_users,pagination=pagination)

@app.route('/<category>/<manufacturer>/<product>')
def product_info(category,manufacturer,product):
    p = db.stoves.find_one({"name":product})
    print(product.replace(" ", "_"))
    pics  = glob("static/%s/%s/%s/*.png"%(category,manufacturer,product.replace(" ", "_")))
    pics.extend(glob("static/%s/%s/%s/*.jpg"%(category,manufacturer,product.replace(" ", "_"))))
    return render_template('product-info.html',category=category,manufacturer=manufacturer,product=p,pics=pics)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port="5000", debug=True)
