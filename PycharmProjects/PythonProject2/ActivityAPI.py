from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///indiegames.db'
db = SQLAlchemy(app)
api = Api(app)

# database
class IndieGameModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    developer = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=True)
    price = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f"IndieGame(title={self.title}, developer={self.developer}, genre={self.genre}, price={self.price})"

# request parcer
game_args = reqparse.RequestParser()
game_args.add_argument('title', type=str, required=True, help="Title cannot be blank")
game_args.add_argument('developer', type=str, required=True, help="Developer cannot be blank")
game_args.add_argument('genre', type=str, help="Genre of the game")
game_args.add_argument('price', type=float, help="Price of the game")

game_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'developer': fields.String,
    'genre': fields.String,
    'price': fields.Float
}

# resource
class Games(Resource):
    @marshal_with(game_fields)
    def get(self):
        games = IndieGameModel.query.all()
        return games, 200

    @marshal_with(game_fields)
    def post(self):
        args = game_args.parse_args()
        new_game = IndieGameModel(
            title=args['title'],
            developer=args['developer'],
            genre=args.get('genre'),
            price=args.get('price', 0.0)
        )
        db.session.add(new_game)
        db.session.commit()
        games = IndieGameModel.query.all()
        return games, 201


class Game(Resource):
    @marshal_with(game_fields)
    def get(self, id):
        game = IndieGameModel.query.filter_by(id=id).first()
        if not game:
            abort(404, message="Game not found")
        return game, 200

    @marshal_with(game_fields)
    def patch(self, id):
        args = game_args.parse_args()
        game = IndieGameModel.query.filter_by(id=id).first()
        if not game:
            abort(404, message="Game not found")

        # Update fields
        game.title = args['title']
        game.developer = args['developer']
        game.genre = args['genre']
        game.price = args['price']
        db.session.commit()
        return game, 200

    @marshal_with(game_fields)
    def delete(self, id):
        game = IndieGameModel.query.filter_by(id=id).first()
        if not game:
            abort(404, message="Game not found")
        db.session.delete(game)
        db.session.commit()
        games = IndieGameModel.query.all()
        return games, 200


api.add_resource(Games, '/api/games/')
api.add_resource(Game, '/api/games/<int:id>')


@app.route('/')
def home():
    return '<h1>🎮 Indie Game REST API</h1><p>Use /api/games/ to interact with the database.</p>'


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
