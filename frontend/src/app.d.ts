// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
import type { Session } from 'clerk-sveltekit/server';

declare global {
	namespace App {
		// interface Error {}
		interface Locals {
			session: Session;
		}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};
