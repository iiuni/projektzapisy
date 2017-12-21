from apps.offer.vote.models import SingleVote,SystemState

def run():
	votes = SingleVote.objects.filter(state=SystemState.objects.get(year=2017), correction__gte=1)
	dd = {}
	for v in votes:
		if v.entity not in dd:
			dd[v.entity]=[v.student.matricula]
		else:
			dd[v.entity].append(v.student.matricula)

	for entity in dd:
		print(('['+entity.name_pl.encode('utf-8')+']'))
		for matricula in dd[entity]:
			print(matricula)
		print('')