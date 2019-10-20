import * as React from "react";
import Button from "react-button-component";
import styled from "styled-components";
import update from "immutability-helper";
import * as Mousetrap from "mousetrap";
import "mousetrap-global-bind";
import * as moment from "moment";
import { cloneDeep } from "lodash";

import { ThesisTopRow } from "./ThesisTopRow";
import { ThesisMiddleForm } from "./ThesisMiddleForm";
import { ThesisVotes } from "./ThesisVotes";
import "./style.less";
import { Spinner } from "../Spinner";
import { getDisabledStyle, macosifyKeys } from "../../utils";
import { ThesisWorkMode, ApplicationState } from "../../app_types";
import {
	canModifyThesis, canDeleteThesis, canSeeThesisRejectionReason, canChangeStatusTo, canSeeThesisVotes,
} from "../../permissions";
import { Thesis } from "../../thesis";
import { AppUser, Employee, Student } from "../../users";
import { ThesisStatus, ThesisKind } from "../../protocol";
import { AppMode } from "../../app_logic/app_mode";
import { confirmationDialog } from "../Dialogs/ConfirmationDialog";
import { formatTitle } from "../util";
import { SingleVote } from "../../votes";
import { showMasterRejectionDialog } from "../Dialogs/MasterRejectionDialog";

const ActionButton = React.memo(Button.extend`
	&:disabled:hover {
		background: white;
	}
	&:disabled {
		color: grey;
		cursor: default;
	}
	min-height: initial;
	height: 25px;
`);

const DetailsSectionWrapper = styled.div`
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: center;
	border: 1px solid black;
	padding: 15px;
`;

const MainDetailsContainer = styled.div`
	display: flex;
	flex-direction: row;
	box-sizing: content-box;
	width: 100%;
	flex-wrap: wrap;
`;

const LeftDetailsContainer = styled.div`
	flex-grow: 1;
	margin-right: 20px;
`;

const VotesPlaceholder = styled.div`
	height: 100%;
`;

const RightDetailsContainer = styled.div`
	display: flex;
	flex-direction: column;
	justify-content: space-between;
`;

const ButtonsContainer = styled.div`
	display: grid;
	grid-gap: 10px;
`;

const RejectionReasonContainer = styled.textarea`
	width: 100%;
	height: 100px;
	box-sizing: border-box;
`;

const DEFAULT_THESIS_RESERVATION_YEARS = 2;

type Props = {
	thesis: Thesis;
	original: Thesis;
	thesesBoard: Employee[];
	appState: ApplicationState;
	hasUnsavedChanges: boolean;
	mode: ThesisWorkMode;
	hasTitleError: boolean;
	user: AppUser;
	isBoardMember: boolean;
	isStaff: boolean;
	onThesisModified: (thesis: Thesis) => void;
	onDeletionRequested: () => Promise<void>;
	onSaveRequested: () => Promise<void>;
	onResetRequested: () => void;
	onChangedTitle: () => void;
};

export class ThesisDetails extends React.PureComponent<Props> {
	private actionInProgress: boolean = false;

	public componentDidMount() {
		Mousetrap.bindGlobal(macosifyKeys("ctrl+s"), ev => {
			this.handleSave();
			ev.preventDefault();
		});
		Mousetrap.bind("del", () => {
			this.handleDelete();
		});
	}

	public componentWillUnmount() {
		Mousetrap.unbindGlobal(macosifyKeys("ctrl+s"));
		Mousetrap.unbind("del");
	}

	private shouldRenderRightPanel() {
		return (
			this.shouldRenderVotes() ||
			this.shouldRenderRejectButton() ||
			this.shouldRenderResetButton() ||
			this.shouldRenderDeleteButton() ||
			this.shouldRenderSaveButton()
		);
	}

	public render() {
		return <DetailsSectionWrapper>
			{this.props.appState === ApplicationState.Saving
				? <Spinner style={{ position: "absolute" }}/>
				: null
			}
			<MainDetailsContainer
				style={AppMode.isPerformingBackendOp() ? getDisabledStyle() : {}}
			>
				<LeftDetailsContainer>{this.renderThesisLeftPanel()}</LeftDetailsContainer>
				{this.shouldRenderRightPanel()
					? <RightDetailsContainer>{this.renderThesisRightPanel()}</RightDetailsContainer>
					: null
				}
			</MainDetailsContainer>
			{this.renderRejectionReasonIfApplicable()}
		</DetailsSectionWrapper>;
	}

