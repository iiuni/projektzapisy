import { observable, action, flow } from "mobx";
import { CancellablePromise } from "mobx/lib/api/flow";

import { roundUp, wait } from "common/utils";
import { getThesesList, getNumUngraded } from "../backend_callers";
import { Thesis } from "../thesis";
import { ThesesProcessParams, SortColumn, SortDirection, ApplicationState } from "../app_types";
import { ThesisTypeFilter } from "../protocol";
import { Users } from "./users";
import { AppMode } from "./app_mode";

// Much of the logic in this file relies on MobX flow functions
// see https://mobx.js.org/best/actions.html (the flow section at the bottom)

/** Which string filter is being changed? */
export type StringFilter = "advisor" | "title" | "";

/** How many theses to download in a single request */
const ROWS_PER_PAGE = 100;

/**
 * How long to wait after the last keystroke before dispatching
 * a request to the backend with the specified filter
 * This assumes the user will be typing at at least 240 CPM
 * which is slightly above average, but our target audience is rather
 * more computer literate than the average person, so that should be fine
 */
const STRING_FILTER_QUERY_DELAY = 250;

/** The mode in which we're loading theses:
 * should we append them at the end, or replace the entire list?
 */
export const enum LoadMode {
	Append,
	Replace,
}

class C {
	/** All the theses we currently know about (having downloaded them from the backend) */
	@observable public theses: Thesis[] = [];
	/** The total number of theses matching current filters (on the backend;
	 * including theses we haven't yet downloaded)
	 * Note that this will almost always be more than theses.length - theses
	 * only holds a subset of everything that's available, unless the user
	 * scrolls to the very end
	 */
	@observable public totalCount = 0;
	params: ThesesProcessParams = observable({
		type: ThesisTypeFilter.Default,
		onlyMine: false,
		title: "",
		advisor: "",
		sortColumn: SortColumn.None,
		sortDirection: SortDirection.Asc,
	});
	stringFilterBeingChanged: StringFilter = "";
	private lastRowIndex = 0;
	/** Represents the current asynchronous filter edition action */
	private stringFilterPromise: CancellablePromise<any> | null = null;

	public initialize = flow(function*(this: C) {
		if (yield this.getNumUngraded()) {
			this.params.type = ThesisTypeFilter.Ungraded;
		}
		if (Users.isUserEmployee() && !Users.isUserMemberOfBoard()) {
			// employees are most likely only interested in their own theses
			this.params.onlyMine = true;
		}
		yield this.loadNewTheses();
	});

	public shouldSelectUngradedThesis() {
		return this.params.type === ThesisTypeFilter.Ungraded && this.theses.length > 0;
	}

	/** Get the number of ungraded theses for the current user.
	 * Returns 0 if the user is not a member of the theses board.
	 */
	public async getNumUngraded() {
		return Users.isUserMemberOfBoard() ? getNumUngraded() : 0;
	}

	public indexOfThesis(thesis: Thesis) {
		return this.theses.findIndex(thesis.isEqual);
	}

	public getThesisById(id: number): Thesis | null {
		return this.theses.find(t => t.id === id) || null;
	}

	public findUngraded(): Thesis | null {
		return this.theses.find(t => t.isUngraded()) || null;
	}

	/** After saving we might want to switch away from the ungraded theses filter
	 * if it would make the list empty
	 */
	public adjustFiltersPostSave(numUngraded: number) {
		if (!numUngraded && this.params.type === ThesisTypeFilter.Ungraded) {
			// switch away to the default, this list would be empty
			this.params.type = ThesisTypeFilter.Default;
		}
	}

	@action
	public changeTypeFilter(value: ThesisTypeFilter) {
		if (!ensureCanPerformBackendOp()) {
			return Promise.resolve();
		}
		this.params.type = value;
		return this.reloadWithStateChange();
	}

	@action
	public changeOnlyMineFilter(value: boolean) {
		if (!ensureCanPerformBackendOp()) {
			return Promise.resolve();
		}
		this.params.onlyMine = value;
		return this.reloadWithStateChange();
	}

