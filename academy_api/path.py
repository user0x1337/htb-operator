import datetime
from typing import Optional, List

import dateutil.parser

from academy_api import academy_client


class SkillPath(academy_client.BaseAcademyApiObject):
    title: str
    description: str
    formatted_title: str
    published: bool
    type: str
    enrolled: bool
    progress: float
    estimated_time_of_completion_in_minutes: Optional[int]
    estimated_time_of_completion: Optional[str]
    modules_count: int
    cubes: int
    cubes_reward: int
    cubes_required_to_complete: int
    cubes_awarded_upon_completion: int
    cubes_cost: dict[str, float]
    state: str
    max_tier_id: id
    max_tier_name: str
    max_tier_number: int
    max_tier_cubes_to_unlock: int
    difficulty_id: int
    difficulty_text: str
    difficulty_level: int
    module_ids: List[int]
    created_at: datetime
    updated_at: datetime


    # noinspection PyUnresolvedReferences
    def __init__(self, data: dict, _client: "AcademyClient"):
        self._client = _client
        self.id = data['id']
        self.title = data['title']
        self.description = data['description']
        self.formatted_title = data['formatted_title']
        self.published = data['published']
        self.type = data['type']
        self.enrolled = data['enrolled']
        self.progress = data['progress']
        self.estimated_time_of_completion = data['estimated_time_of_completion']
        self.estimated_time_of_completion_in_minutes = data['estimated_time_of_completion_in_minutes']
        self.modules_count = data['modules_count']
        self.cubes = data['cubes']
        self.cubes_reward = data['cubes_reward']
        self.cubes_required_to_complete = data['cubes_required_to_complete']
        self.cubes_awarded_upon_completion = data['cubes_awarded_upon_completion']
        self.cubes_cost = data['cubes_cost']
        self.state = data['state']
        self.max_tier_id = data["max_tier"]['id']
        self.max_tier_name = data["max_tier"]['name']
        self.max_tier_number = data["max_tier"]['number']
        self.max_tier_cubes_to_unlock = data["max_tier"]['cubes_to_unlock']
        self.difficulty_id = data["difficulty"]['id']
        self.difficulty_text = data["difficulty"]["text"]
        self.difficulty_level = data["difficulty"]["level"]
        self.module_ids = data["module_ids"]
        self.created_at = dateutil.parser.parse(data['created_at']).replace(tzinfo=datetime.timezone.utc)
        self.updated_at = dateutil.parser.parse(data['created_at']).replace(tzinfo=datetime.timezone.utc)

    def __repr__(self):
        return f'<Path {self.id} | {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'formatted_title': self.formatted_title,
            'published': self.published,
            'type': self.type,
            'enrolled': self.enrolled,
            'progress': self.progress,
            'estimated_time_of_completion': self.estimated_time_of_completion,
            'estimated_time_of_completion_in_minutes': self.estimated_time_of_completion_in_minutes,
            'modules_count': self.modules_count,
            'cubes': self.cubes,
            'cubes_reward': self.cubes_reward,
            'cubes_required_to_complete': self.cubes_required_to_complete,
            'cubes_awarded_upon_completion': self.cubes_awarded_upon_completion,
            'cubes_cost': self.cubes_cost,
            'state': self.state,
            'max_tier_id': self.max_tier_id,
            'max_tier_name': self.max_tier_name,
            'max_tier_number': self.max_tier_number,
            'max_tier_cubes_to_unlock': self.max_tier_cubes_to_unlock,
            'difficulty_id': self.difficulty_id,
            'difficulty_text': self.difficulty_text,
            'difficulty_level': self.difficulty_level,
            'module_ids': self.module_ids,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
