from enum import Enum

class RequestMode(str, Enum):
    async_ = "async"
    sync = "sync"