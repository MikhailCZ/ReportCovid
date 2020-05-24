from app.models.databases import Database, SqlDatabase


db = SqlDatabase()

def test_connection():
   assert db.create_connection() is not None

