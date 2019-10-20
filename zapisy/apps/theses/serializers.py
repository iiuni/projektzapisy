"""Defines all (de)serialization logic related
to objects used in the theses system, that is:
* packing/unpacking logic
* validation
* fine-grained permissions checks
* performing modifications/adding new objects
"""
from typing import Dict, Any, Optional, List

from rest_framework import serializers, exceptions
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.contrib.auth.models import User

from apps.users.models import Employee, Student, BaseUser
from .models import (
    Thesis, ThesisStatus, MAX_THESIS_TITLE_LEN,
    VotesToProcess, VoteToProcess,
    MIN_REJECTION_REASON_LENGTH, MAX_REJECTION_REASON_LENGTH,
)
from .users import (
    get_theses_user_full_name, is_theses_admin, is_theses_regular_employee,
    is_theses_board_member,
)
from .permissions import (
    can_set_advisor, can_set_status_for_new, can_change_status_to,
    can_change_title, can_cast_vote_as_user, can_see_thesis_rejection_reason,
    can_see_thesis_votes, can_change_vote_for_thesis
)
from .drf_errors import ThesisNameConflict
from .enums import ThesisUserType, ThesisKind, ThesisVote
from .defs import MAX_STUDENTS_PER_THESIS

GenericDict = Dict[str, Any]


class ThesesPersonSerializer(serializers.Serializer):
    """Used to serialize user profiles as needed by various parts of the system;
    we don't want to use the user serializer from apps.api.rest
    because it serializes a lot of unnecessary data
    """
    default_error_messages = serializers.PrimaryKeyRelatedField.default_error_messages

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop("queryset", None)
        super().__init__(*args, **kwargs)

    def to_representation(self, instance: BaseUser):
        result = {
            "id": instance.pk,
            "name": get_theses_user_full_name(instance)
        }
        if isinstance(instance, Employee):
            result["username"] = instance.user.username
        return result

    def to_internal_value(self, data):
        if not self.queryset:
            raise ImproperlyConfigured(
                "PersonSerializerForThesis cannot deserialize without a queryset provided"
            )
        try:
            return self.queryset.get(pk=data)
        except ObjectDoesNotExist:
            self.fail('does_not_exist', pk_value=data)
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data).__name__)


def can_vote_be_set_for(voter: Employee, thesis: Optional[Thesis]):
    return (
        is_theses_board_member(voter.user) or
        # Changing the value of an existing vote is always legal (assuming correct permissions)
        # even if the user is no longer a member of the theses board
        thesis and thesis.votes.filter(voter=voter).count()
    )


def convert_votes(votes, thesis: Optional[Thesis]) -> VotesToProcess:
    """Validate & convert the votes dict for a thesis to internal representation
    for later processing
    """
    if not isinstance(votes, dict):
        raise exceptions.ParseError("\"votes\" must be a dict")
    result = []
    for key, voteinfo in votes.items():
        try:
            voter_id = int(key)
            voter = Employee.objects.get(pk=voter_id)
        except (ValueError, Employee.DoesNotExist):
            raise exceptions.ParseError(f'bad voter id {key}')
        if not can_vote_be_set_for(voter, thesis):
            raise exceptions.ParseError(f'cannot set vote for {voter}')
        try:
            vote_value = ThesisVote(voteinfo["value"])
        except (TypeError, KeyError, ValueError):
            raise exceptions.ParseError("vote value for voter has wrong format")
        if vote_value == ThesisVote.REJECTED:
            try:
                rejection_reason = voteinfo["reason"]
            except (KeyError, ValueError):
                raise exceptions.ParseError("no reason specified for rejecting vote")
            reason_len = len(rejection_reason)
            if not (MIN_REJECTION_REASON_LENGTH <= reason_len <= MAX_REJECTION_REASON_LENGTH):
                raise exceptions.ParseError("invalid reason specified for rejecting vote")
        else:
            rejection_reason = ""
        result.append(VoteToProcess(voter, vote_value, rejection_reason))
    return result


def validate_new_title_for_instance(title: str, instance: Optional[Thesis]):
    """Validate that the supplied title is valid for the supplied instance,
    or for a new thesis if not supplied"""
    # There is a potential race condition here,
    # but it seems Django doesn't think you should worry about it;
    # they have very similar logic in their validate_unique method:
    # https://docs.djangoproject.com/en/2.1/ref/models/instances/#django.db.models.Model.validate_unique
    # (they first perform this validation, and later hit the DB with the update)
    # and SO seems to agree: https://stackoverflow.com/q/25702813
    qs = Thesis.objects.filter(title=title.strip())
    if instance:
        qs = qs.exclude(pk=instance.pk)
    if qs.exists():
        raise ThesisNameConflict()


