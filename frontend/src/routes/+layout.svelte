<script lang="ts">
	import '../app.css';
	import UserButton from 'clerk-sveltekit/client/UserButton.svelte'
	import SignedIn from 'clerk-sveltekit/client/SignedIn.svelte'
	import SignedOut from 'clerk-sveltekit/client/SignedOut.svelte'
    import { Button } from "$lib/components/ui/button";
</script>

<div class="min-h-screen bg-background">
	<header class="border-b">
		<div class="container flex h-16 items-center px-4">
			<a href="/" class="font-bold">AI Drive-Thru Ordering System</a>
			<nav class="ml-auto flex items-center gap-4">
				<SignedIn>
					<UserButton afterSignOutUrl="/" />
				</SignedIn>
				<SignedOut>
					<div class="flex items-center gap-2">
						<Button variant="ghost" asChild>
							<a href="/sign-in" class="text-sm font-medium">
								Sign in
							</a>
						</Button>
						<Button asChild>
							<a href="/sign-up" class="text-sm font-medium">
								Sign up
							</a>
						</Button>
					</div>
				</SignedOut>
			</nav>
		</div>
	</header>

	<main class="container py-6">
		<slot />
	</main>
</div>
