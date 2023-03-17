from flask import Flask, request, jsonify,render_template,url_for,session,redirect,send_from_directory,current_app
from base64 import b64decode, b64encode
import cv2
import numpy as np
import PIL.Image
import io
import os
import face_recognition

app = Flask(__name__)
app.secret_key = "ramesh"

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

#Registration division
#Registration division
#Registration division

@app.route('/')
def homepage():
    return render_template('home.html')

@app.route('/submit-roll-number')
def submit_roll_number1():
    return render_template('register-roll.html')

@app.route('/instro')
def instro():
    return render_template('instruction.html')

@app.route('/submit-roll-number', methods=['POST'])
def submit_roll_number():
    roll_number = request.form['roll_number']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    gender = request.form['gender']
    email = request.form['email']
    mobile = request.form['mobile']
    department = request.form['department']
    roll_number_upper = roll_number.upper()
    with open('registered.txt', 'r') as f:
        roll_numbers = f.readlines()
    roll_numbers = [rn.strip() for rn in roll_numbers]
    if roll_number_upper in roll_numbers:
        message = "User already exists"
        return render_template('register-roll.html', message=message)
    with open('registered.txt', 'a') as f:
        f.write(roll_number_upper + '\n')
        with open('static/students.txt', 'a') as f:
            f.write(f"{roll_number.upper()},{last_name},{first_name},{gender},{email},{mobile},{department}\n")
    session['roll_number'] = roll_number_upper
    return redirect(url_for('camera',roll=roll_number_upper))



@app.route('/camera')
def camera():
    if 'roll_number' in session:
        roll_number = session['roll_number']
        return render_template('camera.html', roll_number=roll_number)
    return redirect(url_for('homepage'))

@app.route('/upload', methods=['POST'])
def upload():
    if 'roll_number' in session:
        roll_number = session['roll_number']
        app.config['UPLOAD_FOLDER'] = 'static/registered'
        data = request.get_json()
        image_data = b64decode(data['image'].split(',')[1])
        file = io.BytesIO(image_data)
        image = cv2.imdecode(np.frombuffer(file.read(), dtype=np.uint8), cv2.IMREAD_COLOR)
        filename = f"{roll_number}.png"
        filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        cv2.imwrite(filename, image)
        return jsonify({'status': 'success', 'message': 'Image uploaded successfully'})
    return redirect(url_for('homepage'))

@app.route('/success')
def success():
    if 'roll_number' in session:
        session.pop('roll_number', None)
        return render_template('suc.html')
    return redirect(url_for('homepage'))

def bbox_to_bytes(bbox_array):
    bbox_PIL = PIL.Image.fromarray(bbox_array, 'RGB')
    iobuf = io.BytesIO()
    bbox_PIL.save(iobuf, format='png')
    bbox_bytes = 'data:image/png;base64,{}'.format((str(b64encode(iobuf.getvalue()), 'utf-8')))
    return bbox_bytes


#voting division
#voting division
#voting division



@app.route('/vote')
def vot():
    return render_template('vote.html')

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        roll_number = request.form['roll_number'].upper()
        email = request.form['email']
        mobile = request.form['mobile']
        department = request.form['department']
        new_password = request.form['last_name']
        
        with open('static/students.txt', 'r') as f:
            students = f.readlines()
        students = [s.strip().split(',') for s in students]
        for s in students:
            if s[0] == roll_number and s[4] == email and s[5] == mobile and s[6] == department:
                with open('static/students.txt', 'w') as f:
                    for line in students:
                        if line[0] == roll_number:
                            line[1] = new_password
                        f.write(','.join(line) + '\n')
                message = "Your password has been changed."
                return render_template('forgot.html', message=message)
        message = "Invalid details."
        return render_template('forgot.html', message=message)
    return render_template('forgot.html')

@app.route('/vote', methods=['POST'])
def voting():
    session['value'] = os.urandom(4)
    value = session.get('value')
    roll_number = request.form['roll_number']
    password = request.form['password']
    roll_number_upper = roll_number.upper()
    session['response'] = roll_number_upper
    with open('static/students.txt', 'r') as f:
        registered = f.readlines()
    registered = [rn.strip().split(',') for rn in registered]
    with open('voted.txt', 'r') as f:
        voted = f.readlines()
    voted = [vn.strip() for vn in voted]
    if [roll_number_upper, password] in [[rn[0].upper(), rn[1]] for rn in registered]:
        if roll_number_upper not in voted:
            roll_number = roll_number_upper 
            return redirect(url_for('choose', roll_number=roll_number, value=value))
        message = "You have already voted."
    else:
        message = "Invalid Roll Number or Password"
    return render_template('vote.html', message=message)



