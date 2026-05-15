"use client";

import {
  AlertTriangle,
  ArrowDown,
  ArrowUp,
  BarChart3,
  Bath,
  BedDouble,
  Database,
  Home,
  Info,
  RefreshCcw,
  Search,
  TrendingUp,
  MapPin,
  Calendar,
  ChevronDown,
  ChevronUp,
  Navigation,
  Star,
  Users
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import type { KeyboardEvent } from "react";

import { fetchListings, fetchModelMetadata, fetchPriceDecision } from "./api_client";
import { formatCurrency, formatLabel, formatNumber, listingKey } from "./formatters";
import type { ListingSummary, ModelMetadata, PriceDecisionPayload } from "./types";

type LoadState = "loading" | "ready" | "empty" | "error";

export function PriceDashboard() {
  const [metadata, setMetadata] = useState<ModelMetadata | null>(null);
  const [listings, setListings] = useState<ListingSummary[]>([]);
  const [decision, setDecision] = useState<PriceDecisionPayload | null>(null);
  const [cityName, setCityName] = useState("");
  const [periodLabel, setPeriodLabel] = useState("");
  const [selectedKey, setSelectedKey] = useState("");
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [decisionLoading, setDecisionLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const skipNextFilterFetchRef = useRef(true);

  useEffect(() => {
    const controller = new AbortController();
    setLoadState("loading");
    setErrorMessage("");
    Promise.all([
      fetchModelMetadata(controller.signal),
      fetchListings({ limit: 25 }, controller.signal)
    ])
      .then(([nextMetadata, nextListings]) => {
        setMetadata(nextMetadata);
        setListings(nextListings);
        setSelectedKey(nextListings[0] ? listingKey(nextListings[0]) : "");
        setLoadState(nextListings.length > 0 ? "ready" : "empty");
      })
      .catch((error: unknown) => {
        if (!controller.signal.aborted) {
          setErrorMessage(error instanceof Error ? error.message : "Unable to load dashboard data.");
          setLoadState("error");
        }
      });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    if (!metadata) return;
    if (skipNextFilterFetchRef.current) {
      skipNextFilterFetchRef.current = false;
      return;
    }
    const controller = new AbortController();
    setLoadState("loading");
    setErrorMessage("");
    fetchListings(
      {
        city_name: cityName || undefined,
        period_label: periodLabel || undefined,
        limit: 25
      },
      controller.signal
    )
      .then((nextListings) => {
        setListings(nextListings);
        setSelectedKey(nextListings[0] ? listingKey(nextListings[0]) : "");
        setDecision(null);
        setLoadState(nextListings.length > 0 ? "ready" : "empty");
      })
      .catch((error: unknown) => {
        if (!controller.signal.aborted) {
          setErrorMessage(error instanceof Error ? error.message : "Unable to refresh listings.");
          setLoadState("error");
        }
      });
    return () => controller.abort();
  }, [cityName, metadata, periodLabel]);

  const selectedListing = useMemo(
    () => listings.find((listing) => listingKey(listing) === selectedKey) ?? null,
    [listings, selectedKey]
  );

  useEffect(() => {
    if (!selectedListing) return;
    const controller = new AbortController();
    setDecisionLoading(true);
    fetchPriceDecision(selectedListing, controller.signal)
      .then(setDecision)
      .catch((error: unknown) => {
        if (!controller.signal.aborted) {
          setErrorMessage(error instanceof Error ? error.message : "Unable to load price decision.");
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setDecisionLoading(false);
        }
      });
    return () => controller.abort();
  }, [selectedListing]);

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900 p-4 md:p-8 font-sans selection:bg-teal-100 selection:text-teal-900">
      <header className="max-w-[1440px] mx-auto flex flex-col lg:flex-row lg:items-end justify-between gap-6 mb-8">
        <div className="space-y-2">
          <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-slate-900">
            Price Decision <span className="text-teal-600">Dashboard</span>
          </h1>
          <p className="text-slate-500 max-w-2xl leading-relaxed">
            Existing Goal 2 listings benchmark evaluation. The benchmark range acts as the primary decision signal, supported by model estimates.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3" aria-label="Model metadata summary">
          <Badge icon={Database} label={metadata ? metadata.artifact_version : "loading..."} />
          <Badge icon={TrendingUp} label={metadata ? metadata.champion_model_name : "model..."} />
          <Badge icon={Info} label={metadata ? `${formatNumber(metadata.row_count, 0)} rows` : "rows..."} />
        </div>
      </header>

      {errorMessage && (
        <div className="max-w-[1440px] mx-auto mb-8 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl flex items-center gap-3 shadow-sm" role="alert">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span className="font-medium">{errorMessage}</span>
        </div>
      )}

      <div className="max-w-[1440px] mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        <div className="lg:col-span-5 flex flex-col gap-8">
          <ListingPanel
            metadata={metadata}
            listings={listings}
            loadState={loadState}
            cityName={cityName}
            periodLabel={periodLabel}
            selectedKey={selectedKey}
            onCityChange={setCityName}
            onPeriodChange={setPeriodLabel}
            onSelectListing={setSelectedKey}
          />
        </div>
        
        <div className="lg:col-span-7 flex flex-col gap-8">
          <MarketPositioningPanel decision={decision} loading={decisionLoading} selectedListing={selectedListing} />
          <PropertyDetailsPanel listing={selectedListing} />
          <MarketEvidencePanel decision={decision} />
          <AISupportingAnalysisPanel decision={decision} />
          <TechnicalDetailsPanel decision={decision} />
        </div>
      </div>
    </main>
  );
}

function Badge({ icon: Icon, label }: { icon: React.ElementType; label: string }) {
  return (
    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-xs font-semibold text-slate-600 shadow-sm whitespace-nowrap">
      <Icon className="w-4 h-4 text-slate-400" />
      {label}
    </div>
  );
}

function ListingPanel({
  metadata,
  listings,
  loadState,
  cityName,
  periodLabel,
  selectedKey,
  onCityChange,
  onPeriodChange,
  onSelectListing
}: {
  metadata: ModelMetadata | null;
  listings: ListingSummary[];
  loadState: LoadState;
  cityName: string;
  periodLabel: string;
  selectedKey: string;
  onCityChange: (value: string) => void;
  onPeriodChange: (value: string) => void;
  onSelectListing: (value: string) => void;
}) {
  return (
    <section className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden flex flex-col min-h-[500px]" aria-label="Listing selector">
      <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
        <h2 className="text-base font-semibold text-slate-800 flex items-center gap-2">
          <Search className="w-4 h-4 text-slate-400" />
          Listing Directory
        </h2>
      </div>
      
      <div className="p-5 border-b border-slate-100 grid grid-cols-1 sm:grid-cols-2 gap-4 bg-white">
        <div className="space-y-1.5">
          <label htmlFor="city-filter" className="text-xs font-medium text-slate-500 uppercase tracking-wider flex items-center gap-1">
            <MapPin className="w-3 h-3" /> City
          </label>
          <div className="relative">
            <select
              id="city-filter"
              value={cityName}
              onChange={(e) => onCityChange(e.target.value)}
              className="w-full appearance-none bg-slate-50 border border-slate-200 text-slate-700 text-sm rounded-lg focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 pl-3 pr-8 py-2.5 outline-none transition-all cursor-pointer font-medium"
            >
              <option value="">All locations</option>
              {(metadata?.available_cities ?? []).map((city) => (
                <option key={city} value={city}>{city}</option>
              ))}
            </select>
            <ArrowDown className="w-4 h-4 text-slate-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>
        </div>
        
        <div className="space-y-1.5">
          <label htmlFor="period-filter" className="text-xs font-medium text-slate-500 uppercase tracking-wider flex items-center gap-1">
            <Calendar className="w-3 h-3" /> Period
          </label>
          <div className="relative">
            <select
              id="period-filter"
              value={periodLabel}
              onChange={(e) => onPeriodChange(e.target.value)}
              className="w-full appearance-none bg-slate-50 border border-slate-200 text-slate-700 text-sm rounded-lg focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 pl-3 pr-8 py-2.5 outline-none transition-all cursor-pointer font-medium"
            >
              <option value="">All periods</option>
              {(metadata?.available_periods ?? []).map((period) => (
                <option key={period} value={period}>{period}</option>
              ))}
            </select>
            <ArrowDown className="w-4 h-4 text-slate-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-auto">
        {loadState === "loading" ? (
          <StatusBlock title="Loading directory" text="Fetching existing listings from the local API..." />
        ) : loadState === "empty" ? (
          <StatusBlock title="No listings found" text="Adjust your location or period filters to find listings." />
        ) : loadState === "error" ? (
          <StatusBlock title="Directory unavailable" text="The local API encountered an error returning the listing set." />
        ) : (
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="sticky top-0 bg-slate-50 border-b border-slate-200 text-slate-500 text-xs uppercase tracking-wider font-semibold z-10">
              <tr>
                <th className="px-5 py-3">Property</th>
                <th className="px-5 py-3">Location</th>
                <th className="px-5 py-3 text-right">Price</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {listings.map((listing) => {
                const key = listingKey(listing);
                const isSelected = selectedKey === key;
                return (
                  <tr
                    key={key}
                    onClick={() => onSelectListing(key)}
                    onKeyDown={(e: KeyboardEvent<HTMLTableRowElement>) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        onSelectListing(key);
                      }
                    }}
                    tabIndex={0}
                    className={`
                      cursor-pointer transition-all outline-none group
                      ${isSelected ? 'bg-teal-50 hover:bg-teal-100/60' : 'hover:bg-slate-50 focus-visible:bg-slate-50'}
                    `}
                  >
                    <td className="px-5 py-4">
                      <div className="font-semibold text-slate-900 group-hover:text-teal-700 transition-colors">
                        #{listing.listing_id}
                      </div>
                      <div className={`text-xs mt-0.5 ${isSelected ? 'text-teal-600/70' : 'text-slate-400'}`}>
                        {listing.snapshot_date}
                      </div>
                    </td>
                    <td className="px-5 py-4">
                      <div className="font-medium text-slate-700">{listing.neighbourhood_name}</div>
                      <div className={`text-xs mt-0.5 ${isSelected ? 'text-teal-600/70' : 'text-slate-500'}`}>
                        {listing.room_type}
                      </div>
                    </td>
                    <td className="px-5 py-4 text-right">
                      <div className="font-bold text-slate-900">{formatCurrency(listing.nightly_price)}</div>
                      <div className="text-xs text-amber-500 font-medium mt-0.5">
                        ★ {formatNumber(listing.rating_score, 2)}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}

function MarketPositioningPanel({
  decision,
  loading,
  selectedListing
}: {
  decision: PriceDecisionPayload | null;
  loading: boolean;
  selectedListing: ListingSummary | null;
}) {
  if (!selectedListing) {
    return (
      <section className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden min-h-[300px] flex items-center justify-center">
        <StatusBlock title="Select a property" text="Choose a listing from the directory to inspect its benchmark." />
      </section>
    );
  }

  if (loading || !decision) {
    return (
      <section className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden min-h-[300px] flex items-center justify-center">
        <StatusBlock title="Analyzing market data" text="Computing benchmark range, comparables, and local explanations..." />
      </section>
    );
  }

  const isUnderpriced = decision.price_positioning_label === "underpriced";
  const isOverpriced = decision.price_positioning_label === "overpriced";
  const positioningColor = isUnderpriced
    ? "bg-blue-100 text-blue-800 border-blue-200"
    : isOverpriced
    ? "bg-rose-100 text-rose-800 border-rose-200"
    : "bg-emerald-100 text-emerald-800 border-emerald-200";

  return (
    <section className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden" aria-label="Price decision">
      <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between">
        <h2 className="text-base font-semibold text-slate-800 flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-teal-600" />
          Market Positioning Evaluation
        </h2>
        <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border uppercase tracking-wide shadow-sm ${positioningColor}`}>
          <RefreshCcw className="w-3 h-3" />
          {decision.price_positioning_label}
        </span>
      </div>
      
      <div className="p-6 md:p-8 bg-gradient-to-br from-slate-50 to-white">
        <p className="text-sm text-slate-600 font-medium leading-relaxed mb-8 max-w-3xl">
          The price of this listing is evaluated against the market benchmark range generated by the closest comparable properties.
        </p>

        <PricingGauge 
          observedPrice={selectedListing.nightly_price} 
          lowerBound={decision.benchmark_lower_bound} 
          upperBound={decision.benchmark_upper_bound} 
        />
      </div>
    </section>
  );
}

function PricingGauge({ observedPrice, lowerBound, upperBound }: { observedPrice: number; lowerBound: number; upperBound: number }) {
  const rangeWidth = upperBound - lowerBound;
  const padding = rangeWidth * 0.5;
  const minScale = Math.max(0, lowerBound - padding);
  const maxScale = Math.max(upperBound + padding, observedPrice + padding);
  
  const totalScale = maxScale - minScale;
  
  const rangeLeftPercent = ((lowerBound - minScale) / totalScale) * 100;
  const rangeWidthPercent = (rangeWidth / totalScale) * 100;
  const observedLeftPercent = Math.max(0, Math.min(100, ((observedPrice - minScale) / totalScale) * 100));

  return (
    <div className="relative pt-12 pb-12 px-4 select-none">
      <div className="h-3 w-full bg-slate-200 rounded-full relative">
        <div 
          className="absolute h-full bg-teal-500/30 border-y border-teal-500/40 rounded-full"
          style={{ left: `${rangeLeftPercent}%`, width: `${rangeWidthPercent}%` }}
        />
        <div className="absolute top-5 text-sm font-bold text-slate-400" style={{ left: `${rangeLeftPercent}%`, transform: 'translateX(-50%)' }}>
          {formatCurrency(lowerBound)}
        </div>
        <div className="absolute top-5 text-sm font-bold text-slate-400" style={{ left: `${rangeLeftPercent + rangeWidthPercent}%`, transform: 'translateX(-50%)' }}>
          {formatCurrency(upperBound)}
        </div>

        <div 
          className="absolute h-7 w-1.5 bg-slate-900 rounded-full top-1/2 -translate-y-1/2 shadow-sm z-10 transition-all duration-500"
          style={{ left: `${observedLeftPercent}%`, transform: 'translate(-50%, -50%)' }}
        >
          <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-3 bg-slate-900 text-white text-xs font-bold py-1.5 px-3 rounded shadow-lg whitespace-nowrap">
            Observed Price: {formatCurrency(observedPrice)}
            <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-slate-900" />
          </div>
        </div>
      </div>
    </div>
  );
}

function PropertyDetailsPanel({ listing }: { listing: ListingSummary | null }) {
  if (!listing) return null;

  return (
    <section className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden" aria-label="Property details">
      <div className="px-6 py-5 border-b border-slate-100 bg-slate-50/50 flex items-center justify-between gap-4">
        <h2 className="text-base font-semibold text-slate-800 flex items-center gap-2">
          <Home className="w-4 h-4 text-teal-600" />
          Property Details
        </h2>
        <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">#{listing.listing_id}</span>
      </div>

      <div className="p-6 md:p-8 space-y-7">
        <div>
          <div className="flex flex-wrap items-start justify-between gap-4 mb-5">
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1.5">Selected Property</p>
              <h3 className="text-xl font-black text-slate-900">{listing.room_type}</h3>
              <p className="text-sm font-medium text-slate-500 mt-1">{listing.neighbourhood_name}, {listing.city_name}</p>
            </div>
            <div className="text-right">
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1.5">Observed Price</p>
              <p className="text-xl font-black text-slate-900">{formatCurrency(listing.nightly_price)}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <DetailMetric icon={Users} label="Guests" value={formatNullableNumber(listing.accommodates_count, 0)} />
            <DetailMetric icon={BedDouble} label="Bedrooms" value={formatNullableNumber(listing.bedrooms_count, 0)} />
            <DetailMetric icon={BedDouble} label="Beds" value={formatNullableNumber(listing.beds_count, 0)} />
            <DetailMetric icon={Bath} label="Bathrooms" value={formatNullableNumber(listing.bathrooms_count, 1)} />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6 border-t border-slate-100">
          <DetailGroup
            title="Structure"
            rows={[
              ["Room type", listing.room_type],
              ["Bathroom type", formatNullableLabel(listing.bathroom_type)],
              ["Floor layout", "Not captured"],
              ["Snapshot", listing.snapshot_date]
            ]}
          />
          <DetailGroup
            title="Position"
            rows={[
              ["City", listing.city_name],
              ["Neighbourhood", listing.neighbourhood_name],
              ["City center", `${formatNullableNumber(listing.distance_to_city_center_km, 2)} km`],
              ["Area center", `${formatNullableNumber(listing.distance_to_neighbourhood_center_km, 2)} km`],
              ["Coordinates", formatCoordinates(listing.latitude, listing.longitude)]
            ]}
          />
          <DetailGroup
            title="Quality & Host"
            rows={[
              ["Rating", formatNullableNumber(listing.rating_score, 2)],
              ["Reviews", formatNullableNumber(listing.total_reviews, 0)],
              ["Last 12 months", formatNullableNumber(listing.reviews_last_twelve_months, 0)],
              ["Reviews/month", formatNullableNumber(listing.reviews_per_month, 2)],
              ["Superhost", formatBoolean(listing.is_superhost)],
              ["Host tenure", `${formatNullableNumber(listing.host_tenure_days, 0)} days`]
            ]}
          />
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 pt-6 border-t border-slate-100">
          <ScoreMetric label="Accuracy" value={listing.accuracy_score} />
          <ScoreMetric label="Cleanliness" value={listing.cleanliness_score} />
          <ScoreMetric label="Check-in" value={listing.checkin_score} />
          <ScoreMetric label="Communication" value={listing.communication_score} />
          <ScoreMetric label="Value" value={listing.value_score} />
        </div>
      </div>
    </section>
  );
}

function DetailMetric({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: string }) {
  return (
    <div className="flex items-center gap-3">
      <div className="w-9 h-9 rounded-lg bg-slate-100 flex items-center justify-center">
        <Icon className="w-4 h-4 text-slate-500" />
      </div>
      <div>
        <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">{label}</p>
        <p className="text-base font-black text-slate-900">{value}</p>
      </div>
    </div>
  );
}

function DetailGroup({ title, rows }: { title: string; rows: [string, string][] }) {
  return (
    <div>
      <h3 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
        <Navigation className="w-4 h-4 text-slate-400" />
        {title}
      </h3>
      <dl className="space-y-2.5">
        {rows.map(([label, value]) => (
          <div key={`${title}:${label}`} className="flex items-start justify-between gap-4">
            <dt className="text-xs font-bold text-slate-400 uppercase tracking-widest">{label}</dt>
            <dd className="text-sm font-semibold text-slate-700 text-right">{value}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}

function ScoreMetric({ label, value }: { label: string; value: number | null }) {
  return (
    <div className="flex items-center gap-2">
      <Star className="w-4 h-4 text-amber-400 fill-amber-400" />
      <div>
        <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">{label}</p>
        <p className="text-sm font-black text-slate-900">{formatNullableNumber(value, 2)}</p>
      </div>
    </div>
  );
}

function MarketEvidencePanel({ decision }: { decision: PriceDecisionPayload | null }) {
  if (!decision) return null;
  
  const sortedPrices = [...decision.selected_comparables].map(c => c.nightly_price).sort((a, b) => a - b);
  const medianPrice = sortedPrices.length === 0 ? 0 : sortedPrices.length % 2 === 0 
    ? (sortedPrices[sortedPrices.length / 2 - 1] + sortedPrices[sortedPrices.length / 2]) / 2
    : sortedPrices[Math.floor(sortedPrices.length / 2)];

  return (
    <section className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden" aria-label="Comparable listings">
      <div className="px-6 py-5 border-b border-slate-100 bg-slate-50/50">
        <h2 className="text-base font-semibold text-slate-800">Market Evidence (Comparables)</h2>
      </div>
      <div className="px-6 py-5 md:px-8">
        <p className="text-sm text-slate-600 font-medium">
          This evaluation is based on {decision.selected_comparables.length} similar listings in the area:
        </p>
      </div>
      <div className="overflow-x-auto border-t border-slate-100">
        <table className="w-full text-left text-sm whitespace-nowrap">
          <thead className="bg-white border-b border-slate-100 text-slate-400 text-xs uppercase tracking-wider font-semibold">
            <tr>
              <th className="px-6 py-4">Listing ID</th>
              <th className="px-6 py-4">Type</th>
              <th className="px-6 py-4 text-right">Distance</th>
              <th className="px-6 py-4 text-right">Similarity</th>
              <th className="px-6 py-4 text-right">Nightly Price</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {decision.selected_comparables.map((comparable) => (
              <tr key={`${comparable.listing_id}:${comparable.snapshot_date}`} className="hover:bg-slate-50/80 transition-colors">
                <td className="px-6 py-3.5 font-medium text-slate-700">#{comparable.listing_id}</td>
                <td className="px-6 py-3.5">
                  <div className="text-slate-800 font-medium">{comparable.room_type}</div>
                </td>
                <td className="px-6 py-3.5 text-right text-slate-600">{formatNumber(comparable.distance_km, 2)} km</td>
                <td className="px-6 py-3.5 text-right">
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-700">
                    {formatNumber(comparable.similarity_score, 2)}
                  </span>
                </td>
                <td className="px-6 py-3.5 text-right font-bold text-slate-900">{formatCurrency(comparable.nightly_price)}</td>
              </tr>
            ))}
            {decision.selected_comparables.length > 0 && (
              <tr className="bg-slate-50/80">
                <td colSpan={4} className="px-6 py-4 text-right font-bold text-slate-500 uppercase tracking-widest text-xs">
                  Median Market Price
                </td>
                <td className="px-6 py-4 text-right font-black text-teal-700 text-base">
                  {formatCurrency(medianPrice)}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function AISupportingAnalysisPanel({ decision }: { decision: PriceDecisionPayload | null }) {
  if (!decision) return null;
  const agreementTone = modelAgreementTone(decision.model_benchmark_agreement_label);

  return (
    <section className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden" aria-label="Local explanation drivers">
      <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
        <h2 className="text-base font-semibold text-slate-800">AI Supporting Analysis</h2>
      </div>
      <div className="p-6 md:p-8 border-b border-slate-100 bg-white">
        <p className="text-sm text-slate-600 font-medium leading-relaxed mb-6 max-w-3xl">
          The artificial intelligence estimates a theoretical value based on property characteristics. 
          This is a supporting signal, not a final price recommendation.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)] gap-4">
          <div className="flex flex-wrap items-baseline gap-3 px-5 py-4 rounded-xl bg-slate-50 border border-slate-200">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">AI Estimate</span>
            <span className="text-2xl font-black text-slate-900">{formatCurrency(decision.estimated_market_price)}</span>
            <span className="text-xs font-bold text-teal-700 bg-teal-50 px-2.5 py-1 rounded-md shadow-sm border border-teal-100 uppercase tracking-wide">
              {formatLabel(decision.model_estimate_role)}
            </span>
            <div className="basis-full flex flex-wrap items-center gap-2 pt-1">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">Estimate Range</span>
              <span className="text-sm font-bold text-slate-800">
                {formatCurrency(decision.model_estimate_lower_bound)} - {formatCurrency(decision.model_estimate_upper_bound)}
              </span>
            </div>
          </div>
          <div className="flex flex-col justify-center gap-2 px-5 py-4 rounded-xl bg-slate-50 border border-slate-200">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">Benchmark Agreement</span>
              <span className={`text-xs font-bold px-2.5 py-1 rounded-md border uppercase tracking-wide ${agreementTone}`}>
                {formatLabel(decision.model_benchmark_agreement_label)}
              </span>
            </div>
            <p className="text-sm font-medium leading-relaxed text-slate-600">
              {decision.model_benchmark_agreement_summary}
            </p>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-px bg-slate-100">
        <div className="bg-white p-6 md:p-8">
          <DriverList direction="up" drivers={decision.local_explanation.top_upward_drivers} />
        </div>
        <div className="bg-white p-6 md:p-8">
          <DriverList direction="down" drivers={decision.local_explanation.top_downward_drivers} />
        </div>
      </div>
    </section>
  );
}

function DriverList({
  direction,
  drivers
}: {
  direction: "up" | "down";
  drivers: { feature: string; contribution: number }[];
}) {
  const isUp = direction === "up";
  const Icon = isUp ? ArrowUp : ArrowDown;
  const colorClass = isUp ? "text-emerald-600 bg-emerald-50" : "text-rose-600 bg-rose-50";
  
  return (
    <div>
      <div className="flex items-center gap-2 mb-5">
        <div className={`p-1.5 rounded-md ${colorClass}`}>
          <Icon className="w-4 h-4" />
        </div>
        <h3 className="font-bold text-slate-800">{isUp ? "Positive Value Factors" : "Negative Value Factors"}</h3>
      </div>
      
      <ul className="space-y-3">
        {drivers.length === 0 ? (
          <li className="text-sm text-slate-400 font-medium italic">No factors reported</li>
        ) : (
          drivers.map((driver) => (
            <li className="flex items-center justify-between group" key={`${direction}:${driver.feature}`}>
              <span className="text-sm text-slate-600 font-medium group-hover:text-slate-900 transition-colors capitalize">
                {formatLabel(driver.feature)}
              </span>
              <span className="text-sm font-bold text-slate-900 bg-slate-50 px-2.5 py-1 rounded border border-slate-100">
                {isUp ? "+" : ""}{formatCurrency(driver.contribution)}
              </span>
            </li>
          ))
        )}
      </ul>
    </div>
  );
}

function TechnicalDetailsPanel({ decision }: { decision: PriceDecisionPayload | null }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!decision) return null;

  return (
    <section className="bg-transparent rounded-2xl overflow-hidden mt-2 transition-all">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between py-4 px-6 bg-slate-200/50 hover:bg-slate-200/80 text-slate-700 font-semibold text-sm rounded-xl transition-colors border border-slate-200"
      >
        View Technical Details & Fallbacks
        {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {isOpen && (
        <div className="p-6 mt-3 grid grid-cols-2 md:grid-cols-6 gap-4 bg-white rounded-xl border border-slate-200 shadow-sm">
          <MetricCard label="Benchmark Source" value={formatLabel(decision.benchmark_source)} />
          <MetricCard label="Model Agreement" value={formatLabel(decision.model_benchmark_agreement_label)} />
          <MetricCard label="Interval Source" value={formatLabel(decision.model_estimate_interval_source)} />
          <MetricCard label="Fallback Used" value={decision.fallback_used ? "Yes" : "No"} />
          <MetricCard label="Champion Model" value={decision.champion_model_name} />
          <MetricCard label="Fallback Model" value={decision.fallback_model_name} />
        </div>
      )}
    </section>
  );
}

function modelAgreementTone(label: PriceDecisionPayload["model_benchmark_agreement_label"]): string {
  if (label === "strong") return "text-emerald-700 bg-emerald-50 border-emerald-100";
  if (label === "medium") return "text-amber-700 bg-amber-50 border-amber-100";
  return "text-rose-700 bg-rose-50 border-rose-100";
}

function formatNullableNumber(value: number | null | undefined, digits = 1): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "n/a";
  return formatNumber(value, digits);
}

function formatNullableLabel(value: string | null | undefined): string {
  if (!value) return "n/a";
  return formatLabel(value);
}

function formatBoolean(value: boolean | null | undefined): string {
  if (value === null || value === undefined) return "n/a";
  return value ? "Yes" : "No";
}

function formatCoordinates(latitude: number | null | undefined, longitude: number | null | undefined): string {
  if (latitude === null || latitude === undefined || longitude === null || longitude === undefined) return "n/a";
  return `${formatNumber(latitude, 5)}, ${formatNumber(longitude, 5)}`;
}

function MetricCard({ label, value, highlight = false, className = "" }: { label: string; value: string; highlight?: boolean; className?: string }) {
  return (
    <div className={`flex flex-col justify-center ${className}`}>
      <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1.5">{label}</p>
      <p className={`font-semibold ${highlight ? 'text-xl text-slate-900' : 'text-sm text-slate-700'}`}>
        {value}
      </p>
    </div>
  );
}

function StatusBlock({ title, text }: { title: string; text: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center h-full w-full opacity-80" role="status">
      <div className="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mb-4">
        <Info className="w-6 h-6 text-slate-400" />
      </div>
      <strong className="text-slate-800 font-semibold text-base mb-1.5">{title}</strong>
      <span className="text-slate-500 text-sm max-w-[250px] leading-relaxed">{text}</span>
    </div>
  );
}
