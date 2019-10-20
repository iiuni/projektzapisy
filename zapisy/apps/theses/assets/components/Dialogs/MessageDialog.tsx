import * as React from "react";
import { confirmAlert } from "react-confirm-alert";
import styled from "styled-components";
import * as Mousetrap from "mousetrap";
import { ButtonsContainer, DialogContainer, ConfirmButton } from "./Base";

export type MessageProps = {
	title?: string;
	message: string | JSX.Element;
	buttonText?: string;
};

type MessageDialogUIProps = MessageProps & {
	closeUI: () => void;
};

const OkButtonContainer = styled(ButtonsContainer)`
	width: 100%;
	text-align: center;
`;

class MessageDialogUI extends React.PureComponent<MessageDialogUIProps> {
	public componentDidMount() {
		Mousetrap.bindGlobal(["enter", "esc"], this.close);
	}
	public componentWillUnmount() {
		Mousetrap.unbindGlobal(["enter", "esc"]);
	}

	private close = () => {
		this.props.closeUI();
	}

	public render() {
		const { props } = this;
		return <DialogContainer>
			{props.title ? <h2>{props.title}</h2> : null}
			{props.message}
			<OkButtonContainer>
				<ConfirmButton type="button" className="btn" onClick={this.close}>
					{props.buttonText}
				</ConfirmButton>
			</OkButtonContainer>
		</DialogContainer>;
	}
}

export function showErrorMessage(props: MessageProps) {
	confirmAlert({
		message: "",
		title: "",
		customUI: ({ onClose }: any) => (
			<MessageDialogUI
				closeUI={onClose}
				title={props.title || "Błąd"}
				message={props.message}
				buttonText={props.buttonText || "OK"}
			/>
		)
	});
}
