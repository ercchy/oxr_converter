from flask import Flask, jsonify
from config import *
from .models.database import db, ma

# App init
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

# Database and Marshmallow init
db.init_app(app)
ma.init_app(app)


# Controllers
@app.route('/')
def index():
    return_obj = {'msg': 'welcome'}
    return jsonify(return_obj)

@app.route("/grab_and_save", methods=['POST'])
def grab_and_save():
    return jsonify({'msg': 'you need to post some data'})


# @app.route()
# def get_last_record():
#     return


if __name__ == '__main__':
    # Will make the server available externally as well
    app.run(host='0.0.0.0')
