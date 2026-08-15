import sys, os
sys.path.insert(0, os.getcwd())
import unittest
from unittest.mock import patch
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import mysql, sqlite
from app.config import Config, get_db_uri
from app.models import User, Department, Employee, Attendance, Leave

class TestMySQLMigration(unittest.TestCase):
    def test_config_mysql_url_transformation(self):
        os.environ['MYSQL_URL'] = 'mysql://root:password@localhost:3306/employee_db'
        self.assertEqual(get_db_uri(), 'mysql+pymysql://root:password@localhost:3306/employee_db')
        self.assertEqual(Config.SQLALCHEMY_ENGINE_OPTIONS, {'pool_pre_ping': True, 'pool_recycle': 280})
        del os.environ['MYSQL_URL']

    def test_config_database_url_mysql_transformation(self):
        os.environ['DATABASE_URL'] = 'mysql://admin:secret@127.0.0.1:3306/emp_db'
        self.assertEqual(get_db_uri(), 'mysql+pymysql://admin:secret@127.0.0.1:3306/emp_db')
        del os.environ['DATABASE_URL']

    def test_config_sqlite_fallback(self):
        if 'DATABASE_URL' in os.environ: del os.environ['DATABASE_URL']
        if 'MYSQL_URL' in os.environ: del os.environ['MYSQL_URL']
        self.assertTrue(get_db_uri().startswith('sqlite:///'))

    def test_mysql_ddl_table_compilation(self):
        mysql_dialect = mysql.dialect()
        tables = [User.__table__, Department.__table__, Employee.__table__, Attendance.__table__, Leave.__table__]
        for t in tables:
            ddl = str(CreateTable(t).compile(dialect=mysql_dialect))
            self.assertTrue(len(ddl) > 0, f"Table DDL empty for {t.name}")
            self.assertIn("CREATE TABLE", ddl)

if __name__ == '__main__':
    unittest.main()
