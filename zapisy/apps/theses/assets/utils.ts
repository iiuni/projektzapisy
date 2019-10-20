/**
 * @file Misc utils for the thesis system app.
 */

import * as React from "react";
import { Moment } from "moment";
import { isMacOS } from "common/browser_detection";

/**
 * Returns a style object to be applied to "disabled" components.
 * Certain components in the app can enter a "disabled" state;
 * they will then apply this CSS to visually indicate this to the user.
 */
export function getDisabledStyle(): React.CSSProperties {
	return { opacity: 0.5, pointerEvents: "none" };
}

/**
 * Updates the top-menu indicator (the Django template formats it properly,
 * but the theses app uses asynchronous requests to save votes, so it needs to
 * be done here as well
 */
export function adjustDomForUngraded(numUngraded: number): void {
	const elem = document.getElementById("num_ungraded_theses");
	if (!elem) {
		console.error("adjustDomForUngraded: element not found");
		return;
	}
	elem.textContent = numUngraded ? ` (${numUngraded})` : "";
}

/**
 * Format a given moment instance to a date string.
 */
export function formatDate(m: Moment): string {
	return m.format("DD.MM.YYYY");
}

export function formatDateTime(m: Moment): string {
	return m.format("DD.MM.YYYY HH:mm:ss");
}

/**
 * Determine whether two nullable values are equal
 * @param val1 The first value
 * @param val2 The second value
 * @param compare The comparator used when both values are nonnull
 */
export function nullableValuesEqual<T>(
	val1: T | null, val2: T | null, compare: (v1: T, v2: T) => boolean
): boolean {
	return (
		val1 === null && val2 === null ||
		val1 !== null && val2 !== null && compare(val1, val2)
	);
}

// Use Cmd instead of ctrl on MacOS for keyboard shortcuts
export function macosifyKeys(vals: string | string[]) {
	const fixSingle = isMacOS()
		? (key: string) => key.replace("ctrl", "command")
		: (key: string) => key;
	return Array.isArray(vals) ? vals.map(fixSingle) : fixSingle(vals);
}
