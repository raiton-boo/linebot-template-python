from . import (
    message_event,
    follow_event,
    unfollow_event,
    join_event,
    leave_event,
    member_joined_event,
    member_left_event,
    postback_event,
    beacon_event,
    unsend_event,
    video_play_complete_event,
    account_link_event,
)

AVAILABLE_HANDLERS = [
    message_event,
    follow_event,
    unfollow_event,
    join_event,
    leave_event,
    member_joined_event,
    member_left_event,
    postback_event,
    beacon_event,
    unsend_event,
    video_play_complete_event,
    account_link_event,
]
