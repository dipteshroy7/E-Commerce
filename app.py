from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///emobiles.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.config['ALLOWED_EXTENSIONS'] = {'JPG', 'JPEG', 'PNG'}


# database table model - products_table
class products_table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.Text, nullable=False)
    product_price = db.Column(db.Integer, nullable=False)
    product_image_name = db.Column(db.Text, nullable=False)


# database table model - cart_table
class cart_table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image_name = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


# upload file format validation
def allowed_image(filename):
    if not '.' in filename:
        return False
    ext = filename.rsplit('.', 1)[1].upper()
    if ext in app.config['ALLOWED_EXTENSIONS']:
        return True
    else:
        return False


# function to display all the products in Home page
@app.route('/')
def home():
    all_products = products_table.query.all()
    cart_items = cart_table.query.all()
    return render_template('index.html', all_products=all_products,cart_items=cart_items)


# function for search operation
@app.route('/result', methods=['GET'])
def result():
    search = request.args.get("search")
    if search: 
        res_products = products_table.query.filter(products_table.product_name.contains(search)).all()
        return render_template('result.html', res_products=res_products)
    else:
        return render_template('error.html')
    

# function for cart operations
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if request.method=='POST':
        
        action = request.form['action']
        product_id = request.form['product_id']
        
        # item quantity increase
        if action == "increase":
            selected_item = cart_table.query.filter_by(id=product_id).first()
            selected_item.quantity +=1
            db.session.commit()
        
        # item quantity decrease
        elif action == "decrease":
            selected_item = cart_table.query.filter_by(id=product_id).first()
            selected_item.quantity -=1
            db.session.commit()
        
        # item remove
        elif action == "remove":
            selected_item = cart_table.query.filter_by(id=product_id).first()
            db.session.delete(selected_item)
            db.session.commit()

        #item add
        elif action == "addtocart":
            vcart = cart_table.query.filter_by(id=product_id).first()
            if not vcart:
                selected_item = products_table.query.filter_by(id=product_id).first()
                carts = cart_table(id=selected_item.id, name=selected_item.product_name, price=selected_item.product_price, image_name=selected_item.product_image_name, quantity=1)
                db.session.add(carts)
                db.session.commit()
        return redirect(url_for('cart'))
    
    cart_items = cart_table.query.all()
    total_price = 0
    for item in cart_items:
        total_price += item.price * item.quantity
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)


# function for billing page
@app.route('/billing', methods=['GET', 'POST'])
def billing():
    if request.method == "POST":
        total_amount = request.form['total_amount']
        return render_template('billing.html', total_amount=total_amount)
    return render_template('error.html')


# function for success page
@app.route('/success', methods=['GET', 'POST'])
def success():
    if request.method == "POST":
        # cart_items = cart_table.query.all()
        db.session.query(cart_table).delete()
        db.session.commit()
        return render_template('success.html')
    return render_template('error.html')


# function to upload product data
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method=='POST':
        name = request.form['name']
        price = request.form['price']
        image = request.files['image']

        if image.filename.rsplit('.', 1)[0] == "":
            print('Image must have a name, 400')
            return redirect(request.url)
        
        if not allowed_image(image.filename):
            print('Image Extension is not allowed, 400')
            return redirect(request.url)
        
        image.save('static/product_images/' + secure_filename(image.filename))

        product = products_table(product_name=name, product_price=price, product_image_name=image.filename)
        db.session.add(product)
        db.session.commit()
        print('Data Uploaded Successfully')
        return redirect(url_for('upload'))

    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=False)