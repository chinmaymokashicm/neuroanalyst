from typing import Optional

from pydantic import BaseModel

class FormField(BaseModel):
    name: str
    description: Optional[str] = None
    type: str  # e.g., "str", "list", etc.
    required: bool = False
    default: Optional[str | list[str] | dict] = None

class FormSchema(BaseModel):
    fields: list[FormField]
    
# def get_form_schema():
#     return FormSchema(
#         fields=[
#             Field(name="name", description="The name of the pipeline", type="str", required=True),
#             Field(name="description", description="The description of the pipeline", type="str", required=True),
#             Field(name="steps", description="List of pipeline steps", type="list", required=True),
#             Field(name="checkpoint_steps", description="List of steps after which to pause the pipeline", type="list", required=False, default=[])
#         ]
#     )