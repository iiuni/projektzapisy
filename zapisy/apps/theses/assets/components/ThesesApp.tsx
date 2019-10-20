/**
 * @file The main theses app component.
 * Renders all subcomponents and glues them together, also permitting them
 * to change the state via callbacks.
 * Application state/logic is held in app_logic/
 */

import * as React from "react";
import * as Mousetrap from "mousetrap";
import "mousetrap-global-bind";
import { observer } from "mobx-react";
import styled from "styled-components";
import "react-confirm-alert/src/react-confirm-alert.css";
import { withAlert } from "react-alert";

import { ThesisDetails } from "./ThesisDetails";
import { ThesesTable } from "./ThesesTable";
import { ErrorBox } from "./ErrorBox";
import { canAddThesis } from "../permissions";
import { ListFilters } from "./ListFilters";
import { AddNewButton } from "./AddNewButton";
import { ThesisWorkMode, ApplicationState } from "../app_types";
import { ThesisNameConflict, ThesisEmptyTitle } from "../errors";
import { Thesis } from "../thesis";
import { ThesisEditing } from "../app_logic/editing";
import { List } from "../app_logic/theses_list";
import { AppMode } from "../app_logic/app_mode";
import { Users } from "../app_logic/users";
import { LoadingIndicator } from "./LoadingIndicator";
import { macosifyKeys } from "../utils";
import { confirmationDialog } from "./Dialogs/ConfirmationDialog";
import { showErrorMessage } from "./Dialogs/MessageDialog";
import { formatTitle } from "./util";

const TopRowContainer = styled.div`
	display: flex;
	justify-content: space-between;
	flex-wrap: wrap;
`;

type Props = {
	/** A promise representing the app logic initialization process */
	initPromise: PromiseLike<any>;
};

const initialState = {
	/** The error instance, if any. If one exists, we abort the app and display it */
	applicationError: null as Error | null,
	/** Whether the thesis title was invalid */
	hasTitleError: false,
};
type State = typeof initialState;

@observer
class ThesesAppInternal extends React.Component<Props, State> {
	state = initialState;
	private oldOnBeforeUnload: ((this: WindowEventHandlers, ev: BeforeUnloadEvent) => any) | null = null;
	private tableInstance?: ThesesTable;

	async componentDidMount() {
		this.oldOnBeforeUnload = window.onbeforeunload;
		window.onbeforeunload = this.confirmUnload;
		this.initializeKeyboardShortcuts();

		try {
			await this.props.initPromise;
		} catch (err) {
			console.error(err);
			this.setState({ applicationError: err });
		}
	}

	componentWillUnmount() {
		window.onbeforeunload = this.oldOnBeforeUnload;
		this.deconfigureKeyboardShortcuts();
	}

	private initializeKeyboardShortcuts() {
		Mousetrap.bindGlobal(macosifyKeys("ctrl+m"), this.setupForAddingThesis);
	}

	private deconfigureKeyboardShortcuts() {
		Mousetrap.unbindGlobal(macosifyKeys("ctrl+m"));
	}

	private confirmUnload = (ev: BeforeUnloadEvent) => {
		if (ThesisEditing.hasUnsavedChanges) {
			// As specified in https://developer.mozilla.org/en-US/docs/Web/API/WindowEventHandlers/onbeforeunload
			// preventDefault() is what the spec says,
			// in practice some browsers like returnValue to be set
			ev.preventDefault();
			ev.returnValue = "";
		}
	}

	/**
	 * Execute the specified list-modifying action in a safe context - if any
	 * error occurs, it'll be caught and handled
	 */
	private wrapListChanger(context: object, f: (...args: any[]) => PromiseLike<any>) {
		return async (...args: any[]) => {
			try {
				await f.apply(context, args);
				if (this.tableInstance) {
					this.tableInstance.onListReloaded();
				}
			} catch (err) { this.setState({ applicationError: err }); }
		};
	}

