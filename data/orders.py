import datetime
import sqlalchemy

from data.db_session import SqlAlchemyBase


class Order(SqlAlchemyBase):  # таблица в бд с заказами
    __tablename__ = 'orders'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    place = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, nullable=True)
    data_holiday = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    mobile_phone = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    holiday = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    number_of_guests = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    def __repr__(self):
        return f"<order> {self.id} {self.name} {self.place} {self.email} {self.data_holiday} {self.mobile_phone} {self.holiday}"

