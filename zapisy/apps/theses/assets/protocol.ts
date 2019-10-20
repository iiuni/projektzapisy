/**
 * @file Defines misc types & constants used when interacting with the backend;
 * this should be kept synchronized with types defined there
 */

export const MIN_REJECTION_REASON_LENGTH = 100;
export const MAX_REJECTION_REASON_LENGTH = 500;

export const enum ThesisKind {
	Masters = 0,
	Engineers = 1,
	Bachelors = 2,
	Isim = 3,
	BachelorsEngineers = 4,
	BachelorsEngineersIsim = 5,
}

/**
 * Stringify a thesis kind
 * @param kind The kind to stringify
 */
export function thesisKindToString(kind: ThesisKind): string {
	switch (kind) {
		case ThesisKind.Masters: return "mgr";
		case ThesisKind.Engineers: return "inż";
		case ThesisKind.Bachelors: return "lic";
		case ThesisKind.Isim: return "ISIM";
		case ThesisKind.BachelorsEngineers: return "lic+inż";
		case ThesisKind.BachelorsEngineersIsim: return "lic+inż+ISIM";
	}
}

export const enum ThesisStatus {
	BeingEvaluated = 1,
	ReturnedForCorrections = 2,
	Accepted = 3,
	InProgress = 4,
	Defended = 5,
}

/**
 * Stringify a thesis status
 * @param status The status to stringify
 */
export function thesisStatusToString(status: ThesisStatus) {
	switch (status) {
		case ThesisStatus.Accepted: return "Zaakceptowana";
		case ThesisStatus.BeingEvaluated: return "Weryfikowana przez komisję";
		case ThesisStatus.Defended: return "Obroniona";
		case ThesisStatus.InProgress: return "W realizacji";
		case ThesisStatus.ReturnedForCorrections: return "Zwrócona do poprawek";
	}
}

export const enum ThesisVote {
	None = 1,
	Rejected = 2,
	Accepted = 3,
}

/**
 * Defines the type of user using the thesis system
 */
export const enum UserType {
	Student,
	Employee,
	Admin,
}

/** Defines the filter values sent to the backend when retrieving theses */
export const enum ThesisTypeFilter {
	Everything,
	Current,
	Archived,
	Masters,
	Engineers,
	Bachelors,
	BachelorsOrEngineers,
	ISIM,
	AvailableMasters,
	AvailableEngineers,
	AvailableBachelors,
	AvailableBachelorsOrEngineers,
	AvailableISIM,
	Ungraded,	// board members only

	Default = Current,
}

/**
 * Stringify a thesis type filter
 * @param type The type filter to stringify
 */
export function thesisTypeFilterToString(type: ThesisTypeFilter) {
	switch (type) {
		case ThesisTypeFilter.Everything: return "Wszystkie";
		case ThesisTypeFilter.Current: return "Wszystkie aktualne";
		case ThesisTypeFilter.Archived: return "Wszystkie archiwalne";
		case ThesisTypeFilter.Masters: return "Magisterskie";
		case ThesisTypeFilter.Engineers: return "Inżynierskie";
		case ThesisTypeFilter.Bachelors: return "Licencjackie";
		case ThesisTypeFilter.BachelorsOrEngineers: return "Licencjackie lub inżynierskie";
		case ThesisTypeFilter.ISIM: return "ISIM";
		case ThesisTypeFilter.AvailableMasters: return "Magisterskie – dostępne";
		case ThesisTypeFilter.AvailableEngineers: return "Inżynierskie – dostępne";
		case ThesisTypeFilter.AvailableBachelors: return "Licencjackie – dostępne";
		case ThesisTypeFilter.AvailableBachelorsOrEngineers: return "Licencjackie lub inżynierskie – dostępne";
		case ThesisTypeFilter.AvailableISIM: return "ISIM – dostępne";
		case ThesisTypeFilter.Ungraded: return "Wszystkie nieocenione";
	}
}

export type ProtocolVote = { value: ThesisVote; reason?: string };
export type VoteMap = { [_: number]: ProtocolVote };

export const MAX_STUDENTS_PER_THESIS = 2;
