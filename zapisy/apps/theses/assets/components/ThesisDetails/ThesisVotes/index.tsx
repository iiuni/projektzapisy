import * as React from "react";
import styled from "styled-components";
import { compact } from "lodash";
import * as Mousetrap from "mousetrap";

import { Thesis } from "../../../thesis";
import { Employee, AppUser } from "../../../users";
import { ThesisVote } from "../../../protocol";
import { ThesisWorkMode } from "../../../app_types";
import { canChangeThesisVote, canModifyThesis } from "../../../permissions";
import { SingleVote } from "../../../votes";
import { SingleVoteView } from "./SingleVoteView";
import { strcmp } from "common/utils";
import { showRejectionReasonDialog } from "../../Dialogs/RejectionReasonDialog";

const Header = styled.div`
	font-weight: bold;
	font-size: 16px;
	color: black;
	margin-bottom: 20px;
`;

const VotesContainer = styled.div`
	text-align: center;
	width: 100%;
`;

type Props = {
	thesis: Thesis,
	original: Thesis,
	thesesBoard: Employee[],
	user: AppUser,
	isStaff: boolean;
	workMode: ThesisWorkMode;
	hasUnsavedChanges: boolean;
	isBoardMember: boolean;
	onChange: (member: Employee, newValue: SingleVote) => void;
	save: () => void;
};

/**
 * Renders the vote value for this thesis for each theses board member
 */
export class ThesisVotes extends React.Component<Props> {
	public componentDidMount() {
		Mousetrap.bind("a", this.onAcceptThesis);
		Mousetrap.bind("r", this.onRejectThesis);
	}

	public componentWillUnmount() {
		Mousetrap.unbind(["a", "r"]);
	}

	public render() {
		return <VotesContainer>
			<Header>Głosy</Header>
			{this.renderVotesList()}
		</VotesContainer>;
	}

	private renderVotesList() {
		const { thesis, original } = this.props;
		const displayAll = shouldDisplayAllVotes(original);
		const details = thesis.getVoteDetails();
		const votes = Array.from(details.getAllVotes().entries());
		votes.sort(([e1, _1], [e2, _2]) => (
			strcmp(e1.username, e2.username)
		));
		const result = compact(votes.map(([voter, vote], i) => {
			if (!displayAll && vote.value === ThesisVote.None) {
				return null;
			}
			return <SingleVoteView
				key={i}
				voter={voter}
				vote={vote}
				user={this.props.user}
				thesis={this.props.thesis}
				onChange={this.onVoteChanged}
			/>;
		}));
		return result.length ? result : <span>Brak głosów</span>;
	}

	private onVoteChanged = async (member: Employee, newVoteValue: ThesisVote) => {
		const votes = this.props.thesis.getVoteDetails();
		const vote = votes.getVoteForMember(member);
		if (newVoteValue !== ThesisVote.Rejected) {
			this.props.onChange(member, new SingleVote(newVoteValue, vote.reason));
			return true;
		}
		// Change the indicator right away for nice feedback
		this.props.onChange(member, new SingleVote(newVoteValue, vote.reason));
		try {
			const newReason = await showRejectionReasonDialog({
				message: "Wprowadź uzasadnienie oddanego głosu.",
				acceptText: "Potwierdź głos",
				cancelText: "Anuluj",
				initialReason: vote.reason,
			});
			this.props.onChange(member, new SingleVote(newVoteValue, newReason));
			return true;
		} catch (_) {
			// return to the old value
			this.props.onChange(member, vote);
			return false;
		}
	}

	private onAcceptThesis = (e: ExtendedKeyboardEvent) => {
		this.onShortcutVoteCast(ThesisVote.Accepted);
		e.preventDefault();
	}
	private onRejectThesis = (e: ExtendedKeyboardEvent) => {
		this.onShortcutVoteCast(ThesisVote.Rejected);
		e.preventDefault();
	}
	private async onShortcutVoteCast(vote: ThesisVote) {
		const { props } = this;
		if (
			props.isBoardMember &&
			canModifyThesis(props.thesis) &&
			canChangeThesisVote(props.thesis) &&
			!props.hasUnsavedChanges &&
			props.workMode === ThesisWorkMode.Editing
		) {
			const didChange = await this.onVoteChanged(props.user.person as Employee, vote);
			if (didChange) {
				props.save();
			}
		}
	}
}

/** Determine whether or not to display all votes, including
 * indeterminate ones, for this thesis
 */
function shouldDisplayAllVotes(thesis: Thesis) {
	return canChangeThesisVote(thesis);
}