def check_votes_permissions(user: User, votes: List, thesis: Optional[Thesis]):
    """Check that the specified user is permitted to modify the votes as specified"""
    if thesis and not can_change_vote_for_thesis(user, thesis):
        raise exceptions.PermissionDenied(f'this user is not permitted to change vote(s) for thesis {thesis}')
    for vote in votes:
        if not can_cast_vote_as_user(user, vote.voter.user):
            raise exceptions.PermissionDenied(f'user {user} cannot change the vote of {vote.voter}')


def check_advisor_permissions(user: User, advisor: Employee):
    """Check that the current user is permitted to set the specified advisor"""
    if not can_set_advisor(user, advisor):
        raise exceptions.PermissionDenied(f'This type of user cannot set advisor to {advisor}')


def serialize_thesis_votes(thesis: Thesis) -> Dict[int, GenericDict]:
    """Serializes the votes into a dict if the user has permission to see them
    The rejection reason will also be specified for rejecting votes
    """
    definite_votes = (
        vote for vote in thesis.votes.all()
        if vote.value != ThesisVote.NONE.value
    )
    return {
        vote.voter.pk: (
            {"value": vote.value, "reason": vote.reason}
            if vote.value == ThesisVote.REJECTED.value
            else {"value": vote.value}
        )
        for vote in definite_votes
    }


