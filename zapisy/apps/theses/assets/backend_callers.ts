/**
 * @file Contains functions that permit interaction
 * with the backend - both pure getters and modifiers
 */
import { get as getCookie } from "js-cookie";
import * as objectAssignDeep from "object-assign-deep";
import axios, { AxiosRequestConfig, AxiosResponse } from "axios";
import { compact } from "lodash";

import { SortColumn, SortDirection, ThesesProcessParams } from "./app_types";
import { ThesisNameConflict } from "./errors";
import { AppUser, Student, Person, Employee } from "./users";
import { UserType } from "./protocol";
import {
	ThesisInJson, deserializeThesis,
	deserializeCurrentUser, deserializeEmployee, deserializeBoardMember,
} from "./deserialization";
import { Thesis } from "./thesis";
import { serializeThesisDiff, serializeNewThesis } from "./serialization";

const BASE_API_URL = "/theses/api";
const REST_REQUEST_TIMEOUT = 10000;

axios.defaults.timeout = REST_REQUEST_TIMEOUT;

export const FAKE_USER = new AppUser(new Student(-1, "Fake user"), UserType.Student);
const HTTP_STATUS_CONFLICT = 409;

/**
 * Send a request to the backend including the csrf token
 * supplied by Django's auth system; all nonpure requests
 * should go through this function because otherwise they will be rejected
 * as unauthorized
 * @param url The URL
 * @param config Optional Axios request config
 */
async function sendRequestWithCsrf(url: string, config?: AxiosRequestConfig) {
	const tokenValue = getCookie("csrftoken");
	if (!tokenValue) {
		throw new Error("CSRF token not found in cookies");
	}

	return axios.request(
		objectAssignDeep({}, config, {
			url,
			headers: { "X-CSRFToken": tokenValue }
		})
	);
}

/**
 * Perform a request, then return the body of the response
 * @param url The URL
 * @param config Optional Axios request config
 */
async function getData(url: string, config?: AxiosRequestConfig): Promise<any> {
	return (await axios.get(url, config)).data;
}

/** The results the backend returns to us in response to a list query */
type PaginatedThesesResult = {
	count: number;
	next: string;
	previous: string;
	results: ThesisInJson[];
};

/**
 * Convert from the local sort column representation to a string used in the query
 */
function sortColToBackendStr(col: SortColumn) {
	switch (col) {
		case SortColumn.Advisor: return "advisor";
		case SortColumn.Title: return "title";
		case SortColumn.None: return "";
	}
}

/**
 * Convert from the local sort dir representation to a string used in the query
 */
function sortDirToBackendStr(dir: SortDirection) {
	switch (dir) {
		case SortDirection.Asc: return "asc";
		case SortDirection.Desc: return "desc";
	}
}

/**
 * Fetch theses from the backend.
 * @param params The filtering and sorting params
 * @param offset The start row index
 * @param limit How many theses to fetch starting at `offset`
 * @param thesesBoard All current members of the theses board - needed for deserialization
 */
export async function getThesesList(
	params: ThesesProcessParams, offset: number, limit: number
) {
	const paginatedResults: PaginatedThesesResult = await getData(
		`${BASE_API_URL}/theses/`,
		{ params: {
			type: params.type,
			only_mine: params.onlyMine ? 1 : 0,
			title: params.title,
			advisor: params.advisor,
			column: sortColToBackendStr(params.sortColumn),
			dir: sortDirToBackendStr(params.sortDirection),
			offset, limit,
		}},
	);
	return {
		theses: paginatedResults.results.map(deserializeThesis),
		total: paginatedResults.count,
	};
}

/**
 * Get all the employees as an array
 */
export async function getEmployees(): Promise<Employee[]> {
	const emps = await getData(`${BASE_API_URL}/theses_employees/`);
	return emps.map(deserializeEmployee);
}

/**
 * Fetch the current system user from the backend
 */
export async function getCurrentUser(): Promise<AppUser> {
	return deserializeCurrentUser(await getData(`${BASE_API_URL}/current_user/`));
}

