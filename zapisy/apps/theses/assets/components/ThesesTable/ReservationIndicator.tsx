import * as React from "react";
import { TableCellProps } from "react-virtualized";
import styled from "styled-components";
import { Thesis } from "../../thesis";

const Centered = styled.div`
	text-align: center;
`;

/**
 * A component to display the reservation status in the theses table
 */
export function ReservationIndicator(props: TableCellProps): JSX.Element {
	const thesis: Thesis = props.rowData;
	return <Centered><input
		type={"checkbox"}
		checked={!!thesis.reservedUntil}
		style={{ cursor: "default" }}
		disabled
	/></Centered>;
}
