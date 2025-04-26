from databases import Database

database = Database('sqlite:///test.db')

async def fetch_user_data(user_id):
    query = "SELECT * FROM users WHERE id = :id"
    return await database.fetch_one(query=query, values={"id": user_id})