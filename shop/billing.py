def calculate_total(list):
    total_price = 0
    for x in list:
        total_price += x["price"]
    return total_price