import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    brand = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    currency = Column(String, default="INR", nullable=True)
    rating = Column(Float, nullable=True)
    reviews = Column(Integer, default=0)
    dimensions = Column(String, nullable=True)
    availability = Column(String, default="Available")
    store = Column(String, nullable=True)
    url = Column(String, nullable=True)
    image = Column(String, nullable=True)
    searched_query = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(String, nullable=False)
    recommended_product = Column(Text, nullable=True)  # Store JSON representation or name of recommended product
    reason = Column(Text, nullable=True)
    llm_response = Column(Text, nullable=True)  # Full JSON response string from LLM
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
