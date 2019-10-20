import * as React from "react";
import styled from "styled-components";

import QuestionMark from "./question-mark.png";
import { ThesisVote } from "../../../protocol";

type Props = {
	value: ThesisVote;
	active: boolean;
};

/** Renders an indicator icon for the given vote value */
export function VoteIndicator(props: Props) {
	const Component = props.active ? Container : DisabledContainer;
	const { contents, color = "" } = paramsForValue(props.value);
	return <Component cssColor={color}>
		<IndicatorWrapper>{contents}</IndicatorWrapper>
	</Component>;
}

function paramsForValue(value: ThesisVote) {
	switch (value) {
		case ThesisVote.None: return { contents: "\u{2B1C}" };
		case ThesisVote.Accepted: return { contents: "\u{2705}", color: "green" };
		case ThesisVote.Rejected:
			return {
				contents: <img src={QuestionMark} width={"12px"} />,
			};
	}
}

const IndicatorWrapper = styled.div`
	display: flex;
	width: 100%;
	height: 100%;
	align-items: center;
    justify-content: center;
`;

type ContainerProps = { cssColor: string };
const Container = styled.span`
	width: 20px;
	display: inline-block;
	color: ${(props: ContainerProps) => props.cssColor};
`;

const DisabledContainer = styled(Container)`
	filter: grayscale(30%) opacity(0.6);
`;
