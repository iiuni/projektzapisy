import * as React from "react";
import { confirmAlert } from "react-confirm-alert";
import styled from "styled-components";

import { MIN_REJECTION_REASON_LENGTH, MAX_REJECTION_REASON_LENGTH } from "../../protocol";
import { TextDialogUI } from "./TextDialog";

const BAD_REASON_TOOLTIP = (
	`Wymagane jest między ${MIN_REJECTION_REASON_LENGTH} a ${MAX_REJECTION_REASON_LENGTH } znaków`
);
const REASON_INPUT_HEIGHT = 100;

export type RejectionDialogProps = {
	message: string;
	cancelText: string;
	acceptText: string;
	initialReason: string;
};

const ExceededMessage = styled.span`
	color: red;
	font-weight: bold;
`;

function validateReason(reason: string) {
	const len = reason.length;
	return len >= MIN_REJECTION_REASON_LENGTH && len <= MAX_REJECTION_REASON_LENGTH;
}

function renderCharCounts(reason: string) {
	if (reason.length < MIN_REJECTION_REASON_LENGTH) {
		const remaining = MIN_REJECTION_REASON_LENGTH - reason.length;
		return <span>Min. {MIN_REJECTION_REASON_LENGTH} znaków (jeszcze {remaining})</span>;
	}
	const remaining = MAX_REJECTION_REASON_LENGTH - reason.length;
	return <span>Maks. {MAX_REJECTION_REASON_LENGTH} znaków
		{remaining >= 0
		? <span> (pozostało {remaining})</span>
		: <ExceededMessage> (przekroczono o {-remaining})</ExceededMessage>}</span>;
}

export function showRejectionReasonDialog(props: RejectionDialogProps): Promise<string> {
	return new Promise((resolve, reject) => {
		confirmAlert({
			title: "",
			message: "",
			customUI: ({ onClose }: any) => (
				<TextDialogUI
					closeUI={onClose}
					resolve={resolve}
					reject={reject}
					message={props.message}
					cancelText={props.cancelText}
					acceptText={props.acceptText}
					initialText={props.initialReason}
					textInputHeight={REASON_INPUT_HEIGHT}
					textInputMaxLength={MAX_REJECTION_REASON_LENGTH}
					renderLeftHelpContents={renderCharCounts}
					validateText={validateReason}
					badTextTooltip={BAD_REASON_TOOLTIP}
				/>
			)
		});
	});
}
