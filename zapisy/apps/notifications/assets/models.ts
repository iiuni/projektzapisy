import { isNil } from "lodash";

export class Notification {
  constructor(
    public id: string,
    public description: string,
    public issuedOn: Date,
    public target: string
  ) {}
}

export interface NotificationJson {
  id: string;
  description: string;
  issued_on: string;
  target: string;
}

/* Runtime type guard for NotifiactionJson */
export const isJsonNotificationType = (object: any) =>
  !isNil(object.id) &&
  !isNil(object.description) &&
  !isNil(object.issued_on) &&
  !isNil(object.target);
