from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class SharedGoalLink(Base):
    __tablename__ = "shared_goal_links"

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    weightage = Column(Float, nullable=False, default=10.0)

    goal = relationship("Goal", back_populates="shared_links")
    employee = relationship("User")
