class User:
    def __init__(self, db, id=None, email=None, username=None, password=None):
        self.db = db
        self.id = id
        self.email = email
        self.username = username
        self.password = password

    def create(self):
        """Creates a new user in the database."""
        # Note: In production, hash password here.
        query = "INSERT INTO users (email, username, password) VALUES (?, ?, ?)"
        try:
            self.id = self.db.execute(query, (self.email, self.username, self.password))
            return self.id
        except Exception as e:
            # Handle unique constraint violation or DB error
            return None

    def find_by_email(self, email):
        """Finds a user by email."""
        query = "SELECT * FROM users WHERE email = ?"
        row = self.db.query(query, (email,), one=True)
        if row:
            self.id = row['id']
            self.email = row['email']
            self.username = row['username']
            self.password = row['password']
            return self
        return None

    def verify_password(self, input_password):
        """Verifies if the input password matches the stored password."""
        return self.password == input_password
