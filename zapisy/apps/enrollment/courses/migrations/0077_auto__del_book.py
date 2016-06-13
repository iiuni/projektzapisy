# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Book'
        db.delete_table('courses_book')


    def backwards(self, orm):
        # Adding model 'Book'
        db.create_table('courses_book', (
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(related_name='books', to=orm['courses.Course'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('courses', ['Book'])


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'courses.changedday': {
            'Meta': {'object_name': 'ChangedDay'},
            'day': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'weekday': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'courses.classroom': {
            'Meta': {'ordering': "['order', 'floor', 'number']", 'object_name': 'Classroom'},
            'building': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '75', 'blank': 'True'}),
            'can_reserve': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'capacity': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'floor': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': "('number',)", 'max_length': '50', 'populate_from': "'number'"}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'courses.course': {
            'Meta': {'ordering': "['entity__name']", 'object_name': 'Course'},
            'english': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.CourseEntity']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'information': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.CourseDescription']", 'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'records_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'records_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Semester']", 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True'}),
            'students_options': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['users.Student']", 'through': "orm['courses.StudentOptions']", 'symmetrical': 'False'}),
            'teachers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['users.Employee']", 'symmetrical': 'False', 'blank': 'True'}),
            'web_page': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'courses.coursedescription': {
            'Meta': {'object_name': 'CourseDescription'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Employee']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'description_pl': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.CourseEntity']"}),
            'exam': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'exercises': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'exercises_laboratories': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_ready': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'laboratories': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'lectures': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'repetitions': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'requirements': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'+'", 'blank': 'True', 'to': "orm['courses.CourseEntity']"}),
            'seminars': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'courses.courseentity': {
            'Meta': {'ordering': "['name']", 'object_name': 'CourseEntity'},
            'algorytmy_l': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'dyskretna_l': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ects': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'effects': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['courses.Effects']", 'null': 'True', 'blank': 'True'}),
            'english': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'exam': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'exercises': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'exercises_laboratiories': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_prefs': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'information': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.CourseDescription']", 'null': 'True', 'blank': 'True'}),
            'laboratories': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'lectures': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name_pl': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'numeryczna_l': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Employee']", 'null': 'True', 'blank': 'True'}),
            'programowanie_l': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'repetitions': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'semester': ('django.db.models.fields.CharField', [], {'default': "'u'", 'max_length': '1'}),
            'seminars': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'shortName': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'suggested_for_first_year': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['courses.Tag']", 'through': "orm['courses.TagCourseEntity']", 'symmetrical': 'False'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Type']", 'null': 'True'}),
            'ue': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'usos_kod': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'web_page': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'courses.effects': {
            'Meta': {'object_name': 'Effects'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'group_name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'courses.freeday': {
            'Meta': {'object_name': 'Freeday'},
            'day': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'courses.group': {
            'Meta': {'object_name': 'Group'},
            'cache_enrolled': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cache_enrolled_zam': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cache_queued': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'groups'", 'to': "orm['courses.Course']"}),
            'enrolled': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'enrolled_isim': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'enrolled_zam': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'enrolled_zam2012': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'export_usos': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'extra': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'limit_isim': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'limit_zamawiane': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'limit_zamawiane2012': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'queued': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Employee']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'usos_nr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'courses.pointsofcourseentities': {
            'Meta': {'unique_together': "(('entity', 'type_of_point', 'program'),)", 'object_name': 'PointsOfCourseEntities'},
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.CourseEntity']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'program': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['users.Program']", 'null': 'True', 'blank': 'True'}),
            'type_of_point': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.PointTypes']"}),
            'value': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '6'})
        },
        'courses.pointtypes': {
            'Meta': {'object_name': 'PointTypes'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30'})
        },
        'courses.semester': {
            'Meta': {'ordering': "['-year', 'type']", 'unique_together': "(('type', 'year'),)", 'object_name': 'Semester'},
            'desiderata_closing': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'desiderata_opening': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'first_grade_semester': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'fgrade'", 'null': 'True', 'to': "orm['courses.Semester']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_grade_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lectures_beginning': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'lectures_ending': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'records_closing': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'records_ects_limit_abolition': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'records_opening': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'second_grade_semester': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sgrade'", 'null': 'True', 'to': "orm['courses.Semester']"}),
            'semester_beginning': ('django.db.models.fields.DateField', [], {}),
            'semester_ending': ('django.db.models.fields.DateField', [], {}),
            't0_are_ready': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'year': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '7'})
        },
        'courses.studentoptions': {
            'Meta': {'unique_together': "(('course', 'student'),)", 'object_name': 'StudentOptions'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'records_opening_bonus_minutes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Student']"})
        },
        'courses.studentpointsview': {
            'Meta': {'object_name': 'StudentPointsView', 'managed': 'False'},
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.CourseEntity']"}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Student']", 'primary_key': 'True'}),
            'value': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        'courses.tag': {
            'Meta': {'object_name': 'Tag'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'courses.tagcourseentity': {
            'Meta': {'object_name': 'TagCourseEntity'},
            'courseentity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.CourseEntity']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Tag']"}),
            'weight': ('django.db.models.fields.IntegerField', [], {})
        },
        'courses.term': {
            'Meta': {'ordering': "['dayOfWeek']", 'object_name': 'Term'},
            'classroom': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Classroom']", 'null': 'True', 'blank': 'True'}),
            'classrooms': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'new_classrooms'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['courses.Classroom']"}),
            'dayOfWeek': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'end_time': ('django.db.models.fields.TimeField', [], {}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'term'", 'to': "orm['courses.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.TimeField', [], {})
        },
        'courses.type': {
            'Meta': {'object_name': 'Type'},
            'free_in_vote': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Type']", 'null': 'True', 'blank': 'True'}),
            'have_lab': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'have_lecture': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'have_project': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'have_review_lecture': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'have_seminar': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'have_tutorial': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'have_tutorial_lab': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meta_type': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30'}),
            'short_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '5'})
        },
        'users.employee': {
            'Meta': {'ordering': "['user__last_name', 'user__first_name']", 'object_name': 'Employee'},
            'consultations': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'homepage': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_news_view': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2016, 5, 28, 0, 0)'}),
            'receive_mass_mail_enrollment': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'receive_mass_mail_grade': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'receive_mass_mail_offer': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'room': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'employee'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'users.program': {
            'Meta': {'object_name': 'Program'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'type_of_points': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.PointTypes']"})
        },
        'users.student': {
            'Meta': {'ordering': "['user__last_name', 'user__first_name']", 'object_name': 'Student'},
            'algorytmy_l': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'block': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'dyskretna_l': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ects': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'ects_in_semester': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isim': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_news_view': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2016, 5, 28, 0, 0)'}),
            'matricula': ('django.db.models.fields.CharField', [], {'default': "''", 'unique': 'True', 'max_length': '20'}),
            'numeryczna_l': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'program': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['users.Program']", 'null': 'True'}),
            'programowanie_l': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'receive_mass_mail_enrollment': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'receive_mass_mail_grade': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'receive_mass_mail_offer': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'records_opening_bonus_minutes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'semestr': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            't0': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'student'", 'unique': 'True', 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['courses']