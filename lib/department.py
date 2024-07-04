
from __init__ import CURSOR, CONN

class Department:
    all = {}

    def __init__(self, name, location, id=None):
        self.id = id
        self.name = name
        self.location = location

    def __repr__(self):
        return f"<Department {self.id}: {self.name}, {self.location}>"

    @classmethod
    def create_table(cls):
        CURSOR.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                location TEXT NOT NULL)
        """)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS departments")
        CONN.commit()
        cls.all.clear()  

    @classmethod
    def find_by_name(cls, name):
        sql = "SELECT * FROM departments WHERE name = ?"
        row = CURSOR.execute(sql, (name,)).fetchone()
        return cls.instance_from_db(row) if row else None

    
    def update(self):
        sql = """
        UPDATE departments SET name = ?, location = ? WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.location, self.id))
        CONN.commit()

    def save(self):
        if self.id is None:
            CURSOR.execute("""
                INSERT INTO departments (name, location) VALUES (?, ?)
            """, (self.name, self.location))
            self.id = CURSOR.lastrowid
        else:
            CURSOR.execute("""
                UPDATE departments SET name=?, location=? WHERE id=?
            """, (self.name, self.location, self.id))
        CONN.commit()
        Department.all[self.id] = self

    @classmethod
    def create(cls, name, location):
        department = cls(name, location)
        department.save()
        return department

    def delete(self):
        CURSOR.execute("DELETE FROM departments WHERE id=?", (self.id,))
        CONN.commit()
        if self.id in Department.all:
            del Department.all[self.id]
        self.id = None

    @classmethod
    def find_by_id(cls, id):
        department = cls.all.get(id)
        if department is None:
            result = CURSOR.execute("SELECT * FROM departments WHERE id=?", (id,))
            row = result.fetchone()
            if row:
                department = cls(row[1], row[2], row[0])
                cls.all[id] = department
        return department

    @classmethod
    def get_all(cls):
        results = CURSOR.execute("SELECT * FROM departments").fetchall()
        return [cls.instance_from_db(row) for row in results]

    @classmethod
    def instance_from_db(cls, row):
        id, name, location = row
        if id not in cls.all:
            cls.all[id] = cls(name, location, id)
        return cls.all[id]

    def employees(self):
        from employee import Employee
        return Employee.find_by_department_id(self.id)
