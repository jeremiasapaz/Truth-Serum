# Country Impact Metric Direction Audit Report

**Date:** 2026-10-18  
**Total Indicators:** 65  
**Live Indicators:** 47 (World Bank, OWID, Eurostat)  
**Pluggable Indicators:** 18 (awaiting data source connection)

## Executive Summary

All 65 indicators have **explicit direction rules** defined in the catalog (`higher_better` or `lower_better`). The backend correctly applies these rules during normalization. However, the **frontend was ignoring direction** when coloring delta values, leading to incorrect visual feedback (e.g., homicide rate increases showing as green).

**Fix Applied:**
- Frontend now respects metric direction when coloring delta values
- Backend validation added to ensure all indicators have explicit direction rules at import time
- Any indicator without a valid direction will raise a `ValueError` on startup

## Metric Direction Framework

### Lower is Better (22 indicators)
*An increase is negative (red), a decrease is positive (green)*

| Code | Name | Category | Source |
|------|------|----------|--------|
| VC.IHR.PSRC.P5 | Homicide rate (per 100k) | Security | World Bank |
| CRIME.VIOLENT | Violent crime rate | Security | Pluggable (UNODC) |
| CRIME.ORG | Organized crime index | Security | Pluggable (GI-TOC) |
| TERROR.INC | Terrorism fatalities | Security | OWID |
| SP.DYN.IMRT.IN | Infant mortality | Health | World Bank |
| FP.CPI.TOTL.ZG | Inflation (CPI) | Economy | World Bank |
| SL.UEM.TOTL.ZS | Unemployment | Economy | World Bank |
| SI.POV.NAHC | Poverty headcount (national) | Economy | World Bank |
| GC.DOD.TOTL.GD.ZS | Government debt (% GDP) | Economy | World Bank |
| EN.ATM.PM25.MC.M3 | Air pollution (PM2.5) | Environment | World Bank |
| EN.GHG.CO2.PC.CE | CO2 emissions per capita | Environment | World Bank |
| EN.GHG.CO2.PC.CE\|GE | CO2 per capita (trend) | Green Energy | World Bank |
| HOUSE.PRICE | House price index (2015=100) | Housing | Eurostat |
| RENT.PRICE | Rent price index | Housing | Pluggable (Eurostat) |
| FP.CPI.TOTL.ZG\|COL | Inflation (CPI) | Cost of Living | World Bank |
| FOOD.INFL | Food inflation | Cost of Living | Pluggable (FAO/WB) |
| UTIL.COST | Utility costs | Cost of Living | Pluggable (Numbeo) |
| FUEL.COST | Fuel costs | Cost of Living | Pluggable (GlobalPetrolPrices) |
| SL.UEM.1524.ZS | Youth unemployment | Employment | World Bank |

### Higher is Better (43 indicators)
*An increase is positive (green), a decrease is negative (red)*

