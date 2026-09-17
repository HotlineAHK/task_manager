from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "secret"

db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    done = db.Column(db.Boolean, default=False)
    category = db.Column(db.String, nullable=False)

class TaskForm(FlaskForm):
    title = StringField("Название", validators=[DataRequired()])
    description = TextAreaField("Описание", validators=[DataRequired()])
    category = StringField("Категория", validators=[DataRequired()])
    submit = SubmitField("Сохранить")

@app.route("/")
def index():
    c = request.args.get("category")
    s = request.args.get("sort")
    q = Task.query
    
    if c:
        q = q.filter_by(category=c)
        
    if s == "done":
        q = q.order_by(Task.done.desc())
    elif s == "undone":
        q = q.order_by(Task.done.asc())
        
    tasks = q.all()
    
    done_count = Task.query.filter_by(done=True).count()
    undone_count = Task.query.filter_by(done=False).count()
    cats = [cat[0] for cat in db.session.query(Task.category).distinct().all()]
    
    return render_template("index.html", tasks=tasks, d=done_count, u=undone_count, cats=cats)

@app.route("/add", methods=["GET", "POST"])
def add():
    form = TaskForm()
    if form.validate_on_submit():
        t = Task(title=form.title.data, description=form.description.data, category=form.category.data)
        db.session.add(t)
        db.session.commit()
        return redirect("/")
    return render_template("form.html", form=form, title="Добавить задачу")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    t = Task.query.get(id)
    form = TaskForm(obj=t)
    if form.validate_on_submit():
        t.title = form.title.data
        t.description = form.description.data
        t.category = form.category.data
        db.session.commit()
        return redirect("/")
    return render_template("form.html", form=form, title="Редактировать задачу")

@app.route("/toggle/<int:id>")
def toggle(id):
    t = Task.query.get(id)
    t.done = not t.done
    db.session.commit()
    return redirect("/")

@app.route("/delete/<int:id>")
def delete(id):
    t = Task.query.get(id)
    db.session.delete(t)
    db.session.commit()
    return redirect("/")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
