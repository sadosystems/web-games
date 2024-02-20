from enum import Enum
from dataclasses import dataclass, field

class Elevation(Enum):
    GOD = 1 # Reserved for me
    STAFF = 2 # Other developers
    ADMIN = 3 # Trusted community members
    MEMBER = 4 # Paying members
    USER = 5 # Email verified 
    GUEST = 6 # No email verified 

    def __str__(self):
        return self.name.lower()

