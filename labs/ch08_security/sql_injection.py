# VULNERABLE: String concatenation in SQL
def get_user_by_name_bad(name: str) -> dict | None:
    query = f"SELECT * FROM users WHERE name = '{name}'"
    # If name = "'; DROP TABLE users; --"
    # Query becomes: SELECT * FROM users WHERE name = ''; DROP TABLE users; --'
    return db.execute(query).fetchone()


# SAFE: Parameterised query
def get_user_by_name(name: str) -> dict | None:
    query = "SELECT * FROM users WHERE name = %s"
    return db.execute(query, (name,)).fetchone()
