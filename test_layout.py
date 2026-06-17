#! /usr/bin/env python3

#######################################################################
# Unit tests for the subplot layout logic used by timeseries_animation.py.
#
# Exercises both supported VARLIST styles:
#   CONFIG_A - a tuple plotting two variables on one set of axes
#              (GGALT vs ATX/DPXC), 11 entries
#   CONFIG_B - a tuple plotting one variable against another
#              (GGALT vs ATX), 8 entries
#
# Run with:  python3 -m unittest test_layout
#######################################################################

import unittest

from layout import subplot_rows, classify_entry, subplot_position

# Two-vars-in-one-plot style (the original VARLIST), 11 entries.
CONFIG_A = ["GGALT", "PSX", "ATX", "DPXC", "WIC", "PLWCC", "CONCS_2DS",
            "CONCD_LWI", "FO3C_ACD", ("GGALT", "ATX", "DPXC"),
            ("GGLON", "GGLAT")]

# Two-vars-plotted-against-each-other style, 8 entries.
CONFIG_B = ["GGALT", "DPXC", "PSX", "WIC", "ATX", "CONCD_RWO",
            ("GGALT", "ATX"), ("GGLON", "GGLAT")]


class SubplotRowsTests(unittest.TestCase):
    def test_row_counts(self):
        self.assertEqual(subplot_rows(len(CONFIG_A)), 6)
        self.assertEqual(subplot_rows(len(CONFIG_B)), 4)


class ClassifyEntryTests(unittest.TestCase):
    def _classifications(self, varlist):
        n = len(varlist)
        return [classify_entry(i, n, var)
                for i, var in enumerate(varlist, start=1)]

    def test_last_entry_is_always_the_map(self):
        for varlist in (CONFIG_A, CONFIG_B):
            n = len(varlist)
            self.assertEqual(classify_entry(n, n, varlist[-1]), 'map')

    def test_exactly_one_map(self):
        for varlist in (CONFIG_A, CONFIG_B):
            self.assertEqual(self._classifications(varlist).count('map'), 1)

    def test_config_a_classifications(self):
        # GGALT vs ATX/DPXC tuple is the 'pair'; the rest are time series.
        self.assertEqual(
            self._classifications(CONFIG_A),
            ['time', 'time', 'time', 'time', 'time', 'time', 'time',
             'time', 'time', 'pair', 'map'])

    def test_config_b_classifications(self):
        # GGALT vs ATX tuple is the 'pair'; the rest are time series.
        self.assertEqual(
            self._classifications(CONFIG_B),
            ['time', 'time', 'time', 'time', 'time', 'time', 'pair', 'map'])

    def test_plain_strings_are_time(self):
        for varlist in (CONFIG_A, CONFIG_B):
            n = len(varlist)
            for i, var in enumerate(varlist, start=1):
                if isinstance(var, str):
                    self.assertEqual(classify_entry(i, n, var), 'time')

    def test_non_final_tuples_are_pairs(self):
        for varlist in (CONFIG_A, CONFIG_B):
            n = len(varlist)
            for i, var in enumerate(varlist, start=1):
                if isinstance(var, tuple) and i != n:
                    self.assertEqual(classify_entry(i, n, var), 'pair')


class SubplotPositionTests(unittest.TestCase):
    def test_map_lands_in_bottom_right_cell(self):
        for varlist in (CONFIG_A, CONFIG_B):
            n = len(varlist)
            rows = subplot_rows(n)
            nrows, ncols, pos = subplot_position(n, n)
            self.assertEqual((nrows, ncols), (rows, 2))
            # Bottom-right of a (rows x 2) grid is the last cell index.
            self.assertEqual(pos, 2 * rows)

    def test_pair_keeps_its_natural_slot(self):
        # CONFIG_B's pair is entry 7 of an 8-entry list -> bottom-left.
        self.assertEqual(subplot_position(7, len(CONFIG_B)), (4, 2, 7))
        # CONFIG_A's pair is entry 10 of an 11-entry list.
        self.assertEqual(subplot_position(10, len(CONFIG_A)), (6, 2, 10))

    def test_positions_stay_within_the_grid_and_dont_collide(self):
        for varlist in (CONFIG_A, CONFIG_B):
            n = len(varlist)
            rows = subplot_rows(n)
            seen = set()
            for i in range(1, n + 1):
                nrows, ncols, pos = subplot_position(i, n)
                self.assertEqual((nrows, ncols), (rows, 2))
                self.assertGreaterEqual(pos, 1)
                self.assertLessEqual(pos, 2 * rows)
                self.assertNotIn(pos, seen)
                seen.add(pos)


if __name__ == '__main__':
    unittest.main()
