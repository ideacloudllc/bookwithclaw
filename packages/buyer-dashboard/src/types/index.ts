export interface Room {
  id: string;
  hotel_name: string;
  room_type: string;
  price: number;
  occupancy: number;
  check_in: string;
  check_out: string;
  available: boolean;
}

export interface Offer {
  id: string;
  room_id: string;
  hotel_name: string;
  room_type: string;
  offered_price: number;
  check_in: string;
  check_out: string;
  occupancy: number;
  status: 'pending' | 'negotiating' | 'accepted' | 'rejected';
  created_at: string;
}

export interface Negotiation {
  id: string;
  offer_id: string;
  hotel_name: string;
  room_type: string;
  current_price: number;
  round: number;
  last_message: string;
  last_updated: string;
  status: 'active' | 'closed';
}

export interface Booking {
  id: string;
  offer_id: string;
  hotel_name: string;
  room_type: string;
  check_in: string;
  check_out: string;
  occupancy: number;
  final_price: number;
  booking_ref: string;
  status: 'completed' | 'cancelled';
}

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  phone?: string;
  payment_methods?: PaymentMethod[];
}

export interface PaymentMethod {
  id: string;
  type: string;
  last_four: string;
  expiry_date: string;
}

export interface SearchFilters {
  check_in: string;
  check_out: string;
  occupancy: number;
  room_type?: string;
}
