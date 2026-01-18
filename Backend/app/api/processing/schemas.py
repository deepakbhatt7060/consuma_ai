from pydantic import BaseModel, HttpUrl, field_serializer

class WorkPayload(BaseModel):
    number: int

class AsyncPayload(WorkPayload):
    callback_url: HttpUrl
    
    @field_serializer("callback_url")
    def serialize_callback_url(self, v):
        return str(v)
    
