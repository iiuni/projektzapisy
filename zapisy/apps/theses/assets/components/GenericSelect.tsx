/**
 * @file A generic select component that renders a <select>
 * widget for the specified options and optionally a label
 */
import * as React from "react";

/**
 * The format in which users are required to supply select options
 */
type SelectOptionsInfo<T> = Array<{
	val: T;
	displayName: string;
}>;

type Props<T> = {
	value: T;
	onChange: (val: T) => void;
	/** The options to be displayed in the <select> */
	optionInfo: SelectOptionsInfo<T>;
	/** Optional label, will be displayed to the left by default */
	label?: string;
	/** Optional styles */
	inputCss?: React.CSSProperties;
	labelCss?: React.CSSProperties;
	enabled?: boolean;
	/** If specified, those values will be disabled in the select box */
	disabledValues?: T[];
};

/**
 * A wrapper around the HTML select component with a convenient API
 * and an optional label
 */
export class GenericSelect<T> extends React.PureComponent<Props<T>> {
	public render() {
		const shouldDisable = typeof this.props.enabled === "boolean" ? !this.props.enabled : false;
		const styles: React.CSSProperties = {};
		if (shouldDisable) {
			Object.assign(styles, { backgroundColor: "lightgray" });
		}
		if (this.props.label) {
			Object.assign(styles, { marginLeft: "5px" });
		}
		if (this.props.inputCss) {
			Object.assign(styles, this.props.inputCss);
		}
		const key = Math.random();
		const disabledVals = this.props.disabledValues || [];
		return <div>
				<span style={this.props.labelCss || {}}>{this.props.label || ""}</span>
				<select
					onChange={ev => this.onChange(ev.target.value)}
					value={String(this.getCurrentSelectValue())}
					style={styles}
					disabled={shouldDisable}
				>
				{
					this.props.optionInfo.map((info, i) => (
						<option
							key={`select_${key}_${i}`}
							value={String(info.val)}
							disabled={disabledVals.includes(info.val)}
						>
							{info.displayName}
						</option>
					))
				}
				</select>
		</div>;
	}

	private getCurrentSelectValue() {
		return this.props.optionInfo.find(info => info.val === this.props.value)!.val;
	}

	private onChange = (newValue: string) => {
		const convertedValue = this.convertToExternalValue(newValue);
		if (convertedValue !== null) {
			this.props.onChange(convertedValue);
		}
	}

	private convertToExternalValue(stringValue: string): T | null {
		// The HTML select widget will stringify all values passed to it,
		// so we need to perform the reverse conversion here
		for (const info of this.props.optionInfo) {
			if (stringValue === String(info.val)) {
				return info.val;
			}
		}
		return null;
	}
}
