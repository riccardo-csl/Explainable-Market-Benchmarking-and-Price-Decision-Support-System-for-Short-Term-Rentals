"""Static source dataset registry and target contract definitions."""

from __future__ import annotations

from .contracts import (
    CandidateKeyDefinition,
    DatasetRelationship,
    SourceDatasetDescriptor,
    TargetDatasetContract,
    TargetFieldDescriptor,
)


def source_dataset_descriptors() -> list[SourceDatasetDescriptor]:
    return [
        SourceDatasetDescriptor(
            name="airbnb_listing_snapshots",
            relative_path="data/raw/airbnb/listing_snapshots.csv",
            original_filename="airbnb.csv",
            file_format="csv",
            grain="listing_snapshot_per_scrape_date",
            role="primary_listing_level_dataset",
            source_category="third_party_export",
            encoding="utf-8",
            steward="project_team",
            description=(
                "Listing-level Airbnb snapshot data with pricing, review metrics, "
                "location, and seasonal scrape metadata."
            ),
            candidate_keys=[
                CandidateKeyDefinition(["Listings id", "Date of scraping"]),
                CandidateKeyDefinition(["Listings id", "Season"]),
            ],
            city_columns=["City"],
            period_columns=["Season"],
            date_columns=["Date of scraping"],
            categorical_hints=[
                "Host is superhost",
                "Property type",
                "City",
                "Season",
                "Bathrooms type",
            ],
            known_limitations=[
                "Listing identifiers repeat across multiple scrape dates by design.",
                "The `Coordinates` column stores latitude and longitude as a combined string.",
                "The `Property type` field behaves as a room-type style category in the observed source data.",
            ],
        ),
        SourceDatasetDescriptor(
            name="city_period_summary",
            relative_path="data/raw/airbnb/city_period_summary.csv",
            original_filename="airbnb_italian_city_grouped.csv",
            file_format="csv",
            grain="city_period_aggregate",
            role="city_level_benchmark_dataset",
            source_category="project_derived_source",
            encoding="utf-8",
            steward="project_team",
            description=(
                "City-period aggregate statistics derived from listing-level data. "
                "Intended for city-level benchmarking and contextual market summaries."
            ),
            candidate_keys=[CandidateKeyDefinition(["place", "period"])],
            city_columns=["place"],
            period_columns=["period"],
            categorical_hints=["place", "period", "neighbourhood_mode", "room_type_mode"],
            known_limitations=[
                "This dataset is aggregated and cannot be used for property-level modeling by itself.",
                "City and period labels use different header names than the listing-level source dataset.",
            ],
        ),
        SourceDatasetDescriptor(
            name="neighbourhood_period_summary",
            relative_path="data/raw/airbnb/neighbourhood_period_summary.csv",
            original_filename="airbnb_italian_neighbourhood_grouped.csv",
            file_format="csv",
            grain="city_neighbourhood_period_aggregate",
            role="neighbourhood_level_benchmark_dataset",
            source_category="project_derived_source",
            encoding="utf-8",
            steward="project_team",
            description=(
                "Neighbourhood-period aggregate statistics used for local benchmark context."
            ),
            candidate_keys=[CandidateKeyDefinition(["place", "neighbourhood", "period"])],
            city_columns=["place"],
            period_columns=["period"],
            categorical_hints=["place", "period", "neighbourhood", "room_type_mode"],
            known_limitations=[
                "This dataset is aggregated and should be treated as benchmark context, not as listing-level evidence.",
            ],
        ),
        SourceDatasetDescriptor(
            name="neighbourhood_reference",
            relative_path="data/raw/airbnb/neighbourhood_reference.csv",
            original_filename="airbnb_italy_city_neighbourhoods.csv",
            file_format="csv",
            grain="city_neighbourhood_reference_row",
            role="reference_mapping_dataset",
            source_category="reference_source",
            encoding="utf-8",
            steward="project_team",
            description=(
                "Reference mapping between neighbourhoods, neighbourhood groups, and cities."
            ),
            candidate_keys=[CandidateKeyDefinition(["city", "neighbourhood"])],
            city_columns=["city"],
            categorical_hints=["city", "neighbourhood", "neighbourhood_group"],
            known_limitations=[
                "Neighbourhood group values can be null and must be treated as optional reference data.",
            ],
        ),
        SourceDatasetDescriptor(
            name="neighbourhood_boundaries",
            relative_path="data/raw/airbnb/neighbourhood_boundaries.geojson",
            original_filename="airbnb_italy_city_neighbourhoods_geojson.geojson",
            file_format="geojson",
            grain="boundary_feature",
            role="spatial_boundary_dataset",
            source_category="spatial_source",
            encoding="utf-8",
            steward="project_team",
            description=(
                "GeoJSON neighbourhood boundaries used for mapping and spatial context."
            ),
            categorical_hints=["neighbourhood", "neighbourhood_group"],
            known_limitations=[
                "The GeoJSON features do not expose a city property directly.",
                "The boundary file contains multiple features for some logical neighbourhood entities.",
                "Some neighbourhood names require encoding normalization to align cleanly with the reference CSV.",
            ],
        ),
    ]


