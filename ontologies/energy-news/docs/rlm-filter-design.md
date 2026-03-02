# SkyGent Energy Domain Filter — Complete Deliverable

**Filter Name:** Energy Domain Signal Filter v1.0
**Architecture:** `(ENERGY_FOCUSED_AUTHORS) OR (GENERAL_AUTHORS AND ENERGY_SIGNAL)`
**DSL Version:** SkyGent CLI DSL
**Prepared by:** Energy Domain Expert / SkyGent Filter Designer
**Status:** Production-Ready

---

## 1. COMPLETE FILTER EXPRESSION

Copy the block below verbatim into the SkyGent CLI.

```
(
  authorin:electrek.bsky.social,canarymedia.bsky.social,utilitydive.bsky.social,energynews.bsky.social,rechargenews.bsky.social,pv-magazine.bsky.social,windpowermonthly.bsky.social,spglobal.bsky.social,energymonitor.bsky.social,oilprice.bsky.social
)
OR
(
  authorin:bloomberg.bsky.social,economist.bsky.social,npr.bsky.social,reuters.bsky.social,apnews.bsky.social,ft.bsky.social,wsj.bsky.social,nytimes.bsky.social,theguardian.bsky.social,politico.bsky.social,axios.bsky.social
  AND
  (

    hashtagin:#solar,#wind,#renewables,#cleanenergy,#EV,#EVs,#electricvehicles,#heatpump,#heatpumps,#nuclear,#hydrogen,#naturalgas,#LNG,#coal,#offshorewind,#onshorewind,#BESS,#geothermal,#energystorage,#gridmodernization,#netzero,#decarbonization,#climatechange,#carbonemissions,#energypolicy,#IRA,#FERC,#energytransition,#cleanpower,#powergrid,#electricgrid,#energysecurity,#criticalMinerals,#carbonmarkets,#carboncapture,#CCS,#DAC,#energyefficiency,#rooftopsolar,#communitysolar,#agrivoltaics,#perovskite,#SMR,#fusion,#greenenergy,#sustainability,#energyaccess,#energyjustice,#energypoverty,#electrification,#EVcharging,#biomass,#bioenergy,#offshore,#onshore,#interconnection,#transmission,#microgrid,#DER,#energyfinance,#projectfinance,#cleantech

    OR

    link-contains:electrek.co
    OR link-contains:canarymedia.com
    OR link-contains:utilitydive.com
    OR link-contains:rechargenews.com
    OR link-contains:pv-magazine.com
    OR link-contains:windpowermonthly.com
    OR link-contains:energymonitor.ai
    OR link-contains:oilprice.com
    OR link-contains:woodmac.com
    OR link-contains:iea.org
    OR link-contains:eia.gov
    OR link-contains:energy.gov
    OR link-contains:ferc.gov
    OR link-contains:irena.org
    OR link-contains:nrel.gov
    OR link-contains:greentechmedia.com
    OR link-contains:renewableenergyworld.com
    OR link-contains:cleantechnica.com
    OR link-contains:insideclimatenews.org
    OR link-contains:rtoinsider.com
    OR link-contains:powermag.com
    OR link-contains:energyintel.com
    OR link-contains:platts.com
    OR link-contains:bnef.com
    OR link-contains:carbonbrief.org
    OR link-contains:climatewire.com
    OR link-contains:eenews.net

    OR

    contains:"solar power"
    OR contains:"solar energy"
    OR contains:"solar panel"
    OR contains:"solar farm"
    OR contains:"solar capacity"
    OR contains:"solar installation"
    OR contains:"rooftop solar"
    OR contains:"utility-scale solar"
    OR contains:"distributed solar"
    OR contains:"agrivoltaic"
    OR contains:"agrivoltaics"
    OR contains:"perovskite solar"
    OR contains:"photovoltaic"
    OR contains:"solar efficiency"
    OR contains:"solar cell"
    OR contains:"solar module"
    OR contains:"solar project"
    OR contains:"solar developer"
    OR contains:"solar inverter"

    OR contains:"wind power"
    OR contains:"wind energy"
    OR contains:"wind farm"
    OR contains:"wind turbine"
    OR contains:"offshore wind"
    OR contains:"onshore wind"
    OR contains:"floating wind"
    OR contains:"wind capacity"
    OR contains:"wind project"
    OR contains:"wind developer"

    OR contains:"geothermal"
    OR contains:"hydroelectric"
    OR contains:"pumped hydro"
    OR contains:"pumped storage"
    OR contains:"run-of-river"

    OR contains:"energy storage"
    OR contains:"battery storage"
    OR contains:"BESS"
    OR contains:"long duration storage"
    OR contains:"long-duration storage"
    OR contains:"long duration energy storage"
    OR contains:"battery recycling"
    OR contains:"second life battery"
    OR contains:"battery circular"
    OR contains:"grid-scale battery"
    OR contains:"grid scale battery"
    OR contains:"lithium-ion"
    OR contains:"lithium ion battery"
    OR contains:"flow battery"
    OR contains:"iron-air battery"
    OR contains:"sodium battery"

    OR contains:"coal power"
    OR contains:"coal plant"
    OR contains:"coal-fired"
    OR contains:"coal mine"
    OR contains:"coal phase"
    OR contains:"coal retirement"
    OR contains:"thermal coal"
    OR contains:"coal capacity"

    OR contains:"natural gas"
    OR contains:"LNG terminal"
    OR contains:"liquefied natural gas"
    OR contains:"gas pipeline"
    OR contains:"gas plant"
    OR contains:"gas-fired"
    OR contains:"gas peaker"
    OR contains:"LNG trade"
    OR contains:"LNG export"
    OR contains:"LNG import"
    OR contains:"LNG price"
    OR contains:"LNG supply"
    OR contains:"gas prices"
    OR contains:"gas price"

    OR contains:"crude oil"
    OR contains:"oil refinery"
    OR contains:"oil pipeline"
    OR contains:"oil price"
    OR contains:"oil production"
    OR contains:"oil demand"
    OR contains:"oil supply"
    OR contains:"oil futures"
    OR contains:"oil market"
    OR contains:"OPEC"
    OR contains:"petroleum"
    OR contains:"oil and gas"
    OR contains:"upstream oil"
    OR contains:"downstream oil"
    OR contains:"oil sanctions"

    OR contains:"nuclear power"
    OR contains:"nuclear plant"
    OR contains:"nuclear reactor"
    OR contains:"nuclear energy"
    OR contains:"nuclear capacity"
    OR contains:"small modular reactor"
    OR contains:"SMR"
    OR contains:"fusion energy"
    OR contains:"nuclear fusion"
    OR contains:"fission"
    OR contains:"uranium"
    OR contains:"nuclear waste"
    OR contains:"nuclear license"
    OR contains:"nuclear decommission"

    OR contains:"green hydrogen"
    OR contains:"blue hydrogen"
    OR contains:"electrolytic hydrogen"
    OR contains:"hydrogen production"
    OR contains:"hydrogen fuel"
    OR contains:"hydrogen economy"
    OR contains:"hydrogen pipeline"
    OR contains:"hydrogen storage"
    OR contains:"electrolyzer"
    OR contains:"fuel cell"
    OR contains:"hydrogen hub"

    OR regex:/\b(power grid|electric grid|grid operator|grid modernization|smart grid|grid stability|grid reliability|grid connection|grid capacity|grid-scale|grid flexibility|grid resilience|grid congestion|grid upgrade|grid expansion|grid investment|grid security)\b/i
    OR contains:"transmission line"
    OR contains:"transmission capacity"
    OR contains:"high-voltage"
    OR contains:"power transmission"
    OR contains:"electricity transmission"
    OR contains:"transmission grid"
    OR contains:"transmission infrastructure"
    OR contains:"distribution network"
    OR contains:"distribution grid"
    OR contains:"local grid"
    OR contains:"power line"
    OR contains:"electricity grid"
    OR contains:"advanced metering"
    OR contains:"independent system operator"
    OR contains:"regional transmission"
    OR contains:"RTO"
    OR contains:"CAISO"
    OR contains:"MISO"
    OR contains:"ERCOT"
    OR contains:"PJM"
    OR contains:"NYISO"
    OR contains:"FERC"
    OR contains:"grid interconnection"
    OR contains:"interconnection queue"
    OR contains:"microgrid"
    OR contains:"virtual power plant"
    OR contains:"demand response"
    OR contains:"distributed energy"
    OR contains:"DER"

    OR contains:"electric vehicle"
    OR contains:"electric car"
    OR contains:"EV battery"
    OR contains:"EV charging"
    OR contains:"EV charger"
    OR contains:"charging station"
    OR contains:"charging infrastructure"
    OR contains:"charging network"
    OR contains:"battery electric"
    OR contains:"plug-in hybrid"
    OR contains:"BEV"
    OR contains:"heat pump"
    OR contains:"heat pumps"
    OR contains:"building electrification"
    OR contains:"gas to electric"
    OR contains:"building retrofit"
    OR contains:"deep retrofit"
    OR contains:"electric bus"
    OR contains:"electric truck"
    OR contains:"electric ferry"
    OR contains:"electric ship"
    OR contains:"e-mobility"
    OR contains:"electric aviation"
    OR contains:"electric flight"

    OR contains:"greenhouse gas"
    OR contains:"GHG"
    OR contains:"carbon emissions"
    OR contains:"CO2 emissions"
    OR contains:"net zero"
    OR contains:"net-zero"
    OR contains:"decarbonization"
    OR contains:"decarbonise"
    OR contains:"decarbonize"
    OR contains:"carbon neutral"
    OR contains:"carbon footprint"
    OR contains:"emissions trading"
    OR contains:"carbon credits"
    OR contains:"carbon credit"
    OR contains:"cap-and-trade"
    OR contains:"carbon market"
    OR contains:"carbon price"
    OR contains:"carbon tax"
    OR contains:"carbon capture"
    OR contains:"CCS"
    OR contains:"CCUS"
    OR contains:"direct air capture"
    OR contains:"DAC"
    OR contains:"carbon removal"
    OR contains:"climate summit"
    OR contains:"COP30"
    OR contains:"COP29"
    OR contains:"COP28"
    OR contains:"UNFCCC"
    OR contains:"Paris Agreement"
    OR contains:"climate target"
    OR contains:"emissions target"
    OR contains:"emissions reduction"
    OR contains:"scope 3"
    OR contains:"scope 1"
    OR contains:"scope 2"

    OR contains:"energy policy"
    OR contains:"clean energy policy"
    OR contains:"Inflation Reduction Act"
    OR contains:"clean energy standard"
    OR contains:"renewable portfolio standard"
    OR contains:"clean electricity"
    OR contains:"energy regulation"
    OR contains:"energy legislation"
    OR contains:"energy bill"
    OR contains:"energy law"
    OR contains:"energy subsidy"
    OR contains:"energy incentive"
    OR contains:"energy tax credit"
    OR contains:"production tax credit"
    OR contains:"investment tax credit"
    OR contains:"Energiewende"
    OR contains:"German energy transition"
    OR contains:"energy permitting"
    OR contains:"permitting reform"
    OR contains:"energy tariff"
    OR contains:"energy sanctions"
    OR contains:"energy trade"
    OR contains:"clean energy transition"
    OR contains:"energy transition"

    OR contains:"energy market"
    OR contains:"power market"
    OR contains:"electricity market"
    OR contains:"wholesale electricity"
    OR contains:"wholesale power"
    OR contains:"power purchase agreement"
    OR contains:"PPA"
    OR contains:"project finance"
    OR contains:"clean energy finance"
    OR contains:"energy investment"
    OR contains:"energy funding"
    OR contains:"energy grant"
    OR contains:"energy loan"
    OR contains:"clean energy investment"
    OR contains:"renewable energy investment"
    OR contains:"energy acquisition"
    OR contains:"energy merger"
    OR contains:"energy company acquisition"
    OR contains:"energy startup"
    OR contains:"energy IPO"

    OR contains:"sustainable aviation fuel"
    OR contains:"aviation decarbonization"
    OR contains:"electric aircraft"
    OR contains:"e-fuel"
    OR contains:"SAF"
    OR contains:"maritime decarbonization"
    OR contains:"ammonia fuel"
    OR contains:"green ammonia"
    OR contains:"industrial decarbonization"
    OR contains:"steel decarbonization"
    OR contains:"cement decarbonization"
    OR contains:"green steel"
    OR contains:"green cement"
    OR contains:"hard-to-abate"

    OR contains:"data center energy"
    OR contains:"AI energy"
    OR contains:"AI power demand"
    OR contains:"data center power"
    OR contains:"AI electricity"
    OR contains:"data center electricity"
    OR contains:"hyperscale"
    OR contains:"AI and energy"
    OR contains:"energy demand from AI"

    OR contains:"energy security"
    OR contains:"energy independence"
    OR contains:"energy resilience"
    OR contains:"energy geopolitics"
    OR contains:"critical minerals"
    OR contains:"critical mineral"
    OR contains:"cobalt supply"
    OR contains:"lithium supply"
    OR contains:"rare earth"
    OR contains:"energy supply chain"
    OR contains:"clean energy supply chain"
    OR contains:"energy blackout"
    OR contains:"power outage"
    OR contains:"grid outage"

    OR contains:"energy justice"
    OR contains:"energy equity"
    OR contains:"energy poverty"
    OR contains:"energy bills"
    OR contains:"electricity bills"
    OR contains:"electricity rates"
    OR contains:"electricity rate"
    OR contains:"utility bills"
    OR contains:"energy affordability"
    OR contains:"community solar"
    OR contains:"community energy"
    OR contains:"cooperative energy"
    OR contains:"energy access"
    OR contains:"energy burden"

    OR contains:"clean energy jobs"
    OR contains:"energy jobs"
    OR contains:"renewable energy jobs"
    OR contains:"solar jobs"
    OR contains:"wind jobs"
    OR contains:"energy workers"
    OR contains:"energy unions"
    OR contains:"energy manufacturing"
    OR contains:"clean energy manufacturing"
    OR contains:"battery manufacturing"
    OR contains:"EV manufacturing"
    OR contains:"solar manufacturing"
    OR contains:"wind manufacturing"
    OR contains:"gigafactory"

    OR contains:"environmental impact"
    OR contains:"land use"
    OR contains:"energy waste"
    OR contains:"cooling water"
    OR contains:"water use"
    OR contains:"wildlife"
    OR contains:"biodiversity"

    OR contains:"energy research"
    OR contains:"energy innovation"
    OR contains:"energy R&D"
    OR contains:"clean energy research"
    OR contains:"biomass energy"
    OR contains:"bioenergy"
    OR contains:"biofuel"
    OR contains:"renewable energy record"
    OR contains:"energy breakthrough"
    OR contains:"energy patent"

  )
)
```

---

## 2. COMPONENT BREAKDOWN

### A. Energy-Focused Author Pass-Through (10 Handles)

These 10 accounts are **dedicated energy trade and specialist media outlets**. Their entire editorial mandate is energy coverage. Every post they publish — whether a headline, a data point, a link share, or a thread — is presumed to be energy-relevant content. They require **no additional signal qualification**; the author identity is itself a sufficient condition for inclusion.

| Handle | Publication | Coverage Focus |
|---|---|---|
| `electrek.bsky.social` | Electrek | EVs, clean energy, Tesla, solar |
| `canarymedia.bsky.social` | Canary Media | Clean energy transition journalism |
| `utilitydive.bsky.social` | Utility Dive | Utility sector, grid, regulation |
| `energynews.bsky.social` | Energy News Network | Regional clean energy journalism |
| `rechargenews.bsky.social` | Recharge News | Wind, solar, hydrogen, storage |
|
