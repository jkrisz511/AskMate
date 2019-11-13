from flask import Flask, render_template, redirect, url_for, request, session
import bcrypt
import data_manager
from datetime import timedelta


app = Flask(__name__)


app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)


@app.route('/')
def route_index():
    return render_template('index.html',  title="Welcome!")


@app.route('/list')
def route_main():
    stored_questions = data_manager.get_questions_fix()
    return render_template('list.html', questions=stored_questions, title="Welcome!")


@app.route('/list', methods=['GET'])
def route_list():
    stored_questions = data_manager.get_questions_fix()
    if request.method == "GET":
        order = request.args.get('order_by')
        direction = request.args.get('direction')
        if order is None:
            order = 'submission_time'
            direction = 'desc'
        stored_questions = data_manager.get_latest5_questions(order, direction)
    return render_template('list.html', questions=stored_questions, title="Welcome!")


@app.route('/question/<int:question_id>')
def route_question_id(question_id):
    stored_questions = data_manager.get_questions()
    stored_answers = data_manager.get_answers()
    stored_comments = data_manager.get_comments()
    user_id = data_manager.get_user_id_by_question_id(question_id)

    return render_template('questiondetails.html',
                           questions=stored_questions,
                           answers=stored_answers,
                           id=question_id,
                           comments=stored_comments,
                           question_id=question_id,
                           user_id=user_id)


@app.route('/question/<question_id>/delete', methods=['GET', 'POST'])
def delete_question(question_id):
    questions = data_manager.get_questions()
    if data_manager.validation(questions, question_id):
        if request.method == "POST":
            data_manager.delete_question(question_id)
            return redirect(url_for('route_list'))
    else:
        return redirect(url_for('route_main'))


@app.route('/question/<int:question_id>/new-answer', methods=['GET', 'POST'])
def route_new_answer(question_id):
    if 'username' in session:
        if request.method == "POST":
            user_id = data_manager.get_user_id_by_username(session['username'])
            data_manager.add_answer(question_id, request.form["answer"],user_id)
            return redirect(url_for('route_question_id', question_id=question_id))

        return render_template('answer.html', title="Add New Answer!", question_id=question_id)
    else:
        return redirect(url_for('login'))


@app.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id):
    questions = data_manager.get_questions()
    if data_manager.validation(questions, question_id):
        if request.method == "POST":
            new_message = request.form['message']
            new_title = request.form['title']
            data_manager.get_update_question(question_id, new_message, new_title)
            return redirect(f'/question/{question_id}')

        return render_template('edit_question.html', questions=questions, question_id=question_id)

    return redirect(url_for('route_main'))


@app.route('/answer/<int:answer_id>/edit', methods=['GET', 'POST'])
def edit_answer(answer_id):
    answers = data_manager.get_answers()
    question_id = data_manager.get_question_id(answer_id)
    if data_manager.validation(answers, answer_id):
        if request.method == "POST":
            new_message = request.form['answer']
            data_manager.get_update(answer_id, new_message)
            return redirect(f'/question/{question_id}')
        return render_template('edit_answer.html', answer_id=answer_id, answers=answers)
    return redirect(url_for('route_main'))


@app.route('/answer/<answer_id>/delete', methods=['GET', 'POST'])
def delete_answer(answer_id):
    answers = data_manager.get_answers()
    if data_manager.validation(answers, answer_id):
        if request.method == "POST":
            data_manager.delete_answer(answer_id)
            return redirect(url_for('route_list'))
    return redirect(url_for('route_main'))


@app.route("/add-question", methods=["GET", "POST"])
def add_question():
    if 'username' in session:
        if request.method == "POST":
            user_id=data_manager.get_user_id_by_username(session['username'])
            user_story_id = data_manager.add_question(request.form["question-title"], request.form["new-question"],user_id)
            return redirect(url_for('route_question_id',  question_id=user_story_id))
    else:
        return redirect(url_for('login'))
    return render_template("newquestion.html")


@app.route('/question/<question_id>/new-comment', methods=['GET', 'POST'])
@app.route('/answer/<answer_id>/new-comment', methods=['GET', 'POST'])
def route_new_comment(question_id='', answer_id=''):
    if 'username' in session:
        if request.method == "POST":
            user_id = data_manager.get_user_id_by_username(session['username'])
            if question_id == '':
                data_manager.add_comment(str(data_manager.get_question_id(answer_id)), answer_id, request.form["comment"],user_id)
                return redirect(url_for('route_list'))
            elif answer_id == '':
                data_manager.add_comment(question_id,None, request.form["comment"],user_id)
                return redirect(url_for('route_list'))
        return render_template('newcomment.html', title="Add New Comment!", answer_id=answer_id, question_id=question_id)
    else:
        return redirect(url_for('route_main'))


