import { Notification } from "./models";

enum NotificationEventType {
  UPDATE = "NotificationsUpdate",
}

abstract class NotificationEvent {
  constructor(private type: NotificationEventType) {}

  protected dispatchEvent(eventInit: CustomEventInit) {
    let event = new CustomEvent(this.type, eventInit);
    document.body.dispatchEvent(event);
  }

  protected subscribeToEvent(listener: EventListener) {
    document.body.addEventListener(this.type, listener);
  }
}

export class NotificationsUpdateEvent extends NotificationEvent {
  constructor() {
    super(NotificationEventType.UPDATE);
  }

  public dispatch(notifications: Notification[]) {
    super.dispatchEvent({ detail: { notifications } });
  }

  public subscribe(callback: (notifications: Notification[]) => void) {
    super.subscribeToEvent(((event: CustomEvent) => {
      callback(event.detail.notifications);
    }) as EventListener);
  }
}
