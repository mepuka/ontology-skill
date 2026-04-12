"""Add MeasuredPropertyScheme and DomainObjectScheme to the vocabulary.

SKY-309: Formalize two new SKOS ConceptSchemes with 40 concepts total
(15 measuredProperty + 25 domainObject) to disambiguate the 37 ambiguous
eval observations.

Design decisions applied:
- CD-004: prefLabel matches TypeScript canonical string (lowercase/snake_case)
- CD-007: Overlap with TechnologyOrFuelScheme is intentional
- CD-008: Suffixed IRIs for name collisions (PriceMeasure, ShareMeasure, etc.)

Usage:
    uv run python scripts/add_new_schemes.py
"""

from __future__ import annotations

from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, SKOS

VOCAB_DIR = Path(__file__).parent.parent
VOCAB_FILE = VOCAB_DIR / "skygest-energy-vocab.ttl"

SEVOCAB = Namespace("https://skygest.dev/vocab/energy/")


def add_scheme(
    g: Graph,
    local_name: str,
    label: str,
    definition: str,
) -> URIRef:
    """Add a ConceptScheme to the graph."""
    scheme = SEVOCAB[local_name]
    g.add((scheme, RDF.type, SKOS.ConceptScheme))
    g.add((scheme, RDFS.label, Literal(label, lang="en")))
    g.add((scheme, SKOS.prefLabel, Literal(label, lang="en")))
    g.add((scheme, SKOS.definition, Literal(definition, lang="en")))
    return scheme


def add_concept(
    g: Graph,
    local_name: str,
    pref_label: str,
    definition: str,
    scheme: URIRef,
    alt_labels_en: list[str] | None = None,
    alt_labels_de: list[str] | None = None,
    broader: URIRef | None = None,
    is_top: bool = True,
) -> URIRef:
    """Add a Concept to the graph with labels, definition, and scheme membership."""
    concept = SEVOCAB[local_name]
    g.add((concept, RDF.type, SKOS.Concept))
    g.add((concept, RDFS.label, Literal(pref_label, lang="en")))
    g.add((concept, SKOS.prefLabel, Literal(pref_label, lang="en")))
    g.add((concept, SKOS.definition, Literal(definition, lang="en")))
    g.add((concept, SKOS.inScheme, scheme))

    if is_top and broader is None:
        g.add((concept, SKOS.topConceptOf, scheme))

    if broader is not None:
        g.add((concept, SKOS.broader, broader))

    for label in alt_labels_en or []:
        g.add((concept, SKOS.altLabel, Literal(label, lang="en")))

    for label in alt_labels_de or []:
        g.add((concept, SKOS.altLabel, Literal(label, lang="de")))

    return concept


