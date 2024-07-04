
from __init__ import CURSOR, CONN

class Employee:
    all = {}

    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self.name = name
        self.job_title = job_title
        self.department_id = department_id

    def __repr__(self):
        return f"<Employee {self.id}: {self.name}, {self.job_title}, Department ID: {self.department_id}>"

    @classmethod
    def create_table(cls):
        CURSOR.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                job_title TEXT NOT NULL,
                department_id INTEGER NOT NULL,
                FOREIGN KEY(department_id) REFERENCES departments(id))
        """)
        CONN.commit()

   

    def save(self):
        if self.id is None:
            CURSOR.execute("""
                INSERT INTO employees (name, job_title, department_id) VALUES (?, ?, ?)
            """, (self.name, self.job_title, self.department_id))
            self.id = CURSOR.lastrowid
        else:
            CURSOR.execute("""
                UPDATE employees SET name=?, job_title=?, department_id=? WHERE id=?
            """, (self.name, self.job_title, self.department_id, self.id))
        CONN.commit()
        Employee.all[self.id] = self
  
    @classmethod
    def find_by_name(cls, name):
        sql = "SELECT * FROM employees WHERE name = ?"
        row = CURSOR.execute(sql, (name,)).fetchone()
        return cls.instance_from_db(row) if row else None 


    def update(self):
        sql = """
        UPDATE employees SET name = ?, job_title = ?, department_id = ? WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id, self.id))
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS employees")
        CONN.commit()
        cls.all.clear()

    @classmethod
    def create(cls, name, job_title, department_id):
        employee = cls(name, job_title, department_id)
        employee.save()
        return employee

    def delete(self):
        CURSOR.execute("DELETE FROM employees WHERE id=?", (self.id,))
        CONN.commit()
        if self.id in Employee.all:
            del Employee.all[self.id]
        self.id = None

    @classmethod
    def find_by_id(cls, id):
        employee = cls.all.get(id)
        if employee is None:
            result = CURSOR.execute("SELECT * FROM employees WHERE id=?", (id,))
            row = result.fetchone()
            if row:
                employee = cls(row[1], row[2], row[3], row[0])
                cls.all[id] = employee
        return employee

    @classmethod
    def find_by_department_id(cls, department_id):
        results = CURSOR.execute("SELECT * FROM employees WHERE department_id=?", (department_id,)).fetchall()
        return [cls.instance_from_db(row) for row in results]

    @classmethod
    def instance_from_db(cls, row):
        id, name, job_title, department_id = row
        if id not in cls.all:
            cls.all[id] = cls(name, job_title, department_id, id)
        return cls.all[id]

    @classmethod
    def get_all(cls):
        results = CURSOR.execute("SELECT * FROM employees").fetchall()
        return [cls.instance_from_db(row) for row in results]
