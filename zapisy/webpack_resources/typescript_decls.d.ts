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
