/**
 * @file Provides a base text input dialog
 */
import * as React from "react";
import styled from "styled-components";
import * as Mousetrap from "mousetrap";
import { ButtonsContainer, DialogContainer, SafeButton, DangerButton } from "./Base";

export type TextDialogProps = {
	message: string;
	cancelText: string;
	acceptText: string;
	initialText: string;
	/** Textarea height in px */
	textInputHeight: number;
	textInputMaxLength?: number;
	/** Render the left side of the help section for current input */
	renderLeftHelpContents?: (t: string) => JSX.Element;
	/** Determines whether the current text value is 'acceptable', i.e. whether
	 * the user should be permitted to hit 'accept' and close the dialog
	 */
	validateText?: (t: string) => boolean;
	/** If `validateText` returns false, this tooltip will be shown to explain
	 * why to the user
	 */
	badTextTooltip?: string;
};

type TextDialogUIProps = TextDialogProps & {
	closeUI: () => void;
	resolve: (res: string) => void;
	reject: () => void;
};

const TextField = styled.textarea`
	margin-top: 10px;
	margin-bottom: 3px;
	width: 100%;
	box-sizing: border-box;
`;

const HelpContainer = styled.div`
	width: 100%;
	font-size: 10.5px;
	display: flex;
	flex-direction: row;
	justify-content: space-between;
`;

type State = {
	currentText: string;
};

export class TextDialogUI extends React.PureComponent<TextDialogUIProps, State> {
	private reasonFieldRef: React.RefObject<HTMLTextAreaElement> = React.createRef();
	public constructor(props: TextDialogUIProps) {
		super(props);
		this.state = {
			currentText: props.initialText,
		};
	}

	public componentDidMount() {
		Mousetrap.bindGlobal("shift+enter", e => {
			this.onAccept();
			e.preventDefault();
		});
		Mousetrap.bindGlobal("esc", this.onCancel);
		const txtarea = this.reasonFieldRef.current;
		if (txtarea) {
			txtarea.focus();
		}
	}

	public componentWillUnmount() {
		Mousetrap.unbindGlobal(["enter", "esc"]);
	}

	private canAccept() {
		const { validateText } = this.props;
		return typeof validateText !== "function" || validateText(this.state.currentText);
	}

	private onAccept = () => {
		if (this.canAccept()) {
			this.props.closeUI();
			this.props.resolve(this.state.currentText);
		}
	}
	private onCancel = () => {
		this.props.closeUI();
		this.props.reject();
	}

	private onChange = (ev: React.ChangeEvent<HTMLTextAreaElement>) => {
		this.setState({ currentText: ev.target.value });
	}

	public render() {
		const { props } = this;
		const canAccept = this.canAccept();
		return <DialogContainer>
			{props.message}
			<TextField
				onChange={this.onChange}
				value={this.state.currentText}
				maxLength={props.textInputMaxLength}
				ref={this.reasonFieldRef}
				style={{ height: props.textInputHeight }}
			/>
			{this.renderHelp()}
			<ButtonsContainer>
				<SafeButton onClick={this.onCancel} text={props.cancelText} />
				<DangerButton
					onClick={this.onAccept}
					text={props.acceptText}
					enabled={canAccept}
					title={canAccept ? "" : props.badTextTooltip}
				/>
			</ButtonsContainer>
		</DialogContainer>;
	}

	private renderKeysHint() {
		return <span><pre>esc</pre> – anuluj, <pre>shift+enter</pre> – potwierdź</span>;
	}

	private renderHelp() {
		return <HelpContainer>
			{this.props.renderLeftHelpContents
				? this.props.renderLeftHelpContents(this.state.currentText)
				// if there's nothing, render an empty element to push the keys hint to the right
				: <span></span>
			}
			{this.renderKeysHint()}
		</HelpContainer>;
	}
}
