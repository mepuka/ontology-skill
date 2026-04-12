"""Expand vocabulary based on gap analysis — corpus-driven domain expansion.

Three work streams:
1. New PolicyInstrumentScheme (10 concepts)
2. New concepts in existing schemes (7 TechOrFuel + 8 DomainObject + 3 MeasuredProperty)
3. Surface form enrichment on existing concepts

Usage:
    uv run python scripts/expand_gap_analysis.py
"""

from __future__ import annotations

from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, SKOS

VOCAB_DIR = Path(__file__).parent.parent
VOCAB_FILE = VOCAB_DIR / "skygest-energy-vocab.ttl"
SEVOCAB = Namespace("https://skygest.dev/vocab/energy/")


def add_scheme(g: Graph, local_name: str, label: str, definition: str) -> URIRef:
    """Add a ConceptScheme."""
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
    rdfs_label: str,
    definition: str,
    scheme: URIRef,
    alt_labels_en: list[str] | None = None,
    broader: URIRef | None = None,
) -> URIRef:
    """Add a Concept with labels and scheme membership."""
    concept = SEVOCAB[local_name]
    g.add((concept, RDF.type, SKOS.Concept))
    g.add((concept, RDFS.label, Literal(rdfs_label, lang="en")))
    g.add((concept, SKOS.prefLabel, Literal(pref_label, lang="en")))
    g.add((concept, SKOS.definition, Literal(definition, lang="en")))
    g.add((concept, SKOS.inScheme, scheme))
    if broader is None:
        g.add((concept, SKOS.topConceptOf, scheme))
    else:
        g.add((concept, SKOS.broader, broader))
    for label in alt_labels_en or []:
        g.add((concept, SKOS.altLabel, Literal(label, lang="en")))
    return concept


def enrich(g: Graph, local_name: str, alt_labels_en: list[str]) -> None:
    """Add surface forms to an existing concept."""
    concept = SEVOCAB[local_name]
    existing = {str(lit) for lit in g.objects(concept, SKOS.altLabel) if lit.language == "en"}
    added = 0
    for label in alt_labels_en:
        if label not in existing:
            g.add((concept, SKOS.altLabel, Literal(label, lang="en")))
            added += 1
    if added:
        print(f"    {local_name}: +{added} surface forms")


