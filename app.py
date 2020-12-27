from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField
from wtforms.validators import InputRequired, length, regexp
import json
import random

app = Flask(__name__)
app.secret_key = "L33T133713371337L33T"

with open("teachers.json") as f:
    teachers = json.load(f)

with open("goals.json") as f:
    goals = json.load(f)

days = {"mon": "Понедельник", "tue": "Вторник", "wed": "Среда", "thu": "Четверг", "fri": "Пятница",
        "sat": "Суббота", "sun": "Воскресенье"}


class RequestForm(FlaskForm):
    goals_list = []
    for goal, name in goals.items():
        goals_list.append((goal, name))
    goal = RadioField("Цель занятий?", choices=goals_list,
                      validators=[InputRequired("Выберите цель занятий!")])
    free_time = RadioField("Сколько готовы уделять?", choices=[("1-2 часа в неделю", "1-2 часа в неделю"),
                                                               ("3-5 часов в неделю", "3-5 часов в неделю"),
                                                               ("5-7 часов в неделю", "5-7 часов в неделю"),
                                                               ("7-10 часов в неделю", "7-10 часов в неделю")],
                           validators=[InputRequired("Выберите свободное время!")])

    name = StringField("Вас зовут", validators=[InputRequired("Введите своё имя!"),
                                                length(min=2, message="Имя не может быть меньше 2 символов!")])

    # regexp https://wtforms.readthedocs.io/en/stable/_modules/wtforms/validators/#Regexp
    phone = StringField("Ваш телефон", validators=[InputRequired("Введите ваш номер!"),
                                                   regexp(
                                                       "^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$",
                                                       message="Некорректный номер телефона!")])


class BookingForm(FlaskForm):
    client_name = StringField("Ваше имя", validators=[InputRequired("Введите своё имя!"),
                                                      length(min=3,
                                                             message="Имя не может быть меньше 2 символов!")])
    client_phone = StringField("Ваш номер телефона", validators=[InputRequired("Введите свой номер телефона!"),
                                                                 regexp(
                                                                     "^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,"
                                                                     "10}$",
                                                                     message="Вы ввели некорректный номер телефона!")])


def update_requests(goal, free_time, name, phone):
    with open("request.json", "r") as f:
        requests = json.load(f)
    requests.append({"goal": goal, "free": free_time, "name": name, "phone": phone})
    with open("request.json", "w") as f:
        json.dump(requests, f)


def update_bookings(teacher_id, name, phone, weekday, time):
    with open("booking.json", "r") as f:
        requests = json.load(f)
    requests.append({"teacher_id": teacher_id, "name": name, "phone": phone, "weekday": weekday, "time": time})
    with open("booking.json", "w") as f:
        json.dump(requests, f)


@app.route("/")
def main():
    random.shuffle(teachers)
    # вывожу рандомно 6 учителей
    return render_template("index.html", goals=goals, teachers=teachers[:6])


@app.route("/all/")
def all_teachers():
    # здесь просто выводим главную страничку без обреза списка учителей
    return render_template("index.html", goals=goals, teachers=teachers)


@app.route("/goals/<goal>/")
def goals_page(goal):
    teachers_goal = list()
    for teacher in teachers:
        if goal in teacher["goals"]:
            teachers_goal.append(teacher)
    return render_template("goal.html", goals=goals, goal=goal, teachers=teachers_goal)


@app.route("/request/", methods=["GET", "POST"])
def request_view():
    form = RequestForm()
    if request.method == "POST":
        if form.validate_on_submit():
            goal = goals[form.goal.data]
            free_time = form.free_time.data
            name = form.name.data
            phone = form.phone.data
            update_requests(goal, free_time, name, phone)
            return render_template("request_done.html", goal=goal, free_time=free_time, name=name, phone=phone)
    return render_template("request.html", form=form)


@app.route("/request_done/")
def request_done():
    pass


@app.route("/profile/<int:teacher_id>/")
def profile_teacher(teacher_id):
    for teacher_name in teachers:
        if teacher_name["id"] == teacher_id:
            teacher = teacher_name
    return render_template("profile.html", days=days, goals=goals, teacher=teacher)


@app.route("/booking/<int:teacher_id>/<day>/<time>/", methods=["GET", "POST"])
def booking_form(teacher_id, day, time):
    time = time[:2] + time[2:].replace("00", ":00")
    for teacher_name in teachers:
        if teacher_name["id"] == teacher_id:
            teacher = teacher_name
    form = BookingForm()
    if request.method == "POST":
        if form.validate_on_submit():
            client_name = form.client_name.data
            client_phone = form.client_phone.data
            update_bookings(teacher_id, client_name, client_phone, day, time)
            return render_template("booking_done.html", client_name=client_name, client_phone=client_phone,
                                   client_weekday=days[day], client_time=time)
    return render_template("booking.html", form=form, day=day, dayname=days[day], time=time, teacher_id=teacher_id,
                           teacher=teacher)


@app.errorhandler(404)
def render_not_found(error):
    return "Ничего не нашлось! Вот неудача, отправляйтесь на главную!"


@app.errorhandler(500)
def render_server_error(error):
    return "Что-то не так, но мы все починим"


if __name__ == '__main__':
    app.run()
