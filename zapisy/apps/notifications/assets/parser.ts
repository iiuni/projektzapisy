import {
  Notification,
  NotificationJson,
  isJsonNotificationType,
} from "./models";

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
