export interface DefectInfo {
  id: number;
  name: string;
  creation_date: Date;
  last_modification: Date;
  place: string;
  reporter: string;
  state: PossibleStates;
  selected: boolean;
  state_id: 0 | 1 | 2 | 3;
  status_color: string;
}

export type PossibleStates =
  | "Zgłoszona"
  | "Oczekująca"
  | "W realizacji"
  | "Zakończona";

export interface KVDict {
  [key: number]: string;
}