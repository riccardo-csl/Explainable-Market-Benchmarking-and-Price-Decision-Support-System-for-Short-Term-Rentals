import { describe, expect, it } from "vitest";

import { formatCurrency, formatLabel, formatNumber, listingKey } from "../src/features/price-dashboard/formatters";

describe("price dashboard formatters", () => {
  it("formats benchmark currency without false precision", () => {
    expect(formatCurrency(112.26)).toBe("€112");
    expect(formatCurrency(null)).toBe("n/a");
  });

  it("formats compact numbers and labels", () => {
    expect(formatNumber(10.872, 2)).toBe("10.87");
    expect(formatLabel("benchmark_led_positioning")).toBe("benchmark led positioning");
  });

  it("builds stable listing keys", () => {
    expect(listingKey({ listing_id: 19965, snapshot_date: "2024-03-15" })).toBe("19965:2024-03-15");
  });
});
