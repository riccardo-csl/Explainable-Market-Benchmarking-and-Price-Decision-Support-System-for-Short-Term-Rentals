# PROJECT OVERVIEW STATEMENT

## Project Name
Explainable Market Benchmarking and Price Decision-Support System for Short-Term Rentals

## Student Name
Casaula, Bonuccelli, Limongi

## Problem / Opportunity
Short-term rental hosts and property managers often make pricing decisions with only partial visibility into the market around them. In many cases, they can observe competitors informally, but they do not have a structured way to understand whether a property is aligned with similar listings in the same city, neighborhood, season, and market segment. This creates uncertainty in price setting and makes it difficult to justify pricing decisions in a consistent and transparent way.

This project responds to that problem by proposing a data-driven pricing intelligence and decision-support system based on observed Airbnb listing data. Rather than attempting to estimate true occupancy or realized revenue, the system will help users interpret market conditions, compare a listing with similar properties, estimate a market-aligned nightly price, and understand the main factors that influence that estimate.

## Goal
By May 7, 2026, our team will design, develop, and deploy a working prototype of an Explainable Market Benchmarking and Price Decision-Support System for our Property Management SaaS. Using Airbnb listing data for Rome, Milan, Florence, Venice, and Naples, the system will generate benchmark price ranges, identify comparable listings, estimate market-aligned nightly prices, and explain the most important drivers behind those estimates through an intuitive dashboard.

The project will be considered successful if it produces a reproducible analytical dataset, a reliable and interpretable price estimation engine, a comparable-listings benchmarking workflow, and a beta dashboard that can support pricing decisions in a clear and practical way.

## Objectives

### Goal 1: Build the Analytical Data Foundation
The first objective is to prepare a clean and reproducible analytical foundation that supports all later modeling and reporting activities. The project will integrate listing-level Airbnb data with grouped city-level and neighborhood-level summaries for the selected cities, while standardizing variables such as city, neighborhood, room type, guest capacity, host activity, review metrics, coordinates, and price.

This phase will also include a documented preprocessing workflow, quality checks, exclusion rules, and a complete data dictionary so that the analytical pipeline can be reproduced consistently. In addition, the team will explore the construction of geographic micro-markets using neighborhood information and spatial patterns in the coordinates, with the goal of moving beyond broad city-level comparisons and capturing finer local market structure. The intention is not only to prepare data for modeling, but also to ensure that the resulting dataset is interpretable, auditable, and usable inside the SaaS environment.

Timeline: March 20, 2026.

### Goal 2: Develop an Explainable Price Estimation Engine
The second objective is to build a beta estimation engine capable of producing market-aligned nightly price estimates for individual listings based on observed characteristics. The engine will rely on interpretable statistical or machine learning approaches and will be evaluated on held-out data to measure how closely its estimates align with observed listing prices.

This phase will focus not only on predictive performance, but also on interpretability. The modeling workflow will move beyond simple rule-based heuristics by comparing more advanced estimation approaches, such as regularized regression, tree-based models, and other suitable machine learning methods, while preserving explainability and robustness. In practical terms, the system should be able to show why a listing is estimated at a certain price level by highlighting the influence of variables such as location, room type, guest capacity, host profile, review quality, and micro-market context. The purpose is to avoid a black-box output and instead provide an explainable decision-support mechanism that users can trust and inspect.

Timeline: April 10, 2026.

### Goal 3: Build a Comparable Listings and Market Benchmarking Module
The third objective is to extend the pricing engine into a market benchmarking system that identifies comparable listings and places each property within a meaningful market context. Instead of returning only a single estimated price, the system will also generate a benchmark range, identify whether the listing appears underpriced, aligned, or overpriced relative to similar listings, and summarize the local market conditions surrounding that property.

This component will make the system more useful in practice because it will connect model outputs to concrete market evidence. Comparable listings will be selected using relevant observed characteristics such as city, neighborhood, room type, capacity, broader listing profile, and, where possible, micro-market segmentation derived from spatial structure within each city. In this way, the system will support both quantitative estimation and qualitative interpretation of price positioning.

Timeline: April 20, 2026.

### Goal 4: Produce the Beta Module and Dashboard
The fourth objective is to embed the pricing intelligence workflow into a functional beta module for the SaaS platform. The backend will expose market estimates, benchmark ranges, comparable listing results, and feature-based explanations, while the frontend will present those outputs in a clear and navigable dashboard.

