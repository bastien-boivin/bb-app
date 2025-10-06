# %%
import os
import sys
import logging
import numpy as np
import pandas as pd
import plotly.io as pio
import plotly.offline as pyo
import plotly.graph_objects as go
import matplotlib.pyplot as plt

from os.path import abspath, dirname

# Get root directory but don't change working directory
# This is important for compatibility with Streamlit Cloud
root_dir = dirname(dirname(dirname(abspath(__file__))))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# -----------------------------------------------------
# Module Imports
# -----------------------------------------------------

class TimeSeriesPlot_Plotly:
    """
    A class for creating and displaying interactive time series plots using Plotly.
    
    This class provides a comprehensive solution for time series data visualization with
    multiple analysis modes, data transformation options, and display customizations.
    
    Features
    --------
    - Time series data filtering, resampling, and interpolation
    - Three visualization modes: historical chronological series, annual cycle comparison, 
      and statistical analysis with reference year comparison
    - Support for different time resolutions (daily, weekly, monthly)
    - Rolling window averaging across multiple years
    - Custom annual cycle starting month
    - Cumulative calculations for annual cycle and statistical analysis
    - Reference year projection across timeline
    - Statistical quantile visualization with ribbons
    - Interactive elements with hover information
    - Automatic title and filename generation
    - Export to HTML or PNG formats
    
    Parameters
    ----------
    title : str, optional
        Title of the plot. If None, a title will be auto-generated.
    x_axis_title : str, optional
        Title for the X-axis. Default is "Date".
    y_axis_title : str, optional
        Title for the Y-axis. Default is "Valeur".
    x_range : tuple, optional
        Tuple specifying the start and end year for the X-axis range (e.g., (2000, 2020)).
    log_x : bool, optional
        Whether to use a logarithmic scale for the X-axis. Default is False.
    log_y : bool, optional
        Whether to use a logarithmic scale for the Y-axis. Default is False.
    mode : str, optional
        Plot mode selection:
        - 'historical' for a standard chronological time series plot,
        - 'annual_cycle' to plot multi-year curves on a single year axis (e.g., annual cycle),
        - 'statistics' to display statistical ribbons (min/max/quantiles) plus one focus year.
        Default is 'historical'.
    focus_year : int, optional
        The focus year for the 'statistics' mode or reference year in 'historical' mode.
        Required if mode is 'statistics'.
    start_month : int, optional
        Specify a custom month (1-12) to start the annual cycle. If > 1, the annual
        cycle will begin on the 1st day of this month and end on the last day of the
        month before. Default is None (calendar year).
    cumul : bool, optional
        If True, calculate cumulative values for annual_cycle and statistics modes.
        Not applicable in 'historical' mode. Default is False.
    """

    def __init__(self,
                 title: str = None,
                 x_axis_title: str = "Date",
                 y_axis_title: str = "Value",
                 x_range: tuple = None,
                 log_x: bool = False,
                 log_y: bool = False,
                 mode: str = 'historical',
                 focus_year: int = None,
                 start_month: int = None,
                 cumul: bool = False,
                 ):
        """
        Initialize the TimeSeriesPlot_Plotly class.
        
        Parameters
        ----------
        title : str, optional
            Title of the plot. If None, a title will be auto-generated.
        x_axis_title : str, optional
            Title for the X-axis. Default is "Date".
        y_axis_title : str, optional
            Title for the Y-axis. Default is "Value".
        x_range : tuple, optional
            Tuple specifying the start and end year for the X-axis range (e.g., (2000, 2020)).
        log_x : bool, optional
            Whether to use a logarithmic scale for the X-axis. Default is False.
        log_y : bool, optional
            Whether to use a logarithmic scale for the Y-axis. Default is False.
        mode : str, optional
            Plot mode selection:
            - 'historical' for a standard chronological time series plot,
            - 'annual_cycle' to plot multi-year curves on a single year axis (e.g., annual cycle),
            - 'statistics' to display statistical ribbons (min/max/quantiles) plus one focus year.
            Default is 'historical'.
        focus_year : int, optional
            The focus year for the 'statistics' mode or reference year in 'historical' mode.
            Required if mode is 'statistics'.
        start_month : int, optional
            Specify a custom month (1-12) to start the annual cycle. If > 1, the annual
            cycle will begin on the 1st day of this month and end on the last day of the
            month before. Default is None (calendar year).
        cumul : bool, optional
            If True, calculate cumulative values for annual_cycle and statistics modes.
            Not applicable in 'historical' mode. Default is False.
        """
        
        self.x_axis_title = x_axis_title
        self.y_axis_title = y_axis_title
        self.x_range = x_range
        self.log_x = log_x
        self.log_y = log_y
        self.mode = mode
        self.focus_year = focus_year
        self.start_month = start_month if start_month is not None and start_month > 1 else None
        self.cumul = cumul
        
        self.title = title
        
        if self.cumul and self.mode == 'historical':
            logging.warning("Cumulative option is not applicable in 'historical' mode. It will be ignored.")
            self.cumul = False      

        if self.mode == 'statistics' and self.focus_year is None:
            logging.warning("The 'statistics' mode requires a reference year (focus_year). The 'historical' mode will be used instead.")
            self.mode = 'historical'

        self.series_list = []
        self.line_list = []
        self.rectangle_list = []

    def add_series(self,
                   df: pd.DataFrame,
                   time_col: str,
                   var_col,
                   legend_name: str = None,
                   year_min: int = None,
                   year_max: int = None,
                   freq: str = None,
                   rolling_window: int = None
                   ):
        """
        Add a time series to the plot.
        
        This method processes and prepares time series data for visualization according to 
        the specified parameters and selected mode. It handles data filtering, resampling,
        rolling averages, and specialized processing for each visualization mode.
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame containing the time series data.
        time_col : str
            Name of the column containing the time data.
        var_col : str or int
            Name or index of the column containing the variable data.
        legend_name : str, optional
            Name to display in the legend for this series. If None, uses var_col.
        year_min : int, optional
            Minimum year to include in the data.
        year_max : int, optional
            Maximum year to include in the data.
        freq : str, optional
            Resampling frequency:
            - 'D' for daily (default if None)
            - 'W' for weekly
            - 'ME' for monthly at month end
        rolling_window : int, optional
            Rolling window size for averaging (number of years to include in each window).
            Not applicable in 'statistics' mode.
            
        Notes
        -----
        The method processes data differently based on the visualization mode:
        - 'historical': Prepares chronological time series with optional reference year projection
        - 'annual_cycle': Creates multi-year comparison on a common timeline
        - 'statistics': Calculates statistical metrics (mean, median, quantiles) and compares with a focus year
        
        It also handles special cases like incomplete time series, leap years,
        custom annual cycles, and cumulative calculations.
        """
        self.freq = freq
        self.legend_name = legend_name
        self.rolling_window = rolling_window

        df = df.copy()
        df[time_col] = pd.to_datetime(df[time_col])

        if self.mode == 'statistics' and self.rolling_window is not None:
            logging.warning("The 'statistics' mode cannot be used with a rolling_window. The rolling_window will be ignored.")
            self.rolling_window = None

        if year_min is not None:
            df = df[df[time_col].dt.year >= year_min]
        if year_max is not None:
            df = df[df[time_col].dt.year <= year_max]

        if isinstance(var_col, int):
            y_data_name = df.columns[var_col]
        else:
            y_data_name = var_col

        start_dates = df.groupby(df[time_col].dt.year)[time_col].min()
        end_dates = df.groupby(df[time_col].dt.year)[time_col].max()

        complete_years = start_dates.index[
            (start_dates.dt.month == 1) &
            (start_dates.dt.day == 1) &
            (end_dates.dt.month == 12) &
            (end_dates.dt.day == 31)
        ].tolist()

        if len(complete_years) > 0:
            date_range = pd.date_range(
                start=f"{min(complete_years)}-01-01",
                end=f"{max(complete_years)}-12-31",
                freq='D'
            )

            df_complete = pd.DataFrame(index=date_range)
            df_complete.index.name = time_col

            df = df.set_index(time_col)
            df = df_complete.join(df).reset_index()

            missing_count = df.isna().sum()
            logging.debug(missing_count)

            df = df.interpolate(method='linear')

        df_analysis = df.copy()

        df_analysis['year'] = df_analysis[time_col].dt.year
        df_analysis['doy'] = df_analysis[time_col].dt.dayofyear

        # Handle leap years by adjusting day of year and removing Feb 29
        mask = (df_analysis[time_col].dt.is_leap_year) & (df_analysis[time_col].dt.dayofyear > 59)
        df_analysis.loc[mask, 'doy'] = df_analysis.loc[mask, 'doy'] - 1
        df_analysis = df_analysis[~((df_analysis[time_col].dt.month == 2) & (df_analysis[time_col].dt.day == 29))]

        df_analysis['week_num'] = ((df_analysis['doy'] - 1) // 7) + 1
        df_analysis.loc[df_analysis['week_num'] > 52, 'week_num'] = 52

        df_analysis['month_num'] = df_analysis[time_col].dt.month
        
        # Handle custom start month for annual cycle if specified
        if self.start_month is not None:    
            days_per_month = {
                1: 31, 2: 28, 3: 31, 4: 30,
                5: 31, 6: 30, 7: 31, 8: 31,
                9: 30, 10: 31, 11: 30, 12: 31
            }

            start = pd.Timestamp(year=df_analysis[time_col].dt.year.min(),
                                month=self.start_month,
                                day=1)

            end = pd.Timestamp(year=df_analysis[time_col].dt.year.max(),
                            month=self.start_month - 1,
                            day=days_per_month[self.start_month - 1])

            df_analysis = df_analysis[(df_analysis[time_col] >= start) & (df_analysis[time_col] <= end)]

            df_analysis['month_num'] = ((df_analysis[time_col].dt.month - self.start_month) % 12) + 1
            
            if self.start_month <= 6:
                df_analysis.loc[df_analysis[time_col].dt.month < self.start_month, 'year'] -= 1
            else:
                df_analysis.loc[df_analysis[time_col].dt.month >= self.start_month, 'year'] += 1
            
            df_analysis = df_analysis.sort_values(by=['month_num', 'doy'])
            df_analysis['doy'] = df_analysis.groupby('year').cumcount() + 1

            df_analysis['week_num'] = ((df_analysis['doy'] - 1) // 7) + 1
            df_analysis.loc[df_analysis['week_num'] > 52, 'week_num'] = 52
                
            df_analysis.reset_index(drop=True, inplace=True)
            df_analysis = df_analysis.sort_values(by=['year', 'doy'])
                
        if self.freq == 'W':
            df = (
                df_analysis
                .groupby(['year', 'week_num'], as_index=False)
                .agg({
                    time_col: 'first',
                    'doy': 'first',
                    'month_num': 'first',
                    var_col: 'mean'
                    })
            )
        elif self.freq == 'ME':
            df = (
                df_analysis
                .groupby(['year', 'month_num'], as_index=False)
                .agg({
                    time_col: 'first',
                    'doy': 'first',
                    'week_num': 'first',
                    var_col: 'mean'
                    })
            )
        else:
            df = df_analysis

        if self.start_month is not None:
            df['month_real'] = df[time_col].dt.month
            
        # Apply cumulative calculation if enabled
        if self.cumul:
            if self.mode in ['annual_cycle', 'statistics']:
                for year in df['year'].unique():
                    year_mask = df['year'] == year
                    if self.freq == 'W':
                        sort_col = 'week_num'
                    elif self.freq == 'ME':
                        sort_col = 'month_num'
                    else:
                        sort_col = 'doy'
                        
                    df.loc[year_mask, var_col] = df.loc[year_mask].sort_values(by=sort_col)[var_col].cumsum()
        
        if self.rolling_window is not None:
            unique_years = sorted(df['year'].unique())
            max_start_year = unique_years[-self.rolling_window]

            output_dfs = []

            for start_year in unique_years:
                if start_year > max_start_year:
                    break

                mask = (df['year'] >= start_year) & (df['year'] < start_year + self.rolling_window)
                block_df = df[mask].copy()

                if self.freq == 'D':
                    avg_values = block_df.groupby('doy').agg({
                        y_data_name: 'mean',
                        time_col: 'first'
                    })
                    result_df = pd.DataFrame({
                        'year': start_year,
                        'doy': avg_values.index,
                        time_col: avg_values[time_col],
                        y_data_name: avg_values[y_data_name]
                    })
                elif self.freq == 'W':
                    avg_values = block_df.groupby('week_num').agg({
                        y_data_name: 'mean',
                        time_col: 'first'
                    })
                    result_df = pd.DataFrame({
                        'year': start_year,
                        'week_num': avg_values.index,
                        time_col: avg_values[time_col],
                        y_data_name: avg_values[y_data_name]
                    })
                elif self.freq == 'ME':
                    avg_values = block_df.groupby('month_num').agg({
                        y_data_name: 'mean',
                        time_col: 'first'
                    })
                    result_df = pd.DataFrame({
                        'year': start_year,
                        'month_num': avg_values.index,
                        time_col: avg_values[time_col],
                        y_data_name: avg_values[y_data_name]
                    })

                output_dfs.append(result_df)

            df = pd.concat(output_dfs, ignore_index=True)

        # Process data for historical mode
        if self.mode == 'historical':
            final_df = df.copy()
            final_df.rename(columns={time_col: 'time'}, inplace=True)

            self.series_list.append({
                'df': final_df,
                'time_col': 'time',
                'var_col': y_data_name,
                'legend_name': legend_name or str(var_col),
                'freq': freq,
                'rolling_window': self.rolling_window
            })

        # Process data for annual_cycle mode
        elif self.mode == 'annual_cycle':
            if self.freq == 'W':
                grouped = df.groupby(['year', 'week_num'])[y_data_name].mean().reset_index()
                x_col = 'week_num'
            elif self.freq == 'ME':
                grouped = df.groupby(['year', 'month_num'])[y_data_name].mean().reset_index()
                x_col = 'month_num'
            else:
                grouped = df.groupby(['year', 'doy'])[y_data_name].mean().reset_index()
                x_col = 'doy'

            for year in grouped['year'].unique():
                year_data = grouped[grouped['year'] == year].copy()

                if self.rolling_window is not None:
                    legend_text = f'{year}-{year + self.rolling_window - 1}'
                else:
                    legend_text = f'Year {year}'

                self.series_list.append({
                    'df': year_data,
                    'time_col': x_col,
                    'var_col': y_data_name,
                    'legend_name': legend_text,
                    'freq': freq,
                    'rolling_window': self.rolling_window,
                    'is_annual_cycle': True
                })

        # Process data for statistics mode
        elif self.mode == 'statistics':
            if self.freq == 'W':
                x_col = 'week_num'
            elif self.freq == 'ME':
                x_col = 'month_num'
            else:
                x_col = 'doy'

            # Split data between focus year and all other years
            df_stats_part = df[df['year'] != self.focus_year].copy()
            df_focus_part = df[df['year'] == self.focus_year].copy()

            grouped = df_stats_part.groupby(x_col).agg({
                y_data_name: ['quantile', 'mean', 'median'],
                time_col: 'first'
            })

            # Calculate quantiles for statistical ribbons
            quantiles_list = [0.0, 0.01, 0.05, 0.10, 0.25, 0.75, 0.90, 0.95, 0.99, 1.0]
            stats_quantiles = df_stats_part.groupby(x_col)[y_data_name].quantile(quantiles_list).unstack(level=-1)
            stats_quantiles.columns = [
                'min', 'q01', 'q05', 'q10', 'q25',
                'q75', 'q90', 'q95', 'q99', 'max'
            ]

            stats_quantiles['mean'] = grouped[(y_data_name, 'mean')]
            stats_quantiles['median'] = grouped[(y_data_name, 'median')]
            stats_quantiles[time_col] = grouped[time_col]['first']

            stats_quantiles.reset_index(inplace=True)

            # Process focus year data
            df_focus_grouped = (df_focus_part
                            .groupby(x_col)
                            .agg({
                                y_data_name: 'mean',
                                time_col: 'first'
                            })
                            .reset_index())

            df_focus_grouped.rename(columns={y_data_name: 'focus'}, inplace=True)

            logging.debug("\nFocus data after groupby:")
            logging.debug(df_focus_grouped.head())

            # Merge statistics with focus year data
            final_df = stats_quantiles.merge(
                df_focus_grouped[[x_col, 'focus']],
                on=x_col,
                how='left'
            )

            final_df.rename(columns={x_col: 'x_value'}, inplace=True)
            logging.debug(final_df['focus'])

            self.series_list.append({
                'df': final_df,
                'time_col': 'x_value',
                'var_col': y_data_name,
                'legend_name': legend_name or str(var_col),
                'freq': freq,
                'rolling_window': None,
                'is_statistics': True
            })
        
        # Generate automatic title if none was provided
        if self.title is None:
            self.title = self._generate_auto_title()

    def generate_color_palette(self, num_colors: int) -> list:
        """
        Generate a color palette for the plot.
        
        Parameters
        ----------
        num_colors : int
            Number of colors to generate.
            
        Returns
        -------
        list
            List of RGB color strings formatted for Plotly.
            
        Notes
        -----
        Uses matplotlib's coolwarm colormap to generate a balanced
        spectrum of colors for distinguishing multiple series.
        """
        if num_colors <= 1:
            return ['rgb(0, 0, 255)']
        cmap = plt.get_cmap('coolwarm')
        colors = [cmap(i / (num_colors - 1)) for i in range(num_colors)]
        return [
            f'rgb({int(c[0]*255)}, {int(c[1]*255)}, {int(c[2]*255)})'
            for c in colors
        ]

    def _generate_auto_filename(self):
        """
        Generate an automatic filename based on plot parameters.
        
        Returns
        -------
        str
            A filename string combining mode, parameters, and data source information.
            
        Notes
        -----
        The filename includes components like:
        - Visualization mode
        - Focus year (if applicable)
        - Frequency (daily, weekly, monthly)
        - Rolling window size (if applicable)
        - Cumulative flag (if enabled)
        - Variable name
        
        Components are joined with underscores to create a filesystem-friendly name.
        """
        components = []
        
        components.append(self.mode)
        
        if self.focus_year is not None:
            components.append(f"focus-({self.focus_year})")
        
        if self.freq is not None:
            freq_names = {'D': 'daily', 'W': 'weekly', 'ME': 'monthly'}
            components.append(freq_names.get(self.freq, self.freq))
        
        if self.rolling_window is not None:
            components.append(f"roll-({self.rolling_window})")
        
        if self.cumul:
            components.append("cumulative")
        
        if hasattr(self, 'var_col') and self.var_col:
            var_name = self.var_col.replace(' ', '_').replace('/', '_')
            components.append(var_name)
        
        filename = "_".join(components)
        
        return filename

    def _generate_auto_title(self):
        """
        Generate an automatic descriptive title based on plot parameters.
        
        Returns
        -------
        str
            A formatted title string that describes the visualization's key characteristics.
            
        Notes
        -----
        The title includes components like:
        - Visualization mode in a readable format
        - Data series description
        - Year range
        - Reference year (if applicable)
        - Cumulative calculation indicator
        - Rolling window information
        
        Components are formatted to create a human-readable title.
        """
        components = []

        mode_names = {
            'historical': 'Time Series',
            'annual_cycle': 'Annual Cycle',
            'statistics': 'Statistical Analysis'
        }
        components.append(mode_names.get(self.mode, self.mode.capitalize()))
        
        if hasattr(self, 'legend_name') and self.legend_name:
            components.append(f"of {self.legend_name}")
        elif hasattr(self, 'var_col') and self.var_col:
            components.append(f"of {self.var_col}")
        
        if self.x_range and len(self.x_range) == 2:
            components.append(f"({self.x_range[0]}-{self.x_range[1]})")
        
        if self.focus_year is not None:
            components.append(f"- Reference Year: {self.focus_year}")
        
        if self.cumul:
            components.append("(Cumulative)")
        
        if self.rolling_window is not None:
            components.append(f"- {self.rolling_window}-year Rolling Average")
        
        title = " ".join(components)
        
        return title

    def add_line(self,
                 orientation: str,
                 position: float,
                 line_dash: str,
                 col: str = 'all',
                 color: str = 'black',
                 label: str = ''):
        """
        Add a vertical or horizontal reference line to the plot.
        
        Parameters
        ----------
        orientation : str
            Orientation of the line ('v' for vertical, 'h' for horizontal).
        position : float
            Position of the line on the axis.
        line_dash : str
            Dash style of the line ('solid', 'dash', 'dot', 'dashdot').
        col : str, optional
            Column to apply the line to. Default is 'all'.
        color : str, optional
            Color of the line. Default is 'black'.
        label : str, optional
            Label for the line. Default is empty string.
            
        Notes
        -----
        This method only stores the line details; the actual line is
        added to the plot when create_figure() is called.
        """
        self.line_list.append({
            'orientation': orientation,
            'position': position,
            'line_dash': line_dash,
            'col': col,
            'color': color,
            'label': label
        })

    def add_rectangle(self,
                      orientation: str,
                      x0: float = None,
                      x1: float = None,
                      y0: float = None,
                      y1: float = None,
                      color: str = 'black',
                      opacity: float = 0.2,
                      label: str = ''):
        """
        Add a rectangular highlight zone to the plot.
        
        Parameters
        ----------
        orientation : str
            Orientation of the rectangle ('v' for vertical, 'h' for horizontal).
        x0 : float, optional
            Starting X position of the rectangle.
        x1 : float, optional
            Ending X position of the rectangle.
        y0 : float, optional
            Starting Y position of the rectangle.
        y1 : float, optional
            Ending Y position of the rectangle.
        color : str, optional
            Color of the rectangle. Default is 'black'.
        opacity : float, optional
            Opacity of the rectangle (0 to 1). Default is 0.2.
        label : str, optional
            Label for the rectangle. Default is empty string.
            
        Notes
        -----
        This method only stores the rectangle details; the actual rectangle is
        added to the plot when create_figure() is called.
        """
        self.rectangle_list.append({
            'orientation': orientation,
            'x0': x0,
            'x1': x1,
            'y0': y0,
            'y1': y1,
            'color': color,
            'opacity': opacity,
            'label': label
        })

    def _get_month_ticks_for_days(self):
        """
        Generate month tick positions and labels for daily data.
        
        Returns
        -------
        tuple
            (month_positions, month_labels) where month_positions is a list
            of day numbers where months start, and month_labels are the
            corresponding month name abbreviations.
            
        Notes
        -----
        Handles adjustments for custom annual cycle starting months.
        """
        standard_month_starts = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
        standard_month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        if self.start_month is None or self.start_month == 1:
            return standard_month_starts, standard_month_labels
        
        shifted_labels = standard_month_labels[self.start_month-1:] + standard_month_labels[:self.start_month-1]
        
        days_per_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        shifted_starts = []
        
        cumulative_days = 0
        for i in range(12):
            adjusted_month_idx = (i + self.start_month - 1) % 12
            if i == 0:
                shifted_starts.append(1)
            else:
                cumulative_days += days_per_month[(adjusted_month_idx - 1) % 12]
                shifted_starts.append(cumulative_days + 1)
        
        return shifted_starts, shifted_labels

    def _get_month_ticks_for_weeks(self):
        """
        Generate month tick positions and labels for weekly data.
        
        Returns
        -------
        tuple
            (week_positions, month_labels) where week_positions is a list
            of week numbers where months approximately start, and month_labels
            are the corresponding month name abbreviations.
            
        Notes
        -----
        Handles adjustments for custom annual cycle starting months.
        """
        standard_week_starts = [1, 6, 10, 14, 18, 22, 26, 30, 35, 39, 43, 48]
        standard_month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        if self.start_month is None or self.start_month == 1:
            return standard_week_starts, standard_month_labels
        
        shifted_labels = standard_month_labels[self.start_month-1:] + standard_month_labels[:self.start_month-1]
        
        weeks_per_month = [5, 4, 4, 4, 4, 4, 4, 5, 4, 4, 5, 5]
        shifted_weeks = []
        
        cumulative_weeks = 0
        for i in range(12):
            adjusted_month_idx = (i + self.start_month - 1) % 12
            if i == 0:
                shifted_weeks.append(1)
            else:
                cumulative_weeks += weeks_per_month[(adjusted_month_idx - 1) % 12]
                shifted_weeks.append(cumulative_weeks + 1)
        
        return shifted_weeks, shifted_labels

    def _get_month_ticks_for_months(self):
        """
        Generate month tick positions and labels for monthly data.
        
        Returns
        -------
        tuple
            (month_numbers, month_labels) where month_numbers is a list
            of month indices (1-12), and month_labels are the corresponding
            month name abbreviations.
            
        Notes
        -----
        Handles adjustments for custom annual cycle starting months.
        """
        standard_month_numbers = list(range(1, 13))
        standard_month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        if self.start_month is None or self.start_month == 1:
            return standard_month_numbers, standard_month_labels
        
        shifted_labels = standard_month_labels[self.start_month-1:] + standard_month_labels[:self.start_month-1]

        return standard_month_numbers, shifted_labels

    def create_figure(self) -> go.Figure:
        """
        Create and configure the Plotly figure object.
        
        Returns
        -------
        go.Figure
            A fully configured Plotly figure object ready for display or export.
            
        Notes
        -----
        This method performs different visualization operations based on the selected mode:
        - 'historical': Creates a chronological time series plot with optional reference year
          projections across the timeline
        - 'annual_cycle': Creates multiple series with common time axis for yearly comparison
        - 'statistics': Creates statistical ribbons (quantiles) alongside reference year data
        
        It also adds any configured reference lines and rectangles, and applies
        styling to the plot.
        """
        fig = go.Figure()

        # ---------------------------------------------------------------
        # MODE = historical
        # ---------------------------------------------------------------
        if self.mode == 'historical':
            # Trace the main time series first
            for series in self.series_list:
                df = series['df'].copy()
                legend_name = series.get('legend_name', 'var')
                var_col = series['var_col']
                self.var_col = var_col  # Store for later reference

                # Add the main time series trace
                fig.add_trace(
                    go.Scatter(
                        x=df['time'],
                        y=df[var_col],
                        mode='lines',
                        name=legend_name,
                        line=dict(color='rgb(31, 119, 180)'),  # Default blue
                        hovertemplate=(
                            "Date : %{x|%d/%m/%Y}<br>" + f"{var_col} : " + "%{y:.2f}<extra></extra>"
                        )
                    )
                )
                
                # If a reference year is specified, project it across all years
                if self.focus_year is not None:
                    # Extract reference year data
                    mask_focus_year = df['time'].dt.year == self.focus_year
                    df_focus = df[mask_focus_year].copy()
                    
                    if not df_focus.empty:
                        
                        # For each year in the range
                        unique_years = df['time'].dt.year.unique()
                        unique_years = unique_years[unique_years != self.focus_year]  # Exclude the reference year
                        
                        for year in unique_years:
                            # Calculate the offset between current year and reference year
                            year_offset = pd.DateOffset(years=year - self.focus_year)
                            
                            # Create a shifted version of the reference year data
                            df_shifted = df_focus.copy()
                            df_shifted['time'] = df_shifted['time'] + year_offset
                            
                            # Add the shifted series to the plot (with different styling)
                            fig.add_trace(
                                go.Scatter(
                                    x=df_shifted['time'],
                                    y=df_shifted[self.var_col],
                                    mode='lines',
                                    line=dict(color='rgba(255, 165, 0, 0.5)', dash='dot', width=1),  # Transparent orange dotted
                                    name=f'Reference {self.focus_year}',
                                    showlegend=bool(year == unique_years[0]),  # Only show once in legend
                                    hovertext=f"Projected year {year}",
                                )
                            )
                        
                        # Highlight the reference year itself
                        fig.add_trace(
                            go.Scatter(
                                x=df_focus['time'],
                                y=df_focus[self.var_col],
                                mode='lines',
                                line=dict(color='rgb(255, 0, 0)', width=2),  # Thicker red
                                name=f'Reference {self.focus_year}',
                                hovertemplate=(
                                    "Date : %{x|%d/%m/%Y}<br>" + f"{var_col} : " + "%{y:.2f}<extra></extra>"
                                )
                            )
                        )

            # Set the year range for X axis
            start_year = min(df['time']).year
            end_year = max(df['time']).year

            fig.update_layout(
                xaxis=dict(
                    type='date',
                    range=[f"{start_year}-01-01", f"{end_year}-12-31"],
                    dtick="M12",
                    tickformat="%Y",
                ),
                hovermode='x unified',
                hoverdistance=1,
            )
        # ---------------------------------------------------------------
        # MODE = annual_cycle
        # ---------------------------------------------------------------
        elif self.mode == 'annual_cycle':
            all_x = []
            num_series = len(self.series_list)
            colors = self.generate_color_palette(num_series)

            for idx, series in enumerate(self.series_list):
                df = series['df'].copy()
                x_col = series['time_col']
                y_col = series['var_col']
                legend_name = series.get('legend_name', '')

                all_x.extend(df[x_col].unique())

                fig.add_trace(go.Scatter(
                    x=df[x_col],
                    y=df[y_col],
                    mode='lines',
                    name=legend_name,
                    line=dict(color=colors[idx])
                ))

            if self.freq == 'W':
                max_x = 52
                ticks, labels = self._get_month_ticks_for_weeks()
            elif self.freq == 'ME':
                max_x = 12
                ticks, labels = self._get_month_ticks_for_months()
            else:
                max_x = 365
                ticks, labels = self._get_month_ticks_for_days()

            fig.update_layout(
                xaxis=dict(
                    range=[1, max_x],
                    tickmode='array',
                    tickvals=ticks,
                    ticktext=labels
                ),
            )
        
        # ---------------------------------------------------------------
        # MODE = statistics
        # ---------------------------------------------------------------
        elif self.mode == 'statistics':
            if not self.series_list:
                logging.warning("No series for mode=statistics")
                return fig
            
            df = self.series_list[0]['df']
            x_col = 'x_value'

            bands = [
                ('min','max', 'rgba(128,128,128,0.2)', 'Min/Max'),
                ('q25','q75', 'rgba(128,128,128,0.6)', 'Q25/Q75'),
                ('q10','q90', 'rgba(128,128,128,0.5)', 'Q10/Q90'),
                ('q05','q95', 'rgba(128,128,128,0.4)', 'Q05/Q95'),
                ('q01','q99', 'rgba(128,128,128,0.3)', 'Q01/Q99'),
            ]

            for lower_col, upper_col, fill_color, name in bands:
                fig.add_trace(go.Scatter(
                    x=df[x_col],
                    y=df[lower_col],
                    mode='lines',
                    line_color='rgba(0,0,0,0)',
                    showlegend=False
                ))
                fig.add_trace(go.Scatter(
                    x=df[x_col],
                    y=df[upper_col],
                    fill='tonexty',
                    fillcolor=fill_color,
                    mode='lines',
                    line_color=fill_color,
                    name=f"{name}"
                ))

            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df['median'],
                mode='lines',
                line=dict(color='blue'),
                name='Median'
            ))
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df['mean'],
                mode='lines',
                line=dict(color='red'),
                name='Mean'
            ))
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df['focus'],
                mode='lines',
                line=dict(color='black'),
                name='Reference Year'
            ))

            if self.freq == 'W':
                max_x = 52
                ticks, labels = self._get_month_ticks_for_weeks()
            elif self.freq == 'ME':
                max_x = 12
                ticks, labels = self._get_month_ticks_for_months()
            else:
                max_x = 365
                ticks, labels = self._get_month_ticks_for_days()

            fig.update_layout(
                xaxis=dict(
                    range=[1, max_x],
                    tickmode='array',
                    tickvals=ticks,
                    ticktext=labels
                ),
            )
        else:
            logging.warning(f"Unknown mode: {self.mode}")

        # Add reference lines and rectangles
        for line_dict in self.line_list:
            orientation = line_dict['orientation']
            position = line_dict['position']
            dash_style = line_dict['line_dash']
            color = line_dict['color']
            label = line_dict['label']

            if orientation == 'v':
                fig.add_vline(
                    x=position,
                    line_dash=dash_style,
                    line_color=color,
                    annotation_text=label,
                    annotation_position='top left'
                )
            elif orientation == 'h':
                fig.add_hline(
                    y=position,
                    line_dash=dash_style,
                    line_color=color,
                    annotation_text=label,
                    annotation_position='top left'
                )

        for rect in self.rectangle_list:
            orientation = rect['orientation']
            color = rect['color']
            opacity = rect['opacity']
            label = rect['label']

            if orientation == 'v':
                fig.add_vrect(
                    x0=rect['x0'],
                    x1=rect['x1'],
                    fillcolor=color,
                    opacity=opacity,
                    layer='below',
                    line_width=0,
                    annotation_text=label,
                    annotation_position='top left'
                )
            elif orientation == 'h':
                fig.add_hrect(
                    y0=rect['y0'],
                    y1=rect['y1'],
                    fillcolor=color,
                    opacity=opacity,
                    layer='below',
                    line_width=0,
                    annotation_text=label,
                    annotation_position='top left'
                )

        # Final styling
        fig.update_layout(
            title=self.title,
            xaxis_title=self.x_axis_title,
            yaxis_title=self.y_axis_title,
            plot_bgcolor='white',
            legend=dict(
                title="Legend:",
                orientation='v',
                yanchor='bottom',
                y=0,
                x=1.05,
                xanchor='left',
                bgcolor='rgba(255, 255, 255, 0.5)',
                bordercolor='black',
                borderwidth=1
            ),
            margin=dict(r=50)
        )
        
        fig.update_xaxes(
            mirror=True,
            ticks='outside',
            linecolor='black',
            zeroline=False,
        )

        fig.update_yaxes(
            mirror=True,
            ticks='outside',
            linecolor='black',
            zeroline=False,
            type='log' if self.log_y else 'linear'
        )

        return fig

    def show(self, open_browser: bool = False):
        """
        Display the visualization.
        
        Parameters
        ----------
        open_browser : bool, optional
            Whether to open the figure in a web browser. Default is False.
            
        Notes
        -----
        When open_browser is False, the figure is displayed inline in
        the current environment (e.g., Jupyter notebook). When True,
        the figure opens in the default web browser.
        """
        fig = self.create_figure()
        if open_browser:
            pyo.plot(fig, auto_open=True)
        else:
            fig.show()

    def save(self, file_path: str = None, file_name: str = None, format: str = 'html', open_browser: bool = False):
        """
        Save the visualization to a file.
        
        Parameters
        ----------
        file_path : str, optional
            Directory path to save the figure. If None, uses the 'output' directory
            in the root directory, or current directory as fallback.
        file_name : str, optional
            Name of the file without extension. If None, a name will be auto-generated
            based on plot parameters.
        format : str, optional
            Format for saving the figure ('html' or 'png'). Default is 'html'.
        open_browser : bool, optional
            Whether to open the figure in a web browser after saving. Default is False.
            
        Notes
        -----
        HTML format provides an interactive visualization that can be viewed in a browser.
        PNG format provides a static image suitable for reports or publications.
        """
        fig = self.create_figure()

        if file_path is None:
            try:
                file_path = os.path.join(root_dir, "output")
                os.makedirs(file_path, exist_ok=True)
            except:
                file_path = os.getcwd()
        
        if file_name is None:
            file_name = self._generate_auto_filename()
        
        full_path = os.path.join(file_path, f"{file_name}.{format}")
        
        if format == 'html':
            pio.write_html(fig, full_path, auto_open=open_browser)
        elif format == 'png':
            fig.write_image(full_path)
        else:
            logging.warning(f"Unsupported format: {format}. Saving as HTML.")
            pio.write_html(fig, os.path.join(file_path, f"{file_name}.html"), auto_open=open_browser)
            
#%%
if __name__ == "__main__":
    csv_file_path = r"C:\\Users\\basti\\Documents\\Output_HydroModPy\\LakeRes\\Reservoir\\Donnees journalieres EBR\\dam_input_2004_2024.csv"

    df = pd.read_csv(csv_file_path, sep=";")
    df["time"] = pd.to_datetime(df["time"], format="%d/%m/%Y")
        
    plot = TimeSeriesPlot_Plotly(
        x_axis_title="Date",
        y_axis_title="Volume (m3)",
        x_range=(2004, 2024),
        log_y=False,
        mode='historical',
        focus_year=2017,
        start_month=10,
        cumul=False
    )

    plot.add_series(
        df=df,
        time_col="time",
        var_col="cheze_vol",
        legend_name="Volume m3 of Cheze",
        freq='D',
        year_min=2004,
        year_max=2024,
        rolling_window=2,
    )

    # # Example of adding a reference line:
    # plot.add_line(orientation="h",
    #               label="Dam Limit",
    #               position=14500000,
    #               line_dash="dash",
    #               )

    plot.show(open_browser=True)
    
    # Example of saving with auto-generated filename
    # plot.save(open_browser=False)
# %%