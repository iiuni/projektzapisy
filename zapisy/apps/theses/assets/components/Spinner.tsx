/**
 * @file A simple spinner component used as a base by other components
 */

import * as React from "react";
import styled from "styled-components";

type Props = {
	style?: React.CSSProperties;
};

const DivContainer = styled.div`
	width: 100px;
	height: 100px;
	z-index: 999;
`;

export const Spinner = React.memo(function(props: Props): JSX.Element {
	return <DivContainer className="spinner-border" style={props.style || {}} role="status">
		<span className="sr-only">Wczytywanie...</span>
	</DivContainer>;
});
