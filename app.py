from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://kxverjehefpkby:04e0afa65b478c82173448dd49f6856b64563be6311c6861f875899ff56f5748@ec2-44-196-8-220.compute-1.amazonaws.com:5432/d6bkj7orsspv6f"

db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String, nullable=False)
    collection = db.Column(db.String)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    images = db.relationship("Image", backref="product", cascade="all, delete, delete-orphan")

    def __init__(self, category, collection, name, description, price):
        self.category = category
        self.collection = collection
        self.name = name
        self.description = description
        self.price = price

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
        fields = ("id", "category", "collection", "name", "description", "price", "images")
    images = ma.Nested(multi_image_schema)

product_schema = ProductSchema()
multi_product_schema = ProductSchema(many=True)




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

    existing_product_check = db.session.query(Product).filter(Product.collection == collection).filter(Product.name == name).first()
    if existing_product_check is not None:
        return jsonify("ERROR: Product already exists in database")

    new_product = Product(category, collection, name, description, price)
    db.session.add(new_product)
    db.session.commit()

    return jsonify(product_schema.dump(new_product))

@app.route("/product/get", methods=["GET"])
def get_products():
    all_products = db.session.query(Product).all()
    return jsonify(multi_product_schema.dump(all_products))

@app.route("/product/get/category/<category>", methods=["GET"])
def get_products_by_category(category):
    products = db.session.query(Product).filter(Product.category == category).all()
    return jsonify(multi_product_schema.dump(products))



















if __name__ == "__main__":
    app.run(debug=True)



# pipenv install flask flask-sqlalchemy flask-marshmallow marshmallow-sqlalchemy flask cors gunicorn psycopg2