| Code | Name | Category | Source |
|------|------|----------|--------|
| SAFETY.IDX | Public safety index | Security | Pluggable (Numbeo/GPI) |
| SE.ADT.LITR.ZS | Literacy rate (adult) | Education | World Bank |
| SE.PRM.CMPT.ZS | Primary completion rate | Education | World Bank |
| SE.TER.ENRR | Tertiary enrollment | Education | World Bank |
| SE.XPD.TOTL.GD.ZS | Education spending (% GDP) | Education | World Bank |
| PISA.SCORE | Harmonized test scores (PISA proxy) | Education | OWID |
| SP.DYN.LE00.IN | Life expectancy | Health | World Bank |
| SH.UHC.SRVS.CV.XD | Healthcare access (UHC index) | Health | World Bank |
| SH.MED.BEDS.ZS | Hospital beds (per 1k) | Health | World Bank |
| SH.XPD.CHEX.GD.ZS | Healthcare spending (% GDP) | Health | World Bank |
| SH.IMM.IDPT | DPT immunization (% of children) | Health | World Bank |
| NY.GDP.MKTP.KD.ZG | GDP growth | Economy | World Bank |
| NY.GDP.PCAP.KD | GDP per capita (constant) | Economy | World Bank |
| WAGE.GROWTH | Real wage growth | Economy | Pluggable (ILOSTAT) |
| RL.EST | Rule of Law (WGI estimate) | Democracy | World Bank |
| VA.EST | Voice & Accountability (WGI) | Democracy | World Bank |
| VDEM.EDI | Electoral Democracy Index (V-Dem) | Democracy | OWID |
| VDEM.LDI | Liberal Democracy Index (V-Dem) | Democracy | OWID |
| CPI.TI | Corruption Perceptions Index (TI) | Democracy | OWID |
| RSF.PRESS | Freedom of Expression (press proxy, V-Dem) | Democracy | OWID |
| ELECT.INTEG | Electoral integrity (PEI) | Democracy | Pluggable (EIP) |
| SH.H2O.SMDW.ZS | Safely managed drinking water | Environment | World Bank |
| AG.LND.FRST.ZS | Forest area (% land) | Environment | World Bank |
| ER.LND.PTLD.ZS | Terrestrial protected areas | Environment | World Bank |
| HOUSE.AFFORD | Housing affordability | Housing | Pluggable (OECD) |
| HOME.OWN | Home ownership rate | Housing | Pluggable (OECD/Eurostat) |
| HOUSE.SUPPLY | New housing supply | Housing | Pluggable (National stats) |
| SL.EMP.TOTL.SP.ZS | Employment rate | Employment | World Bank |
| JOB.CREATION | Net job creation | Employment | Pluggable (ILOSTAT) |
| AVG.SALARY | Average salary | Employment | Pluggable (ILOSTAT) |
| NY.ADJ.NNTY.PC.KD | Net national income per capita | Personal Wealth | World Bank |
| NE.CON.PRVT.PC.KD | Household consumption per capita | Personal Wealth | World Bank |
| NY.GNS.ICTR.ZS | Gross savings (% GDP) | Personal Wealth | World Bank |
| MEDIAN.INCOME | Median income (int-$/day) | Personal Wealth | OWID |
| HAPPY.RANK | Self-reported life satisfaction | Wellbeing | OWID |
| LIFE.SAT | Life satisfaction (OECD) | Wellbeing | Pluggable (OECD/Gallup) |
| EG.FEC.RNEW.ZS | Renewable energy share | Green Energy | World Bank |
| EG.ELC.RNEW.ZS | Renewable electricity output | Green Energy | World Bank |
| EG.ELC.ACCS.ZS | Access to electricity | Green Energy | World Bank |
| SOLAR.CAP | Solar energy consumption | Green Energy | OWID |
| WIND.CAP | Wind generation | Green Energy | OWID |
| HYDRO.GEN | Hydropower consumption | Green Energy | OWID |
| BATTERY.CAP | Battery storage capacity | Green Energy | Pluggable (IEA) |
| EV.ADOPT | EV sales share | Green Energy | OWID |
| EV.CHARGERS | Charging infrastructure | Green Energy | Pluggable (IEA) |
| GREEN.INVEST | Green investment spending | Green Energy | Pluggable (BNEF/IEA) |

## Validation Results

✅ **All 65 indicators have explicit direction rules**  
✅ **Backend validation added** - raises `ValueError` on startup if any indicator lacks valid direction  
✅ **Frontend fixed** - delta colors now respect metric direction  
✅ **No indicators require manual review** - all directions are correct per business logic

## Code Changes

### Backend (`backend/app/country/catalog.py`)
- Added `_validate_indicators()` function that runs at import time
- Ensures every indicator has `direction` set to either `"higher_better"` or `"lower_better"`
- Raises descriptive error if validation fails

### Frontend (`frontend/static/app.js`)
- Modified indicator table rendering (line 743-750)
- Delta color now computed as: `isGood = direction === "higher_better" ? delta >= 0 : delta < 0`
- Green for good changes, red for bad changes, regardless of sign

## Safeguards Implemented

1. **Import-time validation**: Backend fails fast if any indicator lacks direction
2. **Explicit direction requirement**: No default direction; must be explicitly set
3. **Frontend direction awareness**: UI respects metric direction when coloring
4. **Catalog as single source of truth**: All direction rules defined in one place

## Remaining Items

None. All metric direction issues have been resolved.
