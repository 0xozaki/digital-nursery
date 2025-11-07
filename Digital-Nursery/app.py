from flask import Flask,render_template,jsonify,redirect,make_response,request
from json import dumps,loads,load,dump


app = Flask(__name__, template_folder="app/templates")


@app.route("/login",methods=['GET','POST'])
def login():
    if request.method == "GET":
        return render_template("login.html")
    

@app.route("/",methods=['GET'])
def home():
    if request.method == "GET":
        with open("categories.json",encoding="utf-8") as f:
            categories = load(f)
        return render_template("home.html", categories=categories)
    

if __name__ == "__main__":
    app.run()