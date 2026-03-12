# Graph Explanations

## Goal

This file explains every chart currently stored under `modeling/reports/`.

It is meant to help a reader understand:

- what each chart shows
- why the chart exists
- how to read it correctly
- what conclusion can be taken from it

## Who This Is For

- project team members
- instructors and reviewers
- anyone building slides from the EDA output

## Scope

At the moment, the charts in `modeling/reports/` are the midterm EDA charts stored in:

- `modeling/reports/eda/midterm_charts/`

These charts are based on the cleaned `listing_snapshot` dataset and related benchmark summaries.

## Chart List

- `listing_rows_by_city.svg`
- `listing_rows_by_city_and_period.svg`
- `room_type_share.svg`
- `nightly_price_histogram.svg`
- `nightly_price_boxplot.svg`
- `median_price_by_city.svg`
- `median_price_heatmap_city_period.svg`
- `median_price_by_room_type.svg`
- `median_price_by_accommodates_band.svg`
- `neighbourhood_price_extremes.svg`

## 1. `listing_rows_by_city.svg`

### What this chart shows

This chart shows how many listing snapshot rows are available for each city.

### How to read it

- Each bar is one city.
- Taller bars mean more observations in the dataset.
- This is a coverage chart, not a price chart.

### Main message

- Roma has the largest volume of observations.
- Milano is the second largest.
- Firenze, Napoli, and Venezia have smaller but still useful coverage.

### Why it matters

- It shows where the dataset is strongest.
- It helps explain why some later comparisons may be more stable in larger cities.

### Main takeaway

The dataset has strong city-level coverage, especially for Roma and Milano.

## 2. `listing_rows_by_city_and_period.svg`

### What this chart shows

This chart breaks dataset coverage down by both city and seasonal period.

### How to read it

- Cities are grouped on the x-axis.
- Inside each city, there are four bars, one for each period:
  - Early Spring
  - Early Summer
  - Early Autumn
  - Early Winter
- Higher bars mean more listing snapshot rows for that city-period combination.

### Main message

- The data is distributed across multiple cities and multiple seasonal snapshots.
- Coverage is not perfectly equal, but it is balanced enough for seasonal comparison.

### Why it matters

- It supports later analysis of seasonality.
- It shows that the project is not based on a single time snapshot.

### Main takeaway

The dataset supports both cross-city analysis and seasonal benchmarking.

## 3. `room_type_share.svg`

### What this chart shows

This chart shows the share of listings by room type.

### How to read it

- Each horizontal bar is one room type.
- The x-axis shows percentage share of the dataset.
- The total is divided across:
  - Entire home
  - Private room
  - Hotel room
  - Shared room

### Main message

- Entire home dominates the dataset.
- Private room is the second largest segment.
- Hotel room and shared room are very small segments.

### Why it matters

- Room type is an important market segmentation variable.
- Model behavior and benchmark behavior may differ by room type.
- Small categories may be harder to model robustly.

### Main takeaway

The market represented in this dataset is heavily concentrated in entire-home listings.

## 4. `nightly_price_histogram.svg`

### What this chart shows

This chart shows the distribution of nightly prices.

### How to read it

- The x-axis is nightly price.
- The y-axis is the number of listing snapshot rows.
- The chart is clipped at the 99th percentile to make the main distribution readable.

### Main message

- Most listings are concentrated in the lower price ranges.
- The distribution is strongly right-skewed.
- There are relatively few high-price listings, but they stretch far to the right.

### Why it matters

- It shows that price is not normally distributed.
- It explains why median and quantiles are more informative than mean alone.
- It supports using transformations or robust summaries during modeling.

### Main takeaway

Most listings are priced in the low-to-middle range, with a long high-price tail.

## 5. `nightly_price_boxplot.svg`

### What this chart shows

This chart summarizes nightly price using quartiles and whiskers.

### How to read it

- The box represents the interquartile range:
  - Q1 = lower quartile
  - Median = middle line
  - Q3 = upper quartile
- The whiskers show the non-extreme spread.
- The axis is capped at `EUR 400` so the main price structure stays readable.

### Main message

- The core market is concentrated far below the maximum recorded price.
- The median is much lower than the most extreme values.
- A few outliers exist far beyond the main market range.

### Why it matters

- It gives a compact summary of central tendency and spread.
- It makes clear that very large maximum prices should not drive interpretation of the typical market.

### Main takeaway

Typical nightly prices are in the hundreds, while extreme outliers are not representative of the main market.

## 6. `median_price_by_city.svg`

### What this chart shows

This chart compares median nightly price across cities.

### How to read it