def main() -> None:
    """Add MeasuredPropertyScheme and DomainObjectScheme."""
    g = Graph()
    g.parse(VOCAB_FILE, format="turtle")

    print("Adding MeasuredPropertyScheme...")
    mp_scheme = add_scheme(
        g,
        "MeasuredPropertyScheme",
        "measured property scheme",
        "A concept scheme that classifies what is being measured in an energy"
        " statistic, aligned with IEA energy balance flow categories",
    )

    # ── MeasuredProperty concepts (15) ──────────────────────────

    add_concept(
        g,
        "Generation",
        "generation",
        "A measuredProperty concept representing the production of energy or"
        " electricity over a time interval",
        mp_scheme,
        alt_labels_en=[
            "generation",
            "output",
            "produced",
            "power production",
            "gross electricity production",
            "net electricity production",
        ],
        alt_labels_de=["Erzeugung", "Stromerzeugung", "Nettostromerzeugung"],
    )

    add_concept(
        g,
        "Capacity",
        "capacity",
        "A measuredProperty concept representing the maximum output capability"
        " of an energy installation",
        mp_scheme,
        alt_labels_en=["capacity", "installed", "nameplate", "fleet", "installed capacity"],
        alt_labels_de=["Kapazitat", "installierte Leistung"],
    )

    add_concept(
        g,
        "Demand",
        "demand",
        "A measuredProperty concept representing the quantity of energy or"
        " power consumed or required",
        mp_scheme,
        alt_labels_en=["demand", "consumption", "use", "usage", "load", "final consumption"],
        alt_labels_de=["Verbrauch", "Nachfrage", "Bedarf"],
    )

    add_concept(
        g,
        "EmissionsMeasure",
        "emissions",
        "A measuredProperty concept representing the release of greenhouse"
        " gases from energy activities",
        mp_scheme,
        alt_labels_en=[
            "emissions",
            "CO2",
            "carbon intensity",
            "GHG",
            "greenhouse gas",
            "CO2 emissions",
        ],
        alt_labels_de=["Emissionen", "CO2-Emissionen", "Treibhausgase"],
    )

    add_concept(
        g,
        "Investment",
        "investment",
        "A measuredProperty concept representing capital expenditure in energy"
        " infrastructure or technology",
        mp_scheme,
        alt_labels_en=["investment", "spending", "capex", "funding"],
        alt_labels_de=["Investition", "Investitionen"],
    )

    add_concept(
        g,
        "PriceMeasure",
        "price",
        "A measuredProperty concept representing the monetary cost per unit"
        " of energy commodity or service",
        mp_scheme,
        alt_labels_en=["price", "cost", "tariff", "rate", "LCOE"],
        alt_labels_de=["Preis", "Kosten", "Strompreis"],
    )

    add_concept(
        g,
        "ShareMeasure",
        "share",
        "A measuredProperty concept representing the proportional contribution"
        " of a part to a whole",
        mp_scheme,
        alt_labels_en=["share", "proportion", "fraction", "mix", "penetration"],
        alt_labels_de=["Anteil"],
    )

    add_concept(
        g,
        "CountMeasure",
        "count",
        "A measuredProperty concept representing a discrete tally of equipment"
        " or infrastructure units",
        mp_scheme,
        alt_labels_en=["installations", "units deployed", "count", "number"],
        alt_labels_de=["Anzahl", "Installationen"],
    )

    # ── Domain expansion measuredProperty concepts (7) ──────────

    add_concept(
        g,
        "Trade",
        "trade",
        "A measuredProperty concept representing cross-border energy trade flows",
        mp_scheme,
        alt_labels_en=["trade", "imports", "exports", "interconnector flow", "net imports"],
        alt_labels_de=["Handel", "Importe", "Exporte"],
    )

    add_concept(
        g,
        "Efficiency",
        "efficiency",
        "A measuredProperty concept representing the ratio of useful energy output to total input",
        mp_scheme,
        alt_labels_en=[
            "efficiency",
            "conversion efficiency",
            "system efficiency",
            "thermal efficiency",
        ],
        alt_labels_de=["Wirkungsgrad", "Effizienz"],
    )

    add_concept(
        g,
        "Curtailment",
        "curtailment",
        "A measuredProperty concept representing generation that was reduced"
        " or prevented by grid constraints",
        mp_scheme,
        alt_labels_en=["curtailment", "curtailed", "spilled", "constrained off"],
    )

    add_concept(
        g,
        "Revenue",
        "revenue",
        "A measuredProperty concept representing monetary income from energy activities",
        mp_scheme,
        alt_labels_en=["revenue", "earnings", "turnover", "income"],
        alt_labels_de=["Umsatz", "Einnahmen"],
    )

    add_concept(
        g,
        "DischargeMeasure",
        "discharge",
        "A measuredProperty concept representing energy released from a storage system",
        mp_scheme,
        alt_labels_en=["discharge", "dispatched", "storage output"],
    )

    add_concept(
        g,
        "ConsumptionMeasure",
        "consumption",
        "A measuredProperty concept representing the actual use of energy by end consumers",
        mp_scheme,
        alt_labels_en=[
            "consumption",
            "final consumption",
            "energy consumption",
            "total consumption",
        ],
        alt_labels_de=["Endverbrauch", "Energieverbrauch"],
    )

    add_concept(
        g,
        "EnergySupply",
        "supply",
        "A measuredProperty concept representing total primary energy supply entering the system",
        mp_scheme,
        alt_labels_en=["supply", "primary supply", "TPES", "total primary energy supply"],
        alt_labels_de=["Energieversorgung", "Primarenergie"],
    )

    print("  Added 15 MeasuredProperty concepts")

    # ── DomainObjectScheme ──────────────────────────────────────

    print("Adding DomainObjectScheme...")
    do_scheme = add_scheme(
        g,
        "DomainObjectScheme",
        "domain object scheme",
        "A concept scheme that classifies the domain object to which an energy"
        " measurement applies, covering IEA sectors, energy carriers, and"
        " technology domains",
    )

    # Energy carriers
    add_concept(
        g,
        "ElectricityDomain",
        "electricity",
        "A domainObject concept representing electrical energy as the subject of measurement",
        do_scheme,
        alt_labels_en=["electricity", "power", "electric", "electrical energy"],
        alt_labels_de=["Strom", "Elektrizitat", "elektrische Energie"],
    )

    add_concept(
        g,
        "HeatDomain",
        "heat",
        "A domainObject concept representing heat energy and the heating"
        " sector as the subject of measurement",
        do_scheme,
        alt_labels_en=["heat", "heating", "thermal", "district heat", "district heating"],
        alt_labels_de=["Warme", "Fernwarme", "Heizung"],
    )

    add_concept(
        g,
        "NaturalGasDomain",
        "natural gas",
        "A domainObject concept representing natural gas as an energy carrier"
        " and measurement subject",
        do_scheme,
        alt_labels_en=["natural gas", "gas supply", "LNG", "gas"],
        alt_labels_de=["Erdgas"],
    )

    add_concept(
        g,
        "HydrogenDomain",
        "hydrogen",
        "A domainObject concept representing hydrogen as an energy carrier and measurement subject",
        do_scheme,
        alt_labels_en=["hydrogen", "green hydrogen", "H2"],
        alt_labels_de=["Wasserstoff", "gruner Wasserstoff"],
    )

    add_concept(
        g,
        "OilDomain",
        "oil",
        "A domainObject concept representing petroleum and the oil sector as measurement subject",
        do_scheme,
        alt_labels_en=["oil", "petroleum", "crude", "crude oil"],
        alt_labels_de=["Ol", "Erdol", "Petroleum"],
    )

    # Sectors
    add_concept(
        g,
        "TransportDomain",
        "transport",
        "A domainObject concept representing the transport sector and"
        " electric vehicles as measurement subject",
        do_scheme,
        alt_labels_en=[
            "transport",
            "EV",
            "vehicle",
            "mobility",
            "electric vehicle",
            "transportation",
        ],
        alt_labels_de=["Verkehr", "Elektromobilitat"],
    )

    add_concept(
        g,
        "BuildingsDomain",
        "buildings",
        "A domainObject concept representing the buildings sector energy"
        " use as measurement subject",
        do_scheme,
        alt_labels_en=["buildings", "residential", "commercial", "building energy"],
        alt_labels_de=["Gebaude", "Wohngebaude"],
    )

    add_concept(
        g,
        "IndustryDomain",
        "industry",
        "A domainObject concept representing the industrial sector energy"
        " use as measurement subject",
        do_scheme,
        alt_labels_en=["industry", "industrial", "manufacturing", "industrial energy"],
        alt_labels_de=["Industrie"],
    )

    add_concept(
        g,
        "EnergyConsumptionDomain",
        "energy consumption",
        "A domainObject concept representing aggregate energy consumption as measurement subject",
        do_scheme,
        alt_labels_en=["energy consumption", "total energy use", "primary energy consumption"],
        alt_labels_de=["Energieverbrauch"],
    )

    add_concept(
        g,
        "EnergyTransitionDomain",
        "energy transition",
        "A domainObject concept representing the energy transition as an investment domain",
        do_scheme,
        alt_labels_en=["energy transition", "clean energy transition"],
        alt_labels_de=["Energiewende"],
    )

    add_concept(
        g,
        "CleanEnergyDomain",
        "clean energy",
        "A domainObject concept representing the aggregate clean energy"
        " sector as measurement subject",
        do_scheme,
        alt_labels_en=["clean energy", "green energy", "low-carbon energy"],
        alt_labels_de=["saubere Energie"],
    )

    add_concept(
        g,
        "GridDomain",
        "grid",
        "A domainObject concept representing the electrical grid"
        " infrastructure as measurement subject",
        do_scheme,
        alt_labels_en=["grid", "transmission", "distribution", "power grid", "electrical grid"],
        alt_labels_de=["Stromnetz", "Ubertragungsnetz", "Verteilnetz"],
    )

    # Technology domains
    add_concept(
        g,
        "BatteryStorageDomain",
        "battery storage",
        "A domainObject concept representing electrochemical storage systems"
        " as measurement subject",
        do_scheme,
        alt_labels_en=["battery storage", "BESS", "energy storage", "battery energy storage"],
        alt_labels_de=["Batteriespeicher"],
    )

    add_concept(
        g,
        "DataCenterDomain",
        "data center",
        "A domainObject concept representing data center infrastructure as measurement subject",
        do_scheme,
        alt_labels_en=["data center", "datacenter", "data centre"],
        alt_labels_de=["Rechenzentrum"],
    )

    add_concept(
        g,
        "ElectrolyzerDomain",
        "electrolyzer",
        "A domainObject concept representing hydrogen electrolyzer equipment"
        " as measurement subject",
        do_scheme,
        alt_labels_en=["electrolyzer", "electrolysis", "electrolyser"],
        alt_labels_de=["Elektrolyseur", "Wasserelektrolyseur"],
    )

    add_concept(
        g,
        "HeatPumpDomain",
        "heat pump",
        "A domainObject concept representing heat pump equipment as measurement subject",
        do_scheme,
        alt_labels_en=["heat pump", "heat pumps"],
        alt_labels_de=["Warmepumpe", "Warmepumpen"],
    )

    add_concept(
        g,
        "NuclearReactorDomain",
        "nuclear reactor",
        "A domainObject concept representing nuclear reactor installations as measurement subject",
        do_scheme,
        alt_labels_en=["nuclear reactor", "reactor", "nuclear plant"],
        alt_labels_de=["Kernreaktor", "Kernkraftwerk"],
    )

    add_concept(
        g,
        "SolarPhotovoltaicDomain",
        "solar photovoltaic",
        "A domainObject concept representing solar PV technology as measurement subject",
        do_scheme,
        alt_labels_en=["solar photovoltaic", "solar PV", "PV", "photovoltaic"],
        alt_labels_de=["Photovoltaik", "Solarenergie"],
    )

    wt = add_concept(
        g,
        "WindTurbineDomain",
        "wind turbine",
        "A domainObject concept representing wind turbine equipment as measurement subject",
        do_scheme,
        alt_labels_en=["wind turbine", "wind turbines"],
        alt_labels_de=["Windturbine", "Windkraftanlage", "Windenergieanlage"],
    )

    add_concept(
        g,
        "OffshoreWindTurbineDomain",
        "offshore wind turbine",
        "A domainObject concept representing offshore wind turbine equipment"
        " as measurement subject",
        do_scheme,
        alt_labels_en=["offshore wind turbine", "offshore turbine"],
        alt_labels_de=["Offshore-Windturbine"],
        broader=wt,
        is_top=False,
    )

    add_concept(
        g,
        "OffshoreWindFarmDomain",
        "offshore wind farm",
        "A domainObject concept representing offshore wind farm installations"
        " as measurement subject",
        do_scheme,
        alt_labels_en=["offshore wind farm", "offshore wind park"],
        alt_labels_de=["Offshore-Windpark"],
    )

    add_concept(
        g,
        "RenewablePowerDomain",
        "renewable power",
        "A domainObject concept representing renewable power generation as measurement subject",
        do_scheme,
        alt_labels_en=["renewable power", "renewable electricity", "renewable generation"],
        alt_labels_de=["erneuerbare Energie", "Okostrom"],
    )

    # Product-specific
    bs = SEVOCAB["BatteryStorageDomain"]
    add_concept(
        g,
        "LithiumIonBatteryPackDomain",
        "lithium-ion battery pack",
        "A domainObject concept representing lithium-ion battery packs as measurement subject",
        do_scheme,
        alt_labels_en=["lithium-ion battery pack", "li-ion pack", "battery pack"],
        alt_labels_de=["Batteriepack"],
        broader=bs,
        is_top=False,
    )

    add_concept(
        g,
        "InterconnectionQueueDomain",
        "interconnection queue",
        "A domainObject concept representing the electricity grid"
        " interconnection queue as measurement subject",
        do_scheme,
        alt_labels_en=["interconnection queue", "grid queue", "interconnection backlog"],
    )

    print("  Added 25 DomainObject concepts")

    # Serialize
    g.serialize(destination=str(VOCAB_FILE), format="turtle")
    print(f"\nSaved: {VOCAB_FILE}")


if __name__ == "__main__":
    main()
