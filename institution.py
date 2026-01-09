class Institution:
    def __init__(self, db, id=None, name=None, type=None, latitude=None, longitude=None, details=None, website=None, ranking=None, courses=None):
        self.db = db
        self.id = id
        self.name = name
        self.type = type
        self.latitude = latitude
        self.longitude = longitude
        self.details = details
        self.website = website
        self.ranking = ranking
        self.courses = courses

    def get_all(self):
        """Retrieves all institutions."""
        query = "SELECT * FROM institutions"
        rows = self.db.query(query)
        institutions = []
        if rows:
            for row in rows:
                institutions.append({
                    "id": row['id'],
                    "name": row['name'],
                    "type": row['type'],
                    "latitude": row['latitude'],
                    "longitude": row['longitude'],
                    "details": row['details'],
                    "website": row['website'],
                    "ranking": row['ranking'],
                    "courses": row['courses']
                })
        return institutions

    def create(self):
        """Creates a new institution."""
        query = '''
            INSERT INTO institutions (name, type, latitude, longitude, details, website, ranking, courses)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.id = self.db.execute(query, (self.name, self.type, self.latitude, self.longitude, self.details, self.website, self.ranking, self.courses))
        return self.id
