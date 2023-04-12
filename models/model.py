from dataclasses import dataclass, field
from typing import List

@dataclass
class User():
    name: str
    email: str
    password: str
    assigned_tasks: List["Task"] = field(default_factory=list)
    reported_tasks: List["Task"] = field(default_factory=list)
    comments: List["Comment"] = field(default_factory=list)

@dataclass
class Task(): 
    reporter_email: str   
    assignee_email: str
    title: str
    description: str
    reporter: User
    assignee: User
    comments: List["Comment"] = field(default_factory=list)

@dataclass
class Comment():
    task: Task 
    author: User
    content: str 
    