The dashboard will be designed to help users answer practical questions such as whether a property is priced above or below comparable listings, how benchmark levels differ across neighborhoods or cities, and how market price levels vary across the available seasonal snapshots. A central requirement of this phase is that the interface should translate analytical outputs into operationally understandable insights rather than simply displaying raw model results.

Timeline: April 30, 2026.

### Goal 5: Validate the Beta with an Industry Reviewer
The final objective is to produce a validation package that demonstrates practical usefulness, usability, and a realistic path for future expansion. This will involve a structured review session with at least one industry stakeholder, such as a property manager or operations professional, using realistic scenarios that focus on listing comparison, market positioning, and pricing interpretation.

The purpose of this phase is not to claim commercial-grade optimization, but to verify whether the system is understandable, useful, and credible as a pricing decision-support tool. The review will generate written feedback, a beta readiness decision, and a prioritized roadmap for future improvements.

Timeline: May 7, 2026.

## Metric Definitions
In this project, Estimated Market Price refers to the nightly price predicted or benchmarked for a listing based on observed characteristics and comparable market observations. Benchmark Range refers to the expected lower and upper interval within which similar listings are positioned in the same market context. Price Positioning Score refers to the classification of a listing as underpriced, aligned, or overpriced relative to comparable listings. Comparable Listing Relevance refers to the degree to which the listings returned by the system are similar to the target property according to the selected comparison logic. Model Error Metrics refers to measures such as MAE and RMSE that evaluate estimation quality on held-out data. Seasonal Benchmark Change refers to the relative difference in benchmark levels between the seasonal snapshots available in the dataset. Explanation Quality refers to the clarity and consistency with which the system can communicate the main factors affecting a given estimate.

## Scope Limitation
This project is not intended to function as a full revenue management system. The available data does not include confirmed bookings, realized revenue, transaction-level performance, or longitudinal daily availability histories. As a result, the system cannot support strong claims about occupancy forecasting, demand forecasting, RevPAR optimization, or dynamic daily pricing in the strict revenue management sense.

Instead, the system is intentionally framed as an explainable pricing intelligence and market benchmarking tool. Its purpose is to support human pricing decisions by providing structured market evidence, price estimates, comparable listings, and interpretable positioning signals.

## Assumptions, Risks, Obstacles
The project assumes that the available Airbnb listing snapshots are sufficient to support meaningful price estimation and market benchmarking across the selected cities, and that the observed listing attributes contain enough information to capture a substantial share of price variation. It also assumes that users will find interpretable benchmarks and comparable-listing outputs useful even in the absence of true booking and revenue data.

The main risks derive from the structure of the available data. The dataset consists of seasonal snapshots rather than continuous daily time series, which limits temporal analysis and prevents full dynamic pricing logic. The absence of booking and occupancy data means that conclusions must remain focused on market pricing rather than operational performance. There is also a risk that listed prices may differ from transacted prices, and a risk that some relevant determinants of price, such as event-level demand, lead time, cancellation behavior, or internal property quality variables, are not directly observable. Finally, any model developed on the available cities and listing structure may have limited generalizability outside the observed context.

## Future Improvements
If richer data sources become available in the future, the project could be extended in directions that are closer to full revenue management. One possible extension would be probabilistic occupancy modeling, where the system estimates the likelihood of booking rather than relying on coarse availability assumptions. Another natural extension would be the estimation of price sensitivity or price elasticity, so that the system could analyze how changes in nightly price are associated with changes in booking behavior. These components are not included in the current project scope because they require booking, availability, or longitudinal behavioral data that is not present in the current dataset.

## Success Criteria
By May 7, 2026, the project will be considered successful if a reproducible and versioned analytical dataset has been prepared for Rome, Milan, Florence, Venice, and Naples, with documented cleaning rules and a complete data dictionary. It will also be necessary for the team to implement and evaluate an explainable price estimation engine on held-out data using clearly reported error metrics and interpretable feature effects. Success further requires the development of a comparable listings and market benchmarking workflow capable of producing benchmark ranges and price positioning outputs for individual properties. In addition, a beta dashboard must be deployed in a staging environment and must provide on-demand price estimates, benchmark ranges, comparable listing outputs, and seasonal market comparisons in a clear and usable way. Finally, the project must include a structured review with at least one industry stakeholder and a final report summarizing technical results, practical limitations, and opportunities for future extension with richer data sources.
