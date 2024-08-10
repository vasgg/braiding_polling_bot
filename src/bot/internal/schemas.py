from pydantic import BaseModel

from bot.internal.enums import Nomination, TaskType


class VoteTask(BaseModel):
    nomination: Nomination
    user_fullname: str
    user_id: int
    user_username: str
    user_phone_number: str
    nominee_name: str
    user_vote_for: int
    date: str


class CounterTask(BaseModel):
    counter: int


class TaskModel(BaseModel):
    task_type: TaskType
    task_data: VoteTask | CounterTask