@app.route('/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
def edit_comment(comment_id):
    comments = data_manager.get_comments()
    if data_manager.validation(comments, comment_id):
        if request.method == "POST":
            edit_counter = ''
            for comment in comments:
                if comment['id'] == comment_id:
                    edit_counter = comment['edited_count']
            if edit_counter is None:
                new_message = request.form['comment']
                data_manager.get_update_for_comment(comment_id, new_message)
                return redirect(url_for('route_main'))
            elif edit_counter is not None:
                new_message = request.form['comment']
                data_manager.get_new_update_for_comment(comment_id, new_message)
                return redirect(url_for('route_main'))
        return render_template('edit_comment.html', comment_id=comment_id, comments=comments)
    return redirect(url_for('route_main'))


@app.route('/comments/<comment_id>/delete', methods=['GET', 'POST'])
def delete_comment(comment_id):
    comments = data_manager.get_comments()
    if data_manager.validation(comments, comment_id):
            if request.method == "POST":
                data_manager.delete_comments(comment_id)
                return redirect(url_for('route_main'))

    return redirect(url_for('route_main'))


@app.route("/search")
def search():
    searched_word = request.args.get('q').lower()
    if searched_word is not None:
        questions = data_manager.search_in(searched_word)
        updated_questions = []
        for question in questions:
            if question not in updated_questions:
                updated_questions.append(question)
        print(updated_questions)

        return render_template('search.html', searched_word=searched_word, questions=updated_questions)
    return redirect(url_for('route_list'))


@app.route("/question/<int:question_id>/vote-up", methods=['GET', 'POST'])
def vote_up_question(question_id):
    if request.method == 'POST':
        data_manager.vote_up_question(question_id)
        return redirect(url_for('route_question_id', question_id=question_id))


@app.route("/question/<int:question_id>/vote-down", methods=['GET', 'POST'])
def vote_down_question(question_id):
    if request.method == 'POST':
        data_manager.vote_down_question(question_id)
        return redirect(url_for('route_question_id', question_id=question_id))


@app.route("/question/<int:question_id>/<int:answer_id>/vote-up", methods=['GET', 'POST'])
def vote_up_answer(question_id, answer_id):
    if request.method == 'POST':
        data_manager.vote_up_answer(question_id, answer_id)
        return redirect(url_for('route_question_id', question_id=question_id))


@app.route("/question/<int:question_id>/<int:answer_id>/vote-down", methods=['GET', 'POST'])
def vote_down_answer(question_id, answer_id):
    if request.method == 'POST':
        data_manager.vote_down_answer(question_id, answer_id)
        return redirect(url_for('route_question_id', question_id=question_id))


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if session.get('username') is not None:
            return redirect(url_for('loginerror'))
        else:
            return render_template('login.html', error=None)
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = data_manager.get_password_by_username(username)
        if hashed_password is not None:
            hashed_password = hashed_password.encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password) is True:
                session['username'] = username
                session['user_id'] = int(data_manager.get_user_id_by_username(username))
                session.permanent = True
                return redirect(url_for('route_main'))
            else:
                return render_template('login.html', error="not valid")
        else:
            return render_template('login.html', error="not valid")


@app.route("/registration", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        if session.get('username') is not None:
            return redirect(url_for('loginerror'))
        else:
            return render_template('register.html', error=None)
    elif request.method == 'POST':
        username = request.form['username']
        if data_manager.check_username(username) == username:
            return render_template('register.html', error="taken")
        else:
            password = request.form['password']
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            hashed_password = hashed_password.decode('utf-8')
            data_manager.registration(username, hashed_password)
            return redirect(url_for('route_main'))


@app.route("/user/<int:user_id>/")
def profile(user_id):
    stored_questions = data_manager.get_questions()
    user_name = data_manager.get_user_name(user_id)
    return render_template('user_profile.html', questions=stored_questions, user_id=user_id,user_name=user_name)


@app.route("/user/<int:user_id>/<type>")
def profile_question(user_id,type):
    try:
        get_user_id = data_manager.get_user_id_by_username(session['username'])
    except KeyError:
        return redirect(url_for('route_main'))

    if get_user_id == user_id:
        if type == "question":
            some_data = data_manager.get_questions()
        elif type == "answer":
            some_data = data_manager.get_answers_for_user()
        elif type == "comment":
            some_data = data_manager.get_comment_for_user()
        user_name = data_manager.get_user_name(user_id)
        return render_template('user_profile.html', datas=some_data, user_id=user_id, user_name=user_name)
    else:
        return redirect(url_for('route_main'))


@app.route("/question/<int:question_id>/<int:answer_id>/accept-answer", methods=['GET', 'POST'])
def accept_answer(question_id, answer_id):
    if request.method == 'POST':
        data_manager.accept_answer(question_id, answer_id)
        return redirect(url_for('route_question_id', question_id=question_id))


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('route_main'))


@app.route('/users')
def route_users():
    stored_users = data_manager.get_users()
    return render_template('users_list.html', users=stored_users, title="Welcome!")


@app.route('/loginerror')
def loginerror():
    return render_template('loginerror.html')


if __name__ == "__main__":
    app.run(
        debug=True,
        port=8000
    )
