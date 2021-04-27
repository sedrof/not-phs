def rent_charged_func(lower, uper, max, family, rent):
    # if lower and uper and max and family and rent is not None:
    if float(family or 0) > float(rent or 0) and float(rent or 0) > float(uper or 0):
        rent_charged = float(rent or 0)
    elif float(family or 0) <= float(lower or 0):
        rent_charged = min(float(rent or 0), float(family or 0))
    elif float(family or 0) <= (float(lower or 0) + 0.25 * (float(uper or 0) - float(lower or 0))):
        rent_charged = min(
            float(rent or 0),
            4 * (float(family or 0) - 0.75 * float(lower or 0)),
        )
    elif float(family or 0) <= float(uper or 0) and float(rent or 0) > float(uper or 0):
        rent_charged = min(
            float(rent or 0),
            (float(family or 0) + float(max or 0)),
        )
    elif float(family or 0) <= float(uper or 0) and float(rent or 0) < float(uper or 0):
        rent_charged = min(
            float(rent or 0),
            4 * float(family or 0) - 0.75 * float(lower or 0),
        )
    else:
        rent_charged = min(
            float(rent or 0),
            float(family or 0) + float(max or 0),
        )
    return float(rent_charged or 0)


def family_contribution_fun(income, ftb_a, ftb_b, maintenance, property_market_rent):
    # if income and ftb_a and ftb_b and maintenance and property_market_rent is not None:
    family_contribution = min(
        float(income or 0) + float(ftb_a or 0) + float(ftb_b or 0) + float(maintenance or 0), float(property_market_rent or 0))
    return float(family_contribution or 0)


def maintenance_income_above_Free_area(maintenance_amount, income_free_area):
    if maintenance_amount > float(income_free_area or 0):
        maintenance_income_above_Free_area = float(maintenance_amount) - float(
            income_free_area)
    else:
        maintenance_income_above_Free_area = 0
    return maintenance_income_above_Free_area

def adj_max_func(cra):
    adj_maximum_cra_payment = float(cra or 0)*7 / 365
    return adj_maximum_cra_payment

def lower_func(cra, lower):
    if cra == 0:
            adj_lower_threshold = 0
    else:
        adj_lower_threshold = float(lower or 0)
    return adj_lower_threshold

def upper_fucn(cra, max, lower):
    if cra == 0:
            adj_upper_thershold = 0
    else:
        adj_upper_thershold = (float(max or 0) / 3) * 4 + float(
            lower or 0
        )
    return adj_upper_thershold

def cra_func(rent_charged, lower_threshold, upper_thershold, maximum_cra_payment, *args, **kwargs):
    if float(rent_charged or 0) <= float(lower_threshold or 0):
        cra = 0
    elif float(rent_charged or 0) >= float(upper_thershold or 0):
        cra = float(maximum_cra_payment or 0)
    else:
        cra = (float(rent_charged or 0) -
                         float(lower_threshold or 0)) * 0.75
    return float(cra or 0)


""" Calculation for method 3 """


def CRA_3(lower_threshold, upper_thershold, maximum_cra_payment,
          property_market_rent, last_rent, income_component, cra_amount, maintenance_component):
    # ftb_b = 0
    family_contribution_caped = family_contribution_fun(
        income_component, 0.00, 0.00, maintenance_component, property_market_rent)
    # Calculate cra_rate last rent
    cra_last_rent = cra_func(
        last_rent, lower_threshold, upper_thershold, maximum_cra_payment
    )
    cra_amount_recieved = 0
    if cra_amount == 0:
        cra_amount_recieved = cra_last_rent
    else:
        cra_amount_recieved = cra_amount

    cra_reduction_last_rent_pw = max(
        float(cra_last_rent or 0) - float(cra_amount_recieved or 0), 0
    )

    cra_reduction_last_rent_pa = (
        float(cra_reduction_last_rent_pw or 0) / 7) * 365
    cra_annum_last_rent = (float(cra_last_rent or 0) / 7) * 365
    rent_charged_initial = rent_charged_func(lower_threshold, upper_thershold, maximum_cra_payment,
                                            family_contribution_caped, property_market_rent)
    cra_initial = cra_func(rent_charged_initial, lower_threshold,
                           upper_thershold, maximum_cra_payment)
    for i in range(20):
        cra_initial_pa = (float(cra_initial or 0) / 7) * 365

        cra_recievable_initial_pa = float(
            cra_initial_pa or 0) - float(cra_reduction_last_rent_pa or 0)

        adj_maximum_cra_payment = adj_max_func(cra_recievable_initial_pa)
        adj_lower_threshold = lower_func(cra_reduction_last_rent_pa, lower_threshold)
        
        adj_upper_thershold = upper_fucn(cra_recievable_initial_pa, adj_maximum_cra_payment, adj_lower_threshold)

        rent_charged_adjusted = rent_charged_func(
            adj_lower_threshold, adj_upper_thershold, adj_maximum_cra_payment, family_contribution_caped , property_market_rent)

        cra_adjusted = cra_func(rent_charged_adjusted, lower_threshold, upper_thershold,
                                maximum_cra_payment)
        cra_initial = cra_adjusted

    latest_cra = cra_func(rent_charged_adjusted, adj_lower_threshold, adj_upper_thershold,
                        adj_maximum_cra_payment)
    return float(rent_charged_adjusted), float(latest_cra)

