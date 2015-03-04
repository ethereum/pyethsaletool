# Script to determine how much ETH can be bought by employees

btc_prices = [
    479.04,  # aug 31
    391.09,  # sep 30
    337.99,  # oct 31
    377.01,  # nov 30
    321,     # dec 31
]

fiat_prices = {
    # [aug 31, sep 31, oct 31, nov 31, dec 31, <add more later>]
    "usd": [1, 1, 1, 1, 1],
    "eur": [1.31347, 1.26299, 1.25248, 1.24478, 1.21002],
    "chf": [1.08834, 1.04718, 1.03875, 1.03552, 1.00624],
    "gbp": [1.65898, 1.62158, 1.59882, 1.56369, 1.55371]
}

current_fiat_prices = {
    # adjust immediately before processing
    "usd": 1, "eur": 1.12, "chf": 1.14, "gbp": 1.50
}


def calc_buy(month_joined,   # eg. 8 for aug 1, 9.5 for sep 15, 12.0 for jan 1
             time_share,     # eg. 0.5 for part-time, 1 for full-time
             salary,         # annual salary in usd
             currency,       # currency of salary
             fiat_to_sell):  # quantity of fiat to sell
    # eth/usd prices per month
    prices = [max(p, 300) / 2000. for p in btc_prices]

    # How much fiat you can sell per month
    avail = salary / 12. / time_share * 0.2

    # How much usd you can sell in each month
    thresholds = [max(0, min(i + 9 - month_joined, 1)) * avail * p
                  for i, p in enumerate(fiat_prices[currency])]
    opportunities = sorted(zip(prices, thresholds))
    # Current price of your fiat
    fiat_price = current_fiat_prices[currency]
    # How much USD you are selling
    usd_to_sell = fiat_to_sell * fiat_price
    # Main selling loop
    usd = usd_to_sell
    eth = 0
    print '%.2f %s converted to %.2f usd' % (fiat_to_sell, currency, usd)
    for price, threshold in opportunities:
        print price, threshold
        sub_usd = min(usd, threshold)
        add_eth = sub_usd / price
        if sub_usd > 0:
            print 'Purchased %.3f ether for %.2f usd at price %.4f eth/usd' % \
                (add_eth, sub_usd, price)
        usd -= sub_usd
        eth += add_eth
    # Did we exceed the maximum?
    if usd > 0:
        max_usd = sum([t for _, t in opportunities])
        print 'Threshold exceeded, max usd: %.2f (%.2f %s)' % \
            (max_usd, max_usd / fiat_price, currency)
    # Print out how much we purchased for what total
    print 'Total: purchased %.3f ether for %.2f usd (%.2f %s)' % \
        (eth, (usd_to_sell - usd), (usd_to_sell - usd) / fiat_price, currency)
    return eth

# Example: etherbuy.calc_buy(8, 1, 152000, 'chf', 8000)
# "I started on August 1 as a full-time employee earning 152000
# chf per year and want to buy 8000 chf worth of ether"
