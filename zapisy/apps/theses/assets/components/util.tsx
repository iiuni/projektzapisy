/** @file Miscellaneous component related utilities */

import * as React from "react";
import styled from "styled-components";

const ThesisTitle = styled.span`
	font-style: italic;
`;
/**
 * Format a thesis title in italic font style
 * @param title The title
 * @returns A component that renders the font in italic font
 */
export function formatTitle(title: string) {
	return <ThesisTitle>{title}</ThesisTitle>;
}
