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

  console.log(isFree);
  return isFree;
}

export function calculateLength(
  startTime: string,
  endTime: string
) {
  let hS = Number(startTime.substr(0, 2));
  let mS = Number(startTime.substr(3, 5));
  let hE = Number(endTime.substr(0, 2));
  let mE = Number(endTime.substr(3, 5));

  let hD = hE - hS;
  let mD = mE - mS < 0 ? 60 + mE - mS : mE - mS;
  hD = mE - mS < 0 ? hD - 1 : hD;

  return String(((hD + mD / 60) / 14) * 100) + "%";
}
