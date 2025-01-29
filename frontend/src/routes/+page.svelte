<script lang="ts">
  import { Button } from "$lib/components/ui/button";
  import { onMount } from "svelte";
  import toast from 'svelte-french-toast';
  import { fade, scale } from 'svelte/transition';
  import { flip } from 'svelte/animate';

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  let orders: Array<{
    id: number;
    items: Array<{ item: string; quantity: number }>;
    total_items: number;
  }> = [];
  
  let userInput = "";
  let loading = false;
  let error = "";

  // Track previous values for animation
  let prevBurgers = 0;
  let prevFries = 0;
  let prevDrinks = 0;
  
  $: {
    // Trigger animation
    const currentBurgers = orders.reduce((sum, order) => 
      sum + (order.items.find(item => item.item === 'burgers')?.quantity || 0), 0);
    const currentFries = orders.reduce((sum, order) => 
      sum + (order.items.find(item => item.item === 'fries')?.quantity || 0), 0);
    const currentDrinks = orders.reduce((sum, order) => 
      sum + (order.items.find(item => item.item === 'drinks')?.quantity || 0), 0);
    
    if (currentBurgers !== prevBurgers) prevBurgers = currentBurgers;
    if (currentFries !== prevFries) prevFries = currentFries;
    if (currentDrinks !== prevDrinks) prevDrinks = currentDrinks;
  }

  // Fetch all orders
  async function fetchOrders() {
    const response = await fetch(`${API_URL}/orders`);
    orders = await response.json();
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
      error = e.message;
      // Show error toast
      toast.error(e.message, {
        duration: 3000,
        position: 'top-center'
      });
    } finally {
      loading = false;
    }
  }

  // Load orders when component mounts
  onMount(fetchOrders);
</script>

<div class="max-w-2xl mx-auto space-y-8">
  <h1 class="text-3xl font-bold">Drive-thru AI Ordering System</h1>
  
  <!-- Order Stats -->
  <div class="grid grid-cols-3 gap-4">
    <!-- Total Burgers -->
    <div class="bg-card p-4 rounded-lg shadow hover:shadow-lg transition-shadow">
      <div class="flex flex-col items-center">
        <div class="w-12 h-12 mb-2">
          <svg class="w-full h-full text-orange-500" viewBox="0 0 24 24" fill="currentColor">
            <path d="M2 16h20v2a2 2 0 01-2 2H4a2 2 0 01-2-2v-2zm1-9h18a1 1 0 011 1v5H1V8a1 1 0 011-1zm9-3a5 5 0 015 5H7a5 5 0 015-5z"/>
          </svg>
        </div>
        <h2 class="text-xl font-semibold mb-2">Total Burgers</h2>
        <p class="text-3xl font-bold">
          {orders.reduce((sum, order) => 
            sum + (order.items.find(item => item.item === 'burgers')?.quantity || 0), 0)}
        </p>
      </div>
    </div>

    <!-- Total Fries -->
    <div class="bg-card p-4 rounded-lg shadow hover:shadow-lg transition-shadow">
      <div class="flex flex-col items-center">
        <div class="w-12 h-12 mb-2">
          <svg class="w-full h-full text-yellow-500" viewBox="0 0 24 24" fill="currentColor">
            <path d="M17 3a1 1 0 011 1v16a1 1 0 01-1 1H7a1 1 0 01-1-1V4a1 1 0 011-1h10zm-7 3v12h4V6h-4z"/>
          </svg>
        </div>
        <h2 class="text-xl font-semibold mb-2">Total Fries</h2>
        <p class="text-3xl font-bold">
          {orders.reduce((sum, order) => 
            sum + (order.items.find(item => item.item === 'fries')?.quantity || 0), 0)}
        </p>
      </div>
    </div>

    <!-- Total Drinks -->
    <div class="bg-card p-4 rounded-lg shadow hover:shadow-lg transition-shadow">
      <div class="flex flex-col items-center">
        <div class="w-12 h-12 mb-2">
          <svg class="w-full h-full text-blue-500" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 3H5a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2V5a2 2 0 00-2-2zm-8 14h2v-4h4V7h-6v10z"/>
          </svg>
        </div>
        <h2 class="text-xl font-semibold mb-2">Total Drinks</h2>
        <p class="text-3xl font-bold">
          {orders.reduce((sum, order) => 
            sum + (order.items.find(item => item.item === 'drinks')?.quantity || 0), 0)}
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
        placeholder="I would like to order..."
        class="flex-1 p-2 border rounded"
        on:keydown={(e) => e.key === "Enter" && handleSubmit()}
      />
      <Button on:click={handleSubmit} disabled={loading}>
        {loading ? "Processing..." : "Submit"}
      </Button>
    </div>
    {#if error}
      <p class="text-red-500">{error}</p>
    {/if}
  </div>

  <!-- Orders List -->
  <div>
    <h2 class="text-xl font-semibold mb-4">Current Orders</h2>
    {#if orders.length === 0}
      <p class="text-muted-foreground">No orders yet</p>
    {:else}
      <div class="space-y-4">
        {#each orders as order}
          <div class="bg-card p-4 rounded-lg shadow">
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
