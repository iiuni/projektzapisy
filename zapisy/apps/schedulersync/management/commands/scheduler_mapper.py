"""Maps teachers and courses in SchedulerData to objects in database.

Object SchedulerMapper maps SchedulerData.teachers and SchedulerData.courses,
which contain teachers and courses names, to objects in database.
Then replace corresponding teachers and courses in terms in SchedulerData
object. If course or teacher cannot be found and interactive flag is set,
then user will be asked for proper input.
Fills summary object given in constructor.

"""
from typing import Dict, Optional, Set

from apps.enrollment.courses.models import CourseInstance
from apps.offer.proposal.models import Proposal, ProposalStatus
from apps.schedulersync.models import CourseMap, EmployeeMap
from apps.users.models import Employee

from .scheduler_data import SchedulerData, SZTerm


class SchedulerMapper:
    def __init__(self, interactive_flag, summary, semester):
        self.interactive_flag = interactive_flag
        self.summary = summary
        self.semester = semester

    def _prompt(self, text):
        print()
        print(text)
        print("Type 'quit' to exit script. All changes will be commited (unless --dry_run was on).")
        print("Press Ctrl + C to exit script. All changes will be rolled back.")
        var = input("->: ")
        if var == 'quit':
            exit(0)
        return var

    def _map_teachers(self, teachers: 'Dict[str, str]') -> 'Dict[str, Employee]':
        """Maps teachers by scheduler username to Employees in database.

        If a teacher cannot be found, the user will be prompted for Employee's
        correct username in an interactive mode, or the teacher will be mapped
        to 'Nieznany Prowadzący'.
        """

        def get_employee(username: str, full_name: str, interactive: bool = True) -> Employee:
            """Finds matching employee in the database.

            If the employee with a given username is not found, in interactive
            mode it will ask the user to provide correct username and add it to
            the mapping.

            Args:
                username: The username coming from Scheduler API.
                full_name: The full name of the employee for convenience of the
                    interactive mode.
                interactive: A boolean flag enabling interactive mode.

            Returns:
                The matched Employee object or 'Nieznany Prowadzący' object
            """
            # First, use the mapping.
            try:
                return EmployeeMap.objects.get(scheduler_username=username).employee
            except EmployeeMap.DoesNotExist:
                pass

            # In interactive mode we will try to find the employee until we
            # succeed.
            sh_username = username
            while True:
                try:
                    emp = Employee.objects.get(user__username='Nn') if username == 'None' \
                        else Employee.objects.get(user__username=username)
                    if sh_username != username:
                        EmployeeMap.objects.create(scheduler_username=sh_username, employee=emp)
                        self.summary.maps_added.append((sh_username, str(emp)))
                        print(">Employee '{}' mapped to {}".format(sh_username, emp))
                    return emp
                except Employee.DoesNotExist:
                    pass
                if not interactive:
                    nieznany = Employee.objects.get(user__username='Nn')
                    self.summary.maps_added.append((username, str(nieznany)))
                    return nieznany
                username = self._prompt("No employee found for username {}.\nPlease provide the correct "
                                        "username for {}.\nType 'None' if that teacher should be replaced with "
                                        "'Nieznany Prowadzący'.".format(username, full_name))

        for teacher in teachers:
            teachers[teacher] = get_employee(teacher, teachers[teacher], self.interactive_flag)
        return teachers

    def _map_courses(self, courses: 'Set(str)') -> 'Dict[str, CourseInstance]':
        """Maps courses by scheduler names to object in database.

        If corresponding proposal cannot be found, in interactive mode user will
        be asked for proper proposal name.
        """

        def get_proposal(course_name: str, interactive: bool = True) -> 'Optional[Proposal]':
            """Finds a proposal in offer with a given name.

            If the proposal is not found, in interactive mode this function will
            prompt the user for the correct proposal and add it to the mapping.

            Returns:
                Proposal if the match is found or None if the course should be ignored.
            """
            # First try the mapping.
            try:
                return CourseMap.objects.get(scheduler_course__iexact=course_name).proposal
            except CourseMap.DoesNotExist:
                pass
            # In interactive mode we will try to find proposal until we succeed.
            name = course_name
            while True:
                error = ""
                try:
                    try:
                        proposal = None if name == 'None' else Proposal.objects.filter(
                            status__in=[ProposalStatus.IN_OFFER, ProposalStatus.IN_VOTE]).get(id=int(name))
                    except ValueError:
                        proposal = Proposal.objects.filter(
                            status__in=[ProposalStatus.IN_OFFER, ProposalStatus.IN_VOTE]).get(name__iexact=name)
                    if name != course_name:
                        CourseMap.objects.create(scheduler_course=course_name.upper(), proposal=proposal)
                        self.summary.maps_added.append((course_name, str(proposal)))
                        print(">Proposal '{}' mapped to {}".format(course_name, proposal))
                    return proposal
                except Proposal.DoesNotExist:
                    error = "No proposal was found"
                    if not interactive:
                        CourseMap.objects.create(scheduler_course=course_name.upper(), proposal=None)
                        self.summary.maps_added.append((course_name, "None"))
                        return None
                except Proposal.MultipleObjectsReturned:
                    error = "Multiple proposal were found"
                    if not interactive:
                        self.summary.multiple_proposals.append(course_name)
                        return None
                name = self._prompt("{} for name {}.\nPlease provide correct name or id of "
                                    "the course proposal in the database.\n"
                                    "Type 'None' to mark the course to be ignored.".format(error, name))

        def get_course(proposal: 'Proposal') -> 'CourseInstance':
            """Return CourseInstance object from SZ database."""
            course = None
            try:
                course = CourseInstance.objects.get(semester=self.semester, offer=proposal)
                self.summary.used_courses += 1
            except CourseInstance.DoesNotExist:
                course = CourseInstance.create_proposal_instance(proposal, self.semester)
                self.summary.created_courses += 1
                print(f"+ Course instance '{proposal.name}' created")
            return course

        mapped_courses = {}
        for course in courses:
            proposal = get_proposal(course, self.interactive_flag)
            if proposal is None:
                mapped_courses[course] = None
            else:
                mapped_courses[course] = get_course(proposal)
        return mapped_courses

    def map_scheduler_data(self, scheduler_data: 'SchedulerData'):
        """Maps teachers and courses in given scheduler_data.

        In given scheduler_data map teachers and courses names to
        objects in database. First in scheduler_data.teachers and
        scheduler_data.courses, then replace in scheduler_data.terms.

        Args:
            Data from scheduler api, obtained by SchedulerData object.
        """
        scheduler_data.teachers = self._map_teachers(scheduler_data.teachers)
        scheduler_data.courses = self._map_courses(scheduler_data.courses)
        mapped_terms = []
        for term in scheduler_data.terms:
            course = scheduler_data.courses[term.course]
            teacher = scheduler_data.teachers[term.teacher]
            mapped_terms.append(SZTerm(term.scheduler_id, teacher, course, term.type, term.limit,
                                       term.dayOfWeek, term.start_time, term.end_time, term.classrooms))
        scheduler_data.terms = mapped_terms
