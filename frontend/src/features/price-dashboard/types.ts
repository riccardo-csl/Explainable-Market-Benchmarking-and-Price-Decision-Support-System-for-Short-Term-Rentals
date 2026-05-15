export type ModelMetadata = {
  artifact_version: string;
  bundle_version?: string;
  champion_model_name: string;
  fallback_model_name: string;
  training_date?: string;
  row_count: number;
  available_cities: string[];
  available_periods: string[];
  metrics?: Record<string, unknown>;
};

export type ListingSummary = {
  listing_id: number;
  snapshot_date: string;
  city_name: string;
  period_label: string;
  neighbourhood_name: string;
  room_type: string;
  nightly_price: number;
  accommodates_count: number;
  beds_count: number | null;
  bedrooms_count: number | null;
  bathrooms_count: number | null;
  bathroom_type: string | null;
  host_listing_count: number | null;
  total_reviews: number | null;
  reviews_last_twelve_months: number | null;
  reviews_per_month: number | null;
  rating_score: number | null;
  accuracy_score: number | null;
  cleanliness_score: number | null;
  checkin_score: number | null;
  communication_score: number | null;
  location_score: number | null;
  value_score: number | null;
  latitude: number | null;
  longitude: number | null;
  host_tenure_days: number | null;
  distance_to_city_center_km: number | null;
  distance_to_neighbourhood_center_km: number | null;
  is_superhost: boolean | null;
  season_peak_flag: boolean | null;
  season_shoulder_flag: boolean | null;
  venezia_group_name: string | null;
};

export type ComparableListing = {
  listing_id: number;
  snapshot_date: string;
  city_name: string;
  neighbourhood_name: string;
  room_type: string;
  nightly_price: number;
  distance_km: number;
  similarity_score: number;
  used_city_fallback: boolean;
};

export type ExplanationDriver = {
  feature: string;
  contribution: number;
};

export type LocalExplanation = {
  source_model_name: string;
  top_upward_drivers: ExplanationDriver[];
  top_downward_drivers: ExplanationDriver[];
  comparable_median_price: number;
};

export type PriceDecisionPayload = {
  listing_id: number;
  snapshot_date: string;
  city_name: string;
  period_label: string;
  primary_decision_signal: string;
  decision_policy: string;
  decision_signal_summary: string;
  benchmark_lower_bound: number;
  benchmark_upper_bound: number;
  price_positioning_label: "underpriced" | "aligned" | "overpriced";
  benchmark_source: string;
  estimated_market_price: number;
  model_estimate_lower_bound: number;
  model_estimate_upper_bound: number;
  model_estimate_interval_confidence_level: number | null;
  model_estimate_interval_source: string;
  model_estimate_role: string;
  model_benchmark_agreement_label: "strong" | "medium" | "weak";
  model_benchmark_gap_amount: number;
  model_benchmark_gap_ratio: number;
  model_benchmark_agreement_summary: string;
  champion_model_name: string;
  fallback_model_name: string;
  selected_comparables: ComparableListing[];
  local_explanation: LocalExplanation;
  fallback_used: boolean;
};