""" Calcullations for method 2 """
# def cra_m_3(rent_charged, lower, upper, max):
#     rent_charged = CRA_3()[2]


def CRA_2(lower_threshold, upper_thershold, maximum_cra_payment,
          property_market_rent, income_component, maintenance_component,
          last_rent):
    family_rent = income_component + maintenance_component

    rent_charged = rent_charged_func(
        lower_threshold, upper_thershold, maximum_cra_payment, family_rent, property_market_rent)

    # Calculate CRA

    cra_rate = cra_func(rent_charged, lower_threshold,
                        upper_thershold, maximum_cra_payment)

    return "%.2f" % float(cra_rate), float(last_rent), "%.2f" % float(rent_charged)


""" Calculations for method 4 """


def CRA_4(lower_threshold, upper_thershold, maximum_cra_payment,
          property_market_rent, income_component, ftb_component, last_rent):

    family_rent = float(income_component) + float(ftb_component)
    rent_charged = rent_charged_func(
        lower_threshold, upper_thershold, maximum_cra_payment, family_rent, property_market_rent)
    cra_rate = cra_func(rent_charged, lower_threshold,
                        upper_thershold, maximum_cra_payment)
    return "%.2f" % float(cra_rate), float(last_rent), "%.2f" % float(rent_charged)


""" Calcuations for method 5 """


