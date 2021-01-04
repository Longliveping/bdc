import unittest
from flask import current_app
from app import create_app, db
from app.models import Word, Article, Sentence, Mydict, sentences_words_relations, \
    Sequence, Annotation, Customer, Order, Item, OrderLine
import os
import time


class Timer:
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, value, tb):
        self.duration = time.time() - self.start

def drop_everything():
    """(On a live db) drops all foreign key constraints before dropping all tables.
    Workaround for SQLAlchemy not doing DROP ## CASCADE for drop_all()
    (https://github.com/pallets/flask-sqlalchemy/issues/722)
    """
    from sqlalchemy.engine.reflection import Inspector
    from sqlalchemy.schema import DropConstraint, DropTable, MetaData, Table

    con = db.engine.connect()
    trans = con.begin()
    inspector = Inspector.from_engine(db.engine)

    # We need to re-create a minimal metadata with only the required things to
    # successfully emit drop constraints and tables commands for postgres (based
    # on the actual schema of the running instance)
    meta = MetaData()
    tables = []
    all_fkeys = []

    for table_name in inspector.get_table_names():
        fkeys = []

        for fkey in inspector.get_foreign_keys(table_name):
            if not fkey["name"]:
                continue

            fkeys.append(db.ForeignKeyConstraint((), (), name=fkey["name"]))

        tables.append(Table(table_name, meta, *fkeys))
        all_fkeys.extend(fkeys)

    for fkey in all_fkeys:
        con.execute(DropConstraint(fkey))

    for table in tables:
        con.execute(DropTable(table))

    trans.commit()

def get_file(filetype):
    sourcedir = current_app.config.get('TESTING_FOLDER')
    for basename in os.listdir(sourcedir):
        file = os.path.join(sourcedir, basename)
        basename = os.path.basename(file)
        extention = basename.split('.')[1]
        if extention == filetype:
            return file

class WordsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()


    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        # drop_everything()
        cls.app_context.pop()

    def test_orderline(self):
        pass

    def test_customer_item(self):
        c1 = Customer(first_name='Toby',
                      last_name='Miller',
                      username='tmiller',
                      email='tmiller@example.com',
                      address='1662 Kinney Street',
                      town='Wolfden'
                      )

        c2 = Customer(first_name='Scott',
                      last_name='Harvey',
                      username='scottharvey',
                      email='scottharvey@example.com',
                      address='424 Patterson Street',
                      town='Beckinsdale'
                      )
        c3 = Customer(
            first_name="John",
            last_name="Lara",
            username="johnlara",
            email="johnlara@mail.com",
            address="3073 Derek Drive",
            town="Norfolk"
        )

        c4 = Customer(
            first_name = "Sarah",
            last_name = "Tomlin",
            username = "sarahtomlin",
            email = "sarahtomlin@mail.com",
            address = "3572 Poplar Avenue",
            town = "Norfolk"
        )

        c5 = Customer(first_name = 'Toby',
                      last_name = 'Miller',
                      username = 'tmiller',
                      email = 'tmiller@example.com',
                      address = '1662 Kinney Street',
                      town = 'Wolfden'
                      )

        c6 = Customer(first_name = 'Scott',
                      last_name = 'Harvey',
                      username = 'scottharvey',
                      email = 'scottharvey@example.com',
                      address = '424 Patterson Street',
                      town = 'Beckinsdale'
                      )

        db.session.add_all([c1, c2, c3, c4, c5, c6])
        db.session.commit()

        i1 = Item(name = 'Chair', cost_price = 9.21, selling_price = 10.81, quantity = 5)
        i2 = Item(name = 'Pen', cost_price = 3.45, selling_price = 4.51, quantity = 3)
        i3 = Item(name = 'Headphone', cost_price = 15.52, selling_price = 16.81, quantity = 50)
        i4 = Item(name = 'Travel Bag', cost_price = 20.1, selling_price = 24.21, quantity = 50)
        i5 = Item(name = 'Keyboard', cost_price = 20.1, selling_price = 22.11, quantity = 50)
        i6 = Item(name = 'Monitor', cost_price = 200.14, selling_price = 212.89, quantity = 50)
        i7 = Item(name = 'Watch', cost_price = 100.58, selling_price = 104.41, quantity = 50)
        i8 = Item(name = 'Water Bottle', cost_price = 20.89, selling_price = 25, quantity = 50)

        db.session.add_all([i1, i2, i3, i4, i5, i6, i7, i8])
        db.session.commit()

        o1 = Order(customer = c1)
        o2 = Order(customer = c1)

        line_item1 = OrderLine(order = o1, item = i1, quantity =  3)
        line_item2 = OrderLine(order = o1, item = i2, quantity =  2)
        line_item3 = OrderLine(order = o2, item = i1, quantity =  1)
        line_item4 = OrderLine(order = o2, item = i2, quantity =  4)

        db.session.add_all([o1, o2])
        db.session.add_all([line_item1, line_item2,line_item3,line_item4])

        # db.session.new
        db.session.commit()

        o3 = Order(customer = c2)
        orderline1 = OrderLine(item = i1, quantity = 5)
        orderline2 = OrderLine(item = i2, quantity = 10)

        o3.orderlines.append(orderline1)
        o3.orderlines.append(orderline2)

        db.session.add_all([o3])
        db.session.commit()

    # def test_sequence(self):
    #     for i in range(1000,2000):
    #         sequence = Sequence(name=f's{i}')
    #         sequence.annotations = [Annotation(name=f'a{i}', sequence=sequence),
    #                                 Annotation(name=f'b{i}', sequence=sequence)]
    #         db.session.add(sequence)
    #         db.session.add_all(sequence.annotations)
    #         # annotation = Annotation(name=f'a{i}', sequence=sequence)
    #         # db.session.add_all([sequence, annotation])
    #     with Timer() as timer:
    #         db.session.commit()
    #     print(timer.duration, 'seconds')
    #     count_s = Sequence.query.count()
    #     count_a = Annotation.query.count()
    #     self.assertTrue(count_s>0)
    #     self.assertTrue(count_a>0)

    def test_sentences_to_words(self):
        # Sentence.import_sentence_to_words(get_file())
        # count = sentences_words_relations.query.count()
        # self.assertTrue(count>0)
        pass

    def test_import_mydict(self):
        Mydict.imports()
        count = Mydict.query.count()
        self.assertTrue(count>0)

    def test_import_sentence(self):
        Sentence.import_sentence(get_file('txt'))
        count = Sentence.query.count()
        self.assertTrue(count>0)

    def test_create_words_to_wheres(self):
        pass

    def test_import_articles(self):
        Article.import_articles(get_file('txt'))
        count = Article.query.count()
        self.assertTrue(count>0)

    def test_import_word(self):
        Word.import_words(get_file('csv'))
        count = Word.query.count()
        self.assertTrue(count>0)



