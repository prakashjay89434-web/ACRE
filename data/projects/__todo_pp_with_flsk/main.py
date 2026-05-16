from flask import Flask, render_template, request, redirect, url_for
from models import TaskModel
from service import TaskService
from forms import TaskForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SECRET_KEY'] = 'your_secret_key'

@app.before_first_request
def init_db():
    with app.app_context():
        db.create_all()

@app.route('/')
def index():
    tasks = TaskService.get_tasks()
    return render_template('index.html', tasks=tasks)

@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    form = TaskForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        task = TaskModel(title=form.title.data, description=form.description.data)
        TaskService.create_task(task)
        return redirect(url_for('index'))
    return render_template('add_task.html', form=form)

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = TaskModel.query.get_or_404(task_id)
    form = TaskForm(request.form, obj=task)
    if request.method == 'POST' and form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        TaskService.update_task(task)
        return redirect(url_for('index'))
    return render_template('edit_task.html', form=form)

@app.route('/delete_task/<int:task_id>', methods=['GET'])
def delete_task(task_id):
    task = TaskModel.query.get_or_404(task_id)
    TaskService.delete_task(task)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)