from pydantic import BaseModel
from typing import List, Optional


class SharedGoalCreate(BaseModel):
    thrust_area_id: int
    title: str
    description: Optional[str] = None
    uom_type: str
    target: Optional[float] = None
    target_date: Optional[str] = None
    employee_ids: List[int]
    default_weightage: float = 10.0


class SharedGoalWeightageUpdate(BaseModel):
    weightage: float
