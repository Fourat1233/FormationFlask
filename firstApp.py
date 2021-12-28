
from re import template
from flask import Flask,render_template,request,url_for,redirect,session
from flask_mysqldb import MySQL
import os
from werkzeug.utils import secure_filename 

app = Flask(__name__)
app.secret_key = "any random string"
mysql = MySQL(app)
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_user']= 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'firstappdb'

app.config['MYSQL_HOST'] = 'bovlzvqjffn9w70jq1fi-mysql.services.clever-cloud.com'
app.config['MYSQL_USER'] = 'unzpifeacqd5u7x6'
app.config['MYSQL_PASSWORD'] = 'Pz5IcdExDt05yQfjDeux'
app.config['MYSQL_DB'] = 'bovlzvqjffn9w70jq1fi'

app.config['UPLOAD_FOLDER'] = 'static'

@app.route('/hello')
def hello():
    return 'This is my first App <H1> Hello </H1>'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        details = request.form
        mail = details['mail']
        password = details['password']
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO user(email, password)VALUES(%s,%s)",(mail, password))
        except Exception:
            return render_template("index.html",error = "this email is already in use")
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('login',status="succes"))
    return render_template("index.html")


@app.route('/login',methods=['GET','POST'])
def login():
    session["cart"] = []
    session["total"] = 0
    status = request.args.get('status')
    if request.method == 'POST':
        session["mail"] = []
        details = request.form
        mail = details['mail']
        password = details['password']
        cur = mysql.connection.cursor()
        query_string = "SELECT * FROM user Where email = %s and password=%s"
        cur.execute(query_string,(mail,password))
        data=cur.fetchall()
        cur.close()
        if len(data)>0:
            session["mail"]=mail
            msg = "connected " + data[0][0]
            return redirect(url_for("profile",mail=mail))
        else:
            msg = "Connection failed"
        return render_template('login.html',msg=msg)
    return render_template('login.html',status=status)


@app.route("/profile/<mail>",methods=["POST","GET"])
def profile(mail):
    file=""
    
    if not 'mail' in session:
        return redirect(url_for('login'))
    if request.method == "POST":
        details = request.form
        mail= details["mail"]
        nom = details["nom"]
        prenom = details["prenom"]
        file = request.files["file"]
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cur = mysql.connection.cursor()
            cur.execute("UPDATE user set photo=%s where email=%s",(filename,mail))
            mysql.connection.commit()
            cur.close()
        cur = mysql.connection.cursor()
        cur.execute("update user set nom=%s ,prenom=%s where email=%s",(nom,prenom,mail))
        mysql.connection.commit()
        cur.close()

    cur= mysql.connection.cursor()
    requete = "Select * from user where email=%s"
    cur.execute(requete,(mail,))
    data = cur.fetchall()
    cur.close()
    return render_template('profile.html',data=data)

        


@app.route('/hello/<name>')
def helloName(name):
    return f'{name}\'s profile'

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404


@app.route('/add_product',methods=['POST','GET'])
def add_product():
    if not 'mail' in session:
        return redirect(url_for('login'))
    if request.method == "POST":
        filename="default.png"
        details = request.form
        nom = details['nom']
        prix = details['prix']
        qte = details['qte']
        file = request.files['file']
        if file:
            filename = secure_filename (file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        cur = mysql.connection.cursor()
        requete = "insert into product (nom,prix,qte,photo) values (%s,%s,%s,%s)"
        cur.execute(requete,(nom,prix,qte,filename))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("add_product"))
    return render_template("add_product.html")


@app.route("/list_product")
def list_product ():
    if not 'mail' in session:
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    requete = "SELECT * from product"
    cur.execute(requete)
    data = cur.fetchall()
    cur.close()
    return render_template("list_product.html",data=data)


@app.route('/logout')
def logout():
    session.pop("mail",None)
    return redirect(url_for('login'))

@app.route('/add_cart/<id>',methods=['POST','GET'])
def add_cart(id):
    cur= mysql.connection.cursor()
    query = "SELECT * from product where id = %s"
    cur.execute(query,(id,))
    data = cur.fetchall()
    plist = session['cart']
    plist.append(data[0])
    session['total'] += int(data[0][2])
    session['cart'] = plist 
    cur.close()
    return redirect(url_for('list_product',total=session['total'])) #------

@app.route('/pay',methods=['POST','GET'])
def pay():
    for product in session['cart']:
        cur = mysql.connection.cursor()
        requete ="INSERT INTO bill(email, product_id)VALUES(%s,%s)"
        cur.execute(requete,(session['mail'], product[0]))
        cur.close()
        mysql.connection.commit()
    session['cart'] = []
    return redirect(url_for('list_product'))


@app.route('/bill/<mail>')
def bill(mail):
    cur= mysql.connection.cursor()
    query = "SELECT * from bill,product where email = %s and product.id=bill.product_id"
    cur.execute(query,(session['mail'],))
    data = cur.fetchall()
    cur.close()
    return render_template('bill.html',data = data)


@app.route('/update/<id>',methods=["GET","POST"])
def update(id):
    if request.method =="POST":
        details = request.form
        nom = details['nom']
        prix = details['prix']
        qte = details['qte']
        file = request.files['file']
        if file : 
            filename= secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            cur = mysql.connection.cursor()
            requete = "UPDATE product set photo=%s where id=%s"
            cur.execute(requete,(filename,id))
            mysql.connection.commit()
            cur.close()
        cur = mysql.connection.cursor()
        cur.execute("update product set nom=%s,prix=%s,qte=%s where id=%s",(nom,prix,qte,id))
        mysql.connection.commit()
        cur.close()

    cur = mysql.connection.cursor()
    requete = "select * from product where id = %s"
    cur.execute(requete,(id,))
    data = cur.fetchall()
    cur.close()
    return render_template('update_product.html',data=data)



@app.route('/remove_cart/<id>',methods=['POST','GET'])
def remove_cart(id):
    index = 0
    plist = session['cart']
    for item in plist:
        #if item[0] == id :
        session['total'] -= int(item[2])
        del plist[index]
        index+=1
    

    session['cart'] = plist 
    return redirect(url_for('list_product'))