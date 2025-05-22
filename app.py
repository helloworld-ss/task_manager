from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Task {self.id}>'


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['task_content']
        new_task = Todo(task=task_content)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'
    tasks = Todo.query.order_by(Todo.date_created).all()
    return render_template('index.html', tasks=tasks)


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Todo.query.order_by(Todo.date_created).all()
    return jsonify([{'id': task.id, 'task': task.task, 'date_created': task.date_created} for task in tasks])


@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    new_task = Todo(task=data['task'])
    try:
        db.session.add(new_task)
        db.session.commit()
        return jsonify({'message': 'Task added successfully'}), 201
    except:
        return jsonify({'error': 'Could not add task'}), 500


@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Todo.query.get_or_404(id)
    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted successfully'})
    except:
        return jsonify({'error': 'Could not delete task'}), 500


@app.route('/api/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    task = Todo.query.get_or_404(id)
    data = request.get_json()
    task.task = data['task']
    try:
        db.session.commit()
        return jsonify({'message': 'Task updated successfully'})
    except:
        return jsonify({'error': 'Could not update task'}), 500


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.task = request.form['task_content']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'
    else:
        return render_template('update.html', task=task)


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
