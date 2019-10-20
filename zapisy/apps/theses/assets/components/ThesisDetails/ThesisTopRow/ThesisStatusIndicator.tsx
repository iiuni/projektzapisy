import * as React from "react";
import { without } from "lodash";

import { GenericSelect } from "../../GenericSelect";
import { InputWithLabel, InputType } from "./InputWithLabel";
import { ThesisStatus, thesisStatusToString } from "../../../protocol";
import { Thesis } from "../../../thesis";
import { canChangeStatusTo } from "../../../permissions";

const LABEL_TEXT = "Status";
const ALL_STATUSES = [
	ThesisStatus.BeingEvaluated,
	ThesisStatus.Accepted,
	ThesisStatus.InProgress,
	ThesisStatus.Defended,
	ThesisStatus.ReturnedForCorrections,
];

const statusSelectInfos = ALL_STATUSES.map(
	kind => ({ val: kind, displayName: thesisStatusToString(kind) })
);

type Props = {
	thesis: Thesis;
	original: Thesis;
	onChange: (val: ThesisStatus) => void;
	enabled: boolean;
};

const STATUS_FIELD_WIDTH = 210;

/**
 * Shows the thesis status in a <select> field if modification
 * is allowed or a read-only text input otherwise
 */
export const ThesisStatusIndicator = React.memo(function(props: Props) {
	const disabledValues = ALL_STATUSES.filter(status => (
		!canChangeStatusTo(props.original, status)
	));
	if (!props.enabled || disabledValues.length === ALL_STATUSES.length) {
		// If no status can be set by the current user, there's no point
		// showing it as a <select> field
		return <InputWithLabel
			labelText={LABEL_TEXT}
			inputText={thesisStatusToString(props.thesis.status)}
			inputType={InputType.ReadOnly}
			inputWidth={STATUS_FIELD_WIDTH}
		/>;
	}
	return <GenericSelect<ThesisStatus>
		value={props.thesis.status}
		onChange={props.onChange}
		// Don't disable the value we already have selected
		disabledValues={without(disabledValues, props.original.status)}
		optionInfo={statusSelectInfos}
		label={LABEL_TEXT}
		inputCss={{ width: STATUS_FIELD_WIDTH }}
	/>;
});
