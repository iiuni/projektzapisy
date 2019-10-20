/**
 * @file Defines types we'll be sending to the backend and provides
 * functions to serialize local objects to those types
 */
import { ThesisKind, ThesisStatus, VoteMap, ThesisVote, ProtocolVote } from "./protocol";
import { Thesis, MAX_THESIS_TITLE_LEN } from "./thesis";
import { Person } from "./users";
import { Moment } from "moment";
import { canChangeThesisVote } from "./permissions";
import { SingleVote } from "./votes";

/**
 * The representation of a new thesis object sent to the backend
 */
type ThesisAddOutSerialized = {
	title?: string;
	advisor?: number | null;
	supporting_advisor?: number | null;
	kind?: ThesisKind;
	reserved_until?: string | null;
	description?: string;
	status?: ThesisStatus;
	students?: number[];
	votes?: VoteMap;
	reason?: string;
};

/**
 * The representation of a diff for an existing thesis object sent to the backend
 */
type ThesisModOutSerialized = {
	id: number;
} & ThesisAddOutSerialized;

/** Serializes a single thesis vote */
function serializeVote(vote: SingleVote): ProtocolVote {
	return vote.value === ThesisVote.Rejected
		? { value: vote.value, reason: vote.reason }
		: { value: vote.value };
}

/**
 * Given a new thesis object, convert it to a representation
 * consumed by the backend
 * @param thesis The thesis object to convert
 */
export function serializeNewThesis(thesis: Thesis): ThesisAddOutSerialized {
	const result: ThesisAddOutSerialized = {
		title: thesis.title,
		kind: thesis.kind,
		description: thesis.description,
		status: thesis.status,
		students: thesis.students.map(toPersonDispatch) as number[],
	};
	if (thesis.advisor) {
		result.advisor = toPersonDispatch(thesis.advisor);
	}
	if (thesis.supportingAdvisor) {
		result.supporting_advisor = toPersonDispatch(thesis.supportingAdvisor);
	}
	if (thesis.reservedUntil) {
		result.reserved_until = serializeReservationDate(thesis.reservedUntil);
	}
	if (thesis.status === ThesisStatus.ReturnedForCorrections) {
		result.reason = thesis.rejectionReason;
	}
	if (canChangeThesisVote(thesis)) {
		const details = thesis.getVoteDetails();
		const votes = details.getAllVotes();
		result.votes = {};
		for (const [voter, vote] of votes) {
			if (vote.value !== ThesisVote.None) {
				result.votes[voter.id] = serializeVote(vote);
			}
		}
	}
	return result;
}

/**
 * Given an old and new person value, determine whether it should be considered
 * to have "changed" - based on this we will include it in the info sent to the backend
 */
function hadPersonChange(old: Person | null, newp: Person | null) {
	return (
		old === null && newp !== null ||
		old !== null && newp === null ||
		old !== null && newp !== null && !old.isEqual(newp)
	);
}

/**
 * Given a person instance, convert it to the backend representation
 */
function toPersonDispatch(newPerson: Person | null): number | null {
	return newPerson ? newPerson.id : null;
}

/**
 * Given the previous and new thesis object, compute the diff to be
 * sent to the backend
 * @param orig The old thesis object
 * @param mod The new (modified) thesis object
 */
export function serializeThesisDiff(orig: Thesis, mod: Thesis): ThesisModOutSerialized {
	console.assert(orig.isEqual(mod));
	const result: ThesisModOutSerialized = { id: orig.id };
	if (orig.title !== mod.title) {
		result.title = mod.title.slice(0, MAX_THESIS_TITLE_LEN);
	}
	if (hadPersonChange(orig.advisor, mod.advisor)) {
		result.advisor = toPersonDispatch(mod.advisor);
	}
	if (hadPersonChange(orig.supportingAdvisor, mod.supportingAdvisor)) {
		result.supporting_advisor = toPersonDispatch(mod.supportingAdvisor);
	}
	if (!orig.sameStudentsAs(mod)) {
		result.students = mod.students.map(toPersonDispatch) as number[];
	}
	if (orig.kind !== mod.kind) {
		result.kind = mod.kind;
	}
	if (!orig.isReservationDateSame(mod.reservedUntil)) {
		result.reserved_until = mod.reservedUntil ? serializeReservationDate(mod.reservedUntil) : null;
	}
	if (orig.description !== mod.description) {
		result.description = mod.description;
	}
	if (orig.status !== mod.status) {
		result.status = mod.status;
	}
	if (mod.status === ThesisStatus.ReturnedForCorrections) {
		result.reason = mod.rejectionReason;
	}

	if (canChangeThesisVote(orig)) {
		const diff: { [_: number]: ProtocolVote } = {};
		const origVotes = orig.getVoteDetails(); const modVotes = mod.getVoteDetails();
		for (const [emp, vote] of modVotes.getAllVotes()) {
			if (!origVotes.getVoteForMember(emp).isEqual(vote)) {
				diff[emp.id] = serializeVote(vote);
			}
		}
		if (Object.keys(diff).length) {
			result.votes = diff;
		}
	}

	return result;
}

function serializeReservationDate(date: Moment) {
	return date.format("YYYY-MM-DD");
}
