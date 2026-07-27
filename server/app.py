from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from . import create_app
from .models import db, User, Note

app = create_app()


@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if User.query.filter_by(username=data.get('username')).first():
        return {"error": "Username already taken"}, 422

    try:
        user = User(username=data['username'])
        user.password_hash = data['password']
        db.session.add(user)
        db.session.commit()

        access_token = create_access_token(identity=user.id)
        return jsonify(user=user.to_dict(), access_token=access_token), 201
    except Exception as e:
        return {"error": str(e)}, 500


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()

    if user and user.authenticate(data.get('password')):
        access_token = create_access_token(identity=user.id)
        return jsonify(user=user.to_dict(), access_token=access_token), 200

    return {"error": "Invalid username or password"}, 401


@app.route('/me', methods=['GET'])
@jwt_required()
def check_session():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user:
        return jsonify(user.to_dict()), 200
    return {"error": "Unauthorized"}, 401


@app.route('/notes', methods=['GET', 'POST'])
@jwt_required()
def handle_notes():
    current_user_id = get_jwt_identity()

    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        pagination = Note.query.filter_by(user_id=current_user_id).paginate(
            page=page, per_page=per_page, error_out=False)
        notes = [note.to_dict() for note in pagination.items]

        return jsonify(
            notes=notes,
            total=pagination.total,
            pages=pagination.pages,
            current_page=pagination.page
        ), 200

    elif request.method == 'POST':
        data = request.get_json()
        try:
            new_note = Note(
                title=data.get('title'),
                content=data.get('content'),
                user_id=current_user_id
            )
            db.session.add(new_note)
            db.session.commit()
            return new_note.to_dict(), 201
        except Exception as e:
            return {"error": str(e)}, 400


@app.route('/notes/<int:id>', methods=['PATCH', 'DELETE'])
@jwt_required()
def handle_note_detail(id):
    current_user_id = get_jwt_identity()
    note = Note.query.filter_by(id=id, user_id=current_user_id).first()

    if not note:
        return {"error": "Note not found or unauthorized"}, 404

    if request.method == 'PATCH':
        data = request.get_json()
        for key, value in data.items():
            setattr(note, key, value)
        db.session.commit()
        return note.to_dict(), 200

    elif request.method == 'DELETE':
        db.session.delete(note)
        db.session.commit()
        return {}, 204


if __name__ == '__main__':
    app.run(port=5555, debug=True)
