from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import math


with open('config.json', 'r') as c:
    params = json.load(c)["params"]


app = Flask(__name__)
app.secret_key = 'secret-super'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/myblog'
db = SQLAlchemy(app)

class Contacts(db.Model):
    '''srn , Name , Email, phone no, message ,date/time
    this adds the db elements to the flask'''
    srn = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(80), nullable=False)
    Email = db.Column(db.String(12), nullable=False)
    phoneno = db.Column(db.String(120), nullable=False)
    message = db.Column(db.String(12), nullable=False)
    datetim = db.Column(db.String(120), nullable=True)


class Posts(db.Model):
    '''
    this adds the db elements to the flask
    '''
    sr = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    tagline = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(25), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(20), nullable=False)
    author = db.Column(db.String(100), nullable=True)
    

@app.route('/')
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(params["no_of_posts"]))
    page = request.args.get('page')


    if (not str(page).isnumeric()):
        page = 1
    
    page= int(page)

    posts = posts[(page-1)*int(params["no_of_posts"]):(page-1)*int(params["no_of_posts"]) + int(params["no_of_posts"])]
    # Pagination Logic
    if (page == 1): 
        prev = "#"
        nexts = "/?page=" + str(page + 1)
    elif (page == last):
        prev = "/?page=" + str(page - 1)
        nexts = "#"
    else:
        nexts = "/?page=" + str(page + 1)
        prev = "/?page=" + str(page - 1)

    return render_template('index.html', params=params, posts=posts, prev=prev, nexts=nexts)


@app.route('/delete/<string:sno>', methods=['GET','POST'])
def delete(sno):
    if ('user' in session and session['user'] == params["admin_user"]):
        post = Posts.query.filter_by(sr=sno).first()
        db.session.delete(post)
        db.session.commit()
    
    return redirect('/dashboard')


@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashboard')


@app.route('/edit/<string:sno>', methods=['GET','POST'])
def edit(sno):
    if ('user' in session and session['user'] == params["admin_user"]):
        if request.method=='POST':
            box_title = request.form.get('title')
            tline = request.form.get('tline') 
            content = request.form.get('content') 
            slug = request.form.get('slug') 
            img_file = request.form.get('img_file') 
            date = datetime.now()

            if sno == '0':
                post = Posts(title=box_title, tagline=tline, content=content, slug=slug,
                                 img_file=img_file, date=date, author="admin")
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(sr=sno).first()
                post.title = box_title
                post.tagline = tline
                post.slug = slug
                post.content = content
                post.date = date
                post.img_file=img_file
                
                db.session.commit()
                return redirect('/edit/'+ sno)
            
        post = Posts.query.filter_by(sr=sno).first()
        return render_template('edit.html', params=params, post=post)




@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    
    if ('user' in session and session['user'] == params["admin_user"]):
        posts = Posts.query.all() 
        return render_template('dashboard.html', params=params, posts=posts)
    
    if request.method=='POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if (username== params["admin_user"] and userpass== params["admin_pass"]):
            session['user'] = username
            posts = Posts.query.all()
            return render_template('dashboard.html', params=params, posts=posts)
        
    
    return render_template('signin.html', params=params)




@app.route('/contact', methods=["GET","POST"])
def contacts():
    if (request.method=='POST'):
        # add entry to database
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        entry = Contacts(Name=name, Email=email, phoneno=phone, datetim=datetime.now(),
                             message=message)
        db.session.add(entry)
        db.session.commit()

    return render_template('contact.html', params=params)

@app.route('/post/<string:post_slug>', methods=['GET'])
def posts(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)

@app.route('/about')
def about():
    return render_template('about.html', params=params)

# @app.route('/post')
# def post():
#     return render_template('post.html', params=params)


app.run(debug=True)