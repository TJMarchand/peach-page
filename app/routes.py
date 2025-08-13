"""
Flask routes for the forum. Uses the clean logic.py API.
"""

from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from . import logic

main = Blueprint("main", __name__)


# Decorator connects index function to webpage with route "/". index is called whenever we are at "/" and request is "GET" or "POST".
@main.route("/", methods=["GET", "POST"])
def index():
    user = session.get("username")
    threads = logic.get_threads()
    # Don't understand line below
    current_thread = logic.get_current_thread() or (threads[0] if threads else None)

    # POST actions: post message, delete message, start thread, change thread
    if request.method == "POST":
        action = request.form.get("action")

        if action == "post":
            if not user:
                flash("Please login to post.")
                return redirect(url_for("main.login"))
            # .strip removes any start and end white spaces in message.
            content = request.form.get("content", "").strip()
            if content:
                logic.save_message(user, content, thread=current_thread)

        elif action == "thread":
            if not user:
                flash("Please login to start a thread.")
                return redirect(url_for("main.login"))
            new_thread = request.form.get("content", "").strip()
            if new_thread:
                created = logic.start_thread(new_thread)
                logic.set_current_thread(new_thread)

        elif action == "change_thread":
            new_thread = request.form.get("new_thread")
            if new_thread:
                logic.set_current_thread(new_thread)
        
        elif action == "delete":
            message_id = request.form.get("message_id")
            try:
                m_id = int(message_id)
            except (TypeError, ValueError):
                m_id = None
            if user and logic.is_admin(user) and m_id is not None:
                logic.delete_message(current_thread, m_id)

        return redirect(url_for("main.index"))  # Prevent re-posting on refresh
    
    # GET: render page
    messages = logic.get_messages_for_thread(current_thread)
    # Have to return to send things back to browser. It is what Flask sends to browser.
    return render_template("index.html",
                           messages=messages,
                           current_thread=current_thread,
                           threads=threads, user=user,
                           admin=logic.is_admin(user))


@main.route("/register", methods=["GET", "POST"])
def register():
    prev_username = ""
    user = session.get("username")
    user_exist = False
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        prev_username = username
        if logic.save_user(username, password, admin=False):
            session["username"] = username
            return redirect(url_for("main.index"))
        else:
            user_exist = True
    # If request.method == "GET", we didn't return yet. So we want to simply render the template.
    return render_template("register.html", user=user, user_exist=user_exist, prev_username=prev_username)


@main.route("/login", methods=["GET", "POST"])
def login():
    prev_username = ""
    user = session.get("username")
    non_exist = False
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        prev_username = username
        if logic.verify_user(username, password):
            session["username"] = username
            return redirect(url_for("main.index"))
        else:
            return render_template("login.html", non_exist=True, prev_username=prev_username)
        
    return render_template("login.html", user=user, non_exist=non_exist, prev_username=prev_username)


@main.route("/logout_forum")
def logout_forum():
    session.pop("username", None)
    return redirect(url_for("main.index"))


@main.route("/logout_login")
def logout_login():
    session.pop("username", None)
    return redirect(url_for("main.login"))


@main.route("/logout_register")
def logout_register():
    session.pop("username", None)
    return redirect(url_for("main.register"))


@main.route("/userlist", methods=["GET"])
def userlist():
    users = list(logic.load_users().keys())
    return render_template("userlist.html", users=users)


"""
main is an instance of the class Blueprint.
Inside this instance is stored essentially a list of routes (like "/") with corresponding method and function (like "GET" and index())

main.route is a method which takes as arguments a path ("/"), and a list (["GET", "POST"]). It returns a function.
This function is used as decorator function, as @main.route(...).

The decorator function is essentially equal to setting index=decorator(index).
In our case the decorator function essentially just stores the function passed to it in the list of the main instance.
It then simply returns the original function so that the original function is unaffected.
"""