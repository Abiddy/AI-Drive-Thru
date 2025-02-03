<script lang="ts">
  import { Button } from "$lib/components/ui/button";
  import { Toaster, toast } from 'svelte-french-toast';
  import { fade, scale } from 'svelte/transition';
  import { flip } from 'svelte/animate';
  import { Beef, MemoryStick, CupSoda } from 'lucide-svelte';
  import { writable } from 'svelte/store';
  import SignedIn from 'clerk-sveltekit/client/SignedIn.svelte';
  import SignedOut from 'clerk-sveltekit/client/SignedOut.svelte';

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const ordersStore = writable<Array<{
    id: number;
    items: Array<{ item: string; quantity: number }>;
    total_items: number;
    order_number: number;
  }>>([]);

  const totalsStore = writable({
    burgers: 0,
    fries: 0,
    drinks: 0
  });

  // Subscribe to the store
  $: orders = $ordersStore;  // Reactive declaration

  $: {
  console.log('Server loaded data:', data.initialOrders);
  console.log('Current orders:', orders);
  console.log('Current totals:', $totalsStore);
}
  
  let userInput = "";
  let loading = false;

  // Update totals whenever orders change
// Subscribe to the store and update totals
$: if (orders && orders.length > 0) {
  const newTotals = {
    burgers: orders.reduce((sum, order) => {
      const burgerItem = order.items.find(item => 
        item.item.toLowerCase() === 'burgers');
      return sum + (burgerItem?.quantity || 0);
    }, 0),
    
    fries: orders.reduce((sum, order) => {
      const friesItem = order.items.find(item => 
        item.item.toLowerCase() === 'fries');
      return sum + (friesItem?.quantity || 0);
    }, 0),
    
    drinks: orders.reduce((sum, order) => {
      const drinkItem = order.items.find(item => 
        item.item.toLowerCase() === 'drinks');
      return sum + (drinkItem?.quantity || 0);
    }, 0)
  };
  
  console.log('Setting new totals:', newTotals);
  totalsStore.set(newTotals);
}

export let data;

// Initialize stores with server-loaded data
$: {
  if (data.initialOrders) {
    const ordersData = Array.isArray(data.initialOrders) 
      ? data.initialOrders 
      : data.initialOrders.orders || [];
      
    console.log('Setting initial orders:', ordersData);
    ordersStore.set(ordersData);
    
    // Calculate initial totals immediately
    const initialTotals = {
      burgers: ordersData.reduce((sum, order) => {
        const burgerItem = order.items.find(item => 
          item.item.toLowerCase() === 'burgers');
        return sum + (burgerItem?.quantity || 0);
      }, 0),
      
      fries: ordersData.reduce((sum, order) => {
        const friesItem = order.items.find(item => 
          item.item.toLowerCase() === 'fries');
        return sum + (friesItem?.quantity || 0);
      }, 0),
      
      drinks: ordersData.reduce((sum, order) => {
        const drinkItem = order.items.find(item => 
          item.item.toLowerCase() === 'drinks');
        return sum + (drinkItem?.quantity || 0);
      }, 0)
    };
    
    console.log('Setting initial totals:', initialTotals);
    totalsStore.set(initialTotals);
  }
}


  // API CALL FUNCTIONS FOR SIGNED IN USER
  async function handleSubmit(userId: string) {
    if (!userInput.trim()) return;
    
    loading = true;
    try {
      const response = await fetch(`${API_URL}/process-request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_input: userInput,
          user_id: userId
        })
      });

      if (!response.ok) throw new Error('Failed to process order');
      
      const result = await response.json();
      userInput = "";
      toast.success(result.message);
      
      // Update orders store directly
      const newOrders = await fetchUserOrders(userId);
      ordersStore.update(() => newOrders.orders);
      
    } catch (e) {
      toast.error('Failed to process order');
    } finally {
      loading = false;
    }
  }

  async function fetchUserOrders(userId: string) {
    const response = await fetch(`${API_URL}/orders/${userId}`);
    const orders = await response.json();
    
    
    return { orders };
  }

</script>


<Toaster />

<!-- Signed Out UI -->
<SignedOut>
  {#key $ordersStore}
  <div class="mb-8">
    <h2 class="text-2xl font-semibold tracking-tight text-center">Welcome to AI Drive-Thru</h2>
    <p class="text-muted-foreground mb-10 text-center">Sign in to save and track your orders</p>
  </div>
  {/key}
</SignedOut>

<!-- Signed In UI -->
<SignedIn let:user>
  {#if user}
    <div class="mb-8 text-center">
      <h2 class="text-2xl font-semibold tracking-tight">Welcome {user.primaryEmailAddress?.emailAddress}!</h2>
      <p class="text-muted-foreground">Your orders are displayed below</p>
    </div>

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
              {$totalsStore.burgers}
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
              {$totalsStore.fries}
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
              {$totalsStore.drinks}
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
            on:keydown={(e) => e.key === "Enter" && handleSubmit(user.id)}
          />
          <Button on:click={() => handleSubmit(user.id)} disabled={loading}>
            {loading ? "Processing..." : "Submit"}
          </Button>
        </div>
      </div>

      <!-- Orders List -->
      <div>
        <h2 class="text-xl font-semibold mb-4">Current Orders - {$ordersStore.length}</h2>
        {#if $ordersStore.length === 0}
          <p class="text-muted-foreground">No orders yet</p>
        {:else}
          <div class="space-y-4">
            {#each $ordersStore as order (order.id)}
              <div class="bg-card p-4 rounded-lg shadow"
                   in:fade={{ duration: 300 }}
                   animate:flip={{ duration: 300 }}>
                <h3 class="font-semibold">Order #{order.order_number}</h3>
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
  {/if}
</SignedIn>
