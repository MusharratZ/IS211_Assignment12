from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from auth import login_required
from db import get_db

bp = Blueprint("class_app", __name__)


# index bp
@bp.route("/dashboard")
def index():
    db = get_db()
    # user_id = g.user["id"]
    # lists = db.execute(
    #     "SELECT p.id, title, complete, created, user_id, username"
    #     " FROM todo p JOIN user u ON p.user_id = u.id"
    #     " WHERE p.user_id = ?"
    #     " ORDER BY created ASC",
    #     (user_id,),
    # ).fetchall()
    students = db.execute("SELECT * FROM Students").fetchall()
    quizes = db.execute("SELECT * FROM Quizes ").fetchall()
    return render_template(
        "class/dashboard.html",
        students=students,
        quizes=quizes,
    )


# create pb
@bp.route("/student/add", methods=("GET", "POST"))
@login_required
def create_students():
    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        # body = request.form["body"]
        error = None

        if not firstname:
            error = "Firstname is required."
        if not lastname:
            error = "Lastname is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO Students (firstname,  lastname)" " VALUES (?,  ?)",
                (firstname, lastname),
            )
            db.commit()
            return redirect(url_for("class_app.index"))

    return render_template("class/create_students.html")


# create pb
@bp.route("/quiz/add", methods=("GET", "POST"))
@login_required
def create_quizes():
    if request.method == "POST":
        title = request.form["title"]
        questions = request.form["questions"]
        date = request.form["date_given"]
        error = None

        if not title:
            error = "title is required."
        if not questions:
            error = "questions is required."
        if not date:
            error = "Date is required"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO Quizes (title,  questions,date_given)" " VALUES (?, ?, ?)",
                (title, questions, date),
            )
            db.commit()
            return redirect(url_for("class_app.index"))

    return render_template("class/create_quizes.html")


# getting student results
@bp.route("/student/<int:id>")
def view_student_results(id):
    student_results = get_student_results(id)
    if student_results["student"] is None:
        abort(404, f"Student id {id} doesn't exist.")

    return render_template("class/student_results.html", **student_results)


def get_student_results(student_id):
    student = (
        get_db()
        .execute(
            "SELECT id, firstname, lastname FROM Students WHERE id = ?",
            (student_id,),
        )
        .fetchone()
    )

    results = (
        get_db()
        .execute(
            "SELECT r.id, q.title, q.date_given, r.score, r.created"
            " FROM Results r JOIN Quizes q ON r.quiz_id = q.id"
            " WHERE r.student_id = ?",
            (student_id,),
        )
        .fetchall()
    )

    return {"student": student, "results": results}


# adding student reslts
@bp.route("/results/add", methods=("GET", "POST"))
@login_required
def add_quiz_result():
    if request.method == "POST":
        student_id = request.form["student_id"]
        quiz_id = request.form["quiz_id"]
        score = request.form["score"]
        error = None

        if not student_id or not quiz_id or not score:
            error = "All fields are required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO Results (student_id, quiz_id, created, score)"
                " VALUES (?, ?, CURRENT_TIMESTAMP, ?)",
                (student_id, quiz_id, score),
            )
            db.commit()
            return redirect(url_for("class_app.index"))
    db = get_db()
    students = db.execute("SELECT * FROM Students").fetchall()
    quizes = db.execute("SELECT * FROM Quizes ").fetchall()

    return render_template("class/add_results.html", students=students, quizes=quizes)


# getting a single student
def get_student(id, check_author=True):
    student = (
        get_db()
        .execute(
            "SELECT id, created, firstname, lastname" " FROM Students" " WHERE id = ?",
            (id,),
        )
        .fetchone()
    )

    if student is None:
        abort(404, f"Student id {id} doesn't exist.")

    return student


# update bp
@bp.route("/student/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    student = get_student(id)

    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]

        error = None

        if not firstname or not lastname:
            error = "First name and last name are required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE Students SET firstname = ?, lastname = ? WHERE id = ?",
                (firstname, lastname, id),
            )
            db.commit()
            return redirect(url_for("class_app.index"))

    return render_template("class/update_students.html", student=student)


# delete student
@bp.route("/student/<int:id>/delete", methods=("POST",))
@login_required
def delete_student(id):
    get_student(id)
    db = get_db()
    db.execute("DELETE FROM Students WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("class_app.index"))


# get quizes
def get_quiz(id, check_author=True):
    quiz = (
        get_db()
        .execute(
            "SELECT * FROM Quizes WHERE id = ?",
            (id,),
        )
        .fetchone()
    )

    if quiz is None:
        abort(404, f" Quiz id {id} doesn't exist.")

    return quiz


# # update bp
@bp.route("/quiz/<int:id>/update", methods=("GET", "POST"))
@login_required
def update_quiz(id):
    quiz = get_quiz(id)

    if request.method == "POST":
        title = request.form["title"]
        questions = request.form["questions"]
        date_given = request.form["date_given"]
        error = None

        if not title or not questions or not date_given:
            error = "All fields are required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE Quizes SET title = ?, questions = ?, date_given = ? WHERE id = ?",
                (title, questions, date_given, id),
            )
            db.commit()
            return redirect(url_for("class_app.index"))

    return render_template("class/update_quiz.html", quiz=quiz)


# delete quiz
@bp.route("/quiz/<int:id>/delete", methods=("POST",))
@login_required
def delete_quiz(id):
    get_quiz(id)
    db = get_db()
    db.execute("DELETE FROM Quizes WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("class_app.index"))


# get result
def get_result(id, check_author=True):
    result = (
        get_db()
        .execute(
            "SELECT * FROM Results WHERE id = ?",
            (id,),
        )
        .fetchone()
    )

    if result is None:
        abort(404, f"result id {id} doesn't exist.")

    return result


# # update rsults bp
@bp.route("/results/<int:id>/update", methods=("GET", "POST"))
@login_required
def update_results(id):
    result = get_result(id)

    if result is None:
        abort(404, f"Result id {id} doesn't exist.")

    if request.method == "POST":
        score = request.form["score"]
        error = None

        if not score:
            error = "Score is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute("UPDATE Results SET score = ? WHERE id = ?", (score, id))
            db.commit()
            return redirect(url_for("class_app.index"))

    return render_template("class/update_students_results.html", result=result)


@bp.route("/results/<int:id>/delete", methods=("POST",))
@login_required
def delete_result(id):
    get_result(id)
    db = get_db()
    db.execute("DELETE FROM Results WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("class_app.index"))