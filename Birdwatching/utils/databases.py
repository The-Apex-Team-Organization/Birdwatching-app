
from sqlalchemy import DateTime, insert, select, func, text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Sequence
from sqlalchemy import Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

engine = None


def init_db(app):
    global engine
    engine = create_engine(app.config["DATABASE_URL"], echo=True)


class Base(DeclarativeBase):
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column("id", Integer, Sequence(
        "users_id_seq", 1), primary_key=True, nullable=False)
    user_role: Mapped[str] = mapped_column(
        "user_role", String, default="user", nullable=False)
    username: Mapped[str] = mapped_column(
        "username", String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(
        "password", String, nullable=False)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, user_role={self.user_role!r}, username={self.username!r}, password={self.password!r})"


class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column("id", Integer, Sequence(
        "posts_id_seq", 1), primary_key=True, nullable=False)

    user_id: Mapped[int] = mapped_column(
        "user_id", Integer, nullable=False)

    created: Mapped[DateTime] = mapped_column(
        "created", DateTime, server_default=func.now(), nullable=False)

    location: Mapped[str] = mapped_column(
        "location", String, default="Kyiv", nullable=False)

    image_path: Mapped[str] = mapped_column(
        "image_path", String, nullable=False)

    def __repr__(self) -> str:
        return f"Post(id={self.id!r}, user_id={self.user_id!r}, created={self.created!r}, location={self.location!r}, image_path={self.image_path!r})"


class BlackList(Base):
    __tablename__ = "black_list"
    id: Mapped[int] = mapped_column("id", Integer, Sequence(
        "black_list_id_seq", 1), primary_key=True, nullable=False)
    ip_address: Mapped[str] = mapped_column(
        "ip_address", String, unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"BlackList(id={self.id!r}, ip_address={self.ip_address!r}"


def get_post(post_id):
    stmt = select(Post).where(Post.id == post_id)
    res = None
    with Session(engine) as session:
        res = session.scalar(stmt).to_dict()
    return res


def get_user_posts(user_id):
    stmt = select(Post).where(Post.user_id == user_id)
    res = None
    with Session(engine) as session:
        res = session.scalars(stmt).all()
        return [p.to_dict() for p in res]
    return None


def insert_user(username, hashed_pw):
    stmt = insert(User).values(username=username, password=hashed_pw)
    with Session(engine) as session:
        session.execute(stmt)
        session.commit()
    return


def post_sql(sql, params=None):
    with Session(engine) as session:
        session.execute(text(sql), params)
        session.commit()


def get_user(id):
    stmt = select(User.id,
                  User.user_role,
                  User.username,
                  User.password).where(User.id == id)
    res = None
    with Session(engine) as session:
        res = session.execute(stmt).mappings().first()
    return res


def get_user_by_username(username):
    stmt = select(User.id,
                  User.user_role,
                  User.username,
                  User.password).where(User.username == username)
    res = None
    with Session(engine) as session:
        res = session.execute(stmt).mappings().first()
    return res


def get_ip_address(hashed_ip):
    stmt = select(BlackList.ip_address).where(
        BlackList.ip_address == hashed_ip)
    res = None
    with Session(engine) as session:
        res = session.execute(stmt).mappings().first()
    return res


def get_users():
    stmt = select(User.id, User.user_role, User.username)
    res = None
    with Session(engine) as session:
        res = session.execute(stmt).mappings().all()
    return res


def get_posts_users():
    stmt = select(Post.id,
                  Post.user_id,
                  Post.location,
                  Post.image_path,
                  Post.created,
                  User.username).join(User, Post.user_id == User.id)
    res = None
    with Session(engine) as session:
        res = session.execute(stmt).mappings().all()
    return res
