from flask import Flask, jsonify, make_response, abort
from flask_restful import Api, Resource, reqparse, marshal_with, fields
import sys
import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)

# write your code here

api = Api(app)

db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendar.db'


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.VARCHAR, nullable=False)
    date = db.Column(db.Date, nullable=False)
db.create_all()

model = {
    'id': fields.Integer,
    "event": fields.String,
    "date": fields.String
}


class EventByID(Resource):
    @marshal_with(model)
    def get(self, event_id):
        event = Event.query.filter(Event.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        return event

    def delete(self, event_id):
        event = Event.query.filter(Event.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        db.session.delete(event)
        db.session.commit()
        rs = {
                "message": "The event has been deleted!"
             }
        return make_response(jsonify(rs), 200)


class TodayEventResource(Resource):
    @marshal_with(model)
    def get(self):
        return Event.query.filter(Event.date == datetime.date.today()).all()


class EventResource(Resource):

    @marshal_with(model)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'start_time',
            type=lambda x: datetime.date.fromisoformat(x),
        )
        parser.add_argument(
            'end_time',
            type=lambda x: datetime.date.fromisoformat(x),
        )
        args = parser.parse_args()
        if args['start_time'] and args['end_time']:
            return Event.query.filter(func.DATE(Event.date) >= args['start_time'],
                                      func.DATE(Event.date) <= args['end_time']).all()
        return Event.query.all()

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'date',
            type=lambda x: datetime.date.fromisoformat(x),
            help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
            required=True
        )
        parser.add_argument(
            'event',
            type=str,
            help="The event name is required!",
            required=True
        )
        args = parser.parse_args()
        event = Event(event=args['event'], date=args['date'])
        db.session.add(event)
        db.session.commit()
        rs = {
            "message": "The event has been added!",
            "event": args['event'],
            "date": args['date'].strftime('%Y-%m-%d')
        }
        return make_response(jsonify(rs), 200)


api.add_resource(TodayEventResource, '/event/today')
api.add_resource(EventResource, '/event/')
api.add_resource(EventByID, '/event/<int:event_id>')

# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()