def CRA_5(lower_threshold, upper_thershold, maximum_cra_payment,
          property_market_rent, income_component, maintenance_amount, maintenance_component,
          ftb_a, ftb_b, ftb_a_adjustable_basket,
          income_free_area, last_rent, cra_amount):

    ftb_b_component = (float(ftb_b or 0) * 0.15)

    cra_last_rent = cra_func(
        last_rent, lower_threshold, upper_thershold, maximum_cra_payment
    )

    cra_amount_recieved = 0
    if cra_amount == 0:
        cra_amount_recieved = cra_last_rent
    else:
        cra_amount_recieved = cra_amount
    cra_reduction_last_rent_pw = max(
        float(cra_last_rent or 0) - float(cra_amount_recieved or 0), 0
    )  # K48 family1

    cra_reduction_last_rent_pa = (
        float(cra_reduction_last_rent_pw or 0) / 7) * 365  # D13
    cra_annum_last_rent = (float(cra_last_rent or 0) / 7) * 365  # H13
    total_cra_ftb = float(ftb_a_adjustable_basket or 0) + \
        float(cra_annum_last_rent or 0)

    maintenance_income_above_Free_area_iniital = maintenance_income_above_Free_area(maintenance_amount,
                                                                                    income_free_area)

    reduction_in_ftb_cra = float(
        maintenance_income_above_Free_area_iniital or 0) * 50 / 100

    if total_cra_ftb > 0:
        cra_prop_last_rent = float(
            cra_annum_last_rent or 0) / float(total_cra_ftb or 0)
    else:
        cra_prop_last_rent = 0

    cra_reduction = float(reduction_in_ftb_cra or 0) * \
        float(cra_prop_last_rent or 0)
    adj_last_cra_annum = max(
        float(cra_annum_last_rent or 0) - float(cra_reduction or 0), 0)

    if total_cra_ftb > 0:
        ftb_prop_last_rent = float(
            ftb_a_adjustable_basket or 0) / float(total_cra_ftb or 0)
    else:
        ftb_prop_last_rent = 0
    ftb_reduction_caped = min((float(reduction_in_ftb_cra) * float(ftb_prop_last_rent)),
                              float(ftb_a_adjustable_basket))
    ftb_reduction = float(reduction_in_ftb_cra) * float(ftb_prop_last_rent)

    ftb_payable_unadjusted = float(ftb_reduction_caped) + (float(ftb_a) /
                                                           7) * 365
    ftb_payable_unadjusted_pw = (
        float(ftb_payable_unadjusted or 0) / 365) * 7 * (15/100)
    ftb_payable_adjusted = float(ftb_payable_unadjusted) - float(ftb_reduction)
    ftb_a_Adjusted = (float(ftb_payable_adjusted) / 365) * 7 * (15 / 100)
    ftb_b = float(ftb_b or 0) * 15 / 100
    # ftb_total = float(ftb_a_Adjusted) + float(ftb_b)

    family_contribution_caped_initial = family_contribution_fun(income_component, ftb_payable_unadjusted_pw, ftb_b,
                                                                maintenance_component, property_market_rent)

    rent_charged_initial = rent_charged_func(lower_threshold, upper_thershold, maximum_cra_payment,
                                            family_contribution_caped_initial, property_market_rent)


    cra_initial = cra_func(rent_charged_initial, lower_threshold, upper_thershold,
                           maximum_cra_payment)

    for i in range(20):
        initial_cra_annum = (float(cra_initial or 0) / 7) * 365
        total_cra_ftb = initial_cra_annum + ftb_a_adjustable_basket
        if total_cra_ftb > 0:
            cra_prop = (float(initial_cra_annum or 0) /
                        float(total_cra_ftb or 0))
        else:
            cra_prop = 0
        if total_cra_ftb > 0:
            ftb_prop = float(ftb_a_adjustable_basket or 0) / \
                float(total_cra_ftb or 0)
        else:
            ftb_prop = 0

        cra_reduction_initial = float(
            reduction_in_ftb_cra or 0) * float(cra_prop or 0)
        ftb_reduction_initial = float(
            reduction_in_ftb_cra or 0) * float(ftb_prop or 0)  # F85
        adjusted_initial_cra = max(
            float(initial_cra_annum or 0) -
            float(cra_reduction_initial or 0), 0
        )  # G86
        ftb_a_adjusted_pw = (
            (float(ftb_payable_unadjusted or 0) -
             float(ftb_reduction_initial or 0)) / 365 * 7
        ) * 0.15  # M73
        adj_maximum_cra_payment = (float(adjusted_initial_cra or 0) / 365) * 7

        if adjusted_initial_cra == 0:
            adj_lower_threshold = 0
        else:
            adj_lower_threshold = lower_threshold
        if adjusted_initial_cra == 0:
            adj_upper_thershold = float(adj_maximum_cra_payment or 0)
        else:
            adj_upper_thershold = (float(adj_maximum_cra_payment or 0) / 3) * 4 + float(
                adj_lower_threshold or 0
            )

        adj_family_contribution = family_contribution_fun(income_component,
                                                          ftb_a_adjusted_pw, ftb_b,
                                                          maintenance_component, property_market_rent)

        adj_rent_charged = rent_charged_func(adj_lower_threshold, adj_upper_thershold,
                                            adj_maximum_cra_payment,
                                            adj_family_contribution, property_market_rent)

        adj_cra = cra_func(adj_rent_charged, lower_threshold, upper_thershold,
                           maximum_cra_payment)

        cra_initial = adj_cra
    latest_cra = cra_func(adj_rent_charged, adj_lower_threshold, adj_upper_thershold,
                          adj_maximum_cra_payment,
                          adj_family_contribution, property_market_rent)
    latest_ftb = float(ftb_a_adjusted_pw or 0) + ftb_b
    return "%.2f" % float(latest_cra), float(adj_rent_charged), "%.2f" % float(latest_ftb), float(cra_last_rent)


""" Calculations for method 6 """


