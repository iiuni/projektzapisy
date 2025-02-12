from django.utils.deprecation import MiddlewareMixin

# list of database keys which are user preferences
PREFERENCE_KEYS = ["last_searched_params"]

# Extra session key so that we dont attempt to load database
# preferences each time page is reloaded
ALREADY_LOADED_KEY = "preferences_loaded"


# returns database model or None if user is not Student/Employee
def get_user_db_object(user):
    if user.is_authenticated:
        if hasattr(user, "student"):
            return user.student
        elif hasattr(user, "employee"):
            return user.employee
    return None


# loads user preferences from database either when page loads
# for the first time with logged user or when user logs in later
def load_user_preferences_from_database(request):
    user_object = get_user_db_object(request.user)
    if user_object is None:
        request.session[ALREADY_LOADED_KEY] = True
        return

    # Set non-default user preferences in the session
    for key in PREFERENCE_KEYS:
        if key not in request.session:
            if hasattr(user_object, key):
                request.session[key] = getattr(user_object, key)
    request.session[ALREADY_LOADED_KEY] = True


# when user closes website we save his preferences
# from sessionStorage to database if he was logged
def save_user_preferences_to_database(request):
    user_object = get_user_db_object(request.user)
    if user_object is None:
        return

    # Save non-default user preferences to database
    for key in PREFERENCE_KEYS:
        if key in request.session:
            if hasattr(user_object, key):
                setattr(user_object, key, request.session[key])
    user_object.save()


# TODO: this feature is now disabled in zapisy/zapisy/settings.py
# MIDDLEWARE variable because of migration problems

# once per session, when website is loaded for the first time,
# we should load user preferences from database to session storage
class InitUserPreferences(MiddlewareMixin):
    def process_request(self, request):
        # Save up time by not checking user preferences each time page is reloaded
        if request.session.get(ALREADY_LOADED_KEY, False):
            return
        load_user_preferences_from_database(request)
