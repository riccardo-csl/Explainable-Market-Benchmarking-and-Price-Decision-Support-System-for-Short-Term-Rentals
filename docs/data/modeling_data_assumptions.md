# Modeling Data Assumptions

This document records the data assumptions that Goal 2 must respect.

It exists to prevent the modeling layer from silently expanding the project beyond what the available data can support.

## What These Data Support

The current data foundation supports:

- market benchmarking
- price estimation
- comparable listing analysis
- city-level and neighbourhood-level contextual comparison
- explainable pricing intelligence

## What These Data Do Not Support

The current data foundation does not support:

- true occupancy modeling
- realized revenue modeling
- booking conversion modeling
- price elasticity estimation
- lead-time modeling
- daily dynamic pricing validation
- true revenue management claims

## Listing-Level Assumptions

- `listing_snapshot` is a market snapshot table, not a transaction table
- `nightly_price` is an observed listing price, not realized booked revenue
- `snapshot_date` is the scrape date, not a booked stay date

## Grouped Dataset Assumptions

- `city_period_summary` and `neighbourhood_period_summary` are benchmark context tables
- they should not be treated as substitutes for listing-level evidence
- they should not be used in ways that create circular price targets or leakage

## Location Assumptions

- `city_name` and `period_label` are canonical and should be treated as stable interfaces
- `neighbourhood_name` is the main local join label across cleaned datasets
- `neighbourhood_group_name` is not a universal market feature
- in practice, `neighbourhood_group_name` is meaningful mainly for Venezia and should be handled conditionally

## Validation Assumptions

- the cleaned layer has been structurally validated
- validation means schema, keys, required fields, and a few critical semantic constraints were checked
- validation does not imply that the data are complete enough for unsupported economic claims

## Recommended Modeling Boundary

Goal 2 should stay inside this boundary:

- estimate market-aligned listing price levels
- compare listings against city and neighbourhood benchmarks
- explain the main drivers of estimated market price

Goal 2 should not reframe itself as a revenue management system unless new supporting datasets are added.
