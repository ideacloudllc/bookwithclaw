export interface Room {
  id: string;
  name: string;
  type: string;
  current_price: number;
  base_price: number;
  floor_price: number;
  ceiling_price?: number;
  occupancy: number;
  max_occupancy: number;
  availability_dates: string[];
}

export interface Offer {
  id: string;
  guest_budget: number;
  dates: {
    check_in: string;
    check_out: string;
  };
  room_type: string;
  status: 'pending' | 'negotiating' | 'accepted' | 'rejected';
  occupancy: number;
}

export interface Booking {
  id: string;
  guest_name?: string;
  room?: string;
  room_name?: string;
  room_id?: string;
  check_in?: string;
  checkin_date?: string;
  check_out?: string;
  checkout_date?: string;
  rate?: number;
  agreed_price?: number;
  final_price?: number;
  status?: string;
}

export interface SellerProfile {
  id: string;
  email: string;
  hotel_name: string;
  address?: string;
  phone?: string;
  check_in_time?: string;
  check_out_time?: string;
  stripe_status?: string;
  stripe_connect_id?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type?: string;
}

export interface DashboardStats {
  active_listings: number;
  pending_offers: number;
  total_revenue_month: number;
  occupancy_rate?: number;
}
