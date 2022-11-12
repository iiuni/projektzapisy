import axios from "axios";
import { ActionContext } from "vuex";
import { Notification } from "../models";
import { parseNotificationsArray } from "../parser";
import { clone } from "lodash";

function truncateDescription(description: string) {
  if (description.length <= 200) return description;
  return description.substr(0, 200) + "...";
}

interface State {
  notifications: Array<Notification>;
}

const state: State = {
  notifications: [],
};

const getters = {
  truncatedNotifications(state: State): Notification[] {
    return state.notifications.map((notification) => {
      let notificationClone = clone(notification);
      notificationClone.description = truncateDescription(
        notification.description
      );
      return notificationClone;
    });
  },
};

const mutations = {
  setNotificationsList(state: State, notifications: Array<Notification>) {
    state.notifications = notifications;
  },
};

const actions = {
  async get({ commit }: ActionContext<State, any>) {
    let response = await axios.get("/notifications/get");
    let notifications = parseNotificationsArray(response.data);
    commit("setNotificationsList", notifications);
  },

  async delete({ commit }: ActionContext<State, any>, id: string) {
    axios.defaults.xsrfCookieName = "csrftoken";
    axios.defaults.xsrfHeaderName = "X-CSRFToken";
    let response = await axios.post("/notifications/delete", {
      uuid: id,
    });
    let notifications = parseNotificationsArray(response.data);
    commit("setNotificationsList", notifications);
  },

  async deleteAll({ commit }: ActionContext<State, any>) {
    axios.defaults.xsrfCookieName = "csrftoken";
    axios.defaults.xsrfHeaderName = "X-CSRFToken";
    let response = await axios.post("/notifications/delete/all");
    let notifications = parseNotificationsArray(response.data);
    commit("setNotificationsList", notifications);
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
