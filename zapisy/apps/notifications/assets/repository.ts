import axios from "axios";
import { Notification } from "./models";
import { parseNotificationsArray } from "./parser";

class NotificationRepository {
  constructor() {}

  public async getAll(): Promise<Notification[]> {
    let response = await axios.get("/notifications/get");
    let notifications = parseNotificationsArray(response.data);
    return notifications;
  }

  public async delete(id: string): Promise<Notification[]> {
    axios.defaults.xsrfCookieName = "csrftoken";
    axios.defaults.xsrfHeaderName = "X-CSRFToken";
    let response = await axios.post("/notifications/delete", {
      uuid: id,
    });
    let notifications = parseNotificationsArray(response.data);
    return notifications;
  }

  public async deleteAll(): Promise<Notification[]> {
    axios.defaults.xsrfCookieName = "csrftoken";
    axios.defaults.xsrfHeaderName = "X-CSRFToken";
    let response = await axios.post("/notifications/delete/all");
    let notifications = parseNotificationsArray(response.data);
    return notifications;
  }
}

export default NotificationRepository;
