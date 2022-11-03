import axios from "axios";
import { parse, ParseFn, fromMap, aString, anArrayContaining } from "spicery";
import { ActionContext } from "vuex";

export class Notification {
  constructor(
    public id: string,
    public description: string,
    public issuedOn: string,
    public target: string
  ) {}
}

// Defines a parser that validates and parses Notifications from JSON.
const notifications: ParseFn<Notification> = (x: any) =>
  new Notification(
    fromMap(x, "id", aString),
    fromMap(x, "description", aString),
    fromMap(x, "issued_on", aString),
    fromMap(x, "target", aString)
  );
const notificationsArray = anArrayContaining(notifications);

interface State {
  notifications: Array<Notification>;
}

const state: State = {
  notifications: [],
};

const getters = {};

const mutations = {
  setNotificationsList(state: State, notifications: Array<Notification>) {
    state.notifications = notifications;
  },
};

const actions = {
  async get({ commit }: ActionContext<State, any>) {
    let response = await axios.get("/notifications/get");
    let notifications = parse(notificationsArray)(response.data);
    commit("setNotificationsList", notifications);
  },

  async delete({ commit }: ActionContext<State, any>, id: string) {
    axios.defaults.xsrfCookieName = "csrftoken";
    axios.defaults.xsrfHeaderName = "X-CSRFToken";
    let response = await axios.post("/notifications/delete", {
      uuid: id,
    });
    let notifications = parse(notificationsArray)(response.data);
    commit("setNotificationsList", notifications);
  },

  async deleteAll({ commit }: ActionContext<State, any>) {
    axios.defaults.xsrfCookieName = "csrftoken";
    axios.defaults.xsrfHeaderName = "X-CSRFToken";
    let response = await axios.post("/notifications/delete/all");
    let notifications = parse(notificationsArray)(response.data);
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
