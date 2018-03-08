print("Studenci zapisani na wykład ale nie na ćwiczenia\n")
s = Semester.get_current_semester()
cs = s.get_courses()
ss = Student.get_active_students()
for c in cs:
	w = c.groups.filter(type=1)
	cw = c.groups.filter(type__in=[2,3,5])
	if (len(w) == 1) and (len(cw) > 0):
		rw = Record.get_students_in_group(w[0].id)
		rw = set(rw)
		rc = set()
		sum = 0
		for g in cw:
			rr = Record.get_students_in_group(g.id)
			rq = Queue.get_students_in_queue(g.id)
			rc = rc.union(rr)
			sum += len(rr)
		if not rw == rc:
			print(len(rw),len(rc),sum,c)
			studs_q = rw.difference(rc).intersection(rq)
			studs_not_q = rw.difference(rc).difference(studs_q)
			print("bez kolejki:")
			for s in studs_not_q:
				print(s.user.get_full_name() + ' <'+s.user.email+'>')
			print("w kolejce:")
			for s in studs_q:
				print(s.user.get_full_name() + ' <'+s.user.email+'>')
			print("#################################")