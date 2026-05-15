import type { ListingSummary, ModelMetadata, PriceDecisionPayload } from "./types";

const DEFAULT_API_BASE_URL = "http://localhost:8000";

export function getApiBaseUrl(): string {
  return (process.env.NEXT_PUBLIC_API_BASE_URL || DEFAULT_API_BASE_URL).replace(/\/$/, "");
}

export async function fetchModelMetadata(signal?: AbortSignal): Promise<ModelMetadata> {
  return fetchJson<ModelMetadata>("/api/model/metadata", { signal });
}

export async function fetchListings(
  filters: { city_name?: string; period_label?: string; limit?: number },
  signal?: AbortSignal
): Promise<ListingSummary[]> {
  const params = new URLSearchParams();
  if (filters.city_name) params.set("city_name", filters.city_name);
  if (filters.period_label) params.set("period_label", filters.period_label);
  params.set("limit", String(filters.limit ?? 25));
  return fetchJson<ListingSummary[]>(`/api/listings?${params.toString()}`, { signal });
}

export async function fetchPriceDecision(
  listing: { listing_id: number; snapshot_date: string },
  signal?: AbortSignal
): Promise<PriceDecisionPayload> {
  const params = new URLSearchParams({
    listing_id: String(listing.listing_id),
    snapshot_date: listing.snapshot_date
  });
  return fetchJson<PriceDecisionPayload>(`/api/price-decisions?${params.toString()}`, { signal });
}

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, init);
  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}
