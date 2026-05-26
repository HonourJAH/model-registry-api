from sqlmodel import create_engine, Session, SQLModel

DATABASE_URL = "sqlite:///./registry.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def init_db():
    SQLModel.metadata.create_all(engine)


def get_db():
    with Session(engine) as session:
        yield session
