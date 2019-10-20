import { observable } from "mobx";
import { ApplicationState, ThesisWorkMode } from "../app_types";

class C {
	@observable public applicationState = ApplicationState.FirstLoad;
	/** Work state: just viewing, modifying an existing one or adding a new one */
	@observable public workMode = ThesisWorkMode.Viewing;

	/**
	 * Determine whether the app is currently performing a backend
	 * operation (if so, another one won't be permitted)
	 */
	public isPerformingBackendOp() {
		return this.applicationState !== ApplicationState.Normal;
	}
}

export const AppMode = new C();
