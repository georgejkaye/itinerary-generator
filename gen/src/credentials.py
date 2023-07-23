from dataclasses import dataclass
from dotenv import dotenv_values


@dataclass
class Credentials:
    user: str
    password: str


rtt = "RTT"


def get_api_credentials(prefix: str) -> Credentials:
    env_values = dotenv_values()
    user = env_values.get(f"{prefix}_USER")
    password = env_values.get(f"{prefix}_PASSWD")
    if user is not None and password is not None:
        return Credentials(user, password)
    else:
        raise RuntimeError(f"Invalid {prefix} user and password")
