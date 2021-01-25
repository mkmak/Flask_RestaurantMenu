Simple Restaurant Menu Web application

SQLALchemy is used as the ORM (Object-Relational Mapping) that translates Python classes to tables on relational databases and automatically converts function calls to SQL statements.
sqlite3 is used for testing

CRUD = CREATE, READ, UPDATE, DELETE

"webserver.py" uses the python's http.server library to implement the restaurants CRUD operations.

"project.py" uses the Flask framework instead of http.server library. It is more convenience and organized. It contains implementation of restaurants and each restaurant's menu items CRUD operations. JSON data can also retrieve through API endpoints.

"populate_menu.py" is simply a script to populate the database with data.
