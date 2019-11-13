from flask import redirect, url_for,session
import connection
from psycopg2.extensions import AsIs
from datetime import datetime


@connection.connection_handler
def get_questions_fix(cursor):
    cursor.execute("""SELECT * FROM question ORDER BY submission_time DESC LIMIT 5;""")
    questions = cursor.fetchall()
    return questions

@connection.connection_handler
def get_questions(cursor):
    cursor.execute("""SELECT * FROM question ORDER BY submission_time DESC;""")
    questions = cursor.fetchall()
    return questions


@connection.connection_handler
def delete_question(cursor, question_id):
    cursor.execute("""DELETE FROM question WHERE id=%(id)s;""", {'id': question_id})


@connection.connection_handler
def get_latest5_questions(cursor, order, direction):

    cursor.execute("""SELECT * FROM question ORDER BY %(order)s %(direction)s;""", {"order": AsIs(order), "direction":AsIs(direction.upper())})

    questions = cursor.fetchall()
    return questions


@connection.connection_handler
def get_answers(cursor):
    cursor.execute("""SELECT * FROM answer ORDER BY submission_time DESC;""")
    answers = cursor.fetchall()
    return answers


@connection.connection_handler
def delete_answer(cursor, answer_id):
    cursor.execute("""DELETE FROM comment WHERE answer_id=%(answer_id)s;""", {'answer_id': answer_id})
    cursor.execute("""DELETE FROM answer WHERE id=%(answer_id)s;""", {'answer_id': answer_id})


@connection.connection_handler
def get_comments(cursor):
    cursor.execute("""SELECT * FROM comment ORDER BY submission_time DESC;""")
    comments = cursor.fetchall()
    return comments


@connection.connection_handler
def add_question(cursor, title, message,user_id):
    user_story = {
        'submission_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'view_number': 0,
        'vote_number': 0,
        'title': title,
        'message': message,
        'user_id':user_id,
        'image': ""
    }

    cursor.execute("""INSERT INTO question(submission_time, view_number, vote_number, title, message, image,user_id)
                      VALUES(%(submission_time)s, %(view_number)s, %(vote_number)s,
                      %(title)s, %(message)s, %(image)s,%(user_id)s);""",
                   user_story)

    cursor.execute("""SELECT id FROM question
                      ORDER BY id DESC
                      LIMIT 1;""")
    return cursor.fetchone()['id']


@connection.connection_handler
def add_answer(cursor, question_id, message,user_id):

    user_story = {
        'submission_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'vote_number': 0,
        'question_id': question_id,
        'message': message,
        'user_id': user_id,
        'image': ""
    }

    cursor.execute("""INSERT INTO answer(submission_time, vote_number, question_id, message, image,user_id)
                      VALUES(%(submission_time)s,%(vote_number)s,%(question_id)s, %(message)s,%(image)s,%(user_id)s);""",
                   user_story)


@connection.connection_handler
def add_comment(cursor, question_id, answer_id, message,user_id):
        user_story = {
            'submission_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'message': message,
            'answer_id': answer_id,
            'question_id': question_id,
            'user_id': user_id
        }

        cursor.execute("""INSERT INTO comment(submission_time, question_id, answer_id, message,user_id)
                          VALUES(%(submission_time)s,%(question_id)s, %(answer_id)s, %(message)s,%(user_id)s);""", user_story)



@connection.connection_handler
def delete_comments(cursor, comment_id):
    cursor.execute("""DELETE FROM comment WHERE id=%(comment_id)s;""", {'comment_id': comment_id})


@connection.connection_handler
def get_update(cursor, answer_id, message):
    time = datetime.now()
    cursor.execute("""UPDATE answer SET message = %(message)s,submission_time = %(time)s WHERE id=%(answer_id)s;""",
                   {"message": message, 'answer_id': answer_id, 'time': time})


@connection.connection_handler
def get_update_question(cursor, question_id, message, title):
    time = datetime.now()
    cursor.execute("""UPDATE question SET message = %(message)s,submission_time = %(time)s,title = %(title)s 
                        WHERE id=%(question_id)s;""",
                   {"message": message, 'question_id': question_id, 'time': time, 'title': title})


@connection.connection_handler
def get_update_for_comment(cursor, comment_id, message):
    time = datetime.now()
    cursor.execute("""UPDATE comment SET 
                      message = %(message)s, 
                      submission_time = %(time)s, 
                      edited_count = %(count)s 
                      WHERE id=%(comment_id)s;""",
                   {"message": message, 'comment_id': comment_id, 'time': time, 'count': 1})


@connection.connection_handler
def get_new_update_for_comment(cursor, comment_id, message):
    time = datetime.now()
    cursor.execute("""UPDATE comment SET 
                      message = %(message)s, 
                      submission_time = %(time)s, 
                      edited_count = edited_count + 1 
                      WHERE id=%(comment_id)s;""", {"message": message, 'comment_id': comment_id, 'time': time})


@connection.connection_handler
def get_question_id(cursor, answer_id):
    cursor.execute("""
                    SELECT * FROM answer
                    WHERE id=%(id)s LIMIT 1
                   """,
                   {'id': answer_id})
    return cursor.fetchone()['question_id']


