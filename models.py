from sqlalchemy import Column, Integer, String, Boolean
from database import Base

# 1. 사용자 테이블
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)      
    user_id = Column(String(50))                            
    phone = Column(String(100), unique=True, index=True)     
    password = Column(String(100))                          

# 2. 노래방 부스(방) 테이블
class Booth(Base):
    __tablename__ = "booths"

    booth_id = Column(Integer, primary_key=True, index=True) # 방 번호 (1, 2, 3...)
    name = Column(String(50))                                # 방 이름
    status = Column(String(20), default="empty")             # 상태 (empty, busy)