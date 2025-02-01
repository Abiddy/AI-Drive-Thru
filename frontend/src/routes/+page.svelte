<script lang="ts">
  import { Button } from "$lib/components/ui/button";
  import { onMount } from "svelte";
  import { Toaster, toast } from 'svelte-french-toast';
  import { fade, scale } from 'svelte/transition';
  import { flip } from 'svelte/animate';
  import { Beef, MemoryStick, CupSoda } from 'lucide-svelte';
  import SignedIn from 'clerk-sveltekit/client/SignedIn.svelte';
  import SignedOut from 'clerk-sveltekit/client/SignedOut.svelte';
  import { page } from "$app/stores";

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  let orders: Array<{
    id: number;
    items: Array<{ item: string; quantity: number }>;
    total_items: number;
  }> = [];
  
  let userInput = "";
  let loading = false;
  let error = "";
  let userEmail = "";

  console.log({orders});

  $: totalBurgers = orders.reduce((sum, order) => 
    sum + (order.items.find(item => 
      item.item.toLowerCase() === 'burgers' || 
      item.item.toLowerCase() === 'burger'
    )?.quantity || 0), 0);

  $: totalFries = orders.reduce((sum, order) => 
    sum + (order.items.find(item => 
      item.item.toLowerCase() === 'fries' || 
      item.item.toLowerCase() === 'fry'
    )?.quantity || 0), 0);

  $: totalDrinks = orders.reduce((sum, order) => 
    sum + (order.items.find(item => 
      item.item.toLowerCase() === 'drinks' || 
      item.item.toLowerCase() === 'drink'
    )?.quantity || 0), 0);

  // Fetch all orders
  async function fetchOrders() {
    const response = await fetch(`${API_URL}/orders`);
    orders = await response.json();
    console.log({orders});
  }

  // Process user request (new order or cancellation)
  async function handleSubmit() {
    if (!userInput.trim()) return;
    
    loading = true;
    error = "";
    
    try {
      const response = await fetch(`${API_URL}/process-request`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_input: userInput }),
      });
      
      const result = await response.json();
      
      if (!response.ok) {
        throw new Error(result.detail || "Something went wrong");
      }
      
      // Show success toast with the message from backend
      toast.success(result.message, {
        duration: 3000,
        position: 'top-center'
      });
      
      // Clear input and refresh orders
      userInput = "";
      await fetchOrders();
      
    } catch (e) {
      error = "Please enter a menu item (burgers, fries, or drinks) to add your order!";
      // Show error toast
      toast.error("Please enter a menu item (burgers, fries, or drinks) to add your order!", {
        duration: 3000,
        position: 'top-center'
      });
    } finally {
      loading = false;
    }
  }

  // Load orders when component mounts
  onMount(async () => {
    await fetchOrders();
    const { user } = await auth();
    if (user) {
      userEmail = user.primaryEmailAddress?.emailAddress || "";
    }
  });

  async function fetchUserOrders(userId: string) {
    const response = await fetch(`${API_URL}/orders/${userId}`);
    const orders = await response.json();
    return orders;
  }

  // When submitting an order, include the user_id
  async function submitOrder(userId: string, userInput: string) {
    const response = await fetch(`${API_URL}/process-request`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_input: userInput,
        user_id: userId
      })
    });
    // Refresh orders after submission
    if (response.ok) {
      orders = await fetchUserOrders(userId);
    }
  }
</script>

<Toaster />

