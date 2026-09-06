from pydantic import BaseModel ,EmailStr,AnyUrl,Field,model_validator
from typing import List, Optional

class User(BaseModel):
    name: str
    age: int=Field(..., gt=0, description="Age must be greater than zero")
    url:AnyUrl
    email:EmailStr
    item: List[str] 


def add_user_data(user_data:User):
    print(f"User Name: {user_data.name}, Age: {user_data.age}")
    


user={"name": "John Doe", "age": 30}

patient = User(**user)
add_user_data(patient)