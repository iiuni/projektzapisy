import * as React from "react";
import styled from "styled-components";

export const enum IconType {
	Add,
	Remove,
}

type Props = {
	type: IconType,
	onClick: () => void;
};

const Icon = styled.i`
	vertical-align: top;
	margin-top: 10px;
	margin-left: 10px;
	cursor: pointer;
`;

/**
 * The icon rendered next to advisor/student fields; either + or -
 * depending on whether the secondary advisor/student is present
 */
export const AddRemoveIcon = React.memo(function(props: Props) {
	// You can't install onClick handlers on <i> elements
	return <span onClick={props.onClick}>
		<Icon
			className={`fa ${props.type === IconType.Add ? "fa-plus" : "fa-minus"}`}
			onClick={props.onClick}
			aria-hidden={true}
		/>
	</span>;
});
