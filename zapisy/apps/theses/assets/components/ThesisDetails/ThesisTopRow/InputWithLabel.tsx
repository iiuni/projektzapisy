import * as React from "react";

export const enum InputType {
	Normal,
	ReadOnly,
	Disabled,
}

type Props = {
	labelText: string;
	inputText: string;
	inputWidth?: number;
	inputType: InputType,
};

/**
 * A simple component to render a text input with a label to the left,
 * used by more specific components
 */
export const InputWithLabel = React.memo(function(props: Props) {
	return <div>
		<span>{props.labelText}</span>
		<input
			type={"text"}
			value={props.inputText}
			style={{
				width: props.inputWidth != null ? props.inputWidth : "auto",
				paddingLeft: "2px",
				marginLeft: "5px",
			}}
			readOnly={props.inputType === InputType.ReadOnly}
			disabled={props.inputType === InputType.Disabled}
		/>
	</div>
});
