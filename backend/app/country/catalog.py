"""Indicator catalog for the Country Performance & Administration Impact Engine.

Every metric in the specification is listed here and mapped to a concrete,
traceable dataset. Metrics backed by the World Bank Open Data API are fetched
live (free, no key); metrics whose best source is not a free API (PISA, EIU
Democracy Index, RSF Press Freedom, World Happiness, housing/energy-capacity
series) are declared with `source=None` and marked `pluggable` so the catalog
stays complete and honest — add a collector to activate them.

direction: "higher_better" or "lower_better" (used to sign improvements).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Indicator:
    code: str            # internal code (World Bank code when available)
    name: str
    category: str        # performance/QoL/green group
    unit: str
    direction: str       # higher_better | lower_better
    source: str | None   # "worldbank" | "owid" | None (pluggable)
    dataset: str = ""
    provider_code: str = ""   # provider series id / OWID grapher slug
    pluggable_source: str = ""  # intended source if not yet wired
    col_index: int = 3        # OWID CSV value column index (Entity,Code,Year,<value>)


def WB(code, name, category, unit, direction, dataset="World Bank Open Data"):
    return Indicator(code=code, name=name, category=category, unit=unit,
                     direction=direction, source="worldbank", dataset=dataset,
                     provider_code=code)


def OWID(code, name, category, unit, direction, slug, col_index=3):
    return Indicator(code=code, name=name, category=category, unit=unit,
                     direction=direction, source="owid", dataset=f"Our World in Data: {slug}",
                     provider_code=slug, col_index=col_index)


def PLUG(code, name, category, unit, direction, src):
    return Indicator(code=code, name=name, category=category, unit=unit,
                     direction=direction, source=None, pluggable_source=src)


# ---------------------------------------------------------------------------
# Performance categories
# ---------------------------------------------------------------------------
INDICATORS: list[Indicator] = [
    # SECURITY
    WB("VC.IHR.PSRC.P5", "Homicide rate (per 100k)", "Security", "per 100k", "lower_better"),
    PLUG("CRIME.VIOLENT", "Violent crime rate", "Security", "per 100k", "lower_better", "UNODC"),
    PLUG("CRIME.ORG", "Organized crime index", "Security", "index", "lower_better", "GI-TOC"),
    PLUG("TERROR.INC", "Terrorism incidents", "Security", "count", "lower_better", "GTD"),
    PLUG("SAFETY.IDX", "Public safety index", "Security", "index", "higher_better", "Numbeo/GPI"),

    # EDUCATION
    WB("SE.ADT.LITR.ZS", "Literacy rate (adult)", "Education", "%", "higher_better"),
    WB("SE.PRM.CMPT.ZS", "Primary completion rate", "Education", "%", "higher_better"),
    WB("SE.TER.ENRR", "Tertiary enrollment", "Education", "% gross", "higher_better"),
    WB("SE.XPD.TOTL.GD.ZS", "Education spending (% GDP)", "Education", "% GDP", "higher_better"),
    PLUG("PISA.SCORE", "PISA score (mean)", "Education", "score", "higher_better", "OECD PISA"),

    # HEALTH
    WB("SP.DYN.LE00.IN", "Life expectancy", "Health", "years", "higher_better"),
    WB("SP.DYN.IMRT.IN", "Infant mortality", "Health", "per 1k births", "lower_better"),
    WB("SH.UHC.SRVS.CV.XD", "Healthcare access (UHC index)", "Health", "index", "higher_better"),
    WB("SH.MED.BEDS.ZS", "Hospital beds (per 1k)", "Health", "per 1k", "higher_better"),
    WB("SH.XPD.CHEX.GD.ZS", "Healthcare spending (% GDP)", "Health", "% GDP", "higher_better"),
    WB("SH.IMM.IDPT", "DPT immunization (% of children)", "Health", "%", "higher_better"),

    # ECONOMY
    WB("NY.GDP.MKTP.KD.ZG", "GDP growth", "Economy", "% annual", "higher_better"),
    WB("NY.GDP.PCAP.KD", "GDP per capita (constant)", "Economy", "USD", "higher_better"),
    WB("FP.CPI.TOTL.ZG", "Inflation (CPI)", "Economy", "% annual", "lower_better"),
    WB("SL.UEM.TOTL.ZS", "Unemployment", "Economy", "%", "lower_better"),
    WB("SI.POV.NAHC", "Poverty headcount (national)", "Economy", "%", "lower_better"),
    WB("GC.DOD.TOTL.GD.ZS", "Government debt (% GDP)", "Economy", "% GDP", "lower_better"),
    PLUG("WAGE.GROWTH", "Real wage growth", "Economy", "% annual", "higher_better", "ILOSTAT"),

    # DEMOCRACY
    WB("RL.EST", "Rule of Law (WGI estimate)", "Democracy", "z-score", "higher_better",
       dataset="World Bank Worldwide Governance Indicators"),
    WB("VA.EST", "Voice & Accountability (WGI)", "Democracy", "z-score", "higher_better",
       dataset="World Bank Worldwide Governance Indicators"),
    OWID("VDEM.EDI", "Electoral Democracy Index (V-Dem)", "Democracy", "0-1", "higher_better",
         "electoral-democracy-index"),
    PLUG("RSF.PRESS", "Press Freedom Index", "Democracy", "score", "higher_better", "RSF"),
    PLUG("ELECT.INTEG", "Electoral integrity (PEI)", "Democracy", "index", "higher_better", "EIP"),

    # ENVIRONMENT
    WB("EN.ATM.PM25.MC.M3", "Air pollution (PM2.5)", "Environment", "µg/m³", "lower_better"),
    WB("SH.H2O.SMDW.ZS", "Safely managed drinking water", "Environment", "% pop", "higher_better"),
    WB("AG.LND.FRST.ZS", "Forest area (% land)", "Environment", "% land", "higher_better"),
    WB("ER.LND.PTLD.ZS", "Terrestrial protected areas", "Environment", "% land", "higher_better"),
    WB("EN.GHG.CO2.PC.CE", "CO2 emissions per capita", "Environment", "t/capita", "lower_better"),

    # ---- QUALITY OF LIFE ----
    # HOUSING (mostly pluggable; WB has little housing time series)
    PLUG("HOUSE.PRICE", "House price index", "Housing", "index", "lower_better", "OECD/BIS"),
    PLUG("RENT.PRICE", "Rent price index", "Housing", "index", "lower_better", "Numbeo/Eurostat"),
    PLUG("HOUSE.AFFORD", "Housing affordability", "Housing", "ratio", "higher_better", "OECD"),
    PLUG("HOME.OWN", "Home ownership rate", "Housing", "%", "higher_better", "OECD/Eurostat"),
    PLUG("HOUSE.SUPPLY", "New housing supply", "Housing", "units", "higher_better", "National stats"),

    # COST OF LIVING
    WB("FP.CPI.TOTL.ZG|COL", "Inflation (CPI)", "Cost of Living", "% annual", "lower_better"),
    PLUG("FOOD.INFL", "Food inflation", "Cost of Living", "% annual", "lower_better", "FAO/WB"),
    PLUG("UTIL.COST", "Utility costs", "Cost of Living", "index", "lower_better", "Numbeo"),
    PLUG("FUEL.COST", "Fuel costs", "Cost of Living", "price", "lower_better", "GlobalPetrolPrices"),

    # EMPLOYMENT
    WB("SL.EMP.TOTL.SP.ZS", "Employment rate", "Employment", "%", "higher_better"),
    WB("SL.UEM.1524.ZS", "Youth unemployment", "Employment", "%", "lower_better"),
    PLUG("JOB.CREATION", "Net job creation", "Employment", "count", "higher_better", "ILOSTAT"),
    PLUG("AVG.SALARY", "Average salary", "Employment", "USD", "higher_better", "ILOSTAT"),

    # PERSONAL WEALTH
    WB("NY.ADJ.NNTY.PC.KD", "Net national income per capita", "Personal Wealth", "USD", "higher_better"),
    WB("NE.CON.PRVT.PC.KD", "Household consumption per capita", "Personal Wealth", "USD", "higher_better"),
    PLUG("MEDIAN.INCOME", "Median disposable income", "Personal Wealth", "USD", "higher_better", "OECD/LIS"),
    PLUG("SAVINGS.RATE", "Household savings rate", "Personal Wealth", "%", "higher_better", "OECD"),

    # WELLBEING
    OWID("HAPPY.RANK", "Self-reported life satisfaction", "Wellbeing", "0-10", "higher_better",
         "happiness-cantril-ladder"),
    PLUG("LIFE.SAT", "Life satisfaction (OECD)", "Wellbeing", "0-10", "higher_better", "OECD/Gallup"),

    # ---- GREEN ENERGY & SUSTAINABILITY ----
    WB("EG.FEC.RNEW.ZS", "Renewable energy share", "Green Energy", "% final energy", "higher_better"),
    WB("EG.ELC.RNEW.ZS", "Renewable electricity output", "Green Energy", "% of total", "higher_better"),
    WB("EG.ELC.ACCS.ZS", "Access to electricity", "Green Energy", "% pop", "higher_better"),
    WB("EN.GHG.CO2.PC.CE|GE", "CO2 per capita (trend)", "Green Energy", "t/capita", "lower_better"),
    OWID("SOLAR.CAP", "Solar energy consumption", "Green Energy", "TWh", "higher_better",
         "solar-energy-consumption"),
    PLUG("WIND.CAP", "Wind capacity", "Green Energy", "MW", "higher_better", "IRENA"),
    OWID("HYDRO.GEN", "Hydropower consumption", "Green Energy", "TWh", "higher_better",
         "hydropower-consumption"),
    PLUG("BATTERY.CAP", "Battery storage capacity", "Green Energy", "MWh", "higher_better", "IEA"),
    OWID("EV.ADOPT", "EV sales share", "Green Energy", "% new cars", "higher_better",
         "electric-car-sales-share"),
    PLUG("EV.CHARGERS", "Charging infrastructure", "Green Energy", "count", "higher_better", "IEA"),
    PLUG("GREEN.INVEST", "Green investment spending", "Green Energy", "USD", "higher_better", "BNEF/IEA"),
]

# ---------------------------------------------------------------------------
# Composite definitions
# ---------------------------------------------------------------------------
PERFORMANCE_CATEGORIES = ["Security", "Education", "Health", "Economy", "Democracy", "Environment"]
QOL_CATEGORIES = ["Housing", "Cost of Living", "Employment", "Personal Wealth", "Wellbeing"]
GREEN_CATEGORY = "Green Energy"

# Citizen Reality Score weights (sum ~1.0). Uses category scores where available.
CRS_WEIGHTS = {
    "Housing": 0.16,
    "Cost of Living": 0.18,
    "Health": 0.14,
    "Employment": 0.16,
    "Personal Wealth": 0.14,
    "Security": 0.12,
    "Wellbeing": 0.10,
}

# Sustainability sub-indices derived from the Green Energy category + environment.
SUSTAINABILITY_INDICES = {
    "Climate Action Index": ["EN.GHG.CO2.PC.CE|GE", "EG.FEC.RNEW.ZS", "EG.ELC.RNEW.ZS"],
    "Energy Independence Index": ["EG.ELC.ACCS.ZS", "EG.FEC.RNEW.ZS"],
    "Natural Resource Protection Index": ["AG.LND.FRST.ZS", "ER.LND.PTLD.ZS", "SH.H2O.SMDW.ZS"],
    "Citizen Sustainability Score": ["EN.ATM.PM25.MC.M3", "SH.H2O.SMDW.ZS", "EG.FEC.RNEW.ZS"],
    "Future Generations Index": ["EN.GHG.CO2.PC.CE|GE", "AG.LND.FRST.ZS", "SE.XPD.TOTL.GD.ZS"],
}

GEI_CODES = ["EG.FEC.RNEW.ZS", "EG.ELC.RNEW.ZS", "EG.ELC.ACCS.ZS", "EN.GHG.CO2.PC.CE|GE"]


def by_code() -> dict[str, Indicator]:
    return {i.code: i for i in INDICATORS}


def wb_indicators() -> list[Indicator]:
    return [i for i in INDICATORS if i.source == "worldbank"]


def owid_indicators() -> list[Indicator]:
    return [i for i in INDICATORS if i.source == "owid"]


def live_indicators() -> list[Indicator]:
    return [i for i in INDICATORS if i.source is not None]


def wb_series_codes() -> list[str]:
    """Distinct World Bank series ids (strips the internal |suffix aliases)."""
    seen = {}
    for i in wb_indicators():
        series = i.code.split("|")[0]
        seen[series] = True
    return list(seen)


def categories_of(group: str) -> list[str]:
    return [i.category for i in INDICATORS if i.category == group]