@connection.connection_handler
def get_question_id_for_comment(cursor, comment_id):
    cursor.execute("""
                    SELECT * FROM comment
                    WHERE id=%(id)s LIMIT 1
                   """,
                   {'id': comment_id})
    return cursor.fetchone()['question_id']


@connection.connection_handler
def search_in(cursor, searched_word):
    cursor.execute("""SELECT question.* FROM question LEFT JOIN answer ON question.id = answer.question_id
                      WHERE (LOWER(title) LIKE %(searched_word)s OR LOWER(answer.message) LIKE %(searched_word)s 
                      OR LOWER(question.message) LIKE %(searched_word)s);""",
                   {'searched_word': '%' + searched_word + '%'})
    searched_data = cursor.fetchall()
    return searched_data


@connection.connection_handler
def vote_up_question(cursor, question_id):

    variables = {
        'question_id': question_id
    }

    cursor.execute("""UPDATE question
                      SET vote_number = vote_number+1
                      WHERE id = %(question_id)s;""", variables)


@connection.connection_handler
def vote_down_question(cursor, question_id):

    variables = {
        'question_id': question_id
    }

    cursor.execute("""UPDATE question
                      SET vote_number = vote_number-1
                      WHERE id = %(question_id)s;""", variables)


@connection.connection_handler
def vote_up_answer(cursor, question_id, answer_id):

    variables = {
        'question_id': question_id,
        'answer_id': answer_id
    }

    cursor.execute("""UPDATE answer
                      SET vote_number = vote_number+1
                      WHERE question_id = %(question_id)s AND id = %(answer_id)s;""", variables)


@connection.connection_handler
def vote_down_answer(cursor, question_id, answer_id):

    variables = {
        'question_id': question_id,
        'answer_id': answer_id
    }

    cursor.execute("""UPDATE answer
                      SET vote_number = vote_number-1
                      WHERE question_id = %(question_id)s AND id = %(answer_id)s;""", variables)


@connection.connection_handler
def registration(cursor, username, hashed_password):
    user_details = {
        'username': username,
        'password': hashed_password
    }
    cursor.execute("""INSERT INTO users(username, password)
                      VALUES(%(username)s, %(password)s);""", user_details)


@connection.connection_handler
def accept_answer(cursor, question_id, answer_id):

    variables = {
        'question_id': question_id,
        'answer_id': answer_id
    }

    cursor.execute("""UPDATE answer
                      SET acception = TRUE
                      WHERE question_id = %(question_id)s AND id = %(answer_id)s;""", variables)

@connection.connection_handler
def get_user_name(cursor, user_id):
    cursor.execute("""
                      SELECT * FROM users
                      WHERE id=%(id)s LIMIT 1
                       """,
                   {'id': user_id})
    return cursor.fetchone()['username']


@connection.connection_handler
def get_q_and_a_by_user(cursor):
    cursor.execute("""SELECT question.title,question.message AS question_message,answer.message AS answer_message, 
                      question.user_id
                      FROM (question INNER JOIN answer ON question.id=answer.question_id);
""")
    datas = cursor.fetchall()
    return datas

@connection.connection_handler
def get_answers_for_user(cursor):
    cursor.execute("""SELECT submission_time,message AS title,user_id,question_id AS id FROM answer 
    ORDER BY submission_time DESC;""")
    answers = cursor.fetchall()
    return answers\

@connection.connection_handler
def get_comment_for_user(cursor):
    cursor.execute("""SELECT submission_time,message AS title,user_id,question_id AS id FROM comment 
    ORDER BY submission_time DESC;""")
    answers = cursor.fetchall()
    return answers


@connection.connection_handler
def get_password_by_username(cursor, username):

    cursor.execute("""SELECT password FROM users
                      WHERE username = %(username)s;""", {'username': username})
    password = cursor.fetchone()
    if password is not None:
        return password['password']
    else:
        return None


@connection.connection_handler
def check_username(cursor, username):

    cursor.execute("""SELECT username FROM users
                      WHERE username = %(username)s;""", {'username': username})
    user = cursor.fetchone()
    if user is not None:
        return user['username']
    else:
        return None


@connection.connection_handler
def get_user_id_by_username(cursor, username):
    cursor.execute("""SELECT id FROM users WHERE username = %(username)s;""", {'username': username})

    user_id = cursor.fetchone()
    return user_id['id']


@connection.connection_handler
def get_users(cursor):
    cursor.execute("""SELECT * FROM users ORDER BY registration_date;""")
    users = cursor.fetchall()
    return users


@connection.connection_handler
def get_user_id_by_question_id(cursor, question_id):
    cursor.execute("""SELECT user_id FROM question WHERE id = %(question_id)s;""", {'question_id': question_id})
    user_id = cursor.fetchone()
    return user_id['user_id']

@connection.connection_handler
def validation(cursor,questions, get_id):
    try:
        get_user_id = get_user_id_by_username(session['username'])
    except KeyError:
        return False
    for question in questions:
        print(question['id'])
        print(get_id)
        print(question['user_id'])
        print(get_user_id)
        if int(question['id']) == int(get_id) and int(question['user_id']) == int(get_user_id):
            return True
