import psycopg2
from flask import Flask, render_template, request

app = Flask(__name__)
connect = psycopg2.connect("dbname=tp user=postgres password=0307")
cur = connect.cursor()  # create cursor


def rating_update(c):
    if c >= 500000:
        return "gold"
    elif c >= 100000:
        return "silver"
    elif c >= 50000:
        return "bronze"
    else:
        return "welcome"



@app.route('/')
def main():
    return render_template("login.html")


@app.route('/return', methods=['post'])
def re_turn():
    return render_template("login.html")


@app.route('/login/', methods=['post'])
def login():
    id = request.form["id"]
    password = request.form["password"]
    send = request.form["send"]


    if send == "login":
        cur.execute("select * from users;")
        result = cur.fetchall()
        if (id, password) in result:
            cur.execute(
                "select subject_name, lecture_name, tutor from enrollment, subject where enrollment.code = subject.code group by subject_name, tutor, lecture_name having count(tutee) >= all(select count(tutee) from enrollment group by code, tutor, lecture_name);"
            )
            popular = cur.fetchall()
            print("popular: ", popular)
            cur.execute("select * from account where id = '{}';".format(id))
            accounts = cur.fetchall()
            cur.execute("select * from lecture;".format(id))
            lecs = cur.fetchall()
            print("lecs : ", lecs)
            return render_template(
                "main.html",
                popular=popular,
                accounts=accounts,
                lecs=lecs,
                ids=id,
                passwords=password,
            )
        else:
            return render_template("login.html")
    elif send == "sign up": return render_template("signup.html")


@app.route('/sign_up/', methods=['post'])
def sign_up():
    id = request.form["id"]
    password = request.form["password"]
    role = request.form["role"]
    send = request.form["send"]

    if send == "sign up":
        cur.execute("select * from users;")
        result = cur.fetchall()
        for i in result:
            if id == i[0]:
                print("ERROR, ID already exists")
                return render_template("signup.html")
        cur.execute("insert into users values('{}', '{}');".format(id, password))
        cur.execute(
            "insert into account values('{}', {}, '{}', '{}');".format(
                id, 10000, "welcome", role
            )
        )
        connect.commit()
        print("Success, Let's login")
        return render_template("login.html")



@app.route('/admin_function/', methods=['post'])
def admin_function():
    id = request.form["id"]
    password = request.form["password"]
    send = request.form["send"]

    if id == "admin" and password == "0000":
        if send == "users info":
            cur.execute("select * from account;")
            users = cur.fetchall()
            return render_template("admin_users_information.html", users=users, ids=id, passwords=password)
        elif send == "trades info":
            cur.execute("select * from enrollment;")
            enrollments = cur.fetchall()
            return render_template("admin_trades_information.html", enrollments=enrollments, ids=id, passwords=password)
    else: return render_template("login.html")


@app.route('/view_lecture/', methods=['post'])
def view_lecture():
    id = request.form["id"]
    password = request.form["password"]
    role = request.form["role"]
    send = request.form["send"]
    
    if send == "my info":
        if role == "tutee":
            cur.execute("select * from enrollment where tutee='{}';".format(id))
            lectures = cur.fetchall()
            print("lectures : ", lectures)

            return render_template("myinfo_tutee.html", lectures=lectures, ids=id, passwords=password)
        elif role == "tutor":
            cur.execute("select subject_name, s.code, name, tutor, price from subject s join lecture l on s.code = l.code where tutor ='{}';".format(id))
            my_lectures = cur.fetchall()
            print("my lectures : ", my_lectures)

            cur.execute("select subject_name, lecture_name, tutor, lecture_price from subject join enrollment on subject.code = enrollment.code where tutee = '{}';".format(id))
            r_lectures = cur.fetchall()

            return render_template("myinfo_tutor.html", my_lectures=my_lectures, r_lectures=r_lectures, ids=id, passwords=password)

@app.route('/user_info/', methods=['post'])
def user_info():
    send = request.form["send"]
    if send == "Logout":
        return render_template("login.html")