def CRA_6(
    lower_threshold,
    upper_thershold,
    maximum_cra_payment,
    property_market_rent,
    income_component,
    maintenance_component,
    ftb_a,
    ftb_b,
    ftb_a_adjustable_Basket,
    last_rent,
    cra_amount,
):

    ftb_b_component = (float(ftb_b or 0) * 0.15)
    # Calculate CRA for last rent
    cra_last_rent = cra_func(
        last_rent, lower_threshold, upper_thershold, maximum_cra_payment
    )

    cra_amount_recieved = 0
    if cra_amount == 0 or cra_amount == None:
        cra_amount_recieved = float(cra_last_rent or 0)
    else:
        cra_amount_recieved = float(cra_amount or 0)
    cra_reduction_last_rent_pw = max(
        float(cra_last_rent or 0) - float(cra_amount_recieved or 0), 0
    )  # K48 family1
    cra_reduction_last_rent_pa = (
        float(cra_reduction_last_rent_pw or 0) / 7) * 365  # D13
    cra_annum_last_rent = (float(cra_last_rent or 0) / 7) * 365  # H13

    total_cra_ftb = ftb_a_adjustable_Basket + cra_annum_last_rent  # H14
    if total_cra_ftb > 0:
        cra_prop_last_rent = float(
            cra_annum_last_rent or 0) / float(total_cra_ftb or 0)
    else:
        cra_prop_last_rent = 0
    try:
        total_reduction = float(cra_reduction_last_rent_pa or 0) / float(
            cra_prop_last_rent or 0
        )  # J14/F87
    except ZeroDivisionError:
        total_reduction = 0

    ftb_a_pa = (float(ftb_a or 0) / 7) * 365
    ftb_reduction = float(total_reduction or 0) - \
        float(cra_reduction_last_rent_pa or 0)

    ftb_payable_unadjust = float(ftb_a_pa or 0) + min(
        float(ftb_reduction or 0), float(ftb_a_adjustable_Basket or 0)
    )  # H19 & G88
    ftb_payable_adjusted = float(
        ftb_payable_unadjust or 0) - float(ftb_reduction or 0)  # G90
    ftb_payable_unadjust_pw = (
        float(ftb_payable_unadjust or 0) / 365) * 7 * 0.15

    family_contribution_caped_initial = family_contribution_fun(
        income_component,
        ftb_payable_unadjust_pw,
        ftb_b_component,
        maintenance_component,
        property_market_rent
    )
    rent_charged_initial = rent_charged_func(
        lower_threshold,
        upper_thershold,
        maximum_cra_payment,
        family_contribution_caped_initial,
        property_market_rent,
    )
    initial_cra = cra_func(
        rent_charged_initial,
        lower_threshold,
        upper_thershold,
        maximum_cra_payment
    )
    for i in range(20):
        initial_cra_annum = (float(initial_cra or 0) / 7) * 365
        total_cra_ftb = initial_cra_annum + ftb_a_adjustable_Basket

        if total_cra_ftb > 0:
            cra_prop = (float(initial_cra_annum or 0) /
                        float(total_cra_ftb or 0))
        else:
            cra_prop = 0
        if total_cra_ftb > 0:
            ftb_prop = float(ftb_a_adjustable_Basket or 0) / \
                float(total_cra_ftb or 0)
        else:
            ftb_prop = 0

        cra_reduction_initial = float(
            total_reduction or 0) * float(cra_prop or 0)
        ftb_reduction_initial = float(
            total_reduction or 0) * float(ftb_prop or 0)  # F85
        adjusted_initial_cra = max(
            float(initial_cra_annum or 0) -
            float(cra_reduction_initial or 0), 0
        )  # G86
        ftb_a_adjusted_pw = (
            (float(ftb_payable_unadjust or 0) -
             float(ftb_reduction_initial or 0)) / 365 * 7
        ) * 0.15  # M73

        adj_maximum_cra_payment = (float(adjusted_initial_cra or 0) / 365) * 7

        if adjusted_initial_cra == 0:
            adj_lower_threshold = 0
        else:
            adj_lower_threshold = lower_threshold
        if adjusted_initial_cra == 0:
            adj_upper_thershold = float(adj_maximum_cra_payment or 0)
        else:
            adj_upper_thershold = (float(adj_maximum_cra_payment or 0) / 3) * 4 + float(
                adj_lower_threshold or 0
            )

        adj_family_contribution = family_contribution_fun(income_component, ftb_a_adjusted_pw, ftb_b,
                                                          maintenance_component,
                                                          property_market_rent)

        adj_rent_charged = rent_charged_func(adj_lower_threshold, adj_upper_thershold,
                                            adj_maximum_cra_payment,
                                            adj_family_contribution, property_market_rent)

        adj_cra = cra_func(adj_rent_charged, lower_threshold, upper_thershold,
                           maximum_cra_payment)

        initial_cra = adj_cra

    latest_cra = cra_func(adj_rent_charged, adj_lower_threshold, adj_upper_thershold,
                          adj_maximum_cra_payment,
                          adj_family_contribution, property_market_rent)
    ftb_b = float(ftb_b or 0) * 15 / 100
    latest_ftb = float(ftb_a_adjusted_pw or 0) + float(ftb_b or 0)
    return (
        "%.2f" % float(latest_cra),
        "%.2f" % float(adj_rent_charged),
        "%.2f" % float(latest_ftb),
        "%.2f" % float(cra_last_rent)
    )
