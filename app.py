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


# favorites = db.Table('favorites',
#     db.Column('customer_id', db.Integer, db.ForeignKey('customer.id'), primary_key=True),
#     db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
# )

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    favorites = db.relationship("Favorites", backref="customer", cascade="all, delete, delete-orphan")

    def __init__(self, email, password):
        self.email = email
        self.password = password


class Favorites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)

    def __init__(self, customer_id, product_id):
        self.customer_id = customer_id
        self.product_id = product_id

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String, nullable=False)
    collection = db.Column(db.String)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    featured_image = db.Column(db.String, nullable=False)
    favorited_by = db.relationship("Favorites", backref="product", cascade="all, delete, delete-orphan")
    images = db.relationship("Image", backref="product", cascade="all, delete, delete-orphan")

    def __init__(self, category, collection, name, description, price, featured_image):
        self.category = category
        self.collection = collection
        self.name = name
        self.description = description
        self.price = price
        self.featured_image = featured_image


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)

    def __init__(self, image_url, product_id):
        self.image_url = image_url
        self.product_id = product_id



class AdminSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "password")

admin_schema = AdminSchema()
multi_admin_schema = AdminSchema(many=True)

class FavoritesSchema(ma.Schema):
    class Meta:
        fields = ("id", "customer_id", "product_id")

favorites_schema = FavoritesSchema()
multi_favorites_schema = FavoritesSchema(many=True)

class ImageSchema(ma.Schema):
    class Meta:
        fields = ("id", "image_url", "product_id")

image_schema = ImageSchema()
multi_image_schema = ImageSchema(many=True)


class CustomerSchema(ma.Schema):
    class Meta:
        fields = ("id", "email", "password", "favorites")
    favorites = ma.Nested(multi_favorites_schema)

customer_schema = CustomerSchema()
multi_customer_schema = CustomerSchema(many=True)

class ProductSchema(ma.Schema):
    class Meta:
        fields = ("id", "category", "collection", "name", "description", "price", "featured_image", "images", "favorited_by")
    images = ma.Nested(multi_image_schema)
    favorited_by = ma.Nested(multi_favorites_schema)

product_schema = ProductSchema()
multi_product_schema = ProductSchema(many=True)




@app.route("/admin/add", methods=["POST"])
def add_admin():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as json")

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    new_admin = Admin(username, pw_hash)
    db.session.add(new_admin)
    db.session.commit()

    return jsonify(admin_schema.dump(new_admin))

@app.route("/admin/verification", methods=["POST"])
def admin_verification():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as json")

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    admin = db.session.query(Admin).filter(Admin.username == username).first()

    if admin is None:
        return jsonify("ADMIN_NOT_LOGGED_IN")

    if not bcrypt.check_password_hash(admin.password, password):
        return jsonify("ADMIN_NOT_LOGGED_IN")

    return jsonify(admin_schema.dump(admin))

@app.route("/admin/get", methods=["GET"])
def get_all_admins():
    all_admins = db.session.query(Admin).all()
    return jsonify(multi_admin_schema.dump(all_admins))




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

    if customer is None:
        return jsonify("Account NOT Verified")

    if not bcrypt.check_password_hash(customer.password, password):
        return jsonify("Account NOT Verified")

    return jsonify(customer_schema.dump(customer))

@app.route("/customer/get", methods=["GET"])
def get_all_customers():
    all_customers = db.session.query(Customer).all()
    return jsonify(multi_customer_schema.dump(all_customers))

@app.route("/customer/get/<email>", methods=["GET"])
def get_customer(email):
    customer = db.session.query(Customer).filter(Customer.email == email).first()
    return jsonify(customer_schema.dump(customer))






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

    existing_product_check = db.session.query(Product).filter(Product.name == name).filter(Product.category == category).first()
    if existing_product_check is not None:
        return jsonify("Error: Product already exists")

    new_product = Product(category, collection, name, description, price, featured_image, favorited_by)
    db.session.add(new_product)
    db.session.commit()

    return jsonify(product_schema.dump(new_product))

