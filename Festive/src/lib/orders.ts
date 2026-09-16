import { addDoc, collection, serverTimestamp } from "firebase/firestore";
import { db, auth } from "./firebase";
import type { CartItem } from "@/lib/CartContext";

export interface OrderCustomer {
  name: string;
  phone: string;
  email: string;
  address: string;
  city: string;
  state: string;
  pincode: string;
}

export interface PlacedOrder {
  id: string | null;
  persisted: boolean;
}

/**
 * Persists an order to Firestore.
 *
 * Returns { persisted: false } when Firebase is not configured (demo mode —
 * the app keeps working with local-only state), mirroring the fallback
 * pattern used by the catalog data layer.
 */
export async function placeOrder(
  items: CartItem[],
  customer: OrderCustomer,
  totals: { subtotal: number; shipping: number; total: number }
): Promise<PlacedOrder> {
  if (!process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID === "mock_project_id") {
    console.warn("[orders] Firebase not configured — order not persisted (demo mode)");
    return { id: null, persisted: false };
  }

  const docRef = await addDoc(collection(db, "orders"), {
    userId: auth.currentUser?.uid ?? null,
    customer,
    items: items.map((i) => ({
      id: i.id,
      name: i.name,
      price: i.price,
      qty: i.qty,
    })),
    ...totals,
    // Payment gateway (Razorpay) is future work — orders are placed without
    // payment capture for now and never claim to be paid.
    status: "placed",
    paymentStatus: "unpaid",
    createdAt: serverTimestamp(),
  });

  return { id: docRef.id, persisted: true };
}
