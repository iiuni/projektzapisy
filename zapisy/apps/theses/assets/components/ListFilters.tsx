/**
 * Defines the filters component rendered above the theses table.
 */

import * as React from "react";
import styled from "styled-components";

import { GenericSelect } from "./GenericSelect";
import { ApplicationState } from "../app_types";
import { ThesisTypeFilter, thesisTypeFilterToString } from "../protocol";
import { StringFilter } from "../app_logic/theses_list";

const typeFilters = [
	ThesisTypeFilter.Everything,
	ThesisTypeFilter.Current,
	ThesisTypeFilter.Archived,
	ThesisTypeFilter.Masters,
	ThesisTypeFilter.Engineers,
	ThesisTypeFilter.Bachelors,
	ThesisTypeFilter.BachelorsOrEngineers,
	ThesisTypeFilter.ISIM,
	ThesisTypeFilter.AvailableMasters,
	ThesisTypeFilter.AvailableEngineers,
	ThesisTypeFilter.AvailableBachelors,
	ThesisTypeFilter.AvailableBachelorsOrEngineers,
	ThesisTypeFilter.AvailableISIM,
].map(type => ({ val: type, displayName: thesisTypeFilterToString(type) }));

const filtersWithUngraded = [
	{
		val: ThesisTypeFilter.Ungraded,
		displayName: thesisTypeFilterToString(ThesisTypeFilter.Ungraded),
	},
	...typeFilters,
];

type Props = {
	displayUngraded: boolean;

	onTypeChange: (newFilter: ThesisTypeFilter) => void;
	typeValue: ThesisTypeFilter;

	onOnlyMineChange: (onlyMine: boolean) => void;
	onlyMine: boolean;

	onAdvisorChange: (advisorSubstr: string) => void;
	advisorValue: string;

	onTitleChange: (titleSubstr: string) => void;
	titleValue: string;

	state: ApplicationState;
	stringFilterBeingChanged: StringFilter;
};

const ItemContainer = styled.div`
	height: 35px;
	align-items: center;
`;

const TextFilterField = styled.input`
	margin-left: 5px;
	width: auto;
`;

const labelStyle: React.CSSProperties = {
	fontWeight: "bold",
	fontSize: "110%",
};

const OnlyMineContainer = styled.label`
	display: block;
	height: 28px;
	display: flex;
	align-items: center;
	color: inherit;
`;

const OnlyMineCheckbox = styled.input`
	/* _sigh_ bootstrap */
	margin-right: 5px !important;
`;

const FiltersContainer = styled.div`
	display: flex;
	justify-content: space-between;
	align-items: center;
	flex-wrap: wrap;
	flex-grow: 0.6;
`;

export class ListFilters extends React.PureComponent<Props> {
	private handleTypeChange = (newFilter: ThesisTypeFilter): void => {
		this.props.onTypeChange(newFilter);
	}

	private handleOnlyMineChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
		this.props.onOnlyMineChange(e.target.checked);
	}

	private handleTitleChanged = (e: React.ChangeEvent<HTMLInputElement>): void => {
		this.props.onTitleChange(e.target.value);
	}

	private handleAdvisorChanged = (e: React.ChangeEvent<HTMLInputElement>): void => {
		this.props.onAdvisorChange(e.target.value);
	}

	public render() {
		const { state, stringFilterBeingChanged } = this.props;
		if (stringFilterBeingChanged !== "") {
			console.assert(
				state === ApplicationState.Refetching,
				"While changing string filters we should fetching",
			);
		}
		const isNormalState = state === ApplicationState.Normal;
		return <FiltersContainer>
			<ItemContainer><GenericSelect<ThesisTypeFilter>
				value={this.props.typeValue}
				onChange={this.handleTypeChange}
				optionInfo={
					this.props.displayUngraded ? filtersWithUngraded : typeFilters
				}
				label={"Rodzaj"}
				labelCss={labelStyle}
				enabled={isNormalState}
			/></ItemContainer>

			<ItemContainer>
				<span style={labelStyle}>Tytuł</span>
				<TextFilterField
					type="text"
					value={this.props.titleValue}
					onChange={this.handleTitleChanged}
					disabled={!(isNormalState || stringFilterBeingChanged === "title")}
				/>
			</ItemContainer>

			<ItemContainer>
				<span style={labelStyle}>Promotor</span>
				<TextFilterField
					type="text"
					value={this.props.advisorValue}
					onChange={this.handleAdvisorChanged}
					disabled={!(isNormalState || stringFilterBeingChanged === "advisor")}
				/>
			</ItemContainer>

			<ItemContainer>
			<OnlyMineContainer>
				<OnlyMineCheckbox
					type="checkbox"
					checked={this.props.onlyMine}
					onChange={this.handleOnlyMineChange}
					disabled={!isNormalState}
				/>
				<span style={labelStyle}>Tylko moje</span>
			</OnlyMineContainer>
			</ItemContainer>
		</FiltersContainer>
	}
}
