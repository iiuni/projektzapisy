/**
 * @file Defines the Thesis class and associated types
 */
import * as moment from "moment";

import { Employee, Student, Person } from "./users";
import { ThesisKind, ThesisStatus, ThesisVote } from "./protocol";
import { ThesisVoteDetails, SingleVote } from "./votes";
import { Users } from "./app_logic/users";
import { nullableValuesEqual } from "./utils";

export const MAX_THESIS_TITLE_LEN = 300;
export const MAX_RESERVATION_YEARS = 10;

/**
 * Native representation of a thesis
 */
export class Thesis {
	public id: number;
	public title: string;
	public advisor: Employee | null;
	public supportingAdvisor: Employee | null;
	public kind: ThesisKind;
	public reservedUntil: moment.Moment | null;
	public description: string;
	public status: ThesisStatus;
	// while the server will never send us null entries in the array,
	// we may insert some when editing locally
	public students: Array<Student | null>;
	public modifiedDate: moment.Moment;
	public votes: ThesisVoteDetails;
	public rejectionReason: string;

	/** Construct a new thesis object with default values */
	public constructor() {
		this.id = -1;
		this.title = "";
		this.advisor = null;
		this.supportingAdvisor = null;
		this.kind = ThesisKind.Bachelors;
		this.reservedUntil = null;
		this.description = "";
		this.status = ThesisStatus.BeingEvaluated;
		this.students = [];
		this.modifiedDate = moment();
		const entries = Users.thesesBoard.map(e => [e.id, new SingleVote()]);
		this.votes = new ThesisVoteDetails(new Map(entries as Array<[number, SingleVote]>));
		this.rejectionReason = "";
	}

	public toString() {
		return this.title;
	}

	/**
	 * Determine whether this thesis is archived, i.e. has been defended
	 */
	public isArchived() {
		return this.status === ThesisStatus.Defended;
	}

	/**
	 * Is this the same thesis as the supplied one?
	 * @param other The other thesis
	 * Note that because this is a fat arrow it can be conveniently used
	 * as a callback, i.e. theses.find(t.isEqual)
	 */
	public isEqual = (other: Thesis): boolean => {
		return this.id === other.id;
	}

	/**
	 * Determine whether the other instance of the same thesis has been modified;
	 * to compare two possibly different thesis objects, see isEqual above
	 * @param other The other thesis
	 */
	public areValuesEqual(other: Thesis): boolean {
		console.assert(
			this.isEqual(other),
			"Thesis::areValuesEqual only makes sense for two theses with the same ID",
		);
		if (!(
			this.title === other.title &&
			this.description === other.description &&
			nullableValuesEqual(this.advisor, other.advisor, personCompare) &&
			nullableValuesEqual(this.supportingAdvisor, other.supportingAdvisor, personCompare) &&
			this.sameStudentsAs(other) &&
			this.kind === other.kind &&
			this.isReservationDateSame(other.reservedUntil) &&
			this.status === other.status &&
			this.modifiedDate.isSame(other.modifiedDate) &&
			this.getVoteDetails().isEqual(other.getVoteDetails()) &&
			this.rejectionReason === other.rejectionReason
		)) { return false; }
		return true;
	}

	public sameStudentsAs(other: Thesis) {
		const thisStudents = this.onlyDefinedStudents();
		const otherStudents = other.onlyDefinedStudents();
		return (
			thisStudents.length === otherStudents.length &&
			thisStudents.every(s => other.hasStudentAssigned(s))
		);
	}

	public hasStudentAssigned(student: Student): boolean {
		return !!this.students.find(s => !!s && s.isEqual(student));
	}

	public clearUndefinedStudents() {
		this.students = this.onlyDefinedStudents();
	}

	private onlyDefinedStudents(): Student[] {
		return this.students.filter(s => !!s) as Student[];
	}

	public isReservationDateSame(otherDate: moment.Moment | null) {
		return nullableValuesEqual(this.reservedUntil, otherDate, (d1, d2) => d1.isSame(d2));
	}

	public getMaxReservationDate() {
		return moment().add(MAX_RESERVATION_YEARS, "years");
	}

	public getVoteDetails() {
		return this.votes;
	}

	public getDefaultRejectionReason() {
		const voteDetails = this.getVoteDetails();
		const votes = Array.from(voteDetails.getAllVotes().values());
		const rejectionReasons = votes.filter(vote =>
			vote.value === ThesisVote.Rejected && vote.reason
		).map(vote => vote.reason);
		return rejectionReasons.join("\n\n");
	}

	public isUngraded(): boolean {
		if (!Users.isUserMemberOfBoard()) {
			return false;
		}
		const voteDetails = this.getVoteDetails();
		return voteDetails.getVoteForMember(
			Users.currentUser.person as Employee
		).value === ThesisVote.None;
	}
}

function personCompare(p1: Person, p2: Person) {
	return p1.isEqual(p2);
}