@app.route('/lectures/', methods=['post'])
def lectures():
    id = request.form["id"]
    password = request.form["id"]
    role = request.form["role"]
    send = request.form["send"]

    if send == "add":
        if role == "tutor":
            cur.execute("select * from subject;")
            subs= cur.fetchall()
            return render_template("add_lecture.html", subs=subs, ids=id, passwords=password)
        elif role == "tutee":
            print("You cannot access!")
            return render_template("login.html")



@app.route('/add_lecture/', methods=['post'])
def add_lectures():
    code = request.form["code"]
    name = request.form["name"]
    price = request.form["price"]
    tutor = request.form["id"]
    id = request.form["id"]
    password = request.form["password"]
    try:
        cur.execute("SELECT code FROM lecture WHERE code = '{}' AND name = '{}' AND price = '{}' AND tutor = '{}';".format(code, name, price,tutor))
        existing_lecture = cur.fetchall()

        if code not in existing_lecture:
            cur.execute("INSERT INTO lecture VALUES ('{}', '{}', '{}', '{}');".format(code, name, price, tutor))
            connect.commit()
            print("Lecture added successfully!")

    except psycopg2.errors.UniqueViolation:
        connect.rollback()
        print("Error!")
        cur.execute("select * from lecture;")
        ls = cur.fetchall()
        return render_template("add_error.html",ls=ls)

    return render_template("login.html")




@app.route('/register/', methods=['post'])
def register():
    id = request.form["id"]
    password = request.form["password"]
    code = request.form["code"]
    name = request.form["name"]
    price = request.form["price"]
    tutor = request.form["tutor"]
    send = request.form["send"]

    if send == "register":
        lecture = [code,name,price,tutor]
        cur.execute("select * from account where id = '{}';".format(id))
        member = cur.fetchall()
        credit = member[0][1]
        rating = member[0][2]
        cur.execute("select * from rating_info where rating = '{}';".format(rating))
        r_info = cur.fetchall()
        discount = r_info[0][2]
        price = int(price)
        discount_price = int(price * (discount/100))
        final_price = int(price - discount_price)

        cur.execute(
            "select tutee from enrollment where code = '{}' and lecture_name = '{}' and lecture_price = '{}' and tutor = '{}' and tutee='{}';".format(
                code, name, price, tutor, id))
        al_tutee = cur.fetchall()
        print("Fetched al_tutee:", al_tutee)


        if (id==tutor) or (credit < final_price):
            print("sorry, you cannot buy..")
            return render_template("login.html")
        elif any(id == row[0] for row in al_tutee):
            return render_template("login.html")

        return render_template("register.html", lecture=lecture, credit=credit, rating=rating, discount_price=discount_price, final_price = final_price, ids=id, passwords=password)


@app.route('/confirm/', methods=['post'])
def confirm():
    print("Form data Received: ", request.form)
    id = request.form["id"]
    password = request.form["password"]
    code = request.form["code"]
    name = request.form["name"]
    price = int(request.form["price"])
    final_price = int(request.form["final_price"])
    tutor = request.form["tutor"]
    credit = int(request.form["credit"])
    send = request.form["send"]

    if send == "confirm":
        print("Executing SQL: Updating credit")
        cur.execute("update account set credit = credit - '{}' where id = '{}';".format(final_price, id))
        cur.execute("update account set credit = credit + '{}' where id = '{}';".format(final_price, tutor))

        cur.execute("update account set rating = '{}' where id = '{}';".format(rating_update(credit-final_price),id))
        cur.execute("select * from account where id = '{}';".format(tutor))
        tutor_credit = cur.fetchall()[0][1]
        cur.execute("update account set rating = '{}' where id = '{}';".format(rating_update(tutor_credit+price),tutor))
        cur.execute("insert into enrollment values ('{}','{}','{}','{}', '{}');".format(id,tutor,code,name,price))
        print("Committing transaction")
        connect.commit()
        print("Committing transaction")
        cur.execute("select tutee, tutor, subject_name, lecture_name, lecture_price from enrollment e join subject s on e.code=s.code where tutee='{}';".format(id))
        enrolls = cur.fetchall()
        print("Enrollment data fetched:", enrolls)
        return render_template("confirm.html", enrolls=enrolls, ids=id, passwords=password)


if __name__ == '__main__':
    app.run()
