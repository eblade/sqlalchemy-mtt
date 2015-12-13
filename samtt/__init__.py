"""
Multithread transaction support for SQLAlchemy.

Usage:

    import samtt
    
    db = samtt.init(PATH)
    
    # Get this db engines' transaction:
    with db.transaction() as t:
        entry = t.query(Entry).filter(Entry.id==id).one()

    # Get a thread-specific transaction:
    with samtt.get_db().transaction() as t:
        entry = t.query(Entry).filter(Entry.id==id).one()
        entry.name = "New name"
    
    # Commits are done automatically. Transactions are nested, so commits happen
    # when the outermost transaction is done.

"""


__version__ = "0.1"


import os, logging, threading, hashlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import CreateTable


module_local = threading.local()
module_local.engine = None


Base = declarative_base()


class Database(object):
    local = threading.local()
    sql_path = None
    
    def __init__(self, sql_path=None):
        Database.sql_path = sql_path or Database.sql_path
        assert Database.sql_path, "SQL Path must be given at some point"
        logging.debug("Creating new Database Engine at %s.", Database.sql_path)
        self.local.in_transaction = False
        self.local.engine = create_engine(Database.sql_path)
        self.local.session_maker = sessionmaker()
        self.local.session_maker.configure(bind=self.local.engine)

    def transaction(self):
        return Transaction(self.local)

    def create_all(self):
        Base.metadata.create_all(self.local.engine)

    def get_sql_for_table(self, table):
        return CreateTable(table.__table__).compile(self.local.engine)


class Transaction(object):
    def __init__(self, local):
        self.local = local
        self.inner = local.in_transaction
        if not local.in_transaction:
            local.in_transaction = True
            self.session = local.session_maker()
            local.session = self.session
        else:
            self.session = local.session
        logging.debug("DB connect (%s)", 'inner' if self.inner else 'outer')

    def __enter__(self):
        return self.session

    def __exit__(self, type, value, traceback):
        if self.inner:
            logging.debug("DB inner end")
            if type is None:
                logging.debug("DB inner ok")
                return True
            else:
                logging.error("DB inner error (%s, %s)", str(type), str(value))
                return False
        else:
            try:
                if type is None:
                    logging.debug("DB commit")
                    self.session.commit()
                    return True
                else:
                    logging.error("DB rollback (%s, %s)", str(type), str(value))
                    self.session.rollback()
                    return False
            finally:
                logging.debug("DB close")
                self.local.in_transaction = False
                self.session.close()


def init(sql_path):
    """
    Initialize a thread-local instance of the database.
    """
    module_local.engine = Database(sql_path)
    return module_local.engine


def get_db():
    """
    Get the thread-local instance of the database or create one.
    However, init() needs to be run once.
    """
    if hasattr(module_local, 'engine'):
        return module_local.engine
    else:
        logging.debug("Creating a new Database Engine for thread %s", threading.current_thread().name)
        module_local.engine = Database()
        return module_local.engine
