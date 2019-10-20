import { configure, flow } from "mobx";

import { Users } from "./users";
import { List } from "./theses_list";
import { AppMode } from "./app_mode";
import { ApplicationState } from "../app_types";
import { ThesisEditing } from "./editing";

/** Tell MobX to ensure that @observable fields are only modified in actions */
configure({ enforceActions: "observed" });

export const initializeLogic = flow(function*() {
	// initialization order matters
	yield Users.initialize();
	yield List.initialize();
	ThesisEditing.initialize();
	AppMode.applicationState = ApplicationState.Normal;
});
