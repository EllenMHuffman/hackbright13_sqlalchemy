"""Hackbright Project Tracker.

A front-end for a database that allows users to work with students, class
projects, and the grades students receive in class projects.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()


def connect_to_db(app):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///hackbright'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


def get_student_by_github(github):
    """Given a GitHub account name, print info about the matching student."""

    QUERY = """
        SELECT first_name, last_name, github
        FROM students
        WHERE github = :github
        """

    db_cursor = db.session.execute(QUERY, {'github': github})

    row = db_cursor.fetchone()

    print "Student: {first} {last}\nGitHub account: {acct}".format(
        first=row[0], last=row[1], acct=row[2])


def make_new_student(first_name, last_name, github):
    """Add a new student and print confirmation.

    Given a first name, last name, and GitHub account, add student to the
    database and print a confirmation message.
    """

    QUERY = """
        INSERT INTO students (first_name, last_name, github)
        VALUES (:first_name, :last_name, :github)
        """

    db.session.execute(QUERY, {'first_name': first_name,
                               'last_name': last_name,
                               'github': github})

    db.session.commit()

    print "Successfully added student: {first} {last}".format(first=first_name,
                                                              last=last_name)


def get_project_by_title(title):
    """Given a project title, print information about the project."""

    QUERY = """
            SELECT id, title, description, max_grade
            FROM projects
            WHERE title = :title
            """

    db_cursor = db.session.execute(QUERY, {'title': title})
    result = db_cursor.fetchall()

    for row in result:
        print "id: {id}, title: {title},\ndescription: {description},\
            \nmax grade: {max_grade}".format(id=row[0], title=row[1],
                            description=row[2], max_grade=row[3])


def get_grade_by_github_title(github, title):
    """Print grade student received for a project."""

    QUERY = """
            SELECT ROUND(AVG(grade), 2)
            FROM grades
            WHERE project_title = :title AND student_github = :github
            """

    db_cursor = db.session.execute(QUERY, {"github": github, "title": title})
    result = db_cursor.fetchone()

    # result = db_cursor.fetchall()

    print "{github} received a score of {score}".format(github=github,
               score=result[0])

    # for row in result:
    # print "{github} received a score of {score}".format(github=github,
    #            score=row[0])


def assign_grade(github, title, grade):
    """Assign a student a grade on an assignment and print a confirmation."""

    QUERY = """
            INSERT INTO grades (student_github, project_title, grade)
            VALUES (:github, :title, :grade)
            """

    db.session.execute(QUERY, {'github': github,
                               'title': title,
                               'grade': grade})

    db.session.commit()

    print "Grade has been added for {title}".format(title=title)


def handle_input():
    """Main loop.

    Repeatedly prompt for commands, performing them, until 'quit' is received as a
    command."""

    command = None

    while command != "quit":
        input_string = raw_input("HBA Database> ")
        tokens = input_string.split()
        command = tokens[0]
        args = tokens[1:]

        if command == "student":
            github = args[0]
            get_student_by_github(github)

        elif command == "new_student":
            first_name, last_name, github = args  # unpack!
            make_new_student(first_name, last_name, github)

        elif command == 'get_project_by_title':
            title = args[0]
            get_project_by_title(title)

        elif command == 'get_grade_by_github_title':
            github = args[0]
            title = args[1]
            get_grade_by_github_title(github, title)

        elif command == 'assign_grade':
            github = args[0]
            title = args[1]
            grade = args[2]
            assign_grade(github, title, grade)

        else:
            if command != "quit":
                print "Invalid Entry. Try again."


if __name__ == "__main__":
    connect_to_db(app)

    handle_input()

    # To be tidy, we close our database connection -- though,
    # since this is where our program ends, we'd quit anyway.

    db.session.close()