	private onTypeFilterChanged = this.wrapListChanger(List, List.changeTypeFilter);
	private onOnlyMineChanged = this.wrapListChanger(List, List.changeOnlyMineFilter);
	private onAdvisorChanged = this.wrapListChanger(List, List.changeAdvisorFilter);
	private onTitleChanged = this.wrapListChanger(List, List.changeTitleFilter);
	private renderTopRow() {
		const shouldShowNewBtn = canAddThesis();
		return <TopRowContainer>
			<ListFilters
				onTypeChange={this.onTypeFilterChanged}
				typeValue={List.params.type}
				onOnlyMineChange={this.onOnlyMineChanged}
				onlyMine={List.params.onlyMine}
				onAdvisorChange={this.onAdvisorChanged}
				advisorValue={List.params.advisor}
				onTitleChange={this.onTitleChanged}
				titleValue={List.params.title}
				state={AppMode.applicationState}
				displayUngraded={Users.isUserMemberOfBoard()}
				stringFilterBeingChanged={List.stringFilterBeingChanged}
			/>
			{shouldShowNewBtn
				? <AddNewButton
					onClick={this.setupForAddingThesis}
					enabled={!AppMode.isPerformingBackendOp()}
				/>
				: null
			}
		</TopRowContainer>;
	}

	private onLoadMore = async (until: number) => {
		try {
			await List.loadMore(until);
		} catch (err) { console.error("Unable to load more:", err); }
	}
	private onSortChanged = this.wrapListChanger(List, List.changeSort);
	private setTableRef = (ref: ThesesTable) => { this.tableInstance = ref; };
	private renderThesesList() {
		return <ThesesTable
			ref={this.setTableRef}
			applicationState={AppMode.applicationState}
			theses={List.theses}
			selectedIdx={ThesisEditing.selectedIdx}
			sortColumn={List.params.sortColumn}
			sortDirection={List.params.sortDirection}
			isEditingThesis={ThesisEditing.hasUnsavedChanges}
			totalThesesCount={List.totalCount}
			onThesisSelected={this.onThesisSelected}
			onSortChanged={this.onSortChanged}
			loadMoreRows={this.onLoadMore}
		/>;
	}

	private onThesisModified = (nt: Thesis) => { ThesisEditing.updateModifiedThesis(nt); };
	private onChangedTitle = () => {
		if (this.state.hasTitleError) {
			this.setState({ hasTitleError: false });
		}
	}
	private renderThesisDetails() {
		console.assert(!!ThesisEditing.thesis);
		return <ThesisDetails
			thesis={ThesisEditing.thesis!.modified}
			thesesBoard={Users.thesesBoard}
			original={ThesisEditing.thesis!.original}
			appState={AppMode.applicationState}
			hasUnsavedChanges={ThesisEditing.hasUnsavedChanges}
			mode={AppMode.workMode!}
			user={Users.currentUser}
			isBoardMember={Users.isUserMemberOfBoard()}
			isStaff={Users.isUserStaff()}
			hasTitleError={this.state.hasTitleError}
			onChangedTitle={this.onChangedTitle}
			onSaveRequested={this.onSave}
			onDeletionRequested={this.onDelete}
			onResetRequested={this.onResetChanges}
			onThesisModified={this.onThesisModified}
		/>;
	}

	public render() {
		if (this.state.applicationError) {
			return this.renderErrorScreen();
		}
		if (AppMode.applicationState === ApplicationState.FirstLoad) {
			return <LoadingIndicator/>;
		}
		const { thesis } = ThesisEditing;
		if (thesis !== null) {
			// if a thesis is present, we're not just viewing
			console.assert(AppMode.workMode !== ThesisWorkMode.Viewing);
		}
		return <>
			{this.renderTopRow()}
			<br />
			{this.renderThesesList()}
			{
				thesis
				? <><br /><hr />{this.renderThesisDetails()}</>
				: null
			}
		</>;
	}

	private renderErrorScreen() {
		return <ErrorBox
			errorTitle={
				<em>{this.state.applicationError!.toString()}</em>
			}
		/>;
	}

