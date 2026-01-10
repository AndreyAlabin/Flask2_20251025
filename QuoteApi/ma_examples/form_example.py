from flask import Flask, render_template, redirect, url_for, jsonify, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Length, DataRequired, Email

app = Flask(__name__)
app.secret_key = "secret key example"


class MyForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(5, 8)])


@app.route("/submit", methods=["GET", "POST"])
def submit():
    form = MyForm()
    if form.validate_on_submit():
        print(f'{request.form = }')
        return redirect(url_for("done"))
    return render_template("index.html", form=form)

@app.route("/success")
def done():
    return jsonify(message='Well done')


if __name__ == '__main__':
    app.run(debug=True)
