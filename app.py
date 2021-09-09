from flask import Flask
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import INTEGER

# The decorator marshal_with is what actually takes your data object and applies the field filtering.
# The marshalling can work on single objects, dicts, or lists of objects.

# With the fields module, you can use whatever objects (ORM models/custom classes/etc.) you want in your resource.
# fields also lets you format and filter the response so you don’t have to worry about exposing internal
# data structures.

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
db = SQLAlchemy(app)


class TodoModel(db.Model):
    id = db.Column(db.INTEGER, primary_key=True,nullable=False)
    task = db.Column(db.String(200), nullable=True)
    summary = db.Column(db.String(500), nullable=True)
# SQLAlchemy is an ORM-Objects Relational Mapper written in Python.
# It gives away around to interact with the Databases without using SQL statements.



#db.create_all()

task_post_args = reqparse.RequestParser()
task_post_args.add_argument("task", type=str, help="Task is requried", required=True)
task_post_args.add_argument("summary", type=str, help="Summary is required", required=True)

task_update_args = reqparse.RequestParser()
task_update_args.add_argument("task", type=str)
task_update_args.add_argument("summary", type=str)


resource_fields = {
    'id': fields.Integer,
    'task': fields.String,
    'summary': fields.String,
}

#python dictionary is already seriealized so no marshalling
class ToDoList(Resource):
    def get(self):
        tasks = TodoModel.query.all()
        todos = {}
        for task in tasks:
            todos[task.id] = {"task": task.task, "summary": task.summary}
        return todos


class ToDo(Resource):
    @marshal_with(resource_fields)
    def get(self, todo_id):
        task = TodoModel.query.filter_by(id=todo_id).first()
        if not task:
            abort(404, message="Could not find task with that id")
        return task

    @marshal_with(resource_fields)
    def post(self, todo_id):
        args = task_post_args.parse_args()
        task = TodoModel.query.filter_by(id=todo_id).first()
        if task:
            abort(409, message="task id taken...")

        todo = TodoModel(id=todo_id, task=args['task'], summary=args['summary'])
        db.session.add(todo)
        db.session.commit()
        return todo, 201

    @marshal_with(resource_fields)
    def put(self, todo_id):
        args = task_update_args.parse_args()
        task = TodoModel.query.filter_by(id=todo_id).first()
        if not task:
            abort(404, message="task doesn't exist, cannot update")
        if args['task']:
            task.task = args['task']
        if args['summary']:
            task.summary = args['summary']
        db.session.commit()
        return task

    def delete(self, todo_id):
        task = TodoModel.query.filter_by(id=todo_id).first()
        db.session.delete(task)
        return 'Todo Deleted', 204


api.add_resource(ToDo, '/todos/<int:todo_id>')
api.add_resource(ToDoList, '/todos')

if __name__ == "__main__":
    app.run(debug=True)