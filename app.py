from flask import Flask
from flask import redirect
from flask import request

from ExperimentModel import validate_pid

app = Flask(__name__, static_url_path='/static')
group_id = None

# Basic Route
@app.route("/")
def hello():
    return "Hello World!"

#CWI Frist Screen
@app.route("/cwi")
def cwi():
    return "<b>Complex Word Identification</b>"

#Passing Word to cwi
@app.route("/cwi/<pid>", methods=['GET', 'POST'])
def cwi_word(pid):
    cursor = validate_pid(pid)
    if cursor is not None:
        group_id = cursor['gid']
        str = '<center><font color=\'#383838\'><h2>Complex Word Identification in Hindi Sentences</h2>'\
        '<h4>Principal Investigator: Gayatri Venugopal, Symbiosis Institute of Computer Studies and Research<br><br>'\
        'Co-Investigator: Dr. Dhanya Pramod, Symbiosis Centre for Information Technology<br><br>'\
        'Symbiosis International (Deemed University), Pune, India<br><br>'\
        'Project funded by Symbiosis Centre for Research and Innovation, Symbiosis International (Deemed University)<br><br>'\
        'Ethical approval received from the Internal Ethics Committee, Symbiosis International (Deemed University)</font></h4></center>'
        return '<div align=right><font color=green><b>Welcome (' + group_id + ') ' + cursor['pid'] + '!</b></font></div>' + str
    return '<center><h3>Invalid ID!</h3><br>' + '<input type=button value = "Go Back" size = 20 onClick = "location.replace(\'../static/cwi.html\')"></center>'
# Different Route
@app.route("/test")
def test():
    return "Test different route"

# Route with parameter in route
# Variable must be passed to method
@app.route("/test/<param>")
def param_test(param):
    return "Received: {}".format(param)

# Route with parameters passed as args
# Example: /test/args?name=<name>&age=<age>
@app.route("/test/args")
def arg_test():
    name = request.args.get('name')
    age = request.args.get('age')
    return "Name is {}\nAge is {}".format(name, age)

# Route with HTTP method constraints
@app.route("/methods", methods=['GET', 'POST'])
def default():
    if request.method == 'POST':
        return "Received POST Request"
    else:
        return "Received GET Request"

# Route with type constraint on parameter
@app.route("/test/square/<int:param>")
def int_test(param):
    return "Square of {} is {}".format(param, param * param)

# Route to three amigos
@app.route("/three-amigos")
def three_amigos():
    return redirect("https://www.denverpost.com/2013/09/04/broncos-original-three-amigos-ride-again-living-on-in-nfl-history/", code = 302)
