from app import app, db, Professor

with app.app_context():
    db.create_all()
    profs = []
    db.session.add_all(profs)
    db.session.commit()