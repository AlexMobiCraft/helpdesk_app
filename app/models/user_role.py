from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class UserRole(Base):
    __tablename__ = "user_roles"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    
    # Обратная связь с пользователями
    users = relationship("User", back_populates="role")
    
    def __repr__(self):
        return f"<UserRole {self.name}>"