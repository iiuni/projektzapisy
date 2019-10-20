import * as React from "react";

type Props = {
	text: string;
	style?: React.CSSProperties;
	className?: string;
};

/**
 * A simple wrapper around the HTML <input> element, set to readonly
 * Used in the thesis details component if the user does not have edit rights
 */
export const ReadOnlyInput = React.memo(function(props: Props) {
	return <input
		type={"text"}
		readOnly
		value={props.text}
		style={props.style || {}}
		className={props.className}
	/>;
});
