YearsRevenueCoeffs = {
    2017: 75,
    2018: 57,
    2019: 51,
    2020: 38,
    2021: 35,
    2022: 33,
    2023: 32,
}

MinYear = min(YearsRevenueCoeffs.keys())
MaxYear = max(YearsRevenueCoeffs.keys())


def get_year_coeff(year: int) -> int:
    if year in YearsRevenueCoeffs:
        return YearsRevenueCoeffs[year]
    if year < MinYear:
        return YearsRevenueCoeffs[MinYear]
    return YearsRevenueCoeffs[MaxYear]
