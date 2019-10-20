import * as React from "react";
import { confirmAlert } from "react-confirm-alert";

import { TextDialogUI } from "./TextDialog";

const REASON_INPUT_HEIGHT = 300;

export type MasterRejectionDialogProps = {
	message: string;
	cancelText: string;
	acceptText: string;
	initialReason: string;
};

export function showMasterRejectionDialog(props: MasterRejectionDialogProps): Promise<string> {
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
				/>
			)
		});
	});
}
