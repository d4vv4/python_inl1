import sqlite3
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask import json
from flask import Response

app = Flask(__name__)
api = Api(app)

con = sqlite3.connect("db.db", check_same_thread=False)
cur = con.cursor()


def GetModel():

    sql = "SELECT * FROM Data INNER JOIN Foods ON Data.FavoriteFood = Foods.Id ORDER BY Data.Id"

    cur.execute(sql)

    result = cur.fetchall()
    df = pd.DataFrame(result, columns=["A", "B", "C", "D", "E", "F"])

    input = df.drop(columns=["A", "D", "E", "F"])
    output = df["F"]
    model = DecisionTreeClassifier()
    model.fit(input, output)
    return model


class Data(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("gender", required=True)
        parser.add_argument("age", required=True)
        parser.add_argument("favoriteFood", required=True)

        args = parser.parse_args()
        gender = int(args["gender"])
        age = int(args["age"])
        favoriteFood = str(args["favoriteFood"])

        sql = "SELECT * FROM Foods WHERE Name=?"
        cur.execute(sql, (favoriteFood,))
        rows = cur.fetchone()
        sql = "INSERT INTO Data(Gender, Age, FavoriteFood) VALUES(?,?,?)"
        cur.execute(sql, (gender, age, rows[0]))
        con.commit()
        return {"data": args}, 200

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("gender", required=True)
        parser.add_argument("age", required=True)
        args = parser.parse_args()
        gender = int(args["gender"])
        age = int(args["age"])
        if gender != 0 and gender != 1 or age < 0 or age > 200:
            return Response(
                status=400,)
        model = GetModel()
        prediction = model.predict([[gender, age]])
        print(prediction)
        return json.jsonify(
            Gender="Male" if gender == 1 else "Female",
            Age=age,
            FavoriteFood=prediction[0]
        )


api.add_resource(Data, "/data")

if __name__ == '__main__':
    app.run()
