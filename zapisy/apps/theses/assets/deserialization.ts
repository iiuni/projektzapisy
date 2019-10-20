import * as moment from "moment";

import { ThesisKind, ThesisStatus, UserType, VoteMap } from "./protocol";
import { Thesis } from "./thesis";
import { Employee, Student, AppUser } from "./users";
import { ThesisVoteDetails, SingleVote } from "./votes";
import { Users } from "./app_logic/users";

type PersonInJson = {
	id: number;
	name: string;
};
type StudentInJson = PersonInJson;
type EmployeeInJson = { username: string } & PersonInJson;

type ThesisVotesInJson = VoteMap;

/**
 * This is the format in which we receive theses from the backend
 */
export type ThesisInJson = {
	id: number;
	title: string;
	advisor?: number;
	supporting_advisor?: number;
	kind: ThesisKind;
	reserved_until: string | null;
	description: string;
	status: ThesisStatus;
	students?: PersonInJson[];
	modified_date: string;
	votes?: ThesisVotesInJson;
	reason?: string;
};

type CurrentUserInJson = {
	person: EmployeeInJson | StudentInJson;
	type: UserType;
};

export function deserializeEmployee(json: EmployeeInJson) {
	return new Employee(json.id, json.name, json.username);
}

export function deserializeStudent(json: StudentInJson) {
	return new Student(json.id, json.name);
}

export function deserializeThesis(json: ThesisInJson) {
	const result = new Thesis();
	result.id = json.id;
	result.title = json.title;
	result.advisor = json.advisor ? Users.getEmployeeById(json.advisor) : null;
	result.supportingAdvisor = json.supporting_advisor ? Users.getEmployeeById(json.supporting_advisor) : null;
	result.kind = json.kind;
	result.reservedUntil = json.reserved_until ? moment(json.reserved_until) : null;
	result.description = json.description;
	result.status = json.status;
	result.students = json.students ? json.students.map(deserializeStudent) : [];
	result.modifiedDate = moment(json.modified_date);
	if (json.votes) {
		result.votes = deserializeVotes(json.votes);
	}
	if (json.reason) {
		result.rejectionReason = json.reason;
	}
	return result;
}

function deserializeVotes(votes: ThesisVotesInJson) {
	const entries = Object
		.entries(votes)
		.map(([idStr, vote]) => (
			[Number(idStr), new SingleVote(vote.value, vote.reason)]
		)) as Array<[number, SingleVote]>;
	return new ThesisVoteDetails(new Map(entries));
}

export function deserializeCurrentUser(json: CurrentUserInJson) {
	const person = json.type === UserType.Student
		? deserializeStudent(json.person)
		: deserializeEmployee(json.person as EmployeeInJson);
	return new AppUser(person, json.type);
}

type BoardMemberIn = number;
export function deserializeBoardMember(member: BoardMemberIn) {
	const result = Users.getEmployeeById(member);
	if (!result) {
		console.error(`Board member with ID ${member} not found, skipping`);
		return null;
	}
	return result;
}
