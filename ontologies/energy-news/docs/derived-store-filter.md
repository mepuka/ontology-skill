# Energy News Derived Store Filter

**Store:** `energy-news-filtered` (derived from `energy-news`)
**Architecture:** `(ENERGY_FOCUSED_AUTHORS) OR (NOT_ENERGY_FOCUSED AND ENERGY_SIGNAL)`
**Created:** 2026-02-28
**Result:** 34,646 posts (33.0% of 104,994 source posts)

## Filter Design

The filter uses a two-tier approach:

1. **Energy-focused authors pass-through** (74 handles) — all posts from dedicated
   energy/climate publications and energy journalists are included without additional
   signal filtering. These authors' editorial mandate is energy coverage.

2. **Energy signal filter** — for all other authors (general outlets like Bloomberg,
   Economist, NPR, Reuters, etc. + feed-discovered accounts), posts must match at
   least one energy signal: an energy hashtag, a link to an energy publication, or
   an energy keyword phrase in the post text.

## Filtering Results

| Source Category | Original | Filtered | Keep Rate |
|-----------------|----------|----------|-----------|
| Energy-focused (74 handles) | 26,603 | 26,603 | 100% |
| General outlets (17 handles) | 64,770 | 3,742 | 5.8% |
| Feed-sourced other (6,319 handles) | 13,621 | 4,301 | 31.6% |
| **Total** | **104,994** | **34,646** | **33.0%** |

### General Outlet Breakdown

| Author | Original | Filtered | Keep% |
|--------|----------|----------|-------|
| bloomberg.com | 20,354 | 861 | 4.2% |
| economist.com | 18,839 | 212 | 1.1% |
| npr.org | 13,570 | 225 | 1.7% |
| reuters.com | 5,155 | 1,244 | 24.1% |
| theguardian.com | 1,545 | 166 | 10.7% |
| nytimes.com | 1,510 | 317 | 21.0% |
| washingtonpost.com | 893 | 185 | 20.7% |
| apnews.com | 600 | 96 | 16.0% |
| latimes.com | 565 | 82 | 14.5% |
| cnbc.com | 540 | 124 | 23.0% |
| wired.com | 420 | 83 | 19.8% |
| politico.com | 307 | 60 | 19.5% |
| axios.com | 153 | 22 | 14.4% |
| arstechnica.com | 148 | 34 | 23.0% |
| vox.com | 82 | 18 | 22.0% |
| thehill.com | 62 | 10 | 16.1% |
| financialtimes.com | 27 | 3 | 11.1% |

## Energy-Focused Author Handles (74)

These authors pass through with no additional filtering:

```
abbiebennett.bsky.social, akshatrathi.bsky.social, aleach.ca,
alicemhancock.bsky.social, altenergy.bsky.social,
anikanpatel.carbonbrief.org, bigearthdata.ai, brianscheid.bsky.social,
campbellenergy.bsky.social, canarymedia.com, carbonbrief.org,
chelseaeharvey.bsky.social, ckemfert.bsky.social, cleanenergy.org,
cleanenergywire.bsky.social, cleantechnica.bsky.social,
climatenews.bsky.social, costasamaras.com, drpauldorfman.bsky.social,
drsimevans.carbonbrief.org, earthsciinfo.bsky.social, electrek.co,
enerdata.bsky.social, energyinnovation.org, energylawjeff.bsky.social,
energyvoice.com, ethanhowl.bsky.social, euenergy.bsky.social,
gasbuddyguy.bsky.social, gavinjmaguire.bsky.social, greencollective.io,
grist.org, gruberte.bsky.social, hannahdaly.ie, hanseric.bsky.social,
hausfath.bsky.social, heatmap.news, iea.org, insideclimatenews.org,
insideevs.com, janrosenow.bsky.social, javierblas.bsky.social,
jeffstjohn.bsky.social, jessedjenkins.com, jrfhanger.bsky.social,
justingerdes.bsky.social, ketanjoshi.co, latitudemedia.bsky.social,
leohickman.carbonbrief.org, liamdenning.bsky.social, longtail.news,
lovering.bsky.social, mikemunsell.bsky.social, nathanielbullard.com,
opinion.bloomberg.com, patrickgaley.bsky.social, rebleber.bsky.social,
renewableenergy.bsky.social, robinsonmeyer.bsky.social,
rtoinsider.bsky.social, sammyroth.bsky.social,
severinborenstein.bsky.social, shedrills.bsky.social,
sjcasey.bsky.social, sstapczynski.bsky.social, thedriven.io,
theenergymix.com, torsolarfred.bsky.social,
ucenergyinstitute.bsky.social, volts.wtf, wettengel.bsky.social,
windpowermonthly.bsky.social, worldnuclearnews.bsky.social,
yalee360.bsky.social
```