class ThesisSerializer(serializers.ModelSerializer):
    students = ThesesPersonSerializer(
        queryset=Student.objects.select_related('user'), many=True, required=False
    )
    modified = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z", required=False)
    # The two enum fields have to be explicitly defined, or otherwise DRF will
    # try to serialize enum values (since the model field is an EnumIntegerField)
    # and fail, because there is not builtin serialization for choicesenum Enums
    status = serializers.ChoiceField(choices=[(c.value, c.display) for c in ThesisStatus])
    kind = serializers.ChoiceField(choices=[(c.value, c.display) for c in ThesisKind])

    def get_students(self, instance: Thesis):
        """DRF will, by default, order this according to the ordering of the Student table;
        we want to order by ID as defined in the through relation table
        see: https://stackoverflow.com/q/48247490
        """
        return ThesesPersonSerializer(instance.get_students(), many=True).data

    def to_internal_value(self, data):
        result = super().to_internal_value(data)
        if 'votes' in data:
            result['votes'] = convert_votes(data['votes'], self.instance)
        if 'reason' in data:
            result['reason'] = data['reason']
        return result

    def to_representation(self, instance: Thesis):
        result = super().to_representation(instance)
        is_rejected = ThesisStatus(instance.status) == ThesisStatus.RETURNED_FOR_CORRECTIONS
        is_staff = self.context["is_staff"]
        is_employee = self.context["is_employee"]
        if (
            is_rejected and
            can_see_thesis_rejection_reason(instance, is_staff, is_employee, self.context["user"])
        ):
            result["reason"] = instance.rejection_reason
        if can_see_thesis_votes(is_staff):
            result["votes"] = serialize_thesis_votes(instance)
        return result

    # We need to define this field here manually to disable DRF's unique validator which
    # isn't flexible enough to override the error code it returns (throws a 400, we want 409)
    # See https://stackoverflow.com/q/33475334
    # and https://github.com/encode/django-rest-framework/issues/6124
    # Instead of using DRF's validation we override field-level validation below
    # and manually check for uniqueness
    title = serializers.CharField(max_length=MAX_THESIS_TITLE_LEN)

    def validate_title(self, new_title: str):
        validate_new_title_for_instance(new_title, self.instance)
        return new_title

    def validate_students(self, students: List[Student]):
        if len(students) > MAX_STUDENTS_PER_THESIS:
            raise serializers.ValidationError(
                {'students': [f'no more than {MAX_STUDENTS_PER_THESIS} students allowed per thesis']}
            )
        return students

    def create(self, validated_data: GenericDict):
        """If the checks above succeed, DRF will call this method
        in response to a POST request with the dictionary we returned
        from validate_add_thesis
        """
        # First check that the user is permitted to set these values
        user = self.context["request"].user
        if "advisor" in validated_data:
            check_advisor_permissions(user, validated_data["advisor"])
        status = validated_data["status"]
        if not can_set_status_for_new(user, ThesisStatus(status)):
            raise exceptions.PermissionDenied(f'This type of user cannot set status to {status}')
        if "votes" in validated_data:
            check_votes_permissions(user, validated_data["votes"], None)
        status = validated_data.get("status")

        new_instance = Thesis.objects.create(
            title=validated_data.get("title"),
            kind=validated_data.get("kind"),
            status=status,
            reserved_until=validated_data.get("reserved_until"),
            description=validated_data.get("description", ""),
            advisor=validated_data.get("advisor"),
            supporting_advisor=validated_data.get("supporting_advisor"),
            rejection_reason=validated_data.get("reason")
            if status == ThesisStatus.RETURNED_FOR_CORRECTIONS else "",
        )
        new_instance.set_students(validated_data.get("students", []))
        if "votes" in validated_data:
            new_instance.process_new_votes(validated_data["votes"], user, True)
        return new_instance

    def update(self, instance: Thesis, validated_data: GenericDict):
        """Called in response to a successfully validated PATCH request"""
        user = self.context["request"].user
        if "advisor" in validated_data:
            check_advisor_permissions(user, validated_data["advisor"])
        if "status" in validated_data and not can_change_status_to(
            user, self.instance, ThesisStatus(validated_data["status"])
        ):
            raise exceptions.PermissionDenied(
                f'This type of user cannot set status to {validated_data["status"]}'
            )
        if "title" in validated_data and not can_change_title(user, self.instance):
            raise exceptions.PermissionDenied("This type of user cannot change the title")
        if "votes" in validated_data:
            check_votes_permissions(user, validated_data["votes"], instance)

        old_title = instance.title
        instance.title = validated_data.get("title", instance.title)
        instance.kind = validated_data.get("kind", instance.kind)
        instance.reserved_until = validated_data.get("reserved_until", instance.reserved_until)
        instance.description = validated_data.get("description", instance.description)
        instance.status = validated_data.get("status", instance.status)
        instance.advisor = validated_data.get("advisor", instance.advisor)
        instance.supporting_advisor = validated_data.get(
            "supporting_advisor", instance.supporting_advisor
        )
        if "students" in validated_data:
            instance.set_students(validated_data.get("students"))
        if instance.status == ThesisStatus.RETURNED_FOR_CORRECTIONS:
            instance.rejection_reason = validated_data.get("reason", instance.rejection_reason)
        instance.save()
        if "votes" in validated_data:
            instance.process_new_votes(
                validated_data["votes"], user, "status" not in validated_data
            )
        if instance.title != old_title:
            instance.on_title_changed_by(user)
        return instance

    class Meta:
        model = Thesis
        read_only_fields = ("id",)
        fields = (
            "id", "title", "advisor", "supporting_advisor",
            "kind", "reserved_until", "description", "status",
            "students", "modified",
        )
        extra_kwargs = {
            "reserved_until": {
                "required": False,
                "allow_null": True
            },
            "advisor": {
                "required": False,
                "allow_null": True
            },
            "supporting_advisor": {
                "required": False,
                "allow_null": True
            }
        }


class CurrentUserSerializer(serializers.ModelSerializer):
    """Serialize the currently logged in user; this is a separate serializer
    (i.e. we don't just use ThesesPersonSerializer) because it also needs to send the type
    """
    def to_representation(self, instance: User):
        return {
            # The ThesesPersonSerializer needs to work with BaseUser instances,
            # because it's used for serializing thesis person
            "person": ThesesPersonSerializer(CurrentUserSerializer._to_base_person(instance)).data,
            "type": CurrentUserSerializer._serialize_user_type(instance).value,
        }

    @staticmethod
    def _serialize_user_type(user: User):
        if is_theses_admin(user):
            return ThesisUserType.ADMIN
        elif is_theses_regular_employee(user):
            return ThesisUserType.REGULAR_EMPLOYEE
        elif BaseUser.is_student(user):
            return ThesisUserType.STUDENT
        # We're generally not expecting this to happen
        return ThesisUserType.NONE

    @staticmethod
    def _to_base_person(user: User):
        if BaseUser.is_employee(user):
            return user.employee
        elif BaseUser.is_student(user):
            return user.student
        raise exceptions.NotFound()


class ThesesBoardMemberSerializer(serializers.ModelSerializer):
    def to_representation(self, instance: Employee):
        return instance.pk
