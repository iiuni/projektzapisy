// tslint:disable
// Taken from https://github.com/Elvynia/mousetrap-global-bind
// While the package includes the necessary typings, the typescript compiler
// cannot find them for some reason

interface MousetrapStatic {
	bindGlobal(keyArray: string | string[], callback: (e: ExtendedKeyboardEvent, combo: string) => any, action?: string): void;
	unbindGlobal(keys: string | string[], action?: string): void;
}

interface MousetrapInstance {
	bindGlobal(keyArray: string | string[], callback: (e: ExtendedKeyboardEvent, combo: string) => any, action?: string): void;
	unbindGlobal(keys: string | string[], action?: string): void;
}