	private renderThesisLeftPanel() {
		const { thesis, original } = this.props;
		return <>
			<ThesisTopRow
				mode={this.props.mode}
				thesis={thesis}
				original={original}
				onReservedUntilChanged={this.onReservedUntilChanged}
				onStatusChanged={this.onStatusChanged}
			/>
			<ThesisMiddleForm
				thesis={thesis}
				original={original}
				titleError={this.props.hasTitleError}
				onTitleChanged={this.onTitleChanged}
				onKindChanged={this.onKindChanged}
				onAdvisorChanged={this.onAdvisorChanged}
				onSuppAdvisorChanged={this.onSuppAdvisorChanged}
				onAddStudents={this.onAddStudents}
				onStudentRemoved={this.onStudentRemoved}
				onStudentChanged={this.onStudentChanged}
				onDescriptionChanged={this.onDescriptionChanged}
			/>
		</>;
	}

	private shouldRenderVotes() {
		return canSeeThesisVotes();
	}

	private renderThesisRightPanel() {
		return <>
			{this.shouldRenderVotes() ? <ThesisVotes
				thesis={this.props.thesis}
				original={this.props.original}
				thesesBoard={this.props.thesesBoard}
				isStaff={this.props.isStaff}
				isBoardMember={this.props.isBoardMember}
				user={this.props.user}
				workMode={this.props.mode}
				hasUnsavedChanges={this.props.hasUnsavedChanges}
				onChange={this.onVoteChanged}
				save={this.handleSave}
			/> : this.renderVotesPlaceholder()}
			<ButtonsContainer>
				{this.renderRejectButton()}
				{this.renderResetButton()}
				{this.renderDeleteButton()}
				{this.renderSaveButton()}
			</ButtonsContainer>
		</>;
	}

	private renderVotesPlaceholder() {
		return <VotesPlaceholder />;
	}

	private shouldRenderRejectButton() {
		return (
			this.props.mode === ThesisWorkMode.Editing &&
			canChangeStatusTo(this.props.original, ThesisStatus.ReturnedForCorrections)
		);
	}

	private renderRejectButton() {
		if (!this.shouldRenderRejectButton()) {
			return null;
		}
		const { hasUnsavedChanges } = this.props;
		const alreadyReturned = this.props.original.status === ThesisStatus.ReturnedForCorrections;
		let tooltip = "Zwróć pracę do poprawek";
		if (alreadyReturned) {
			tooltip = "Praca została już zwrócona do poprawek";
		} else if (hasUnsavedChanges) {
			tooltip = "Wprowadzono niezapisane zmiany";
		}
		return <ActionButton
			onClick={this.onReject}
			disabled={hasUnsavedChanges || alreadyReturned}
			title={tooltip}
		>Do poprawek</ActionButton>;
	}

	private onReject = async () => {
		const didChange = await this.onStatusChanged(ThesisStatus.ReturnedForCorrections);
		if (didChange) {
			this.handleSave();
		}
	}

	private shouldRenderResetButton() {
		return this.props.mode === ThesisWorkMode.Editing && canModifyThesis(this.props.original);
	}

	private renderResetButton() {
		if (!this.shouldRenderResetButton()) {
			return null;
		}
		const { hasUnsavedChanges } = this.props;
		return <ActionButton
			onClick={this.props.onResetRequested}
			disabled={!hasUnsavedChanges}
			title={hasUnsavedChanges ? "Wycofaj dokonane zmiany" : "Nie dokonano zmian"}
		>Wyczyść</ActionButton>;
	}

	private shouldRenderDeleteButton() {
		return this.props.mode === ThesisWorkMode.Editing && canDeleteThesis(this.props.original);
	}

	private renderDeleteButton() {
		if (!this.shouldRenderDeleteButton()) {
			return null;
		}
		return <ActionButton
			onClick={this.handleDelete}
			title={"Usuń pracę z systemu"}
		>Usuń</ActionButton>;
	}

	private shouldRenderSaveButton() {
		return canModifyThesis(this.props.original);
	}

	private renderSaveButton() {
		if (!this.shouldRenderSaveButton()) {
			return null;
		}
		const { hasUnsavedChanges } = this.props;
		return <ActionButton
			onClick={this.handleSave}
			disabled={!hasUnsavedChanges}
			title={hasUnsavedChanges ? this.getActionDescription() : "Nie dokonano zmian"}
		>{this.getActionTitle()}</ActionButton>;
	}

	private getActionTitle() {
		return this.props.mode === ThesisWorkMode.Adding ? "Dodaj" : "Zapisz";
	}

	private getActionDescription() {
		return this.props.mode === ThesisWorkMode.Adding ? "Dodaj nową pracę" : "Zapisz zmiany";
	}

	private renderRejectionReasonIfApplicable() {
		if (
			this.props.original.status !== ThesisStatus.ReturnedForCorrections ||
			!canSeeThesisRejectionReason(this.props.original)
		) {
			return null;
		}
		return <>
			<hr />
			<RejectionReasonContainer
				readOnly
				defaultValue={this.props.original.rejectionReason}
			/>
		</>;
	}

