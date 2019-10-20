/**
 * @file The "add new thesis" button component shown above the theses table
 * 	if the user has the necessary permissions
 */

import * as React from "react";
import StandardButton from "react-button-component";
import styled from "styled-components";

const Button = styled(StandardButton)`
	width: 100px;
	min-height: initial;
	height: 30px;
`;

type Props = {
	onClick: () => void;
	enabled: boolean;
};

export const AddNewButton = React.memo(function(props: Props) {
	return <Button
		onClick={props.onClick}
		disabled={!props.enabled}
	>Dodaj nową</Button>;
});
