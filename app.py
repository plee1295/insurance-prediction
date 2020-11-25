from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import requests
import pickle
import numpy as np
import sklearn
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///client.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String(6), nullable=False)
    bmi = db.Column(db.Float(), nullable=False)
    children = db.Column(db.Integer, nullable=False)
    smoker = db.Column(db.String(3), nullable=False)
    region = db.Column(db.String(9), nullable=False)
    charges = db.Column(db.Float())

model = pickle.load(open('random_forest_regression_model.pkl', 'rb'))

@app.route('/')
@app.route('/login',methods=['GET'])
def Main():
    return render_template('login.html')


@app.route('/home',methods=['GET'])
def Home():
    return render_template('index.html')


@app.route('/clients',methods=['GET'])
def Table():

    clients = Client.query.all()

    output = []

    for client in clients:
        client_data = {}
        client_data['name'] = client.name
        client_data['age'] = client.age
        client_data['sex'] = client.sex
        client_data['bmi'] = client.bmi
        client_data['children'] = client.children
        client_data['smoker'] = client.smoker
        client_data['region'] = client.region
        client_data['charges'] = client.charges
        output.append(client_data)

    return render_template('table.html', clients=output)


@app.route('/home', methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']

    users = User.query.all()

    user_data = {}
    for user in users:
        if user.username == username and user.password == password:
            user_data['id'] = user.id
            user_data['username'] = user.username
            user_data['password'] = user.password
            
            return render_template('index.html', user_id=user_data['id'])
        else:
            return render_template('login.html')


@app.route('/stats',methods=['GET'])
def Stats():
    
    clients = Client.query.all()

    if len(clients) != 0:
        genderCount = { 'male': 0, 'female': 0 }
        smokerCount = { 'no': 0, 'yes': 0 }
        regionCount = { 'southeast': 0, 'southwest': 0, 'northeast': 0, 'northwest': 0 }
        ageSum = 0
        bmiSum = 0.0
        chargesSum = 0.0

        for client in clients:
            if client.sex == 'Male':
                genderCount['male'] += 1
            elif client.sex == 'Female':
                genderCount['female'] += 1

            if client.smoker == 'No':
                smokerCount['no'] += 1
            elif client.smoker == 'Yes':
                smokerCount['yes'] += 1

            if client.region == 'Southeast':
                regionCount['southeast'] += 1
            elif client.region == 'Southwest':
                regionCount['southwest'] += 1
            elif client.region == 'Northeast':
                regionCount['northeast']
            elif client.region == 'Northwest':
                regionCount['northwest'] += 1

            ageSum += client.age
            bmiSum += client.bmi
            chargesSum += client.charges

        malePercentage = int(float("{:.2f}".format(genderCount['male'] / len(clients))) * 100)
        femalePercentage = int(float("{:.2f}".format(genderCount['female'] / len(clients))) * 100)

        smokerPercentage = int(float("{:.2f}".format(smokerCount['yes'] / len(clients))) * 100)
        nonSmokerPercentage = int(float("{:.2f}".format(smokerCount['no'] / len(clients))) * 100)

        southeastPercentage = int(float("{:.2f}".format(regionCount['southeast'] / len(clients))) * 100)
        southwestPercentage = int(float("{:.2f}".format(regionCount['southwest'] / len(clients))) * 100)
        northeastPercentage = int(float("{:.2f}".format(regionCount['northeast'] / len(clients))) * 100)
        northwestPercentage = int(float("{:.2f}".format(regionCount['northwest'] / len(clients))) * 100)

        avgAge = "{:.2f}".format(ageSum / len(clients))
        year = str(avgAge.split('.')[0])
        month = str(int(int(avgAge.split('.')[1]) / 8))

        avgBmi = float("{:.2f}".format(bmiSum / len(clients)))

        avgCharge = float("{:.2f}".format(chargesSum / len(clients)))
        chargesSum = float("{:.2f}".format(chargesSum))

        return render_template('stats.html', malePct=malePercentage, femalePct=femalePercentage, avgAge="{} years, {} months".format(year, month), avgBmi=avgBmi, smokerPct=smokerPercentage, nonSmokerPct=nonSmokerPercentage, southeastPercentage=southeastPercentage, southwestPercentage=southwestPercentage, northeastPercentage=northeastPercentage, northwestPercentage=northwestPercentage, avgCharge=avgCharge, chargesSum=chargesSum)
    else:
        return render_template('stats.html', malePct=0, femalePct=0, avgAge="0", avgBmi=0, smokerPct=0, nonSmokerPct=0, southeastPercentage=0, southwestPercentage=0, northeastPercentage=0, northwestPercentage=0, avgCharge=0, chargesSum=0)

standard_to = StandardScaler()
@app.route("/predict", methods=['POST'])
def predict():

    sex_male = 0
    smoker_yes = 0
    region_northwest = 0
    region_southeast = 0
    region_southwest = 0

    if request.method == 'POST':
        age = int(request.form['age'])
        sex = request.form['sex']
        height = int(request.form['height'])
        weight = int(request.form['weight'])
        bmi = float("{:.2f}".format((weight * 703) / (height * height)))
        children = int(request.form['children'])
        smoker = request.form['smoker']
        region = request.form['region']

        if(sex == 'Male'):
            sex_male = 1
        else:
            sex_male = 0

        if (smoker == 'Yes'):
            smoker_yes = 1
        else:
            smoker_yes = 0
        
        if (region == 'Southwest'):
            region_northwest = 0
            region_southeast = 0
            region_southwest = 1
        elif (region == 'Southeast'):
            region_northwest = 0
            region_southeast = 1
            region_southwest = 0
        elif (region == 'Northwest'):
            region_northwest = 1
            region_southeast = 0
            region_southwest = 0
        else:
            region_northwest = 0
            region_southeast = 0
            region_southwest = 0

        prediction = model.predict([[age, bmi, children, sex_male, smoker_yes, region_northwest, region_southeast, region_southwest]])
        
        output = round(prediction[0], 2)
        if output < 0:
            return render_template('index.html', prediction_text="Unable to make a prediction")
        else:
            new_client = Client(name=request.form['name'], age=age, sex=sex, bmi=bmi, children=children, smoker=smoker, region=region, charges=output)
            db.session.add(new_client)
            db.session.commit()

            return render_template('index.html', prediction_text="Estimate: ${}".format(output))
    else:
        return render_template('index.html')

if __name__=="__main__":
    app.run(debug=True)