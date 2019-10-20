/**
 * @file An error notification box rendered when an error deemed to be fatal
 * occurs in the app. Note that this isn't the same as ErrorBoundary;
 * that can only catch escaped exceptions thrown in one of React lifecycle
 * functions, such as componentDidMount, render etc, whereas this component
 * is used deliberately and voluntarily by the ThesesApp component when
 * it detects an error.
 */
import * as React from "react";
import styled from "styled-components";

const ErrorTextContainer = styled.div`
	width: 100%;
	padding: 40px;
	text-align: center;
`;

type Props = {
	errorTitle: JSX.Element;
	errorDescription?: JSX.Element;
};

const DEFAULT_ERROR_DESCRIPTION = (
	"Przeładuj stronę i spróbuj jeszcze raz. " +
	"Jeżeli problem powtórzy się, opisz go na trackerze Zapisów."
);

export const ErrorBox = React.memo(function(props: Props) {
	return (
		<ErrorTextContainer>
			<h2>Wystąpił błąd</h2>
			<br />
			<h3>{props.errorTitle}</h3>
			<br />
			<p>{props.errorDescription || DEFAULT_ERROR_DESCRIPTION}</p>
		</ErrorTextContainer>
	);
});
