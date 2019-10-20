import * as React from "react";
import * as moment from "moment";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import styled from "styled-components";

import { InputWithLabel, InputType } from "./InputWithLabel";
import { formatDate } from "../../../utils";
import { Thesis } from "../../../thesis";

type Props = {
	thesis: Thesis;
	readOnly: boolean;

	onChange: (nv: moment.Moment) => void;
};

const LABEL_TEXT = "Zarezerwowana do";
const Label = styled.span`
	margin-right: 5px;
`;
const READONLY_INPUT_WIDTH = 100;

export class ThesisReservationIndicator extends React.PureComponent<Props> {
	public render() {
		const { props } = this;
		if (props.readOnly) {
			return this.renderReadOnly();
		}
		return <div>
			<Label>{LABEL_TEXT}</Label>
			<DatePicker
				selected={props.thesis.reservedUntil}
				onChange={this.props.onChange}
				todayButton={"Dzisiaj"}
				locale="pl_PL"
				className="react-datepicker-input"
				isClearable
				minDate={moment()}
				maxDate={props.thesis.getMaxReservationDate()}
			/>
		</div>;
	}

	private renderReadOnly() {
		const { thesis } = this.props;
		return thesis.reservedUntil
			? <InputWithLabel
				labelText={LABEL_TEXT}
				inputText={formatDate(thesis.reservedUntil)}
				inputType={InputType.ReadOnly}
				inputWidth={READONLY_INPUT_WIDTH}
			/>
			: <span>Niezarezerwowana</span>;
	}
}