@app.route('/choose')
def choose():
    value = session.get('value')
    if 'value' in session:
        roll_number = request.args.get('roll_number')
        if 'response' not in session:
            return redirect(url_for('homepage'))
        if roll_number == session['response']:
            candidate_images = [f for f in os.listdir('static/candidates') if f.endswith('.jpg') or f.endswith('.jpeg') or f.endswith('.png') or f.endswith('.gif')]
            return render_template('choose.html', candidate_images=candidate_images,roll_number=roll_number,value=value)
    return redirect(url_for('homepage'))




#vrify the face to get voted
#verifying the face
#verifying the face

@app.route('/verify')
def verify():
    value = request.args.get('value')
    if 'value' in session:
        roll_number = request.args.get('roll_number')
        candidate_name = request.args.get('candidate_name')
        message1 = request.args.get('message')
        return render_template('verifyface.html', roll_number=roll_number,candidate_name=candidate_name,errormsg=message1)
    return render_template('vote.html')

    

@app.route('/capture', methods=['POST'])
def capture():
    value = request.args.get('value')
    roll_number = request.args.get('roll_number')
    candidate_name = request.args.get('candidate_name')
    
    if 'value' in session:
        session.pop('value', None)
        
        app.config['UPLOAD_FOLDER'] = 'static/captured'
        data = request.get_json()
        image_data = b64decode(data['image'].split(',')[1])
        file = io.BytesIO(image_data)
        image = cv2.imdecode(np.frombuffer(file.read(), dtype=np.uint8), cv2.IMREAD_COLOR)
        filename = f"{roll_number}.png"
        filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        cv2.imwrite(filename, image)

        app.config['REGISTERED_FOLDER'] = 'static/registered'
        app.config['CAPTURED_FOLDER'] = 'static/captured'

        candidate_image_path = os.path.join(app.config['REGISTERED_FOLDER'], f'{roll_number}.png')
        captured_image_path = os.path.join(app.config['CAPTURED_FOLDER'], f'{roll_number}.png')
        print(1)

        if candidate_image_path and captured_image_path:
            print(2)
            candidate_image = face_recognition.load_image_file(candidate_image_path)
            captured_image = face_recognition.load_image_file(captured_image_path)
            candidate_face_locations = face_recognition.face_locations(candidate_image)
            captured_face_locations = face_recognition.face_locations(captured_image)

            if candidate_face_locations and captured_face_locations:
                print(3)
                candidate_face_encoding = face_recognition.face_encodings(candidate_image, candidate_face_locations)[0]
                captured_face_encoding = face_recognition.face_encodings(captured_image, captured_face_locations)[0]
                print(4)

                results = face_recognition.compare_faces([candidate_face_encoding], captured_face_encoding)

                if results[0]:
                    with open("voted.txt", "a") as f:
                        f.write(f"{roll_number}\n")
                    with open("tracking.txt", "r+") as f:
                        lines = f.readlines()
                        f.seek(0)
                        found = False
                        for line in lines:
                            parts = line.strip().split(",")
                            if parts[0] == candidate_name:
                                parts[1] = str(int(parts[1]) + 1)
                                line = f"{parts[0]},{parts[1]}\n"
                                found = True
                            f.write(line)
                        if not found:
                            f.write(f"{candidate_name},1\n")
                        f.truncate()
                    return jsonify({'status': 'voted','message': 'Image uploaded successfully'})
                else:
                    os.remove(captured_image_path)
                    return jsonify({'status': 'error', 'message': 'Faces do not match'})

            else:
                os.remove(captured_image_path)
                return jsonify({'status': 'error', 'message': 'No faces found'})
    
    return jsonify({'status': 'error', 'message': 'Face not matched'})


@app.route('/voted')
def voted():
    session.clear()
    return render_template('voted.html')



#belongs to admin and dashboard area
#belongs to admin and dashboard area
#belongs to admin and dashboard area


users = [
	{'username': 'admin1', 'password': 'Admin@123'},
	{'username': 'admin2', 'password': 'Admin@143'},
	{'username': 'admin3', 'password': 'Admin@156'}
]


def upload_images(image_files, candidate_names):
    app.config['UPLOAD_FOLDER'] = 'static/candidates'
    if not os.path.exists('static/candidates'):
        os.makedirs('static/candidates')
    for i, image in enumerate(image_files):
        filename = '{}.{}'.format(candidate_names[i], image.filename.split('.')[-1])
        image.save('static/candidates/{}'.format(filename))


@app.route("/admin")
def index():
    if 'username' in session:
        return render_template("admin.html")
    else:
        return render_template("admin1.html")


@app.route('/admin',methods=["POST"])
def admin():
    username = request.form['username']
    password = request.form['password']
    for user in users:
        if username == user['username'] and password == user['password']:
            session['username'] = username
            return redirect(url_for('index'))
    error_message = 'Invalid username or password'
    return render_template('admin1.html', error_message=error_message)


