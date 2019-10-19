# projektzapisy Changelog

# Version 3.6.19

* Link to issue tracker replaced with Github (#680)
* Small interface changes
* Re-write of offer/vote application (#678)
* Re-write of offer/preferences application (#686)

# Version 29.4.19

* New model for course Proposal and base model for Course info (#669)

# Version 25.4.19

* CSS library updated to Bootstrap 4 across entire system (#603)
* CAS server redirection back to the system after log-out (#655)
* Attaching security-related (mainly XSS) headers (#552)
* Upgrade of some Python dependencies, including Django (to v2.1) (#666)

# Version 12.2.19

* New opening times computation (#500).
* New ECTS course values computation (#501).
* New enrollment/queues logic (#502).
* New timetable and prototype (#503).

# Version 31.1.19

* REST API for students votes in offer is introduced to make exporting votes to scheduler easier.
* Bug in key-generation is fixed, that was probably introduced by upgrading Django to 2.0.

# Version 5.12.18

* Ubuntu upgraded to 18.04.
* Major changes in users app. We have groups now. UserProfile and ExtendedUser are gone (#444).
* Webpack/Yarn is used for compiling and bundling assets (JS/TS/CSS).
* Django is updated to version 2.0.

# Version 10.06.18

* added consent for students
* small improvement in desideratas
* special reservations api

# Version 18.05.18

* implemented new backups
* moved rest api to seperate app
* added limit on the number of rest calls made by unauthenticated users (100/day)

# Version 18.04.16

* Upgrade to python3
* Added simple semester REST API serving semesters
* Classroom REST API serving classroom data
* Fixed negative counts in grade summary
* Added confirmation pop-up before direct disenrollment

* Removed redundant informations about isim students
* Removed anything related to program "studia zamawiane"
* Removed UserProfile and ExtendedUser
* Changed authentication backend to django's default

# Version 18.02.25

* Added webpack
* Fixed reports generation
* Changed email signature for news

# Version 18.02.02

* Upgrade to Django 1.11
* Fix email sending

# Version 18.01.24

* Fix changing email
* added news author in emails
* Fixed events' start time in iCalc
* Fixed remove student from queue when enrolling to lecture
* Fixed issue with contextprocessors
* Fixed editing course in offer

# Version 18.01.05

* Upgrade to Django 1.10
* Fix for pulling student from queue

# Version 17.12.16

* Improved desideratas form
* Upgrade to Django 1.9

# Version 17.12.11

* Show desiderates in offer menu
* Upgraded the google analytics library

# Version 17.11.28

* Fixed users schedules
* Fixed course proposal form
* Fixed removing student from group in admin
* Removed paranoid sessions
* Fixed ignoring conflicts on reservation edition
* Cleaned main repository directory

# Version 17.11.21

* Upgrade to Django 1.8
* Loading courses with ajax
* Fixed disappearing pop-up
* Fixed issues with reservations and conflicts
* Hid vote summary from non-users

# Version 17.10.25

* Fixed missing title for login page
* Hid vote button for employees
* Added notification when leaving voting page
* Fixed several typos
* Fixed 'None' in news search field
* Improved login UX
* Added displaying links to courses on employee's page
* Added showing records ending time
* Added USOS CAS authentication

# Version 17.06.19

* Upgrade to Django 1.7
* Added maintenance mode switcher
* Fixed course names in vote results
* Enhanced filtering for offer

# Version 17.06.13

* Added possibility to remove reservations
* Added link to tracker to 500 error page

# Version 17.06.07

* Fixed error with not visible plans and not working prototype when new hidden future semester is added
* Fixed 500 error on vote summary
* Fixed password reset functionality after upgrade to Django 1.6. The issue was with wrong url names

# Version 17.06.06

* Added tag/effects filtering
* Bug-fixes after Django 1.6

# Version 17.05.29

* Upgrade to Django 1.6

# Version 17.05.05

* Improved syllabus form

# Version 17.04.20

* Upgrade to Django 1.5

# Version 17.04.20

* Fixed bug with sending emails with "ó"
* Added possibility to edit syllabus
* Added conflict list for secretary

# Version 17.04.07

* Fixed mail-to links escape '+'
* Fixed proper author while creating cyclical reservation
* Added possibility to add reservations with conflicts for secretary
* Fixed FreeDay and ChangedDay are now unique
* Added news content is now included in emails

# Version 17.03.09

* Added new date for records: end of unenrolling

# Version 17.02.26

* Added rooms reports
* Fixed polish fonts in pdfs
* Fixed export to ical
* Fixed display enrollment number (with isim students)

# Version 17.02.13

* Cyclic reservations can now be added with conflicts
* Fixed tight time bounds for reservations

# Version 17.01.31

* Fixed cyclical reservation starts no earlier than semester beginning
* Fixed open only SMTP one connection while sending emails

# Version 17.01.25

* Updated max points for vote information
* Disabled voting for crossed out students
* Adding new event doesn't require description and event is visible for all users by default
* Added python-rq
* Added some schedule/enrollment/vote tests

# Version 16.12.19

* Added cookie law info
* Added tracker for bugs at tracker-zapisy.ii.uni.wroc.pl
* Changed email from zapisy@ii.uni.wroc.pl to zapisy@cs.uni.wroc.pl
* Added feature to email all students
* Fix for bug with unrolling from last lecture

# Version 16.12.03

* Courses in review are no longer visible at all
* Courses not in offer are no longer visible for not authenticated users
* Courses descriptions are now sorted by time of creation
* Fixed proper Freedays and ChangedDays validation while making reservation

# Version 16.11.18

* Reworked sending emails to group and queues
* Voting link is now not visible when voting is closed + added tests

# Version 16.11.04

* Fixed an issue with dev env
* Added working tests to CI
* Fixed decision form for good
* Fixed displayed name of limit_isim field in Group model
* Fixed an issue with unicode method of Event model
* Fixed an issue with invalid user profiles
* Fixed an issue with queues not updating when changing limits of a group
* Lecturers can now add exams

# Version 16.9.23

* Temporary fix for decision form

# Version 16.9.20

* Created unified dev environment with Vagrant
* Fixed template for enabling grade
* Fixed an issue with queue rearrangements
* Added csv/pdf export links for queues
* Reviewed, fixed and merged `Courses Proposals` (Filip's thesis?)
* Button for refreshing opening times
* Fixed way of displaying courses on the calendar page
* Fixed a css issue in prototype
* Fixed rare issue that prevented viewing poll results
* Added link to offer management + fixed related permissions
* Fixed cyclical reservations
* Fixed email notifications

# Version 16.2.10

* First version recovered from BitBucket
