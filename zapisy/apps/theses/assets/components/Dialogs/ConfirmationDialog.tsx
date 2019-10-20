import * as React from "react";
import { confirmAlert } from "react-confirm-alert";
import * as Mousetrap from "mousetrap";
import { DialogContainer, ButtonsContainer, SafeButton, DangerButton } from "./Base";

export type ConfirmationProps = {
	title?: string;
	message: string | JSX.Element;
	yesText: string;
	noText: string;
};

type ConfirmDialogUIProps = ConfirmationProps & {
	closeUI: () => void;
	resolve: (r: boolean) => void;
};

class ConfirmDialogUI extends React.PureComponent<ConfirmDialogUIProps> {
	public componentDidMount() {
		Mousetrap.bindGlobal("enter", this.onYes);
		Mousetrap.bindGlobal("esc", this.onNo);
	}

	public componentWillUnmount() {
		Mousetrap.unbindGlobal(["enter", "esc"]);
	}

	private finishWith(val: boolean) {
		this.props.resolve(val);
		this.props.closeUI();
	}

	private onNo = () => this.finishWith(false);
	private onYes = () => this.finishWith(true);

	public render() {
		const { props } = this;
		return <DialogContainer>
			{props.title ? <h2>{props.title}</h2> : null}
			{props.message}
			<ButtonsContainer>
				<SafeButton onClick={this.onNo} text={props.noText} />
				<DangerButton onClick={this.onYes} text={props.yesText} />
			</ButtonsContainer>
		</DialogContainer>;
	}
}

/**
 * Displays a confirmation dialog with the given parameters.
 * @returns A promise that resolves to the user's choice
 */
export function confirmationDialog(props: ConfirmationProps): Promise<boolean> {
	return new Promise((resolve) => {
		confirmAlert({
			title: "",
			message: "",
			customUI: ({ onClose }: any) => (
				<ConfirmDialogUI
					closeUI={onClose}
					resolve={resolve}
					{...props}
				/>
			)
		});
	});
}