@app.route('/upload-candidates', methods=['POST'])
def upload_candidates():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    candidate1_name = request.form['candidate1_name']
    candidate2_name = request.form['candidate2_name']
    candidate3_name = request.form['candidate3_name']
    candidate1_image = request.files['candidate1_image']
    candidate2_image = request.files['candidate2_image']
    candidate3_image = request.files['candidate3_image']
    upload_images([candidate1_image, candidate2_image, candidate3_image],[candidate1_name,candidate2_name,candidate3_name])

    candidates = []
    with open('tracking.txt', 'r') as f:
        for line in f:
            name, votes = line.strip().split(',')
            candidates.append({'name': name, 'votes': int(votes)})
    return render_template('admin.html',message="SuccessFully Uploaded",candidates=candidates)


@app.route('/refresh-candidates', methods=['GET', 'POST'])
def refresh_candidates():
    candidates = []
    with open('tracking.txt', 'r') as f:
        for line in f:
            name, votes = line.strip().split(',')
            candidates.append({'name': name, 'votes': int(votes)})
    return jsonify(candidates)

@app.route('/delete-poll', methods=['POST'])
def delete_poll():
    poll_id = request.json['poll_id']
    app.config['UPLOAD_FOLDER'] = 'static/candidates'

    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(file_path):
            os.remove(file_path)


    with open('tracking.txt', 'r+') as f:
        lines = f.readlines()
        f.seek(0)
        for line in lines:
            if not line.startswith(poll_id):
                f.write(line)
        f.truncate()


    with open('voted.txt', 'r+') as f:
        lines = f.readlines()
        f.seek(0)
        for line in lines:
            if not line.startswith(poll_id):
                f.write(line)
        f.truncate()

    return jsonify({'emessage': 'Poll deleted successfully.'})

@app.route("/registered")
def registered():
    with open("registered.txt") as f:
        registered_count = f.readlines()
    registered_count = [line.strip() for line in registered_count]
    return "\n".join(registered_count)

@app.route('/delete-register', methods=['POST'])
def delete_register():
    poll_id = request.json['poll_id']
    app.config['UPLOAD_registered'] = 'static/registered'
    app.config['UPLOAD_captured'] = 'static/captured'

    for filename in os.listdir(app.config['UPLOAD_registered']):
        file_path = os.path.join(app.config['UPLOAD_registered'], filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    for filename in os.listdir(app.config['UPLOAD_captured']):
        file_path = os.path.join(app.config['UPLOAD_captured'], filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    
    with open('registered.txt', 'r+') as f:
        lines = f.readlines()
        f.seek(0)
        for line in lines:
            if not line.startswith(poll_id):
                f.write(line)
        f.truncate()
    with open('static/students.txt', 'r+') as f:
        lines = f.readlines()
        f.seek(0)
        for line in lines:
            if not line.startswith(poll_id):
                f.write(line)
        f.truncate()
    return jsonify({'emessage': 'Deleted the Registered Voters'})


@app.route("/voted-fetch")
def voted_fetch():
    with open("voted.txt") as f:
        registered_count = f.read().strip()
    return registered_count

@app.route('/delete-voted', methods=['POST'])
def delete_voted():
    poll_id = request.json['poll_id']
    app.config['UPLOAD_captured'] = 'static/captured'

    for filename in os.listdir(app.config['UPLOAD_captured']):
        file_path = os.path.join(app.config['UPLOAD_captured'], filename)
        if os.path.isfile(file_path):
            os.remove(file_path)


    with open('voted.txt', 'r+') as f:
        lines = f.readlines()
        f.seek(0)
        for line in lines:
            if not line.startswith(poll_id):
                f.write(line)
        f.truncate()
    return jsonify({'emessage': 'Poll deleted successfully.'})
@app.route('/notvoted')
def compare_users():
    voted_users = set()
    with open('voted.txt', 'r') as f:
        for line in f:
            user = line.strip()
            voted_users.add(user)

    registered_users = set()
    with open('registered.txt', 'r') as f:
        for line in f:
            user = line.strip()
            registered_users.add(user)


    not_voted_users = list(registered_users - voted_users)


    return jsonify({'not_voted_users': not_voted_users})

@app.route('/download')
def download_file():
    if 'username' not in session:
        return redirect(url_for('index'))
    else:
        try:
            filename = 'students.txt'
            directory = app.static_folder
            return send_from_directory(directory, filename, as_attachment=True)
        except Exception as e:
            return jsonify({'error': str(e)})

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('homepage'))


if __name__ == '__main__':
    app.run(debug=True, port=8080)