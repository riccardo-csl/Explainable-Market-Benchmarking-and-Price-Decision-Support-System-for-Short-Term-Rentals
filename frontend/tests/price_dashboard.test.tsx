import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { PriceDashboard } from "../src/features/price-dashboard/price_dashboard";
import type { ListingSummary, ModelMetadata, PriceDecisionPayload } from "../src/features/price-dashboard/types";

const metadata: ModelMetadata = {
  artifact_version: "goal2_v10_diagnostics",
  champion_model_name: "catboost_challenger",
  fallback_model_name: "linear_baseline",
  row_count: 281105,
  available_cities: ["Roma", "Milano"],
  available_periods: ["Early Spring", "Early Summer"],
  metrics: { linear_baseline: {} }
};

const listings: ListingSummary[] = [
  {
    listing_id: 19965,
    snapshot_date: "2024-03-15",
    city_name: "Roma",
    period_label: "Early Spring",
    neighbourhood_name: "I Centro Storico",
    room_type: "Entire home",
    nightly_price: 157,
    accommodates_count: 4,
    beds_count: 2,
    bedrooms_count: 1,
    bathrooms_count: 1,
    bathroom_type: "private",
    host_listing_count: 2,
    total_reviews: 118,
    reviews_last_twelve_months: 21,
    reviews_per_month: 1.8,
    rating_score: 4.88,
    accuracy_score: 4.9,
    cleanliness_score: 4.8,
    checkin_score: 4.9,
    communication_score: 5,
    location_score: 4.9,
    value_score: 4.7,
    latitude: 41.895,
    longitude: 12.482,
    host_tenure_days: 1400,
    distance_to_city_center_km: 0.6,
    distance_to_neighbourhood_center_km: 0.2,
    is_superhost: true,
    season_peak_flag: false,
    season_shoulder_flag: true,
    venezia_group_name: null
  },
  {
    listing_id: 2737,
    snapshot_date: "2024-03-15",
    city_name: "Roma",
    period_label: "Early Spring",
    neighbourhood_name: "VIII Appia Antica",
    room_type: "Private room",
    nightly_price: 56,
    accommodates_count: 2,
    beds_count: 1,
    bedrooms_count: 1,
    bathrooms_count: 2,
    bathroom_type: "shared",
    host_listing_count: 7,
    total_reviews: 5,
    reviews_last_twelve_months: 0,
    reviews_per_month: 0.04,
    rating_score: 4.7,
    accuracy_score: 4.6,
    cleanliness_score: 4.6,
    checkin_score: 4.8,
    communication_score: 5,
    location_score: 4.4,
    value_score: 4.4,
    latitude: 41.87136,
    longitude: 12.48215,
    host_tenure_days: 5657,
    distance_to_city_center_km: 2.8,
    distance_to_neighbourhood_center_km: 1.08,
    is_superhost: true,
    season_peak_flag: false,
    season_shoulder_flag: true,
    venezia_group_name: null
  }
];

const decision: PriceDecisionPayload = {
  listing_id: 19965,
  snapshot_date: "2024-03-15",
  city_name: "Roma",
  period_label: "Early Spring",
  primary_decision_signal: "benchmark_range",
  decision_policy: "benchmark_led_positioning",
  decision_signal_summary:
    "The benchmark range is the primary decision signal. The model price estimate is retained as a supporting signal.",
  benchmark_lower_bound: 112.2633,
  benchmark_upper_bound: 199.7367,
  price_positioning_label: "aligned",
  benchmark_source: "comparable_mad",
  estimated_market_price: 158.45,
  model_estimate_lower_bound: 131.2,
  model_estimate_upper_bound: 196.8,
  model_estimate_interval_confidence_level: 0.8,
  model_estimate_interval_source: "heldout_residual_quantiles",
  model_estimate_role: "supporting_signal",
  model_benchmark_agreement_label: "strong",
  model_benchmark_gap_amount: 0,
  model_benchmark_gap_ratio: 0,
  model_benchmark_agreement_summary: "Model estimate sits inside the benchmark range.",
  champion_model_name: "catboost_challenger",
  fallback_model_name: "linear_baseline",
  selected_comparables: [
    {
      listing_id: 50766996,
      snapshot_date: "2024-03-15",
      city_name: "Roma",
      neighbourhood_name: "I Centro Storico",
      room_type: "Entire home",
      nightly_price: 155,
      distance_km: 0.158,
      similarity_score: 10.929,
      used_city_fallback: false
    }
  ],
  local_explanation: {
    source_model_name: "linear_baseline",
    top_upward_drivers: [{ feature: "location", contribution: 27.5 }],
    top_downward_drivers: [{ feature: "bathrooms_count", contribution: -18.5 }],
    comparable_median_price: 156
  },
  fallback_used: false
};

