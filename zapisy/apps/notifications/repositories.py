from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

import redis

from django.contrib.auth.models import User

from apps.common.redis import flush_by_pattern
from apps.notifications.datatypes import Notification
from apps.notifications.serialization import JsonNotificationSerializer, NotificationSerializer

KEY_PREFIX = 'notifications:'
KEY_PATTERN = KEY_PREFIX + '*'


class NotificationsRepository(ABC):

    @abstractmethod
    def get_count_for_user(self, user: User) -> int:
        pass

    @abstractmethod
    def get_all_for_user(self, user: User) -> List[Notification]:
        pass

    @abstractmethod
    def get_unsent_for_user(self, user: User) -> List[Notification]:
        pass

    @abstractmethod
    def mark_as_sent(self, user: User, notification: Notification) -> None:
        pass

    @abstractmethod
    def save(self, user: User, notification: Notification) -> None:
        pass

    @abstractmethod
    def remove_all(self, user: User) -> None:
        pass

    @abstractmethod
    def flush(self) -> None:
        pass

    @abstractmethod
    def remove_all_older_than(self, user: User, until: datetime) -> int:
        pass

    @abstractmethod
    def remove_one_with_id(self, user: User, ID: str) -> int:
        pass


class RedisNotificationsRepository(NotificationsRepository):

    def __init__(self, serializer: NotificationSerializer):
        self.serializer = serializer
        self.redis_client = redis.Redis()
        self.removed_count = 0

    def get_count_for_user(self, user: User) -> int:
        # SCARD returns 0 if one of them does not exist
        # so no need to check for key existence here
        unsent_count = self.redis_client.scard(
            self._generate_unsent_key_for_user(user))
        sent_count = self.redis_client.scard(
            self._generate_sent_key_for_user(user))

        return unsent_count + sent_count

    def get_all_for_user(self, user: User) -> List[Notification]:
        serialized = self.redis_client.smembers(
            self._generate_unsent_key_for_user(user))
        serialized = serialized.union(
            self.redis_client.smembers(self._generate_sent_key_for_user(user)))

        return list(map(self.serializer.deserialize, serialized))

    def get_unsent_for_user(self, user: User) -> List[Notification]:
        return list(map(
            self.serializer.deserialize,
            self.redis_client.smembers(self._generate_unsent_key_for_user(user))))

    def mark_as_sent(self, user: User, notification: Notification) -> None:
        serialized = self.serializer.serialize(notification)

        self.redis_client.srem(
            self._generate_unsent_key_for_user(user), serialized)
        self.redis_client.sadd(
            self._generate_sent_key_for_user(user), serialized)

    def save(self, user: User, notification: Notification) -> None:
        self.redis_client.sadd(
            self._generate_unsent_key_for_user(user),
            self.serializer.serialize(notification))

    def remove_all(self, user: User) -> None:
        self.redis_client.delete(self._generate_unsent_key_for_user(user))
        self.redis_client.delete(self._generate_sent_key_for_user(user))

    def flush(self) -> None:
        flush_by_pattern(self.redis_client, KEY_PATTERN)

    def remove_all_older_than(self, user: User, until: datetime) -> int:
        self.removed_count = 0

        self._remove_all_older_than(
            self._generate_unsent_key_for_user(user), until)
        self._remove_all_older_than(
            self._generate_sent_key_for_user(user), until)

        return self.removed_count

    def _remove_all_older_than(self, key: str, point_in_time: datetime) -> int:
        notifications_under_that_key = map(
            self.serializer.deserialize,
            self.redis_client.smembers(key))

        for notification in notifications_under_that_key:
            if notification.issued_on < point_in_time:
                self.redis_client.srem(
                    key, self.serializer.serialize(notification))
                self.removed_count += 1
        return self.removed_count

    def remove_one_with_id(self, user: User, ID: str) -> int:
        self.removed_count = 0

        self._remove_one_with_id(self._generate_unsent_key_for_user(user), ID)
        self._remove_one_with_id(self._generate_sent_key_for_user(user), ID)

        return self.removed_count

    def _remove_one_with_id(self, key: str, ID: str) -> int:
        notifications_under_that_key = map(self.serializer.deserialize,
                                           self.redis_client.smembers(key))

        for notification in notifications_under_that_key:
            if notification.id == ID:
                self.redis_client.srem(key, self.serializer.serialize(notification))
                self.removed_count += 1
        return self.removed_count

    def _generate_unsent_key_for_user(self, user: User) -> str:
        return f'{KEY_PREFIX}unsent#{user.id}'

    def _generate_sent_key_for_user(self, user: User) -> str:
        return f'{KEY_PREFIX}sent#{user.id}'


def get_notifications_repository() -> NotificationsRepository:
    """Returns a default implementation of NotificationsRepository.

    Return an object implementing NotificationsRepository interface,
    thus providing access to _some_ notifications storage.
    Client code should always call this method instead of
    instantiating such classes directly.
    """
    return RedisNotificationsRepository(JsonNotificationSerializer())
