import { isNil } from "lodash";

export class Notification {
  constructor(
    public id: string,
    public description: string,
    public issuedOn: Date,
    public target: string,
    public targetInfo?: TargetInfo
  ) {}
}

export enum TargetInfoType {
  NEWS,
  THESIS,
  COURSE,
}

interface NewsTargetInfo {
  type: TargetInfoType.NEWS;
}

interface ThesisTargetInfo {
  type: TargetInfoType.THESIS;
}

interface CourseTargetInfo {
  type: TargetInfoType.COURSE;
  courseId: string;
}

export type TargetInfo = NewsTargetInfo | ThesisTargetInfo | CourseTargetInfo;

export interface NotificationJson {
  id: string;
  description: string;
  issued_on: string;
  target: string;
  target_info?: TargetInfoJson;
}

interface NewsTargetInfoJson {
  type: "news";
}

interface ThesisTargetInfoJson {
  type: "thesis";
}

interface CourseTargetInfoJson {
  type: "course";
  course_id: string;
}

export type TargetInfoJson =
  | NewsTargetInfoJson
  | ThesisTargetInfoJson
  | CourseTargetInfoJson;

/* Runtime type guards */
export const isJsonNotificationType = (object: any) =>
  !isNil(object.id) &&
  !isNil(object.description) &&
  !isNil(object.issued_on) &&
  !isNil(object.target) &&
  (isNil(object.target_info) || isJsonTargetInfoType(object.target_info));

export const isJsonTargetInfoType = (object: any) =>
  !isNil(object.type) &&
  (object.type == "course" ||
    object.type == "thesis" ||
    object.type == "news") &&
  (object.type != "courses" || !isNil(object.course_id));
