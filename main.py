from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, URL, Optional
from flask_sqlalchemy import SQLAlchemy

CAFE_QUALITY_HEADINGS = ['Cafe Name', 'Google Maps URL', 'Image URL',
                         'Location', 'Sockets', 'Toilet',
                         'WiFi', 'Takes Calls', 'Seat Count',
                         'Coffee Price']
# DATABASE_KEYS = ["id", "name", "map_url", "img_url", "location", "seats" , "has_toilet",
#                  'has_wifi', 'has_sockets', 'can_take_calls', 'coffee_price']

app = Flask(__name__)
Bootstrap(app)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# Forms
class CafeForm(FlaskForm):
    name = StringField(CAFE_QUALITY_HEADINGS[0], validators=[DataRequired()])
    map_url = StringField(CAFE_QUALITY_HEADINGS[1], validators=[URL(), DataRequired()])
    img_url = StringField(CAFE_QUALITY_HEADINGS[2], validators=[URL(), DataRequired()])
    location = StringField(CAFE_QUALITY_HEADINGS[3], validators=[DataRequired()])
    has_sockets = BooleanField(CAFE_QUALITY_HEADINGS[4])
    has_toilet = BooleanField(CAFE_QUALITY_HEADINGS[5])
    has_wifi = BooleanField(CAFE_QUALITY_HEADINGS[6])
    can_take_calls = BooleanField(CAFE_QUALITY_HEADINGS[7])
    seats = StringField(CAFE_QUALITY_HEADINGS[8], validators=[DataRequired()])
    coffee_price = StringField(CAFE_QUALITY_HEADINGS[9], validators=[DataRequired()])
    submit = SubmitField('Submit')
    
class EditForm(FlaskForm):
    name = StringField(CAFE_QUALITY_HEADINGS[0])
    map_url = StringField(CAFE_QUALITY_HEADINGS[1], validators=[URL(), Optional()])
    img_url = StringField(CAFE_QUALITY_HEADINGS[2], validators=[URL(), Optional()])
    location = StringField(CAFE_QUALITY_HEADINGS[3])
    has_sockets = BooleanField(CAFE_QUALITY_HEADINGS[4])
    has_toilet = BooleanField(CAFE_QUALITY_HEADINGS[5])
    has_wifi = BooleanField(CAFE_QUALITY_HEADINGS[6])
    can_take_calls = BooleanField(CAFE_QUALITY_HEADINGS[7])
    seats = StringField(CAFE_QUALITY_HEADINGS[8])
    coffee_price = StringField(CAFE_QUALITY_HEADINGS[9])
    submit = SubmitField('Submit')


# Formatting
def bool_to_icon(bool_val):
    if bool_val:
        return "✔"
    else:
        return '✘'


def format_cafe(cafe_db_item):
    return {'id': cafe_db_item.id,
            'name': cafe_db_item.name,
            'map_url': cafe_db_item.map_url,
            'img_url': cafe_db_item.img_url,
            'location': cafe_db_item.location,
            'has_sockets': bool_to_icon(cafe_db_item.has_sockets),
            'has_toilet': bool_to_icon(cafe_db_item.has_toilet),
            'has_wifi': bool_to_icon(cafe_db_item.has_wifi),
            'can_take_calls': bool_to_icon(cafe_db_item.can_take_calls),
            'seats': cafe_db_item.seats,
            'coffee_price': cafe_db_item.coffee_price}



# all Flask routes below
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add', methods=['GET', 'POST'])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        new_cafe = Cafe(name=form.name.data,
                        map_url=form.map_url.data,
                        img_url=form.img_url.data,
                        location=form.location.data,
                        seats=form.seats.data,
                        has_toilet=form.has_toilet.data,
                        has_wifi=form.has_wifi.data,
                        has_sockets=form.has_sockets.data,
                        can_take_calls=form.can_take_calls.data,
                        coffee_price=form.coffee_price.data
                        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for('cafes'))
    return render_template('add.html', form=form)


@app.route('/cafes')
def cafes():
    cafes = db.session.query(Cafe).all()
    formatted_cafes = []
    for cafe in cafes:
        formatted_cafes.append(format_cafe(cafe))
    return render_template('cafes.html', cafes=formatted_cafes, qualities=CAFE_QUALITY_HEADINGS)


@app.route('/update/<cafe_id>', methods=["PATCH", "GET", "POST"])
def edit_cafe(cafe_id):
    cafe_to_update = Cafe.query.get(cafe_id)
    if cafe_to_update:
        formatted_cafe = format_cafe(cafe_to_update)
        form = EditForm()
        if form.validate_on_submit():
            for entry in form.data.items():
                if entry[1]:
                    setattr(cafe_to_update, entry[0], entry[1])
                    db.session.commit()
            return redirect(url_for('cafes'))
        return render_template("edit.html", cafe=formatted_cafe, headings=CAFE_QUALITY_HEADINGS, form=form)
    

@app.route('/report-closed/<cafe_id>', methods=["DELETE", "GET", "POST"])
def delete_cafe(cafe_id):
    cafe_to_delete = Cafe.query.get(cafe_id)
    if cafe_to_delete:
        db.session.delete(cafe_to_delete)
        db.session.commit()
    return redirect(url_for("cafes"))


if __name__ == '__main__':
    app.run(debug=True)
