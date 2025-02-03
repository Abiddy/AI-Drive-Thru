import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
  const userId = locals.session?.userId;
  
  if (userId) {
    const API_URL = process.env.VITE_API_URL || 'http://localhost:8000';
    const response = await fetch(`${API_URL}/orders/${userId}`);
    const orders = await response.json();
    
    return {
      userId,
      initialOrders: orders
    };
  }
  
  return {
    userId: null,
    initialOrders: []
  };
}; 