from flask import Flask, redirect, render_template, request, session, flash
import markdown
import pg
import time
from dotenv import load_dotenv, find_dotenv
import os
import requests

load_dotenv(find_dotenv())
tmp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask('SoccerStreets', template_folder=tmp_dir)
app.secret_key = "ksajoivnvaldksdjfj"
db = pg.DB(
    dbname=os.environ.get('PG_DBNAME'),
    host=os.environ.get('PG_HOST'),
    user=os.environ.get('PG_USERNAME'),
    passwd=os.environ.get('PG_PASSWORD')
)

@app.route('/')
def render_homepage():
    return render_template(
        'login.html'
            )

@app.route('/submit_login', methods=['POST'])
def submit_login():
    uname = request.form.get('uname')
    pws = request.form.get('pws')
    results = db.query("select * from individuals where uname = $1", uname).namedresult()
    print results[0]
    if len(results) > 0:
        user = results[0]
        if user.pws == pws and user.uname == uname:
            session['id'] = user.id
            session['username'] = user.uname
            session['firstname'] = user.firstname
            session['lastname'] = user.lastname
            flash("Successfully Logged In")
            return redirect('/'+ user.type + '/' + str(user.id))

        flash("Couldn't Log In")
    return redirect('/')

@app.route('/log_out', methods=['POST'])
def log_out():
   del session['id']
   del session['username']
   del session['firstname']
   del session['lastname']
   flash("Successfully Logged Out")
   return redirect('/')

@app.route('/register')
def render_register():
    return render_template(
        'register.html'
    )

@app.route('/submit_register', methods=['POST'])
def submit_register():
    fname = request.form.get('fname');
    lname = request.form.get('lname');
    phone = request.form.get('phone');
    station = request.form.get('station');
    breeze = request.form.get('breeze');
    # address = request.form.get('address');
    uname = request.form.get('uname');
    pws = request.form.get('pws');
    radio = request.form.get('optradio');
    db.insert('individuals',{
    'lastname' : lname,
    'firstname' : fname,
    'uname' : uname,
    'pws' : pws,
    'type' : radio,
    })
    query = db.query("Select id from individuals where uname = $1",uname);
    if radio == 'kid':
        db.insert('kids_breeze',{
        'kid_id' : query.id,
        'breeze' : breeze,
        })
        db.insert('kids_parents',{
        'kid_id' : query.id,
        'parent_id' : parentid,
        })
        db.insert('phonenums',{
        'individ_id' : query.id,
        'phone' : phone,
        })
    elif radio == 'parent':
        db.insert('phonenums',{
        'individ_id' : query.id,
        'phone' : phone,
        })
    elif radio == 'chaperone':
        db.insert('phonenums',{
        'individ_id' : query.id,
        'phone' : phone,
        })
    return redirect('/')


@app.route('/logout')
def logout():
    del session['username']
    flash("Successfully Logged Out")
    return redirect('/')


@app.route('/checkin', methods=['POST', 'GET'])
def checkin():
    kid_id = request.form.get('kid_id');
    timestamp = time.time();
    origin_id =request.form.get('origin_id');
    if origin_id != 2:
        destination_id = 2
    # print "in checkin route"
    # kid_id = 8
    # timestamp = time.time();
    # origin_id = 1
    # destination_id = 2
    # chaperone_id = 7
    r = requests.post('https://intense-shore-33606.herokuapp.com/api/v1/checkins', data={'participant_id':kid_id, 'timestamp': timestamp, 'chaperone_id': chaperone_id, 'origin_id':origin_id, 'destination_id': destination_id})

    # query = db.insert('chekins',{
    # 'timestamp' : timestamp,
    # 'kid_id' : kid_id,
    # 'chaparone_id' : session[id],
    # 'origin_id' : origin,
    # 'dest_id' : destination
    #
    # })

    return render_template (
    'checkin_submit.html'
    kid_id = kid_qr,
    timestamp = timestamp,
    origin = origin,
    destination = destination
    )

@app.route('/checkin5', methods=['POST'])
def checkin5():
    query = db.query("")
    return redirect('/login')

@app.route('/checkout', methods=['POST'])
def checkout():
    return redirect('/login')

@app.route('/parent/<parent_id>')
def render_parent(parent_id):
    # Query to get parent information
    parent = db.query('select individuals.firstname from individuals inner join phonenums on individuals.id = phonenums.individ_id where individuals.id = $1', parent_id).namedresult()[0]

    # Query to get all the parent's kids
    kids_list = db.query("select kids.id as kid_id, kids.firstname as kid_fname, kids.lastname as kid_lname from individuals as parents inner join kids_parents on parents.id = kids_parents.parent_id inner join individuals as kids on kids_parents.kid_id = kids.id where parents.id = $1", parent_id).namedresult()

    return render_template(
        'parent.html',
        parent = parent,
        kids_list = kids_list
    )

@app.route('/parent/kid/<kid_id>')
def render_parent_kid():


    return render_template(
        'kid.html'
    )

@app.route('/kid/<kid_id>')
def render_kid(kid_id):
    # kid_id = kid_id
    # kid_username = session['username']
    # kid_fname = session['firstname']
    # kid_lname = session['lastname']
    return render_template(
        'kid.html',
        # kid_id = kid_id,
        # kid_username = kid_username,
        # kid_fname = kid_fname,
        # kid_lname = kid_lname
    )

@app.route('/chaperone')
def render_chaperone():
    return render_template(
        'chaperone.html'
    )


@app.route('/upload', methods=['POST'])
def upload():
    file_name_size = 15
    user_id = request.form.get("id")
    print "user id %s\n\n\n" % user_id
    project_id = request.form.get("project_id")
    print "project id %s\n\n\n" % project_id
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1]
        # Create new random name for the file using letters and digits
        filename = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(file_name_size)]) + "." + file_extension
        # Move the file form the temporal folder to
        # the upload folder we setup
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Redirect the user to the uploaded_file route, which
        # will basically show on the browser the uploaded file
        if user_id:
            db.update (
                "users", {
                    "id": user_id,
                    "avatar": filename
                }
            )
        elif project_id:
            db.insert (
                "image",
                image = filename,
                project_id = project_id
            )
        return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
