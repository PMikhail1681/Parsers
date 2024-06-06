from pydantic import BaseModel, root_validator, field_validator
from typing import Optional

class Item(BaseModel):
    id: int
    name: str
    total: Optional[float] = None
    brand: str
    rating: int
    volume: int
    supplierId: int
    pics: int
    image_links: str = None
    root: int
    feedback_count: int = None
    valuation: str = None


    @root_validator(pre=True)
    def extract_total(cls, values):
        sizes = values.get('sizes')
        if sizes and len(sizes) > 0:
            values['total'] = sizes[0]['price']['total'] / 100
        return values



class Items(BaseModel):
    products: list[Item]

class Feedback(BaseModel):
    feedbackCountWithText: int
    valuation: str