	/** Save the new filter value, wait for the user to maybe type more,
	 * after the set delay assume they won't and query the backend
	 */
	private changeStringFilterInternal = flow(function*(
		this: C, thisKey: "title" | "advisor", value: string
	) {
		this.params[thisKey] = value.toLowerCase();
		this.stringFilterBeingChanged = thisKey;
		AppMode.applicationState = ApplicationState.Refetching;
		yield wait(STRING_FILTER_QUERY_DELAY);
		yield this.loadNewTheses();
		AppMode.applicationState = ApplicationState.Normal;
		this.stringFilterBeingChanged = "";
		// we're done with this promise, the action completed
		this.stringFilterPromise = null;
	});

	@action
	private changeStringFilter(
		thisKey: "title" | "advisor", otherKey: "title" | "advisor",
		value: string
	) {
		if (this.stringFilterBeingChanged === otherKey) {
			console.assert(false, "Not allowed, changing other filter already");
			return Promise.resolve();
		}
		// If a string filter action is already going on, it should be
		// cancelled - we won't be interested in the old results anyway,
		// since the filter value changed
		if (this.stringFilterPromise) {
			console.assert(this.stringFilterBeingChanged === thisKey);
			this.stringFilterPromise.cancel();
		}
		const changePromise = this.changeStringFilterInternal(thisKey, value);
		const r = changePromise.catch(err => {
			// This is the error thrown in the promise when we call cancel()
			// so that's expected; anything else is a real error
			if (!err.toString().includes("FLOW_CANCELLED")) {
				throw err;
			}
		});
		this.stringFilterPromise = changePromise;
		return r;
	}

	public changeAdvisorFilter(value: string) {
		return this.changeStringFilter("advisor", "title", value);
	}

	public changeTitleFilter(value: string) {
		return this.changeStringFilter("title", "advisor", value);
	}

	@action
	public changeSort(column: SortColumn, dir: SortDirection) {
		if (!ensureCanPerformBackendOp()) {
			return Promise.resolve();
		}
		this.params.sortColumn = column;
		this.params.sortDirection = dir;
		return this.reloadWithStateChange();
	}

	/** Load more rows as demanded by the table component */
	public loadMore = flow(function* (this: C, upToRow: number) {
		// The table component might call this function many times in response
		// to the same scroll "session"
		if (AppMode.isPerformingBackendOp() || upToRow <= this.lastRowIndex) {
			return;
		}
		try {
			AppMode.applicationState = ApplicationState.LoadingMore;
			yield this.loadTheses(LoadMode.Append, roundUp(upToRow, ROWS_PER_PAGE));
		} finally {
			AppMode.applicationState = ApplicationState.Normal;
		}
	});

	/** Download rows in range 0 - ROWS_PER_PAGE, replacing the current set */
	private loadNewTheses() {
		return this.loadTheses(LoadMode.Replace, ROWS_PER_PAGE);
	}

	/**
	 * Same as `reloadTheses` but also changes the app state to Refetching
	 * Used by filter/sorting code as a shortcut
	 */
	private reloadWithStateChange = flow(function*(this: C) {
		AppMode.applicationState = ApplicationState.Refetching;
		yield this.reloadTheses();
		AppMode.applicationState = ApplicationState.Normal;
	});

	/**
	 * Reload the current theses list (up until the saved last row index)
	 */
	public reloadTheses() {
		return this.loadTheses(LoadMode.Replace, this.lastRowIndex);
	}

	/**
	 * Download theses from the backend
	 * @param mode The mode in which to perform the action - replace or append new rows
	 * @param untilRow Ensure that all rows up to this one are available
	 */
	private loadTheses = flow(function*(this: C, mode: LoadMode, untilRow: number) {
		if (mode === LoadMode.Append) {
			console.assert(untilRow > this.lastRowIndex, "Already loaded");
			const result = yield getThesesList(
				this.params, this.lastRowIndex, untilRow - this.lastRowIndex,
			);
			this.theses = this.theses.concat(result.theses);
			this.totalCount = result.total;
		} else {
			const result = yield getThesesList(this.params, 0, untilRow);
			this.theses = result.theses;
			this.totalCount = result.total;
		}
		this.lastRowIndex = untilRow;
	});
}

function ensureCanPerformBackendOp() {
	if (AppMode.isPerformingBackendOp()) {
		console.error("Not allowed to perform backend op");
		return false;
	}
	return true;
}

export const List = new C();
