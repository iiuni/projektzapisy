// Common utility functions shared between apps

import * as $ from "jquery";

function scrollUpToElementIfWindowBelow(selector: string) {
	const SCROL_TIME = 400;
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
		$("html, body")!.animate({ scrollTop: elemTop }, SCROL_TIME);
	}
}

export { scrollUpToElementIfWindowBelow };
