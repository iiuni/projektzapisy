import dayjs from "dayjs";
import customParseFormat from "dayjs/plugin/customParseFormat";
import duration from "dayjs/plugin/duration";

dayjs.extend(customParseFormat);
dayjs.extend(duration);

// This interface stores all data needed for proper display of term block
// in classroom field. It contains width attribute (as a % of lenght of
// whole day) and occupied attribute which informs how the block should
// be displayed.
export interface TermDisplay {
  width: string;
  occupied: boolean;
}

export interface Classroom {
  label: String;
  type: String;
  capacity: Number;
  id: Number;
  termsLayer: TermDisplay[];
  rawOccupied: { begin: string; end: string }[];
}

export function isFree(
  occupied: { begin: string; end: string }[],
  begin: string,
  end: string
) {
  let isFree = true;
  occupied.forEach((item) => {
    if (
      (begin >= item.begin && begin < item.end) ||
      (end > item.begin && end <= item.end) ||
      (begin <= item.begin && end >= item.end)
    )
      isFree = false;
  });

  return isFree;
}

export function calculateLength(startTime: string, endTime: string) {
  const momentStartTime = dayjs(startTime, "HH:mm");
  const momentEndTime = dayjs(endTime, "HH:mm");
  const duration = dayjs
    .duration(momentEndTime.diff(momentStartTime))
    .asHours();
  return String((duration / 14) * 100) + "%";
}
