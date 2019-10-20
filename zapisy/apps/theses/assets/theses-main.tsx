/**
 * @file The entry point to the theses React app.
 * The only purpose of this file is to bootstrap the app by rendering
 * the root component after the page loads, having first wrapped it in
 * an error boundary to catch any escaped errors and handle them in
 * a (mostly) graceful manner, and then the root react-alert component;
 * see https://github.com/schiehll/react-alert
 */

import * as React from "react";
import * as ReactDOM from "react-dom";
import { Provider as AlertProvider } from "react-alert";
import AlertTemplate from "react-alert-template-basic";
import { whenDomLoaded } from "common/utils";
import { ThesesApp } from "./components/ThesesApp";
import { ErrorBoundary } from "./components/ErrorBoundary";
import "./misc_style.less";
import { initializeLogic } from "./app_logic";

function main() {
	const initPromise = initializeLogic();
	whenDomLoaded(() => renderApp(initPromise));
}
main();

const alertOptions = {
	position: "bottom center",
	timeout: 5000,
	offset: "60px",
	transition: "scale"
} as any;	// TS's type inference with the constants above isn't very good

function renderApp(initPromise: PromiseLike<any>) {
	ReactDOM.render(
		<ErrorBoundary>
			<AlertProvider template={AlertTemplate} {...alertOptions}>
				<ThesesApp initPromise={initPromise}/>
			</AlertProvider>
		</ErrorBoundary>,
		document.getElementById("theses-react-root"),
	);
}
