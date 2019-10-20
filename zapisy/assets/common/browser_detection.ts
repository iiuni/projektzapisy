/**
 * @file Provides browser detection routines
 */
import * as Bowser from "bowser";

const browser = Bowser.getParser(window.navigator.userAgent);

/**
 * Determine whether the user's OS is Mac OS
 */
export function isMacOS() {
	return browser.getOSName() === "macOS";
}