<SignedIn let:user>
  <div class="mb-8 text-center">
    <h2 class="text-2xl font-semibold tracking-tight">Welcome {user.primaryEmailAddress?.emailAddress}!</h2>
    <p class="text-muted-foreground">Your orders are displayed below</p>
  </div>

  {#await fetchUserOrders(user.id)}
    <p>Loading your orders...</p>
  {:then orders}
    <!-- Your existing stats cards -->
    <div class="grid grid-cols-3 gap-4">
      <!-- Total Burgers -->
      <div class="bg-card p-4 rounded-lg shadow hover:shadow-lg transition-shadow"
           in:scale={{ duration: 300 }} out:fade>
        <div class="flex flex-col items-center">
          <div class="w-12 h-12 mb-2 text-orange-500">
            <Beef size={48} />
          </div>
          <h2 class="text-xl font-semibold mb-2">Total Burgers</h2>
          <p class="text-3xl font-bold" in:scale={{ duration: 300 }}>
            {totalBurgers}
          </p>
        </div>
      </div>

      <!-- Total Fries -->
      <div class="bg-card p-4 rounded-lg shadow hover:shadow-lg transition-shadow"
           in:scale={{ duration: 300 }} out:fade>
        <div class="flex flex-col items-center">
          <div class="w-12 h-12 mb-2 text-yellow-500">
            <MemoryStick size={48} />
          </div>
          <h2 class="text-xl font-semibold mb-2">Total Fries</h2>
          <p class="text-3xl font-bold" in:scale={{ duration: 300 }}>
            {totalFries}
          </p>
        </div>
      </div>

      <!-- Total Drinks -->
      <div class="bg-card p-4 rounded-lg shadow hover:shadow-lg transition-shadow"
           in:scale={{ duration: 300 }} out:fade>
        <div class="flex flex-col items-center">
          <div class="w-12 h-12 mb-2 text-blue-500">
            <CupSoda size={48} />
          </div>
          <h2 class="text-xl font-semibold mb-2">Total Drinks</h2>
          <p class="text-3xl font-bold" in:scale={{ duration: 300 }}>
            {totalDrinks}
          </p>
        </div>
      </div>
    </div>

    <!-- Your order form -->
    <div>
      <h2>Place Order or Cancel</h2>
      <!-- Update your form to use submitOrder(user.id, userInput) -->
    </div>

    <!-- Display orders -->
    <div>
      <h2>Current Orders</h2>
      {#each orders as order}
        <div class="p-4 border rounded-lg mb-4">
          <h3>Order #{order.id}</h3>
          {#each order.items as item}
            <p>{item.quantity}x {item.item}</p>
          {/each}
          <p class="text-muted-foreground">Total Items: {order.total_items}</p>
        </div>
      {/each}
    </div>
  {:catch error}
    <p>Error loading orders: {error.message}</p>
  {/await}
</SignedIn>

<SignedOut>
  <div class="mb-8 text-center">
    <h2 class="text-2xl font-semibold tracking-tight">Welcome to AI Drive-Thru</h2>
    <p class="text-muted-foreground">Sign in to save and track your orders</p>
  </div>
</SignedOut>

<div class="max-w-2xl mx-auto space-y-8">
  
  <!-- Order Stats -->
  <div class="grid grid-cols-3 gap-4">
    <!-- Total Burgers -->
    <div class="bg-card p-4 rounded-lg shadow hover:shadow-lg transition-shadow"
         in:scale={{ duration: 300 }} out:fade>
      <div class="flex flex-col items-center">
        <div class="w-12 h-12 mb-2 text-orange-500">
          <Beef size={48} />
        </div>
        <h2 class="text-xl font-semibold mb-2">Total Burgers</h2>
        <p class="text-3xl font-bold" in:scale={{ duration: 300 }}>
          {totalBurgers}
        </p>
      </div>
    </div>

    <!-- Total Fries -->
    <div class="bg-card p-4 rounded-lg shadow hover:shadow-lg transition-shadow"
         in:scale={{ duration: 300 }} out:fade>
      <div class="flex flex-col items-center">
        <div class="w-12 h-12 mb-2 text-yellow-500">
          <MemoryStick size={48} />
        </div>
        <h2 class="text-xl font-semibold mb-2">Total Fries</h2>
        <p class="text-3xl font-bold" in:scale={{ duration: 300 }}>
          {totalFries}
        </p>
      </div>
    </div>

    <!-- Total Drinks -->
    <div class="bg-card p-4 rounded-lg shadow hover:shadow-lg transition-shadow"
         in:scale={{ duration: 300 }} out:fade>
      <div class="flex flex-col items-center">
        <div class="w-12 h-12 mb-2 text-blue-500">
          <CupSoda size={48} />
        </div>
        <h2 class="text-xl font-semibold mb-2">Total Drinks</h2>
        <p class="text-3xl font-bold" in:scale={{ duration: 300 }}>
          {totalDrinks}
        </p>
      </div>
    </div>
  </div>

  <!-- Order Input -->
  <div class="space-y-4">
    <h2 class="text-xl font-semibold">Place Order or Cancel</h2>
    <div class="flex gap-2">
      <input
        type="text"
        bind:value={userInput}
        placeholder="Order burgers, fries, or drinks..."
        class="flex-1 p-2 border rounded"
        on:keydown={(e) => e.key === "Enter" && handleSubmit()}
      />
      <Button on:click={handleSubmit} disabled={loading}>
        {loading ? "Processing..." : "Submit"}
      </Button>
    </div>
    {#if error}
      <p class="text-red-500">Please enter a menu item (burgers, fries, or drinks) to add your order!</p>
    {/if}
  </div>

  <!-- Orders List -->
  <div>
    <h2 class="text-xl font-semibold mb-4">Current Orders</h2>
    {#if orders.length === 0}
      <p class="text-muted-foreground">No orders yet</p>
    {:else}
      <div class="space-y-4">
        {#each orders as order (order.id)}
          <div class="bg-card p-4 rounded-lg shadow"
               in:fade={{ duration: 300 }}
               animate:flip={{ duration: 300 }}>
            <h3 class="font-semibold">Order #{order.id}</h3>
            <ul class="mt-2">
              {#each order.items as item}
                <li>{item.quantity}x {item.item}</li>
              {/each}
            </ul>
            <p class="mt-2 text-sm text-muted-foreground">
              Total Items: {order.total_items}
            </p>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>