def main() -> None:
    """Run all three expansion work streams."""
    g = Graph()
    g.parse(VOCAB_FILE, format="turtle")

    # ═══════════════════════════════════════════════════════════
    # Work Stream 1: PolicyInstrumentScheme (10 concepts)
    # ═══════════════════════════════════════════════════════════
    print("Work Stream 1: PolicyInstrumentScheme")

    pi = add_scheme(
        g,
        "PolicyInstrumentScheme",
        "policy instrument scheme",
        "A concept scheme that classifies energy policy mechanisms"
        " referenced in chart text, covering market mechanisms,"
        " support instruments, and procurement structures",
    )

    add_concept(
        g,
        "FeedInTariff",
        "feed-in tariff",
        "feed-in tariff",
        (
            "A policyInstrument concept representing guaranteed-price mechanisms"
            " for renewable energy producers"
        ),
        pi,
        [
            "feed-in tariff",
            "FIT",
            "feed-in premium",
            "FIP",
            "feed-in law",
            "renewable energy tariff",
        ],
    )

    add_concept(
        g,
        "PowerPurchaseAgreement",
        "power purchase agreement",
        "power purchase agreement",
        ("A policyInstrument concept representing bilateral contracts for electricity procurement"),
        pi,
        [
            "power purchase agreement",
            "PPA",
            "offtake agreement",
            "CPPA",
            "corporate PPA",
            "virtual PPA",
            "VPPA",
        ],
    )

    add_concept(
        g,
        "AuctionInstrument",
        "auction",
        "auction (policy instrument)",
        (
            "A policyInstrument concept representing competitive procurement"
            " mechanisms for energy projects"
        ),
        pi,
        ["auction", "tender", "competitive bidding", "reverse auction", "procurement round"],
    )

    add_concept(
        g,
        "SubsidyInstrument",
        "subsidy",
        "subsidy (policy instrument)",
        (
            "A policyInstrument concept representing financial support mechanisms"
            " for energy technologies"
        ),
        pi,
        [
            "subsidy",
            "incentive",
            "grant",
            "tax credit",
            "PTC",
            "ITC",
            "production tax credit",
            "investment tax credit",
            "rebate",
            "premium payment",
        ],
    )

    add_concept(
        g,
        "CarbonTax",
        "carbon tax",
        "carbon tax",
        ("A policyInstrument concept representing tax-based carbon pricing mechanisms"),
        pi,
        ["carbon tax", "carbon levy", "carbon fee", "carbon pricing", "carbon price floor"],
    )

    add_concept(
        g,
        "EmissionsTrading",
        "emissions trading",
        "emissions trading",
        ("A policyInstrument concept representing market-based emissions cap and trading systems"),
        pi,
        [
            "emissions trading",
            "ETS",
            "cap and trade",
            "EU ETS",
            "allowance",
            "emission allowance",
            "emissions trading scheme",
            "carbon trading",
        ],
    )

    add_concept(
        g,
        "RenewablePortfolioStd",
        "renewable portfolio standard",
        "renewable portfolio standard",
        ("A policyInstrument concept representing mandated renewable energy procurement targets"),
        pi,
        [
            "renewable portfolio standard",
            "RPS",
            "renewable mandate",
            "clean energy standard",
            "CES",
            "renewable obligation",
        ],
    )

    add_concept(
        g,
        "NetMeteringInstrument",
        "net metering",
        "net metering (policy instrument)",
        (
            "A policyInstrument concept representing compensation mechanisms"
            " for distributed generation"
        ),
        pi,
        [
            "net metering",
            "net billing",
            "self-consumption",
            "behind-the-meter compensation",
            "net energy metering",
        ],
    )

    add_concept(
        g,
        "CapacityMarketInstrument",
        "capacity market",
        "capacity market (policy instrument)",
        ("A policyInstrument concept representing market mechanisms ensuring generation adequacy"),
        pi,
        [
            "capacity market",
            "capacity auction",
            "capacity payment",
            "capacity mechanism",
            "capacity remuneration",
        ],
    )

    add_concept(
        g,
        "CarbonCreditInstrument",
        "carbon credit",
        "carbon credit (policy instrument)",
        (
            "A policyInstrument concept representing tradable certificates"
            " representing emission reductions"
        ),
        pi,
        [
            "carbon credit",
            "carbon offset",
            "VER",
            "voluntary carbon market",
            "offset",
            "emission reduction credit",
            "certified emission reduction",
        ],
    )

    print("  Added 10 PolicyInstrument concepts")

    # ═══════════════════════════════════════════════════════════
    # Work Stream 2: New concepts in existing schemes
    # ═══════════════════════════════════════════════════════════
    print("\nWork Stream 2: New concepts in existing schemes")

    # -- TechnologyOrFuelScheme (7 new concepts) --
    tf = SEVOCAB["TechnologyOrFuelScheme"]

    add_concept(
        g,
        "FossilFuel",
        "fossil fuel",
        "fossil fuel",
        (
            "A technologyOrFuel concept representing the aggregate of fossil"
            " fuel energy technologies"
        ),
        tf,
        [
            "fossil fuel",
            "fossil fuels",
            "fossil",
            "conventional generation",
            "conventional power",
            "thermal generation",
        ],
    )

    add_concept(
        g,
        "CarbonCapture",
        "carbon capture",
        "carbon capture",
        (
            "A technologyOrFuel concept representing carbon capture utilization"
            " and storage technology"
        ),
        tf,
        [
            "carbon capture",
            "CCS",
            "CCUS",
            "carbon capture and storage",
            "DAC",
            "direct air capture",
            "carbon removal",
            "BECCS",
            "bioenergy with carbon capture",
        ],
    )

    add_concept(
        g,
        "FuelCell",
        "fuel cell",
        "fuel cell",
        ("A technologyOrFuel concept representing electrochemical fuel cell technology"),
        tf,
        [
            "fuel cell",
            "fuel cells",
            "SOFC",
            "PEMFC",
            "hydrogen fuel cell",
            "solid oxide fuel cell",
            "proton exchange membrane",
        ],
    )

    add_concept(
        g,
        "MethaneFuel",
        "methane",
        "methane",
        ("A technologyOrFuel concept representing methane as fuel or emission source"),
        tf,
        ["methane", "CH4", "fugitive methane", "methane emissions", "methane leakage", "flaring"],
    )

    add_concept(
        g,
        "SyntheticFuel",
        "synthetic fuel",
        "synthetic fuel",
        (
            "A technologyOrFuel concept representing synthetically produced"
            " fuels from renewable electricity"
        ),
        tf,
        [
            "synthetic fuel",
            "e-fuel",
            "efuel",
            "SAF",
            "sustainable aviation fuel",
            "power-to-liquid",
            "power-to-gas",
            "green fuel",
        ],
    )

    add_concept(
        g,
        "CombinedHeatPower",
        "combined heat and power",
        "combined heat and power",
        (
            "A technologyOrFuel concept representing simultaneous heat and"
            " electricity generation technology"
        ),
        tf,
        [
            "combined heat and power",
            "CHP",
            "cogeneration",
            "cogen",
            "trigeneration",
            "district energy",
        ],
    )

    add_concept(
        g,
        "DieselFuel",
        "diesel",
        "diesel",
        ("A technologyOrFuel concept representing diesel and fuel oil used for power generation"),
        tf,
        ["diesel", "fuel oil", "heavy fuel oil", "HFO", "distillate", "gasoil", "diesel generator"],
    )

    print("  Added 7 TechnologyOrFuel concepts")

    # -- DomainObjectScheme (8 new concepts) --
    do = SEVOCAB["DomainObjectScheme"]

    add_concept(
        g,
        "CarbonMarketDomain",
        "carbon market",
        "carbon market (domain object)",
        (
            "A domainObject concept representing carbon emissions trading"
            " markets as measurement subject"
        ),
        do,
        [
            "carbon market",
            "carbon trading",
            "emissions market",
            "EU ETS market",
            "carbon price",
            "allowance market",
        ],
    )

    add_concept(
        g,
        "EVChargingDomain",
        "EV charging",
        "EV charging (domain object)",
        (
            "A domainObject concept representing electric vehicle charging"
            " infrastructure as measurement subject"
        ),
        do,
        [
            "EV charging",
            "charging station",
            "charging infrastructure",
            "EVSE",
            "charge point",
            "charger",
            "fast charging",
        ],
    )

    add_concept(
        g,
        "DecarbonizationDomain",
        "decarbonization",
        "decarbonization (domain object)",
        (
            "A domainObject concept representing decarbonization goals and"
            " progress as measurement subject"
        ),
        do,
        [
            "decarbonization",
            "net zero",
            "carbon neutral",
            "climate target",
            "zero emissions",
            "carbon neutrality",
            "net-zero",
            "deep decarbonization",
        ],
    )

    add_concept(
        g,
        "WholesaleMarketDomain",
        "wholesale market",
        "wholesale market (domain object)",
        (
            "A domainObject concept representing wholesale electricity market"
            " structure as measurement subject"
        ),
        do,
        [
            "wholesale market",
            "spot market",
            "day-ahead",
            "balancing market",
            "power exchange",
            "intraday market",
            "wholesale electricity",
        ],
    )

    add_concept(
        g,
        "GridReliabilityDomain",
        "grid reliability",
        "grid reliability (domain object)",
        (
            "A domainObject concept representing grid reliability and"
            " resilience as measurement subject"
        ),
        do,
        [
            "grid reliability",
            "outage",
            "blackout",
            "brownout",
            "SAIDI",
            "SAIFI",
            "grid stability",
            "power outage",
            "grid resilience",
            "system reliability",
        ],
    )

    add_concept(
        g,
        "VirtualPowerPlantDomain",
        "virtual power plant",
        "virtual power plant (domain object)",
        (
            "A domainObject concept representing virtual power plant"
            " aggregation as measurement subject"
        ),
        do,
        [
            "virtual power plant",
            "VPP",
            "aggregator",
            "demand aggregation",
            "distributed energy resource",
        ],
    )

    add_concept(
        g,
        "EnergyAccessDomain",
        "energy access",
        "energy access (domain object)",
        (
            "A domainObject concept representing energy access and"
            " electrification as measurement subject"
        ),
        do,
        [
            "energy access",
            "electrification",
            "electricity access",
            "universal access",
            "rural electrification",
        ],
    )

    add_concept(
        g,
        "EnergyPovertyDomain",
        "energy poverty",
        "energy poverty (domain object)",
        (
            "A domainObject concept representing energy poverty and"
            " affordability as measurement subject"
        ),
        do,
        [
            "energy poverty",
            "fuel poverty",
            "energy affordability",
            "heating poverty",
            "energy burden",
        ],
    )

    print("  Added 8 DomainObject concepts")

    # -- MeasuredPropertyScheme (3 new concepts) --
    mp = SEVOCAB["MeasuredPropertyScheme"]

    add_concept(
        g,
        "CapacityFactorMeasure",
        "capacity factor",
        "capacity factor (measured property)",
        (
            "A measuredProperty concept representing the ratio of actual"
            " output to maximum possible output"
        ),
        mp,
        [
            "capacity factor",
            "load factor",
            "utilization rate",
            "availability factor",
            "CF",
            "plant factor",
        ],
    )

    add_concept(
        g,
        "DeploymentMeasure",
        "deployment",
        "deployment (measured property)",
        ("A measuredProperty concept representing the rate of new infrastructure installation"),
        mp,
        [
            "deployment",
            "additions",
            "new build",
            "commissioning",
            "coming online",
            "new capacity",
            "installed additions",
            "new installations",
        ],
    )

    add_concept(
        g,
        "DecommissioningMeasure",
        "decommissioning",
        "decommissioning (measured property)",
        ("A measuredProperty concept representing the removal of infrastructure from service"),
        mp,
        [
            "decommissioning",
            "retirement",
            "phase-out",
            "shutdown",
            "closure",
            "retired capacity",
            "plant closure",
            "coal phase-out",
        ],
    )

    print("  Added 3 MeasuredProperty concepts")

    # ═══════════════════════════════════════════════════════════
    # Work Stream 3: Surface form enrichment
    # ═══════════════════════════════════════════════════════════
    print("\nWork Stream 3: Surface form enrichment")

    enrich(
        g,
        "Nuclear",
        [
            "SMR",
            "small modular reactor",
            "advanced nuclear",
            "Gen IV",
            "Generation IV",
            "micro reactor",
            "advanced reactor",
        ],
    )

    enrich(
        g,
        "NaturalGas",
        [
            "LNG",
            "liquefied natural gas",
            "gas pipeline",
            "gas infrastructure",
            "shale gas",
            "gas-fired",
        ],
    )

    enrich(
        g,
        "NaturalGasDomain",
        [
            "LNG",
            "liquefied natural gas",
            "gas pipeline",
            "gas infrastructure",
            "gas storage",
        ],
    )

    enrich(
        g,
        "SolarPv",
        [
            "rooftop solar",
            "utility-scale solar",
            "community solar",
            "floating solar",
            "agrivoltaic",
            "bifacial",
            "solar farm",
            "solar installation",
        ],
    )

    enrich(
        g,
        "OffshoreWind",
        [
            "floating wind",
            "floating offshore",
            "bottom-fixed",
            "floating offshore wind",
        ],
    )

    enrich(
        g,
        "Battery",
        [
            "grid-scale battery",
            "utility-scale battery",
            "behind-the-meter battery",
            "residential battery",
            "grid-scale storage",
        ],
    )

    enrich(
        g,
        "TransportDomain",
        [
            "electric vehicle",
            "e-mobility",
            "zero-emission vehicle",
            "ZEV",
            "plug-in hybrid",
            "PHEV",
            "BEV",
            "battery electric vehicle",
        ],
    )

    enrich(
        g,
        "GridDomain",
        [
            "grid reliability",
            "frequency regulation",
            "ancillary services",
            "grid operator",
            "TSO",
            "DSO",
            "transmission system operator",
        ],
    )

    enrich(
        g,
        "PriceMeasure",
        [
            "LCOE",
            "levelized cost",
            "wholesale price",
            "spot price",
            "day-ahead price",
            "strike price",
            "contract price",
        ],
    )

    enrich(
        g,
        "BatteryStorageDomain",
        [
            "grid-scale storage",
            "utility-scale battery storage",
            "stationary storage",
            "long-duration storage",
        ],
    )

    enrich(
        g,
        "ElectricityDomain",
        [
            "power system",
            "power sector",
            "electricity sector",
            "electricity system",
            "electric grid",
        ],
    )

    enrich(
        g,
        "DimensionlessUnit",
        [
            "ratio",
            "index",
            "fraction",
            "factor",
            "coefficient",
        ],
    )

    enrich(
        g,
        "IntensityUnit",
        [
            "carbon intensity",
            "emission factor",
            "emission intensity",
            "gCO2/kWh",
            "tCO2/MWh",
            "kg CO2/MWh",
        ],
    )

    # ═══════════════════════════════════════════════════════════
    # Serialize
    # ═══════════════════════════════════════════════════════════
    g.serialize(destination=str(VOCAB_FILE), format="turtle")

    # Count results
    from rdflib.namespace import SKOS as SK

    concepts = list(g.subjects(SK.inScheme, None))
    alts = list(g.triples((None, SK.altLabel, None)))
    print(f"\nTotal: {len(concepts)} concepts, {len(alts)} altLabels")
    print(f"Saved: {VOCAB_FILE}")


if __name__ == "__main__":
    main()
