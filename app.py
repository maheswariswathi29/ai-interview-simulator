from flask import Flask, render_template, request, redirect, session
import sqlite3


app = Flask(__name__)

app.secret_key = "secretkey123"



# ==========================
# DEMO USERS
# ==========================

users = {

    "admin":"1234"

}



# ==========================
# INTERVIEW QUESTIONS
# ==========================


questions = {


"python":[

"What is Python?",

"Difference between List and Tuple?",

"Explain Exception Handling.",

"What is Object Oriented Programming?",

"Explain Lambda Functions."

],



"java":[

"What is Java?",

"What is JVM?",

"What is JDK and JRE?",

"Explain OOP concepts in Java.",

"Difference between Interface and Abstract Class."

],




"c":[

"What is C Programming?",

"What are pointers?",

"Explain Arrays.",

"What is Recursion?"

],





"hr":[

"Tell me about yourself.",

"Why should we hire you?",

"What are your strengths?",

"Where do you see yourself after 5 years?"

],




"project":[

"Explain your final year project.",

"Why did you choose this technology?",

"What challenges did you face during project development?"

]


}







# ==========================
# DATABASE
# ==========================


def init_db():

    conn = sqlite3.connect("interview.db")

    cursor = conn.cursor()


    cursor.execute("""

    CREATE TABLE IF NOT EXISTS results(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        question TEXT,

        answer TEXT,

        confidence INTEGER,

        communication INTEGER,

        feedback TEXT

    )

    """)



    conn.commit()

    conn.close()





init_db()








# ==========================
# HOME
# ==========================


@app.route("/")
def home():

    return render_template("index.html")







# ==========================
# LOGIN
# ==========================


@app.route("/login",methods=["GET","POST"])
def login():


    if request.method=="POST":


        username=request.form["username"]

        password=request.form["password"]




        if username in users and users[username]==password:



            conn=sqlite3.connect("interview.db")

            cursor=conn.cursor()


            cursor.execute(
                "DELETE FROM results"
            )


            conn.commit()

            conn.close()



            session["user"]=username

            session["q_index"]=0



            return redirect("/select_category")



        else:

            return "Invalid username or password"



    return render_template("login.html")








# ==========================
# CATEGORY
# ==========================


@app.route("/select_category")
def select_category():


    if "user" not in session:

        return redirect("/login")



    return render_template(
        "select_category.html"
    )








# ==========================
# SET CATEGORY
# ==========================


@app.route("/set_category/<category>")
def set_category(category):


    if category not in questions:

        return redirect("/select_category")



    session["category"]=category


    session["selected_questions"]=questions[category]


    session["q_index"]=0


    session["feedback"]=""



    return redirect("/interview")









# ==========================
# INTERVIEW PAGE
# ==========================


@app.route('/interview')
def interview():

    if "user" not in session:
        return redirect("/login")

    q_list = session.get("selected_questions", [])
    index = session.get("q_index", 0)

    if index >= len(q_list):
        return redirect("/results")

    progress = int((index / len(q_list)) * 100)

    return render_template(
        "interview.html",
        question=q_list[index],
        feedback=session.get("feedback", ""),
        progress=progress
    )










# ==========================
# SAVE ANSWER
# ==========================

@app.route("/next", methods=["POST"])
def next_question():

    if "user" not in session:
        return redirect("/login")

    q_list = session["selected_questions"]
    index = session["q_index"]

    question = q_list[index]

    answer = request.form.get("answer", "").strip()

    words = len(answer.split())

    # Confidence
    confidence = 40
    if words > 10:
        confidence += 20
    if words > 20:
        confidence += 20
    confidence = min(confidence, 100)

    # Communication
    communication = 50
    if words > 10:
        communication += 15
    if words > 20:
        communication += 15
    communication = min(communication, 100)

    # AI Feedback
    if words < 5:
        feedback = "Answer is too short. Explain with more details."
    elif words < 15:
        feedback = "Good answer. Add examples for better explanation."
    else:
        feedback = "Excellent answer. Your explanation is clear."

    conn = sqlite3.connect("interview.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO results
        (question, answer, confidence, communication, feedback)
        VALUES (?, ?, ?, ?, ?)
    """, (
        question,
        answer,
        confidence,
        communication,
        feedback
    ))

    conn.commit()
    conn.close()

    session["feedback"] = feedback

    # Move to next question
    index += 1
    session["q_index"] = index

    # Check if interview completed
    if index >= len(q_list):
        session["completed"] = True
    else:
        session["completed"] = False

    # Always show results after each answer
    return redirect("/results")





    





   







# ==========================
# RESULTS
# ==========================


@app.route("/results")
def results():

    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("interview.db")
    cursor = conn.cursor()

    # Get all interview records
    cursor.execute("SELECT * FROM results")
    data = cursor.fetchall()

    # Calculate average scores
    cursor.execute("""
        SELECT
            AVG(confidence),
            AVG(communication)
        FROM results
    """)
    avg = cursor.fetchone()

    conn.close()

    avg_confidence = round(avg[0], 2) if avg[0] else 0
    avg_communication = round(avg[1], 2) if avg[1] else 0

    return render_template(
        "result.html",
        data=data,
        avg_confidence=avg_confidence,
        avg_communication=avg_communication
    )









# ==========================
# FINAL REPORT
# ==========================


@app.route("/final_report")
def final_report():


    conn=sqlite3.connect(
        "interview.db"
    )


    cursor=conn.cursor()



    cursor.execute("""

    SELECT confidence,communication

    FROM results

    """)



    rows=cursor.fetchall()



    conn.close()





    total=len(rows)



    if total==0:

        avg_confidence=0

        avg_communication=0


    else:


        avg_confidence=sum(
            r[0] for r in rows
        )/total


        avg_communication=sum(
            r[1] for r in rows
        )/total






    final_score=round(

        (avg_confidence+avg_communication)/2,

        2

    )






    if final_score>=80:


        performance="Excellent"

        status="Selected"


        feedback="You are completely interview ready."



        strengths=[

        "Strong communication",

        "Good confidence",

        "Clear explanations"

        ]


        improvements=[

        "Keep learning advanced topics"

        ]




    elif final_score>=60:


        performance="Good"

        status="Selected"


        feedback="Good performance. Continue practicing."



        strengths=[

        "Good technical knowledge"

        ]


        improvements=[

        "Give more examples",

        "Improve confidence"

        ]




    else:


        performance="Needs Improvement"

        status="Needs Improvement"


        feedback="Practice more before interviews."



        strengths=[

        "Completed interview"

        ]



        improvements=[

        "Improve communication",

        "Give detailed answers"

        ]








    return render_template(

        "final_report.html",


        candidate_name=session.get("user"),


        total_questions=total,


        avg_confidence=round(
            avg_confidence,2
        ),


        avg_communication=round(
            avg_communication,2
        ),


        final_score=final_score,


        performance=performance,


        status=status,


        overall_feedback=feedback,


        strengths=strengths,


        improvements=improvements

    )









# ==========================
# RESTART
# ==========================


@app.route("/restart")
def restart():


    session.clear()



    conn=sqlite3.connect(
        "interview.db"
    )

    cursor=conn.cursor()


    cursor.execute(
        "DELETE FROM results"
    )


    conn.commit()

    conn.close()



    return redirect("/")








# ==========================
# LOGOUT
# ==========================


@app.route("/logout")
def logout():


    session.clear()


    return redirect("/")







# ==========================
# RUN
# ==========================


if __name__=="__main__":


    app.run(
        debug=True
    )
