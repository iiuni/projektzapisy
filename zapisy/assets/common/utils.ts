// Common utility functions shared between apps
import * as $ from "jquery";
import { UnconstrainedFunction } from "./types";

const SCROLL_TIME = 400;
export function scrollUpToElementIfWindowBelow(selector: string): void {
	const currentWindowTop = $(window).scrollTop();
	if (!currentWindowTop) {
		return;
	}
	const elem = $(selector);
	if (!elem) {
		throw new Error(`Unable to find ${selector}`);
	}
	const elemTop = elem.offset()!.top;
	if (currentWindowTop > elemTop) {
		$("html, body").animate({ scrollTop: elemTop }, SCROLL_TIME);
	}
}

export function whenDomLoaded(fn: UnconstrainedFunction): void {
	if (document.readyState !== "loading") {
		fn();
	} else {
		window.addEventListener("DOMContentLoaded", fn);
	}
}

/**
 * Returns a promise that resolves after the specified timeout
 * @param ms The timeout in milliseconds
 */
export function wait(ms: number): Promise<void> {
	return new Promise((resolve, _) => {
		window.setTimeout(resolve, ms);
	});
}

/**
 * Compare two strings with the same semantics as C's strcmp
 * @param a The first string
 * @param b The second string
 * @returns -1 if a < b, 0 if a == b, 1 if a > b
 */
export function strcmp(a: string, b: string) {
	return (a < b ? -1 : (a > b ? 1 : 0));
}

export function inRange<T>(value: T, min: T, max: T): boolean {
	return value >= min && value <= max;
}

/**
 * Round up the specified to the nearest multiple
 * @param numToRound The number to round up
 * @param multiple Round up to the nearest multiple of this
 */
export function roundUp(numToRound: number, multiple: number) {
	if (multiple === 0) {
		return numToRound;
	}
	const remainder = numToRound % multiple;
	if (remainder === 0) {
		return numToRound;
	}
	return numToRound + multiple - remainder;
}