@app.route("/product/add/multi", methods=["POST"])
def add_multi_products():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")

    data = request.get_json().get("data")

    new_products = []

    for product in data:
        category = product.get("category")
        collection = product.get("collection")
        name = product.get("name")
        description = product.get("description")
        price = product.get("price")
        featured_image = product.get("featured_image")

        existing_product_check = db.session.query(Product).filter(Product.name == name).filter(Product.category == category).first()
        if existing_product_check is None:

            new_product = Product(category, collection, name, description, price, featured_image)
            db.session.add(new_product)
            db.session.commit()
            new_products.append(new_product)

    return jsonify(multi_product_schema.dump(new_products))

@app.route("/product/get", methods=["GET"])
def get_products():
    all_products = db.session.query(Product).all()
    return jsonify(multi_product_schema.dump(all_products))

@app.route("/product/get/id/<id>", methods=["GET"])
def get_products_by_id(id):
    products = db.session.query(Product).filter(Product.id == id).first()
    return jsonify(product_schema.dump(products))

@app.route("/product/get/category/<category>", methods=["GET"])
def get_products_by_category(category):
    this_category = db.session.query(Product).filter(Product.category == category).all()
    return jsonify(multi_product_schema.dump(this_category))

@app.route("/product/get/collection/<collection>", methods=["GET"])
def get_products_by_collection(collection):
    this_collection = db.session.query(Product).filter(Product.collection == collection).all()
    return jsonify(multi_product_schema.dump(this_collection))


@app.route("/product/update/id/<id>", methods=["PUT"])
def update_product(id):
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as json")

    data = request.get_json()
    category = data.get("category")
    collection = data.get("collection")
    name = data.get("name")
    description = data.get("description")
    price = data.get("price")
    featured_image = data.get("featured_image")

    product = db.session.query(Product).filter(Product.id == id).first()

    if category != None:
        product.category = category
    if collection != None:
        product.collection = collection
    if name != None:
        product.name = name
    if description != None:
        product.description = description
    if price != None:
        product.price = price
    if featured_image != None:
        product.featured_image = featured_image
    db.session.commit()

    return jsonify(product_schema.dump(product))

@app.route("/product/delete/id/<id>", methods=["DELETE"])
def delete_product(id):
    product = db.session.query(Product).filter(Product.id == id).first()
    db.session.delete(product)
    db.session.commit()
    return jsonify("Product successfully deleted")




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

@app.route("/image/update/id/<id>", methods=["PUT"])
def update_image(id):
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")

    image_url = request.get_json().get("image_url")

    image = db.session.query(Image).filter(Image.id == id).first()

    if image_url != None:
        image.image_url = image_url

    db.session.commit()

    return jsonify(image_schema.dump(image))

@app.route("/image/delete/id/<id>", methods=["DELETE"])
def delete_image(id):
    image = db.session.query(Image).filter(Image.id == id).first()
    db.session.delete(image)
    db.session.commit()
    return jsonify("Image successfully deleted")



@app.route("/favorites/add", methods=["POST"])
def add_favorite():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")

    data = request.get_json()
    customer_id = data.get(customer_id)
    product_id = data.get(product_id)

    # TODO: fix this query
    favorite = db.session.query(Favorites).filter(Favorites.customer_id == customer_id).filter(Favorites.product_id == product_id)

    new_favorite = Favorites(customer_id, product_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify(favorites_schema.dump(new_favorite))

@app.route("/favorites/get", methods=["GET"])
def get_favorites():
    all_favorites = db.session.query(Favorites).all()
    return jsonify(multi_favorites_schema.dump(all_favorites))

@app.route("/favorites/get/<customer_id>", methods=["GET"])
def get_favorites_by_customer(customer_id):
    customer_favorites = db.session.query(Customer).filter(Customer.favorites == favorites).all()
    return jsonify(multi_favorites_schema.dump(customer_favorites))
















if __name__ == "__main__":
    app.run(debug=True)



# pipenv install flask flask-sqlalchemy flask-marshmallow marshmallow-sqlalchemy flask cors gunicorn psycopg2