- Each bar is one city.
- The height of the bar is the city median nightly price.
- Median is used instead of mean to reduce sensitivity to outliers.

### Main message

- Venezia has the highest median nightly price.
- Firenze and Roma also show relatively high median prices.
- Napoli has the lowest median price among the five cities.

### Why it matters

- It shows that city location is one of the strongest pricing dimensions.
- It supports the idea that a single national benchmark would be misleading.

### Main takeaway

Airbnb price levels differ substantially across cities, so city-specific benchmarking is necessary.

## 7. `median_price_heatmap_city_period.svg`

### What this chart shows

This chart shows median nightly price for each city-period combination.

### How to read it

- Each row is a city.
- Each column is a seasonal period.
- Darker cells indicate higher median prices.
- The number inside each cell is the median nightly price for that city and period.

### Main message

- Seasonality is stronger in Roma, Firenze, and Venezia.
- Milano and Napoli are more stable across periods.
- Price depends on both place and season, not only one of them.

### Why it matters

- It supports the use of seasonal context in the benchmarking logic.
- It shows that a listing should not be compared only by city, but also by timing.

### Main takeaway

Pricing patterns are seasonal in some cities, so time context must be part of the analysis.

## 8. `median_price_by_room_type.svg`

### What this chart shows

This chart compares median nightly price across room types.

### How to read it

- Each bar is a room type.
- The height is the median nightly price for that category.

### Main message

- Entire home and hotel room have the highest median prices.
- Private room is lower.
- Shared room is the lowest-priced segment.

### Why it matters

- Room type clearly affects price positioning.
- Listings should be compared against similar room-type segments.

### Main takeaway

Room type is a strong structural driver of price and should be part of all comparable logic.

## 9. `median_price_by_accommodates_band.svg`

### What this chart shows

This chart compares median nightly price across guest-capacity bands.

### How to read it

- Each bar is a guest-capacity group:
  - 1-2 guests
  - 3-4 guests
  - 5-6 guests
  - 7+ guests
- Higher bars mean higher median nightly price.

### Main message

- Price rises as guest capacity increases.
- Small listings are cheaper on average.
- Large-capacity listings show a much higher median price.

### Why it matters

- Accommodation size is a key structural predictor.
- Listings with different guest capacities should not be benchmarked together without adjustment.

### Main takeaway

Guest capacity is strongly associated with price and must be included in modeling and comparables.

## 10. `neighbourhood_price_extremes.svg`

### What this chart shows

This chart highlights selected high-price and lower-price neighbourhoods with enough listing volume.

### How to read it

- Each bar is one city-neighbourhood combination.
- The bar length shows the neighbourhood median nightly price.
- Lower-priced neighbourhoods appear at one end of the ranking.
- Higher-priced neighbourhoods appear at the other end.

### Main message

- There is strong local variation inside cities.
- Premium neighbourhoods such as Venezia / San Marco and Milano / DUOMO are clearly separated from lower-price areas.
- Local context matters even within the same city.

### Why it matters

- It shows why neighbourhood-level benchmarking is necessary.
- It supports the project goal of comparing listings against local market context, not only city averages.

### Main takeaway

Neighbourhood effects are strong enough that city-level analysis alone is not sufficient.

## How To Use These Charts In Slides

- Use `listing_rows_by_city.svg` and `listing_rows_by_city_and_period.svg` to explain coverage and representativeness.
- Use `room_type_share.svg` to explain dataset composition.
- Use `nightly_price_histogram.svg` and `nightly_price_boxplot.svg` to explain skewness and outliers.
- Use `median_price_by_city.svg` and `median_price_heatmap_city_period.svg` to explain geographic and seasonal pricing patterns.
- Use `median_price_by_room_type.svg`, `median_price_by_accommodates_band.svg`, and `neighbourhood_price_extremes.svg` to explain structural and local market effects.

## Important Reading Notes

- These charts describe the observed listing market, not realized booking outcomes.
- Prices are listing prices, not confirmed transaction prices.
- The charts support benchmarking and explainable price intelligence.
- They do not support claims about occupancy, revenue, or dynamic pricing optimization.

## Where These Charts Come From

- Data source used by the chart pipeline:
  - `data/processed/airbnb/csv/listing_snapshot.csv`
- Chart generator code:
  - `modeling/src/evaluation/eda_chart_generator.py`
- Chart runner:
  - `modeling/src/evaluation/eda_chart_runner.py`
- Chart manifest:
  - `modeling/reports/eda/midterm_charts/midterm_eda_chart_manifest.json`

## Last Update

This document reflects the graphs currently present in `modeling/reports/` at the time of writing.