def source_dataset_relationships() -> list[DatasetRelationship]:
    return [
        DatasetRelationship(
            from_dataset="airbnb_listing_snapshots",
            to_dataset="city_period_summary",
            relation_type="many_to_one_after_normalization",
            join_columns=["city_name", "period_label"],
            notes=(
                "Join requires header normalization because the listing dataset uses `City` and `Season`, "
                "while the aggregate dataset uses `place` and `period`."
            ),
        ),
        DatasetRelationship(
            from_dataset="airbnb_listing_snapshots",
            to_dataset="neighbourhood_reference",
            relation_type="many_to_one_after_normalization",
            join_columns=["city_name", "neighbourhood_name"],
            notes="Join uses normalized city and neighbourhood labels.",
        ),
        DatasetRelationship(
            from_dataset="neighbourhood_period_summary",
            to_dataset="neighbourhood_reference",
            relation_type="many_to_one_after_normalization",
            join_columns=["city_name", "neighbourhood_name"],
            notes="Neighbourhood aggregates can be enriched through the reference mapping table.",
        ),
        DatasetRelationship(
            from_dataset="neighbourhood_reference",
            to_dataset="neighbourhood_boundaries",
            relation_type="one_to_many_with_encoding_and_spatial_normalization",
            join_columns=["neighbourhood_name", "neighbourhood_group_name"],
            notes=(
                "The GeoJSON does not include city names and may expose multiple features per logical neighbourhood, "
                "so later cleaning must normalize encoding and potentially dissolve boundaries."
            ),
        ),
    ]


def _field(
    name: str,
    data_type: str,
    nullable: bool,
    description: str,
    source_columns: list[str],
) -> TargetFieldDescriptor:
    return TargetFieldDescriptor(
        name=name,
        data_type=data_type,
        nullable=nullable,
        description=description,
        source_columns=source_columns,
    )


def _grouped_metric_fields(prefix: str) -> list[TargetFieldDescriptor]:
    metric_specs = [
        ("reviews_last_twelve_months", "number_of_reviews_ltm", "Median number of reviews observed in the last twelve months."),
        ("host_listing_count", "host_total_listings_count", "Median number of listings managed by the host."),
        ("accommodates_count", "accommodates", "Median guest capacity."),
        ("nightly_price", "price", "Median observed nightly price."),
        ("total_reviews", "number_of_reviews", "Median total review count."),
        ("rating_score", "review_scores_rating", "Median overall rating score."),
        ("accuracy_score", "review_scores_accuracy", "Median accuracy score."),
        ("cleanliness_score", "review_scores_cleanliness", "Median cleanliness score."),
        ("checkin_score", "review_scores_checkin", "Median check-in score."),
        ("communication_score", "review_scores_communication", "Median communication score."),
        ("location_score", "review_scores_location", "Median location score."),
        ("value_score", "review_scores_value", "Median value score."),
        ("reviews_per_month", "reviews_per_month", "Median reviews per month."),
        ("latitude", "latitude", "Median latitude."),
        ("longitude", "longitude", "Median longitude."),
    ]
    fields: list[TargetFieldDescriptor] = []
    for canonical_name, raw_prefix, description in metric_specs:
        fields.append(
            _field(
                f"{canonical_name}_median",
                "float",
                True,
                description,
                [f"{raw_prefix}_median"],
            )
        )
        fields.append(
            _field(
                f"{canonical_name}_median_abs_deviation",
                "float",
                True,
                f"Absolute deviation around the median for {description[:-1].lower()}.",
                [f"{raw_prefix}_median_abs_deviation"],
            )
        )
    return fields


