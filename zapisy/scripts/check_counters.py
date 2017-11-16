
gg = Group.objects.filter(course__semester_id=337)
for g in gg:
	if len(Record.get_students_in_group(g)) != g.enrolled:
		print g.id

for g in gg:
	if len(Queue.get_students_in_queue(g)) != g.queued:
		print g.id, len(Queue.get_students_in_queue(g)), g.queued

