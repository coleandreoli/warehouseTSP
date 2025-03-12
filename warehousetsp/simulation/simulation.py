import pandas as pd


class Simulation:
    def __init__(self, warehouse):
        self.wh = warehouse

    def rm_stock(self, name, bin, qty):
        self.wh.loc[(self.wh["bin"] == bin) & (self.wh["item"] == name), "qty"] -= qty

    def get_qty(self, name, bin):
        return int(
            self.wh.loc[
                (self.wh["bin"] == bin) & (self.wh["item"] == name), "qty"
            ].values[0]
        )

    def get_bins(self, name):
        return self.wh[self.wh["item"] == name]["bin"].to_list()

    def get_lowest_bin(self, name):
        # Filter the DataFrame to only include rows for the specified item
        item_bins = self.wh[self.wh["item"] == name]

        # If there are no bins for this item, return None or an appropriate value
        if item_bins.empty:
            return None

        # Find the row with the smallest 'qty' and return its 'bin' value
        lowest_bin = item_bins.sort_values("qty").iloc[0]["bin"]
        return int(lowest_bin)

    def get_highest_bin(self, name):
        # Filter the DataFrame for the specified item.
        item_bins = self.wh[self.wh["item"] == name]

        # If no bins are found for the item, return None.
        if item_bins.empty:
            return None

        # Sort by 'qty' in descending order and take the first row.
        highest_bin = item_bins.sort_values("qty", ascending=False).iloc[0]["bin"]
        return int(highest_bin)
