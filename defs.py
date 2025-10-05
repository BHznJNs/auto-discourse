from dataclasses import dataclass
from typing import TypedDict

class TopicPoster(TypedDict):
    """话题参与者快照"""
    user_id: int
    primary_group_id: int | None
    flair_group_id: int | None
    extras: str | None          # 如 'latest'、'latest single'
    description: str               # 如 '原始发帖人'、'频繁发帖人'

class TopicThumbnail(TypedDict):
    """缩略图多尺寸版本"""
    max_width: int | None
    max_height: int | None
    width: int
    height: int
    url: str

class Topic(TypedDict):
    """Discourse 话题级摘要对象"""
    # 1. 话题本体
    id: int
    title: str
    fancy_title: str
    slug: str
    category_id: int
    archetype: str
    created_at: str          # ISO-8601
    last_posted_at: str
    bumped_at: str

    # 2. 统计与状态
    posts_count: int
    reply_count: int
    highest_post_number: int
    views: int
    like_count: int
    has_summary: bool
    visible: bool
    closed: bool
    archived: bool
    pinned: bool
    pinned_globally: bool
    unseen: bool
    bookmarked: bool | None
    liked: bool | None
    has_accepted_answer: bool
    can_have_answer: bool
    can_vote: bool

    # 3. 媒体与标签
    image_url: str | None
    thumbnails: list[TopicThumbnail] | None
    tags: list[str]
    tags_descriptions: dict[str, str]
    featured_link: str | None

    # 4. 参与者快照
    last_poster_username: str
    posters: list[TopicPoster]

# --- --- --- --- --- ---

class TopicList(TypedDict):
    topics: list[Topic]

class TopicsResponse(TypedDict):
    topic_list: TopicList
    users: list
    groups: list
