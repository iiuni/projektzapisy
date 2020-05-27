import moment from "moment";

export interface Term {
  width: string;
  occupied: boolean;
}

export interface Classroom {
  label: String;
  type: String;
  capacity: Number;
  id: Number;
  termsLayer: Term[];
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

export function calculateLength(
  startTime: string,
  endTime: string
) {
  let momentStartTime = moment(startTime, "HH:mm");
  let momentEndTime = moment(endTime, "HH:mm");

  var duration = moment
    .duration(momentEndTime.diff(momentStartTime))
    .asHours();

  return String((duration / 14) * 100) + "%";
}
