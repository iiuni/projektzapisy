import { Notification } from "./models";

enum NotificationEventType {
  UPDATE = "NotificationsUpdate",
}

class NotificationEvent {
  constructor(private type: NotificationEventType) {}

  protected dispatchEvent(eventInit: CustomEventInit) {
    let event = new CustomEvent(this.type, eventInit);
    document.body.dispatchEvent(event);
  }

  public subscribe(callback: EventListener) {
    document.body.addEventListener(this.type, callback);
  }
}

export class NotificationsUpdateEvent extends NotificationEvent {
  constructor() {
    super(NotificationEventType.UPDATE);
  }

  public dispatch(notifications: Notification[]) {
    super.dispatchEvent({ detail: { notifications } });
  }
}
