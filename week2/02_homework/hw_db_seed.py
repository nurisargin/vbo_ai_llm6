"""Seed two related tables so that answering a question requires a JOIN.

    departments(id PK, name, location)
    employees(id PK, full_name, department_id -> departments.id, salary, country)

Run once before starting the server:  python hw_db_seed.py
"""
from sqlmodel import Field, Session, SQLModel

from hw_db import get_engine


class Department(SQLModel, table=True):
    __tablename__ = "departments"
    id: int = Field(primary_key=True)
    name: str
    location: str


class Employee(SQLModel, table=True):
    __tablename__ = "employees"
    id: int | None = Field(default=None, primary_key=True)
    full_name: str
    department_id: int = Field(foreign_key="departments.id")
    salary: int
    country: str


DEPARTMENTS = [
    Department(id=1, name="Engineering", location="Berlin"),
    Department(id=2, name="Sales", location="London"),
    Department(id=3, name="HR", location="Istanbul"),
]

EMPLOYEES = [
    Employee(full_name="Alice Johnson", department_id=1, salary=145000, country="USA"),
    Employee(full_name="Bob Smith", department_id=1, salary=132000, country="USA"),
    Employee(full_name="Defne Yılmaz", department_id=1, salary=120000, country="Türkiye"),
    Employee(full_name="Carlos Ruiz", department_id=2, salary=98000, country="Spain"),
    Employee(full_name="Diana Wilson", department_id=2, salary=156000, country="USA"),
    Employee(full_name="Emir Demir", department_id=2, salary=88000, country="Türkiye"),
    Employee(full_name="Fatima Khan", department_id=3, salary=76000, country="UK"),
    Employee(full_name="George Brown", department_id=3, salary=81000, country="USA"),
]


def main():
    engine = get_engine()
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all(DEPARTMENTS)
        session.commit()  # departments first, so the foreign keys exist
        session.add_all(EMPLOYEES)
        session.commit()
    print(f"Seeded {len(DEPARTMENTS)} departments and {len(EMPLOYEES)} employees into {engine.url}")


if __name__ == "__main__":
    main()
