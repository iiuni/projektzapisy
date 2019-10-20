import * as React from "react";
import { Spinner } from "./Spinner";

/**
 * A component to indicate that the theses list is being downloaded
 */
export function LoadingIndicator() {
	return <div
		style={{
			width: "100%",
			textAlign: "center",
		}}
	>
		<Spinner/>;
	</div>;
}
