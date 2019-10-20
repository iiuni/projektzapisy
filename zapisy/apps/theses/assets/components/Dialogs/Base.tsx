/** @file Provides base components for dialogs. Used by specialized implementations */
import * as React from "react";
import styled from "styled-components";

import "./dialog_styles.less";

export const DialogContainer = styled.div`
	font-family: Arial, Helvetica, sans-serif;
	width: 400px;
	padding: 30px;
	text-align: left;
	background: #fff;
	border-radius: 10px;
	box-shadow: 0 20px 75px rgba(0, 0, 0, 0.13);
	color: #666;

	& > h2 {
		margin-top: -10px;
		margin-bottom: 15px;
	}
`;

export const BaseButton = styled.button`
	text-shadow: none;
	background-image: none;
`;

export const ConfirmButton = styled(BaseButton)`
	color: #fff;
	background-color: #337ab7;
	border-color: #2e6da4;
	font-size: 14px;
	min-width: 100px;
	&:hover {
		color: #fff;
		filter: brightness(1.1);
	}
`;

export const ButtonsContainer = styled.div`
	margin-top: 20px;
`;

const DangerButtonComponent = styled(BaseButton)`
	color: #fff;
	background-color: #d9534f;
	border-color: #d43f3a;
	margin-left: 10px;
	&:hover {
		color: #fff;
	}
	&:hover:not(:disabled) {
		filter: brightness(1.1);
	}
`;

const SafeButtonComponent = styled(BaseButton)`
	color: #6f6f6f;
	&:hover {
		color: #6f6f6f;
		filter: brightness(0.9);
	}
`;

type ButtonProps = {
	onClick: () => void;
	text: string;
	enabled?: boolean;
	title?: string;
};
function RenderButtonInternal(
	props: ButtonProps,
	Component: any,
) {
	const shouldDisable = props.enabled === false;
	return <Component
		type="button" className="btn"
		onClick={props.onClick}
		disabled={shouldDisable}
		title={props.title}
	>{props.text}</Component>;
}

/** Renders a button indicating a "dangerous", mutating action */
export const DangerButton = React.memo(function(props: ButtonProps) {
	return RenderButtonInternal(props, DangerButtonComponent);
});

/** Renders a button indicating a bailout from a dangerous action */
export const SafeButton = React.memo(function(props: ButtonProps) {
	return RenderButtonInternal(props, SafeButtonComponent);
});
