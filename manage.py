#!/usr/bin/env python
import os
import sys
import click
from app import create_app, db
from app.models import Word, Sentence, Mydict
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand, upgrade
import unittest

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate =Migrate(app, db)
manager = Manager(app)

def make_shell_context():
    return dict(app=app, db=db, Word=Word, Sentence=Sentence, Mydict=Mydict)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test():
    """Runs the unit tests without test coverage."""
    tests = unittest.TestLoader().discover('./tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


if __name__ == '__main__':
    manager.run()