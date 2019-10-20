// Allow importing images through url/file loader
declare module "*.png" {
	const content: string;
	export default content;
}

declare module "*.gif" {
	const content: string;
	export default content;
}

declare module "*.vue" {
	import Vue from "vue";
	export default Vue;
}

declare module "*.ico" {
	const content: string;
	export default content;
}

// later versions of styled-components require @types/nodejs
// for some reason, but I don't want to include those since they
// mess up stuff like setInterval etc
declare namespace NodeJS {
	export interface ReadableStream {

	}
}
