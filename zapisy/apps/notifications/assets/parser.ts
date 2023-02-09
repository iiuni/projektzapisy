import {
  Notification,
  NotificationJson,
  isJsonNotificationType,
  TargetInfo,
  TargetInfoJson,
  isJsonTargetInfoType,
  TargetInfoType,
} from "./models";

function parseTargetInfo(jsonTargetInfo: TargetInfoJson): TargetInfo {
  if (!isJsonTargetInfoType(jsonTargetInfo)) {
    throw new Error(
      "Target info parser: Object doesn't fit the expected type signature."
    );
  }
  switch (jsonTargetInfo.type) {
    case "course":
      return {
        type: TargetInfoType.COURSE,
        courseId: jsonTargetInfo.course_id,
      };
    case "thesis":
      return {
        type: TargetInfoType.THESIS,
      };
    case "news":
      return {
        type: TargetInfoType.NEWS,
      };
  }
}

export function parseNotification(
  jsonNotification: NotificationJson
): Notification {
  if (!isJsonNotificationType(jsonNotification)) {
    throw new Error(
      "Notification parser: Object doesn't fit the expected type signature."
    );
  }
  return {
    id: jsonNotification.id,
    description: jsonNotification.description,
    issuedOn: new Date(jsonNotification.issued_on),
    target: jsonNotification.target,
    targetInfo: jsonNotification.target_info
      ? parseTargetInfo(jsonNotification.target_info)
      : undefined,
  };
}

export function parseNotificationsArray(
  jsonNotifications: Array<NotificationJson>
): Array<Notification> {
  let notifications: Array<Notification> = [];
  for (let jsonNotification of jsonNotifications) {
    notifications.push(parseNotification(jsonNotification));
  }
  return notifications;
}
