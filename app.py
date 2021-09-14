from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_cors import CORS

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://kxverjehefpkby:04e0afa65b478c82173448dd49f6856b64563be6311c6861f875899ff56f5748@ec2-44-196-8-220.compute-1.amazonaws.com:5432/d6bkj7orsspv6f"

db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
CORS(app)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    favorites = db.relationship("Product", backref="customer", cascade="all, delete, delete-orphan")

    def __init__(self, email, password):
        self.email = email
        self.password = password

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String, nullable=False)
    collection = db.Column(db.String)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    featured_image = db.Column(db.String, nullable=False)
    favorited_by = db.Column(db.Integer, db.ForeignKey("customer.id"))
    images = db.relationship("Image", backref="product", cascade="all, delete, delete-orphan")

    def __init__(self, category, collection, name, description, price, featured_image, favorited_by):
        self.category = category
        self.collection = collection
        self.name = name
        self.description = description
        self.price = price
        self.featured_image = featured_image
        self.favorited_by = favorited_by

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)

    def __init__(self, image_url, product_id):
        self.image_url = image_url
        self.product_id = product_id

class ImageSchema(ma.Schema):
    class Meta:
        fields = ("id", "image_url", "product_id")

image_schema = ImageSchema()
multi_image_schema = ImageSchema(many=True)

class ProductSchema(ma.Schema):
    class Meta:
        fields = ("id", "category", "collection", "name", "description", "price", "featured_image", "images", "favorited_by")
    images = ma.Nested(multi_image_schema)

product_schema = ProductSchema()
multi_product_schema = ProductSchema(many=True)

class CustomerSchema(ma.Schema):
    class Meta:
        fields = ("id", "email", "password")
    favorites = ma.Nested(multi_product_schema)

customer_schema = CustomerSchema()
multi_customer_schema = CustomerSchema(many=True)




@app.route("/product/add", methods=["POST"])
def add_product():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")

    data = request.get_json()
    category = data.get("category")
    collection = data.get("collection")
    name = data.get("name")
    description = data.get("description")
    price = data.get("price")
    featured_image = data.get("featured_image")
    favorited_by = data.get("favorited_by")

    new_product = Product(category, collection, name, description, price, featured_image, favorited_by)
    db.session.add(new_product)
    db.session.commit()

    return jsonify(product_schema.dump(new_product))

@app.route("/product/get", methods=["GET"])
def get_products():
    all_products = db.session.query(Product).all()
    return jsonify(multi_product_schema.dump(all_products))

@app.route("/product/get/<category>", methods=["GET"])
def get_products_by_category(category):
    products = db.session.query(Product).filter(Product.category == category).all()
    return jsonify(multi_product_schema.dump(products))

@app.route("/product/get/collection/<collection>", methods=["GET"])
def get_products_by_collection(collection):
    collections = collection.split("-")
    products = db.session.query(Product).filter(Product.collection == collections).all()
    return jsonify(multi_product_schema.dump(products))




@app.route("/image/add", methods=["POST"])
def add_images():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")

    data = request.get_json()
    image_url = data.get("image_url")
    product_id = data.get("product_id")

    existing_image_check = db.session.query(Image).filter(Image.image_url == image_url).first()
    if existing_image_check is not None:
        return jsonify("Error: Duplicate image. Please check url.")

    new_image = Image(image_url, product_id)
    db.session.add(new_image)
    db.session.commit()

    return jsonify(image_schema.dump(new_image))

@app.route("/image/get", methods=["GET"])
def get_all_images():
    all_images = db.session.query(Image).all()
    return jsonify(multi_image_schema.dump(all_images))

@app.route("/image/get/all/<product_id>", methods=["GET"])
def get_all_images_by_product_id(product_id):
    images = db.session.query(Image).filter(Image.product_id == product_id).all()
    return jsonify(multi_image_schema.dump(images))




@app.route("/customer/add", methods=["POST"])
def add_customer():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as json")

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    new_customer = Customer(email, pw_hash)
    db.session.add(new_customer)
    db.session.commit()

    return jsonify(customer_schema.dump(new_customer))

@app.route("/customer/verification", methods=["POST"])
def verification():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as json")

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    customer = db.session.query(Customer).filter(Customer.email == email).first()

    if user is None:
        return jsonify("Account NOT Verified")

    if not bcrypt.check_password_hash(customer.password, password):
        return jsonify("Account NOT Verified")

    return jsonify(customer_schema.dump(customer))

@app.route("/customer/get", methods=["GET"])
def get_all_customers():
    all_customers = db.session.query(Customer).all()
    return jsonify(multi_customer_schema.dump(all_customers))












if __name__ == "__main__":
    app.run(debug=True)



# pipenv install flask flask-sqlalchemy flask-marshmallow marshmallow-sqlalchemy flask cors gunicorn psycopg2