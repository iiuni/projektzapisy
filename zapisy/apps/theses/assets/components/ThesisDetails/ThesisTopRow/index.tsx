/**
 * @file The top row of the thesis details view
 */
import * as React from "react";
import styled from "styled-components";
import { Moment } from "moment";

import { ThesisStatusIndicator } from "./ThesisStatusIndicator";
import { ThesisWorkMode } from "../../../app_types";
import { canModifyThesis } from "../../../permissions";
import { Thesis } from "../../../thesis";
import { ThesisStatus } from "../../../protocol";
import { ThesisReservationIndicator } from "./ThesisReservationIndicator";
import { InputWithLabel, InputType } from "./InputWithLabel";
import { formatDateTime } from "../../../utils";

const TopRowContainer = styled.div`
	display: flex;
	flex-direction: row;
	grid-column-gap: 10px;
	column-gap: 10px;
	justify-content: space-between;
	width: 100%;
	margin-bottom: 25px;
	flex-wrap: wrap;
`;

const ElementWrapper = styled.div`
	display: flex;
	align-items: center;
	height: 35px;
`;

const DATE_UPDATED_WIDTH = 150;

type Props = {
	thesis: Thesis;
	original: Thesis;
	mode: ThesisWorkMode;
	onReservedUntilChanged: (nr: Moment) => void;
	onStatusChanged: (ns: ThesisStatus) => void;
};

export class ThesisTopRow extends React.PureComponent<Props> {
	public render() {
		const readOnly = !canModifyThesis(this.props.original);
		const { mode, thesis } = this.props;
		return <TopRowContainer>
			<ElementWrapper>
			<ThesisReservationIndicator
				onChange={this.props.onReservedUntilChanged}
				thesis={thesis}
				readOnly={readOnly}
			/>
			</ElementWrapper>
			<ElementWrapper>
			<InputWithLabel
				labelText={"Aktualizacja"}
				inputWidth={DATE_UPDATED_WIDTH}
				inputText={mode === ThesisWorkMode.Editing ? formatDateTime(thesis.modifiedDate) : ""}
				inputType={InputType.ReadOnly}
			/>
			</ElementWrapper>
			<ElementWrapper>
			<ThesisStatusIndicator
				onChange={this.props.onStatusChanged}
				thesis={thesis}
				original={this.props.original}
				enabled={!readOnly}
			/>
			</ElementWrapper>
		</TopRowContainer>;
	}
}
