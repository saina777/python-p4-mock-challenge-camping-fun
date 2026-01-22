#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class Campers(Resource):
    def get(self):
        campers = [c.to_dict(only=('id', 'name', 'age')) for c in Camper.query.all()]
        return make_response(jsonify(campers), 200)

    def post(self):
        data = request.get_json()
        try:
            new_camper = Camper(
                name=data.get('name'),
                age=data.get('age')
            )
            db.session.add(new_camper)
            db.session.commit()
            return make_response(new_camper.to_dict(only=('id', 'name', 'age')), 201)
        except (ValueError, TypeError):
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

api.add_resource(Campers, '/campers')

class CamperByID(Resource):
    def get(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if not camper:
            return make_response(jsonify({"error": "Camper not found"}), 404)
        return make_response(camper.to_dict(), 200)

    def patch(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if not camper:
            return make_response(jsonify({"error": "Camper not found"}), 404)
        
        data = request.get_json()
        try:
            for attr in data:
                setattr(camper, attr, data.get(attr))
            db.session.commit()
            return make_response(camper.to_dict(only=('id', 'name', 'age')), 202)
        except (ValueError, TypeError):
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

api.add_resource(CamperByID, '/campers/<int:id>')

class Activities(Resource):
    def get(self):
        activities = [a.to_dict(only=('id', 'name', 'difficulty')) for a in Activity.query.all()]
        return make_response(jsonify(activities), 200)

api.add_resource(Activities, '/activities')

class ActivityByID(Resource):
    def delete(self, id):
        activity = Activity.query.filter_by(id=id).first()
        if not activity:
            return make_response(jsonify({"error": "Activity not found"}), 404)
        
        db.session.delete(activity)
        db.session.commit()
        return make_response('', 204)

api.add_resource(ActivityByID, '/activities/<int:id>')

class Signups(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_signup = Signup(
                time=data.get('time'),
                camper_id=data.get('camper_id'),
                activity_id=data.get('activity_id')
            )
            db.session.add(new_signup)
            db.session.commit()
            return make_response(new_signup.to_dict(), 201)
        except (ValueError, TypeError):
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

api.add_resource(Signups, '/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
