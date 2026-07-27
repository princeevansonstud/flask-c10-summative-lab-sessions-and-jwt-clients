from server import create_app
from server.models import db, User, Note

app = create_app()

with app.app_context():
    print("Clearing existing data...")
    Note.query.delete()
    User.query.delete()

    print("Creating users...")
    u1 = User(username="alice")
    u1.password_hash = "password123"

    u2 = User(username="bob")
    u2.password_hash = "password123"

    db.session.add_all([u1, u2])
    db.session.commit()

    print("Creating notes...")
    n1 = Note(title="First Note",
              content="Learn Flask-JWT-Extended authentication.", user_id=u1.id)
    n2 = Note(title="Project Ideas",
              content="Build a full stack productivity app.", user_id=u1.id)
    n3 = Note(title="Groceries",
              content="Milk, eggs, coffee beans.", user_id=u2.id)

    db.session.add_all([n1, n2, n3])
    db.session.commit()

    print("Seeding complete!")