## Energy Signal Components

### Hashtags (82)

```
#solar, #wind, #renewables, #cleanenergy, #EV, #EVs, #electricvehicles,
#heatpump, #heatpumps, #nuclear, #hydrogen, #naturalgas, #LNG, #coal,
#offshorewind, #onshorewind, #BESS, #geothermal, #energystorage,
#gridmodernization, #netzero, #decarbonization, #climatechange,
#carbonemissions, #energypolicy, #IRA, #FERC, #energytransition,
#cleanpower, #powergrid, #electricgrid, #energysecurity,
#criticalMinerals, #carbonmarkets, #carboncapture, #CCS, #DAC,
#energyefficiency, #rooftopsolar, #communitysolar, #agrivoltaics,
#perovskite, #SMR, #fusion, #greenenergy, #sustainability,
#energyaccess, #energyjustice, #energypoverty, #electrification,
#EVcharging, #biomass, #bioenergy, #offshore, #onshore,
#interconnection, #transmission, #microgrid, #DER, #energyfinance,
#projectfinance, #cleantech, #energy, #oil, #gas, #OPEC, #climate,
#grid, #battery, #lithium, #uranium, #powerplant, #electricity,
#carbon, #emissions, #methane, #fossilfuels, #oilandgas,
#greenhydrogen, #solarenergy, #windenergy, #windpower, #solarpower,
#nuclearenergy, #nuclearpower
```

### Link Domains (34)

Energy publication domains matched via `link-contains:`:

```
electrek.co, canarymedia.com, utilitydive.com, rechargenews.com,
pv-magazine.com, windpowermonthly.com, energymonitor.ai, oilprice.com,
woodmac.com, iea.org, eia.gov, energy.gov, ferc.gov, irena.org,
nrel.gov, greentechmedia.com, renewableenergyworld.com,
cleantechnica.com, insideclimatenews.org, rtoinsider.com, powermag.com,
energyintel.com, platts.com, bnef.com, carbonbrief.org, eenews.net,
heatmap.news, grist.org, thedriven.io, volts.wtf, canary.media,
latitudemedia.com, insideevs.com, energyvoice.com
```

### Keyword Phrases (99)

Energy topic phrases matched via `contains:` (case-insensitive by default):

Solar, wind, storage, coal, gas, oil, nuclear, hydrogen, grid,
EVs/electrification, emissions/climate, policy/regulation,
markets/finance, transport/industrial, AI/data centers, security,
justice, manufacturing, environment, research.

## Reproduce

```bash
skygent derive energy-news energy-news-filtered --filter '(authorin:abbiebennett.bsky.social,...) OR (NOT authorin:... AND (hashtagin:... OR link-contains:... OR contains:...))'
```

Full filter expression saved at `/tmp/energy-filter.txt`.

## Related

- `rlm-filter-design.md` — Original RLM-generated filter design (used guessed Bluesky handles)
- `abox-ingestion-strategy.md` — ABox ingestion strategy document
