import * as React from "react";
import styled from "styled-components";

const MessageContainer = styled.div`
	position: relative;
	top: 50%;
	transform: translateY(-50%);
	width: 100%;
	text-align: center;
	font-size: 18px;
`;

/**
 * A component to indicate that there are no results in the theses table
 */
export function NoResultsMessage() {
	return <MessageContainer>Brak wyników</MessageContainer>;
}