describe("PriceDashboard", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn(mockFetch));
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders successful benchmark, comparables, explanations, and metadata states", async () => {
    render(<PriceDashboard />);

    expect(screen.getByRole("heading", { name: /Price Decision Dashboard/i })).toBeInTheDocument();
    expect(await screen.findByText("goal2_v10_diagnostics")).toBeInTheDocument();
    const decisionSection = await screen.findByLabelText("Price decision");
    expect(decisionSection).toHaveTextContent("€112");
    expect(decisionSection).toHaveTextContent("€200");
    const propertyDetails = await screen.findByLabelText("Property details");
    expect(propertyDetails).toHaveTextContent("Entire home");
    expect(propertyDetails).toHaveTextContent("Guests");
    expect(propertyDetails).toHaveTextContent("Bedrooms");
    expect(propertyDetails).toHaveTextContent("Floor layout");
    expect(propertyDetails).toHaveTextContent("Not captured");
    expect(propertyDetails).toHaveTextContent("0.6 km");
    expect(propertyDetails).toHaveTextContent("41.895, 12.482");
    expect(screen.getByText("aligned")).toBeInTheDocument();
    expect(screen.getByText("Market Evidence (Comparables)")).toBeInTheDocument();
    expect(screen.getByText("#50766996")).toBeInTheDocument();
    expect(screen.getByText("location")).toBeInTheDocument();
    expect(screen.getAllByText(/supporting signal/i).length).toBeGreaterThan(0);
    expect(screen.getByText("Estimate Range")).toBeInTheDocument();
    expect(screen.getByText("€131 - €197")).toBeInTheDocument();
    expect(screen.getByText("Benchmark Agreement")).toBeInTheDocument();
    expect(screen.getByText("strong")).toBeInTheDocument();
    expect(screen.getByText("Model estimate sits inside the benchmark range.")).toBeInTheDocument();
  });

  it("opens technical details for model and fallback metadata", async () => {
    const user = userEvent.setup();
    render(<PriceDashboard />);

    await screen.findByText("goal2_v10_diagnostics");
    await user.click(await screen.findByRole("button", { name: /View Technical Details/i }));

    expect(screen.getByText("Benchmark Source")).toBeInTheDocument();
    expect(screen.getByText("comparable mad")).toBeInTheDocument();
    expect(screen.getByText("Model Agreement")).toBeInTheDocument();
    expect(screen.getAllByText("strong").length).toBeGreaterThan(0);
    expect(screen.getByText("Interval Source")).toBeInTheDocument();
    expect(screen.getByText("heldout residual quantiles")).toBeInTheDocument();
    expect(screen.getByText("Champion Model")).toBeInTheDocument();
    expect(screen.getAllByText("catboost_challenger").length).toBeGreaterThan(0);
    expect(screen.getByText("Fallback Model")).toBeInTheDocument();
    expect(screen.getAllByText("linear_baseline").length).toBeGreaterThan(0);
  });

  it("renders empty supporting-factor states", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/api/model/metadata")) return jsonResponse(metadata);
        if (url.includes("/api/listings")) return jsonResponse(listings);
        if (url.includes("/api/price-decisions")) {
          return jsonResponse({
            ...decision,
            local_explanation: {
              ...decision.local_explanation,
              top_upward_drivers: [],
              top_downward_drivers: []
            }
          });
        }
        return Promise.resolve(new Response("Not found", { status: 404 }));
      })
    );

    render(<PriceDashboard />);

    const emptyFactorMessages = await screen.findAllByText("No factors reported");
    expect(emptyFactorMessages).toHaveLength(2);
  });

  it("reloads listings when filters change", async () => {
    const user = userEvent.setup();
    render(<PriceDashboard />);

    await screen.findByText("goal2_v10_diagnostics");
    await user.selectOptions(screen.getByLabelText("City"), "Milano");

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining("/api/listings?city_name=Milano"),
        expect.objectContaining({ signal: expect.any(AbortSignal) })
      );
    });
  });

  it("renders an empty listing state", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/api/model/metadata")) return jsonResponse(metadata);
        if (url.includes("/api/listings")) return jsonResponse([]);
        return jsonResponse(decision);
      })
    );

    render(<PriceDashboard />);

    expect(await screen.findByText("No listings found")).toBeInTheDocument();
  });

  it("renders an API error state", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/api/model/metadata")) return Promise.resolve(new Response("Nope", { status: 500 }));
        return jsonResponse([]);
      })
    );

    render(<PriceDashboard />);

    const alert = await screen.findByRole("alert");
    expect(within(alert).getByText(/status 500/)).toBeInTheDocument();
    expect(screen.getByText("Directory unavailable")).toBeInTheDocument();
  });
});

function mockFetch(input: RequestInfo | URL): Promise<Response> {
  const url = String(input);
  if (url.includes("/api/model/metadata")) return jsonResponse(metadata);
  if (url.includes("/api/listings")) return jsonResponse(listings);
  if (url.includes("/api/price-decisions")) return jsonResponse(decision);
  return Promise.resolve(new Response("Not found", { status: 404 }));
}

function jsonResponse(payload: unknown): Promise<Response> {
  return Promise.resolve(
    new Response(JSON.stringify(payload), {
      status: 200,
      headers: { "Content-Type": "application/json" }
    })
  );
}