/** Find out if the current user has master rejecter rights */
export function getIsRejecter(): Promise<boolean> {
	return getData(`${BASE_API_URL}/is_master_rejecter/`);
}

/**
 * Get the theses board as an Employee list
 */
export async function getThesesBoard(): Promise<Employee[]> {
	const members = await getData(`${BASE_API_URL}/theses_board/`);
	return compact(members.map(deserializeBoardMember));
}

/**
 * Get the number of ungraded theses for the current board member
 */
export async function getNumUngraded() {
	return Number(await getData(`${BASE_API_URL}/num_ungraded/`));
}

export const enum PersonType {
	Employee,
	Student,
}

export type PersonAutcompleteResults = {
	results: Person[];
	hasMore: boolean;
};
type PersonAutocompleteJson = {
	next: string | null;
	results: Array<{
		id: number;
		name: string;
	}>;
};
/**
 * Use django-autocomplete-light's endpoint (also used by thesis forms in Django admin)
 * to fetch all matching students/employees
 * @param person The person type - determines which endpoint to use
 * @param substr The name filter - only persons matching this will be returned
 * @param pageNum Which page to return
 */
export async function getPersonAutocomplete(
	person: PersonType, substr: string, pageNum: number,
): Promise<PersonAutcompleteResults> {
	const personUrlPart = person === PersonType.Employee ? "employees" : "students";
	const url = `${BASE_API_URL}/theses_ac_${personUrlPart}/`;
	const acResults = await getData(url, { params: {
		page: pageNum,
		filter: substr,
	}}) as PersonAutocompleteJson;
	const constr = person === PersonType.Employee ? Employee : Student;
	return {
		results: acResults.results.map(
			raw => new constr(raw.id, raw.name)
		),
		hasMore: !!acResults.next,
	};
}

/**
 * Send a thesis operation (new/modify) and handle potential duplicate
 * title conflicts
 */
async function safeSendThesisRequest(url: string, config?: AxiosRequestConfig) {
	try {
		return await sendRequestWithCsrf(url, config);
	} catch (err) {
		if (err.response) {
			const response: AxiosResponse = err.response;
			if (response.status === HTTP_STATUS_CONFLICT) {
				throw new ThesisNameConflict();
			}
		}
		// Otherwise just pass the error we got
		throw err;
	}
}

/**
 * Given a previous and a modified thesis instance, compute the diff
 * and dispatch a request to the backend
 * @param originalThesis The old thesis object
 * @param modifiedThesis The new (modified) thesis object
 */
export async function saveModifiedThesis(
	originalThesis: Thesis, modifiedThesis: Thesis,
): Promise<void> {
	const objToSend = serializeThesisDiff(originalThesis, modifiedThesis);
	const jsonData = JSON.stringify(objToSend);
	await safeSendThesisRequest(
		`${BASE_API_URL}/theses/${objToSend.id}/`,
		{
			method: "PATCH",
			data: jsonData,
			headers: {
				"Content-Type": "application/json"
			},
		},
	);
}

/**
 * Given a thesis object, serialize it and dispatch a request
 * to add it to the backend
 * @param thesis The thesis object to add
 * @returns The ID of the newly added object
 */
export async function saveNewThesis(thesis: Thesis): Promise<number> {
	const objToSend = serializeNewThesis(thesis);
	const jsonData = JSON.stringify(objToSend);
	const res = await safeSendThesisRequest(
		`${BASE_API_URL}/theses/`,
		{
			method: "POST",
			data: jsonData,
			headers: {
				"Content-Type": "application/json"
			},
		},
	);
	return (res.data as ThesisInJson).id;
}

/**
 * Send a DELETE request to the backend for the specified thesis object
 */
export async function deleteThesis(thesis: Thesis): Promise<void> {
	await safeSendThesisRequest(
		`${BASE_API_URL}/theses/${thesis.id}/`,
		{
			method: "DELETE",
		},
	);
}
