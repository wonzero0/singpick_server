from sqlalchemy import Column, Integer, String
from database import Base

# 이 코드가 MySQL에 'users'라는 테이블을 자동으로 만들어줍니다.
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)      # 고유 번호 (1번, 2번...)
    user_id = Column(String(50))                            # 영문 아이디 (예: hong123)
    phone = Column(String(20), unique=True, index=True)     # 전화번호 (로그인 ID 역할)
    password = Column(String(100))                          # 암호화된 비밀번호