def target_dataset_contracts() -> list[TargetDatasetContract]:
    listing_snapshot_fields = [
        _field("listing_id", "integer", False, "Stable listing identifier.", ["Listings id"]),
        _field("reviews_last_twelve_months", "integer", True, "Review count observed in the last twelve months.", ["Last year reviews"]),
        _field("host_since", "date", True, "Host onboarding date.", ["Host since"]),
        _field("is_superhost", "boolean", True, "Whether the host is marked as a superhost after normalization.", ["Host is superhost"]),
        _field("host_listing_count", "integer", True, "Number of listings managed by the host.", ["Host number of listings"]),
        _field("neighbourhood_name", "string", True, "Normalized neighbourhood label.", ["Neighbourhood"]),
        _field("beds_count", "integer", True, "Number of beds.", ["Beds number"]),
        _field("bedrooms_count", "integer", True, "Number of bedrooms.", ["Bedrooms number"]),
        _field("room_type", "string", True, "Normalized room or property type label.", ["Property type"]),
        _field("accommodates_count", "integer", True, "Maximum allowed guests.", ["Maximum allowed guests"]),
        _field("nightly_price", "float", True, "Observed nightly listing price.", ["Price"]),
        _field("total_reviews", "integer", True, "Total number of reviews.", ["Total reviews"]),
        _field("rating_score", "float", True, "Overall rating score.", ["Rating score"]),
        _field("accuracy_score", "float", True, "Accuracy review score.", ["Accuracy score"]),
        _field("cleanliness_score", "float", True, "Cleanliness review score.", ["Cleanliness score"]),
        _field("checkin_score", "float", True, "Check-in review score.", ["Checkin score"]),
        _field("communication_score", "float", True, "Communication review score.", ["Communication score"]),
        _field("location_score", "float", True, "Location review score.", ["Location score"]),
        _field("value_score", "float", True, "Value-for-money review score.", ["Value for money score"]),
        _field("reviews_per_month", "float", True, "Reviews per month.", ["Reviews per month"]),
        _field("city_name", "string", False, "Normalized city label.", ["City"]),
        _field("period_label", "string", False, "Normalized seasonal label shared across datasets.", ["Season"]),
        _field("bathrooms_count", "float", True, "Bathroom count.", ["Bathrooms number"]),
        _field("bathroom_type", "string", True, "Bathroom type classification.", ["Bathrooms type"]),
        _field("latitude", "float", True, "Latitude parsed from the coordinates field.", ["Coordinates"]),
        _field("longitude", "float", True, "Longitude parsed from the coordinates field.", ["Coordinates"]),
        _field("snapshot_date", "date", False, "Source scrape date.", ["Date of scraping"]),
    ]

    city_summary_fields = [
        _field("city_name", "string", False, "Normalized city label.", ["place"]),
        _field("period_label", "string", False, "Normalized seasonal label.", ["period"]),
        _field("dominant_neighbourhood", "string", True, "Most common neighbourhood label within the city-period slice.", ["neighbourhood_mode"]),
        _field("neighbourhood_entropy", "float", True, "Shannon entropy of neighbourhood distribution.", ["neighbourhood_shannon_entropy"]),
        _field("dominant_room_type", "string", True, "Most common room type within the city-period slice.", ["room_type_mode"]),
        _field("room_type_entropy", "float", True, "Shannon entropy of room type distribution.", ["room_type_shannon_entropy"]),
        *_grouped_metric_fields("city"),
    ]

    neighbourhood_summary_fields = [
        _field("city_name", "string", False, "Normalized city label.", ["place"]),
        _field("neighbourhood_name", "string", False, "Normalized neighbourhood label.", ["neighbourhood"]),
        _field("period_label", "string", False, "Normalized seasonal label.", ["period"]),
        _field("dominant_room_type", "string", True, "Most common room type within the neighbourhood-period slice.", ["room_type_mode"]),
        _field("room_type_entropy", "float", True, "Shannon entropy of room type distribution.", ["room_type_shannon_entropy"]),
        *_grouped_metric_fields("neighbourhood"),
    ]

    neighbourhood_reference_fields = [
        _field("city_name", "string", False, "Normalized city label.", ["city"]),
        _field("neighbourhood_name", "string", False, "Normalized neighbourhood label.", ["neighbourhood"]),
        _field("neighbourhood_group_name", "string", True, "Neighbourhood group label if available.", ["neighbourhood_group"]),
    ]

    boundary_fields = [
        _field("boundary_id", "string", False, "Generated stable identifier for the cleaned neighbourhood boundary row.", []),
        _field("city_name", "string", False, "City label derived during cleaning by joining boundary data with the reference mapping.", ["neighbourhood", "neighbourhood_group"]),
        _field("neighbourhood_name", "string", False, "Normalized neighbourhood label.", ["neighbourhood"]),
        _field("neighbourhood_group_name", "string", True, "Neighbourhood group label if available.", ["neighbourhood_group"]),
        _field("geometry_type", "string", False, "GeoJSON geometry type.", ["geometry.type"]),
        _field("geometry", "geojson", False, "GeoJSON geometry payload.", ["geometry"]),
    ]

    return [
        TargetDatasetContract(
            name="listing_snapshot",
            description="Canonical cleaned listing-level snapshot table used by modeling and downstream APIs.",
            grain="listing_snapshot_per_scrape_date",
            primary_key=["listing_id", "snapshot_date"],
            source_datasets=["airbnb_listing_snapshots"],
            fields=listing_snapshot_fields,
            notes=[
                "Coordinates are parsed into latitude and longitude during cleaning.",
                "The superhost field is normalized into a boolean.",
            ],
        ),
        TargetDatasetContract(
            name="city_period_summary",
            description="Canonical city-level benchmark table derived from the grouped city-period source dataset.",
            grain="city_period_aggregate",
            primary_key=["city_name", "period_label"],
            source_datasets=["city_period_summary"],
            fields=city_summary_fields,
            notes=[
                "Field names are normalized into snake_case while preserving the original aggregate semantics.",
            ],
        ),
        TargetDatasetContract(
            name="neighbourhood_period_summary",
            description="Canonical neighbourhood-level benchmark table for localized market context.",
            grain="city_neighbourhood_period_aggregate",
            primary_key=["city_name", "neighbourhood_name", "period_label"],
            source_datasets=["neighbourhood_period_summary"],
            fields=neighbourhood_summary_fields,
            notes=[
                "This dataset is aggregate context and not a substitute for listing-level observations.",
            ],
        ),
        TargetDatasetContract(
            name="neighbourhood_reference",
            description="Canonical reference mapping between cities, neighbourhoods, and neighbourhood groups.",
            grain="city_neighbourhood_reference_row",
            primary_key=["city_name", "neighbourhood_name"],
            source_datasets=["neighbourhood_reference"],
            fields=neighbourhood_reference_fields,
            notes=[
                "Neighbourhood group values remain nullable because the source mapping includes nulls.",
            ],
        ),
        TargetDatasetContract(
            name="neighbourhood_boundary",
            description="Canonical boundary dataset for maps and spatial benchmarking after reference enrichment.",
            grain="cleaned_boundary_row",
            primary_key=["boundary_id"],
            source_datasets=["neighbourhood_boundaries", "neighbourhood_reference"],
            fields=boundary_fields,
            notes=[
                "City names are expected to be enriched during cleaning because the raw GeoJSON does not expose them.",
                "Boundary rows may require dissolve logic if multiple raw features map to one logical neighbourhood.",
            ],
        ),
    ]
