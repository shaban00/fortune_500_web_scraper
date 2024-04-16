from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

def create_db_session():
    engine = create_engine('mysql+mysqlconnector://shab:@localhost/fortune_500_web_scraper')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    
    class SessionScope:
        def __enter__(self):
            self.session = Session()
            return self.session

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.session.close()

    return SessionScope()

