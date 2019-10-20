import * as React from "react";
import styled from "styled-components";

import { PersonType } from "../../../backend_callers";
import { PersonField } from "./PersonField";
import { ThesisKindField } from "./ThesisKindField";
import { AddRemoveIcon, IconType } from "./AddRemoveIcon";
import { canSetArbitraryAdvisor, canModifyThesis, canChangeTitle } from "../../../permissions";
import { Thesis, MAX_THESIS_TITLE_LEN } from "../../../thesis";
import { Employee, Student } from "../../../users";
import { ThesisKind, MAX_STUDENTS_PER_THESIS } from "../../../protocol";

const MidFormTable = styled.table`
	width: 100%;
	margin-bottom: 25px;

	td {
		border-left: 4px solid transparent;
		border-top: 6px solid transparent;
	}
	td:first-child {
		border-left: 0;
	}
	tr:first-child td {
		border-top: 0;
	}

	tr td:first-child {
		width: 13%;
	}
`;

const PersonTableRow = styled.tr`
	height: 44px;
`;

const OptionalFieldLabel = React.memo(styled.span`
	font-style: italic;
`);

type State = {
	displaySuppAdvisor: boolean;
};

type Props = {
	thesis: Thesis;
	original: Thesis;
	/** Should the title field be highlighted to indicate an error? */
	titleError: boolean;
	onTitleChanged: (nt: string) => void;
	onKindChanged: (nk: ThesisKind) => void;
	onAdvisorChanged: (na: Employee | null) => void;
	onSuppAdvisorChanged: (na: Employee | null) => void;
	onAddStudents: (num: number) => void;
	onStudentRemoved: (idx: number) => void;
	onStudentChanged: (index: number, student: Student | null) => void;
	onDescriptionChanged: (nd: string) => void;
};

/** Decide whether to display the fields based on the thesis instance in the props */
function getStateFromProps(props: Props) {
	return {
		displaySuppAdvisor: props.thesis.supportingAdvisor !== null,
	};
}

export class ThesisMiddleForm extends React.PureComponent<Props, State> {
	constructor(props: Props) {
		super(props);
		this.state = getStateFromProps(props);
	}

	public componentWillReceiveProps(nextProps: Props) {
		if (this.props.thesis !== nextProps.thesis) {
			this.setState(getStateFromProps(nextProps));
		}
	}

	private handleDescriptionChanged = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
		this.props.onDescriptionChanged(e.target.value);
	}

	private triggerSuppAdvVisibility = () => {
		const newValue = !this.state.displaySuppAdvisor;
		this.setState({ displaySuppAdvisor: newValue });
		if (!newValue) {
			this.props.onSuppAdvisorChanged(null);
		}
	}

	public render() {
		const readOnly = !canModifyThesis(this.props.original);

		return <div>
			<MidFormTable>
				<tbody>
				{this.renderTitle(readOnly)}
				{this.renderKind(readOnly)}
				{this.renderAdvisors(readOnly)}
				{this.renderStudents(readOnly)}
				</tbody>
			</MidFormTable>
			{this.renderDescription(readOnly)}
		</div>;
	}

	private renderTitle(readOnly: boolean) {
		const titleStyle: React.CSSProperties = {
			width: "100%",
			height: "70px",
			boxSizing: "border-box",
		};
		if (this.props.titleError) {
			Object.assign(titleStyle, {
				border: "1px solid red"
			});
		}
		const titleReadOnly = readOnly || !canChangeTitle(this.props.original);
		return <tr>
			<td>Tytuł</td>
			<td><textarea
				style={titleStyle}
				value={this.props.thesis.title}
				maxLength={MAX_THESIS_TITLE_LEN}
				readOnly={titleReadOnly}
				onChange={this.onTitleChanged}
			/></td>
		</tr>;
	}

	private onTitleChanged = (ev: React.ChangeEvent<HTMLTextAreaElement>) => {
		this.props.onTitleChanged(ev.target.value);
	}

	private renderKind(readOnly: boolean) {
		return <tr>
			<td>Typ</td>
			<td>
				<ThesisKindField
					value={this.props.thesis.kind}
					readOnly={readOnly}
					onChange={this.props.onKindChanged}
				/>
			</td>
		</tr>;
	}

	private renderAdvisors(readOnly: boolean) {
		return <>
			<PersonTableRow>
				<td>Promotor</td>
				<td>
					<PersonField
						personType={PersonType.Employee}
						onChange={this.props.onAdvisorChanged}
						personConstructor={Employee}
						value={this.props.thesis.advisor}
						readOnly={readOnly || !canSetArbitraryAdvisor()}
					/>
					{ readOnly || this.state.displaySuppAdvisor
						? null
						: <AddRemoveIcon
							onClick={this.triggerSuppAdvVisibility}
							type={IconType.Add}
						/>
					}
				</td>
			</PersonTableRow>
			{ this.state.displaySuppAdvisor ? (
				<PersonTableRow>
					<td><OptionalFieldLabel>Promotor wspomagający</OptionalFieldLabel></td>
					<td>
						<PersonField
							personType={PersonType.Employee}
							onChange={this.props.onSuppAdvisorChanged}
							personConstructor={Employee}
							value={this.props.thesis.supportingAdvisor}
							readOnly={readOnly}
						/>
						{ readOnly
							? null
							: <AddRemoveIcon
								onClick={this.triggerSuppAdvVisibility}
								type={IconType.Remove}
							/>
						}
					</td>
				</PersonTableRow>
			) : null }
		</>;
	}

	private renderStudents(readOnly: boolean) {
		let students: Array<Student | null> = this.props.thesis.students;
		if (!students.length) {
			// if there are no students, pretend there is one field
			// with no selection made
			students = [null];
		}
		const len = students.length;
		return <>{
			students.map((s, idx) =>
				<PersonTableRow key={`stud_${idx}`}>
					<td>{len > 1 ? `Student ${idx + 1}.` : "Student"}</td>
					<td>
						<PersonField
							personType={PersonType.Student}
							onChange={nv => this.onStudentChanged(idx, nv)}
							personConstructor={Student}
							value={s}
							readOnly={readOnly}
						/>
						{ !readOnly && idx !== 0
							? <AddRemoveIcon
								onClick={() => this.onStudentRemoved(idx)}
								type={IconType.Remove}
							/>
							: null
						}
						{ !readOnly && idx === len - 1 && len < MAX_STUDENTS_PER_THESIS
							? <AddRemoveIcon
								onClick={() => this.onAddAnotherStudent()}
								type={IconType.Add}
							/>
							: null
						}
					</td>
				</PersonTableRow>
			)
		}</>;
	}

	private onAddAnotherStudent = () => {
		if (!this.props.thesis.students.length) {
			// if there actually aren't any students, we display it as one 'empty' student
			// field, but the expected behavior would be to have two after clicking
			// the button
			this.props.onAddStudents(2);
		} else {
			this.props.onAddStudents(1);
		}
	}

	private onStudentRemoved = (index: number) => {
		this.props.onStudentRemoved(index);
	}

	private onStudentChanged = (index: number, student: Student | null) => {
		this.props.onStudentChanged(index, student);
	}

	private renderDescription(readOnly: boolean) {
		return <textarea
			style={{ width: "100%", height: "100px", boxSizing: "border-box" }}
			value={this.props.thesis.description}
			readOnly={readOnly}
			onChange={this.handleDescriptionChanged}
		/>;
	}
}
