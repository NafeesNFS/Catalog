import sys
import os
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    picture = Column(String(300))


class WebsiteName(Base):
    __tablename__ = 'websitename'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="warname")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self.name,
            'id': self.id
        }


class ToolName(Base):
    __tablename__ = 'toolname'
    id = Column(Integer, primary_key=True)
    name = Column(String(350), nullable=False)
    discription = Column(String(150))
    year = Column(String(10))
    founder = Column(String(250))
    date = Column(DateTime, nullable=False)
    websitenameid = Column(Integer, ForeignKey('websitename.id'))
    websitename = relationship(
        WebsiteName, backref=backref('toolname', cascade='all, delete'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="toolname")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self. name,
            'discription': self. discription,
            'year': self. year,
            'founder': self. founder,
            'date': self. date,
            'id': self. id
        }

engin = create_engine('sqlite:///websites.db')
Base.metadata.create_all(engin)