	private handleDelete = async () => {
		if (this.actionInProgress || !canDeleteThesis(this.props.original)) {
			return;
		}
		this.actionInProgress = true;
		const confirmed = await confirmationDialog({
			message: <>Czy usunąć pracę {formatTitle(this.props.thesis.title)}?</>,
			yesText: "Tak, usuń",
			noText: "Nie, wróć",
		});
		if (confirmed) {
			await this.props.onDeletionRequested();
		}
		this.actionInProgress = false;
	}

	private async confirmArchiveThesis() {
		return confirmationDialog({
			message: <>Czy zarchiwizować pracę {formatTitle(this.props.thesis.title)}?
			Dalszej edycji dokonywać będzie mógł wyłącznie administrator systemu.</>,
			yesText: "Tak, zarchiwizuj",
			noText: "Nie, wróć",
		});
	}

	private handleSave = async () => {
		if (this.actionInProgress || !this.props.hasUnsavedChanges) { return; }
		this.actionInProgress = true;
		const { original, thesis } = this.props;
		if (
			original.status === ThesisStatus.Defended ||
			thesis.status !== ThesisStatus.Defended ||
			await this.confirmArchiveThesis()
		) {
			await this.props.onSaveRequested();
		}
		this.actionInProgress = false;
	}

	private updateThesisState(updateObject: object) {
		this.props.onThesisModified(
			update(this.props.thesis, updateObject)
		);
	}

	private onReservedUntilChanged = (newDate: moment.Moment): void => {
		this.updateThesisState({ reservedUntil: { $set: newDate } });
	}

	private onStatusChanged = async (newStatus: ThesisStatus) => {
		// update UI right away for nice feedback
		this.updateThesisState({ status: { $set: newStatus } });
		const originalStatus = this.props.original.status;
		if (
			originalStatus !== ThesisStatus.ReturnedForCorrections &&
			newStatus === ThesisStatus.ReturnedForCorrections
		) {
			const { thesis } = this.props;
			const msg = "Podaj podsumowanie uwag do tematu w polu poniżej. " +
				"Informacja ta zostanie wysłana do promotora pracy.";
			try {
				const finalRejectionReason = await showMasterRejectionDialog({
					message: msg,
					cancelText: "Anuluj",
					acceptText: "Potwierdź",
					initialReason: thesis.rejectionReason || thesis.getDefaultRejectionReason()
				});
				this.updateThesisState({ rejectionReason: { $set: finalRejectionReason } });
				return true;
			} catch (_) {
				// restore old status
				this.updateThesisState({ status: { $set: originalStatus } });
				return false;
			}
		}
	}

	private onTitleChanged = (newTitle: string): void => {
		// As soon as the user changes the title, we clear the error state
		// it would be annoying if it stayed on until Save is clicked again
		this.props.onChangedTitle();
		this.updateThesisState({ title: { $set: newTitle } });
	}

	private onKindChanged = (newKind: ThesisKind): void => {
		this.updateThesisState({ kind: { $set: newKind } });
	}

	private onAdvisorChanged = (newAdvisor: Employee | null): void => {
		this.updateThesisState({ advisor: { $set: newAdvisor } });
	}

	private onSuppAdvisorChanged = (newSuppAdvisor: Employee | null): void => {
		this.updateThesisState({ supportingAdvisor: { $set: newSuppAdvisor } });
	}

	private updateStateWithStudentChange(update: object) {
		// also update the reservation date, but only if they haven't touched it previously
		const { original, thesis } = this.props;
		if (original.isReservationDateSame(thesis.reservedUntil)) {
			const expires = moment().add(DEFAULT_THESIS_RESERVATION_YEARS, "years");
			Object.assign(update, { reservedUntil: { $set: expires } });
		}
		this.updateThesisState(update);
	}

	private onStudentChanged = (idx: number, student: Student | null) => {
		this.updateStateWithStudentChange({ students: { $splice: [[idx, 1, student]] } });
	}

	private onStudentRemoved = (idx: number): void => {
		this.updateStateWithStudentChange({ students: { $splice: [[idx, 1]] } });
	}

	private onAddStudents = (num: number) => {
		this.updateThesisState({ students: { $push: Array(num).fill(null) } });
	}

	private onDescriptionChanged = (newDesc: string): void => {
		this.updateThesisState({ description: { $set: newDesc } });
	}

	private onVoteChanged = (voter: Employee, newValue: SingleVote): void => {
		const newVotes = cloneDeep(this.props.thesis.getVoteDetails());
		newVotes.setVote(voter, newValue);
		this.updateThesisState({ votes: { $set: newVotes } });
	}
}