	/**
	 * If there are unsaved changes, ask the user whether they should be discarded.
	 * Returns true immediately if there are no changes to be saved.
	 */
	private confirmDiscardChanges() {
		if (ThesisEditing.hasUnsavedChanges) {
			const title = ThesisEditing.thesis!.modified.title;
			return confirmationDialog({
				message: buildUnsavedConfirmation(title),
				yesText: "Tak, porzuć",
				noText: "Nie, wróć",
			});
		}
		return Promise.resolve(true);
	}

	private onThesisSelected = async (thesis: Thesis) => {
		if (!await this.confirmDiscardChanges()) {
			return;
		}
		this.setState({ hasTitleError: false });
		ThesisEditing.selectThesis(thesis);
	}

	private setupForAddingThesis = async () => {
		if (!canAddThesis() || !await this.confirmDiscardChanges()) {
			return;
		}
		this.setState({ hasTitleError: false });
		ThesisEditing.setupForNewThesis();
	}

	private onResetChanges = async () => {
		if (!await this.confirmDiscardChanges()) {
			return;
		}
		ThesisEditing.resetModifiedThesis();
	}

	private onDelete = async () => {
		try {
			await ThesisEditing.delete();
			// Deleting does reload the list
			if (this.tableInstance) {
				this.tableInstance.onListReloaded();
			}
			(this.props as any).alert.success("Praca została usunięta");
		} catch (err) {
			errorWithActionName("usunąć", err);
		}
	}

	private confirmWipeVote() {
		if (!ThesisEditing.shouldShowWipeVotesWarning()) {
			return Promise.resolve(true);
		}
		return confirmationDialog({
			title: "Uwaga",
			message: (
				"Zmiana tytułu spowoduje wykasowanie wszystkich głosów " +
				"i rozpoczęcie głosowania od nowa. Czy kontynuować?"
			),
			yesText: "Tak, zmień tytuł",
			noText: "Nie, wróć",
		});
	}

	private onSave = async () => {
		try {
			if (!await this.confirmWipeVote()) {
				return;
			}
			const oldWorkMode = AppMode.workMode;
			await ThesisEditing.save();
			// Saving does reload the list
			if (this.tableInstance) {
				this.tableInstance.onListReloaded();
			}
			(this.props as any).alert.success(messageForWorkMode(oldWorkMode));
		} catch (err) {
			this.handleSaveError(err);
		}
	}

	private handleSaveError(err: Error) {
		if (err instanceof ThesisNameConflict) {
			(this.props as any).alert.error("Praca o tym tytule już istnieje.");
			this.setState({ hasTitleError: true });
		} else if (err instanceof ThesisEmptyTitle) {
			(this.props as any).alert.error("Tytuł pracy nie może być pusty");
			this.setState({ hasTitleError: true });
		} else {
			errorWithActionName("zapisać", err);
		}
	}
}

function errorWithActionName(actionName: string, err: Error) {
	const message = (
		`Nie udało się ${actionName} pracy (${err}). ` +
		"Odśwież stronę/sprawdź połączenie sieciowe i spróbuj jeszcze raz. " +
		"Jeżeli problem powtórzy się, opisz go na trackerze Zapisów."
	);
	showErrorMessage({ message });
}

function buildUnsavedConfirmation(title: string) {
	return title.trim()
		? <>Czy porzucić niezapisane zmiany w pracy {formatTitle(title)}?</>
		: "Czy porzucić niezapisane zmiany w edytowanej pracy?";
}

function messageForWorkMode(mode: ThesisWorkMode) {
	switch (mode) {
		case ThesisWorkMode.Adding: return "Praca została dodana";
		case ThesisWorkMode.Editing: return "Zapisano zmiany";
		default: throw new Error("bad work mode");
	}
}

// This type juggling is required because react-alert is badly typed
const enhanced = withAlert(ThesesAppInternal as any);
export const ThesesApp = enhanced as any as typeof ThesesAppInternal;
