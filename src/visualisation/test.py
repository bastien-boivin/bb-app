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
root_dir = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(root_dir)
cwd = os.getcwd()
if cwd != root_dir:
    os.chdir(root_dir)

# -----------------------------------------------------
# Modules
# -----------------------------------------------------
import src
import importlib
importlib.reload(src)

class TimeSeriesPlot_Plotly:
    """
    A class for creating and displaying time series plots using Plotly.

    This class allows users to:
      - Add time series data (with optional filtering by years).
      - Resample the time series (daily, weekly, monthly, etc.).
      - Apply either:
         * a standard rolling average (mode='default'),
         * a multi-year rolling average (mode='evolution'),
         * or statistical ribbons vs. a focus year (mode='statistics').
      - Add vertical/horizontal lines and rectangular zones.
      - Configure the plot's title, axis titles, axis ranges, and log scaling.
      - Display the plot in a browser or inline.
      - Specify a custom annual cycle starting month.
      - Apply cumulative calculations for evolution and statistics modes.
    """

    def __init__(self,
                 title: str,
                 x_axis_title: str,
                 y_axis_title: str,
                 x_range: tuple,
                 log_x: bool = False,
                 log_y: bool = False,
                 mode: str = 'chronique',
                 focus_year: int = None,
                 start_month: int = None,
                 cumul: bool = False,
                 ):
        """
        Initialize the TimeSeriesPlot_Plotly class.
        
        Parameters
        ----------
        title : str
            Title of the plot.
        x_axis_title : str
            Title for the X-axis.
        y_axis_title : str
            Title for the Y-axis.
        x_range : tuple
            Tuple specifying the start and end year for the X-axis range (e.g., (2000, 2020)).
        log_x : bool, optional
            Whether to use a logarithmic scale for the X-axis. Default is False.
        log_y : bool, optional
            Whether to use a logarithmic scale for the Y-axis. Default is False.
        mode : str, optional
            Plot mode selection:
            - 'chronique' for a standard chronological time series plot,
            - 'evolution' to plot multi-year curves on a single year axis (e.g., annual cycle),
            - 'statistic' to display statistical ribbons (min/max/quantiles) plus one focus year.
            Default is 'chronique'.
        focus_year : int, optional
            The focus year for the 'statistic' mode. Required if mode is 'statistic'.
        start_month : int, optional
            Specify a custom month (1-12) to start the annual cycle. If > 1, the annual
            cycle will begin on the 1st day of this month and end on the last day of the
            month before. Default is None (calendar year).
        cumul : bool, optional
            If True, calculate cumulative values for evolution and statistic modes.
            Not applicable in 'chronique' mode. Default is False.
        """
        
        self.title = title if title else f"Time Series Plot"
        self.x_axis_title = x_axis_title
        self.y_axis_title = y_axis_title
        self.x_range = x_range
        self.log_x = log_x
        self.log_y = log_y
        self.mode = mode
        self.focus_year = focus_year
        self.start_month = start_month if start_month is not None and start_month > 1 else None
        self.cumul = cumul
        
        if self.cumul and self.mode == 'chronique':
            logging.warning("Cumulative option is not applicable in 'chronique' mode. It will be ignored.")
            self.cumul = False      

        if self.mode == 'statistic' and self.focus_year is None:
            logging.warning("The 'statistic' mode requires a reference year (focus_year). The 'chroniques' mode will be used instead.")
            self.mode = 'chroniques'

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

        This method prepares the time series data for visualization according to the 
        specified mode and parameters. It can filter by year range, resample to different
        frequencies, apply rolling window averages, and calculate cumulative values.

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
            Not applicable in 'statistic' mode.
        """
        self.freq = freq
        self.legend_name = legend_name

        df[time_col] = pd.to_datetime(df[time_col])

        if self.mode == 'statistic' and rolling_window is not None:
            logging.warning("The 'statistic' mode cannot be used with a rolling_window. The rolling_window will be ignored.")
            rolling_window = None

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
            if self.mode in ['evolution', 'statistic']:
                for year in df['year'].unique():
                    year_mask = df['year'] == year
                    if self.freq == 'W':
                        sort_col = 'week_num'
                    elif self.freq == 'ME':
                        sort_col = 'month_num'
                    else:
                        sort_col = 'doy'
                        
                    df.loc[year_mask, var_col] = df.loc[year_mask].sort_values(by=sort_col)[var_col].cumsum()
        
        if rolling_window is not None:
            unique_years = sorted(df['year'].unique())
            max_start_year = unique_years[-rolling_window]

            output_dfs = []

            for start_year in unique_years:
                if start_year > max_start_year:
                    break

                mask = (df['year'] >= start_year) & (df['year'] < start_year + rolling_window)
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

        # Process data for chronique mode
        if self.mode == 'chronique':
            final_df = df.copy()
            final_df.rename(columns={time_col: 'time'}, inplace=True)

            self.series_list.append({
                'df': final_df,
                'time_col': 'time',
                'var_col': y_data_name,
                'legend_name': legend_name or str(var_col),
                'freq': freq,
                'rolling_window': rolling_window
            })

        # Process data for evolution mode
        elif self.mode == 'evolution':
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

                if rolling_window is not None:
                    legend_text = f'{year}-{year + rolling_window - 1}'
                else:
                    legend_text = f'Year {year}'

                self.series_list.append({
                    'df': year_data,
                    'time_col': x_col,
                    'var_col': y_data_name,
                    'legend_name': legend_text,
                    'freq': freq,
                    'rolling_window': rolling_window,
                    'is_evolution': True
                })

        # Process data for statistic mode
        elif self.mode == 'statistic':
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
            List of RGB color strings.
        """
        if num_colors <= 1:
            return ['rgb(0, 0, 255)']
        cmap = plt.get_cmap('coolwarm')
        colors = [cmap(i / (num_colors - 1)) for i in range(num_colors)]
        return [
            f'rgb({int(c[0]*255)}, {int(c[1]*255)}, {int(c[2]*255)})'
            for c in colors
        ]

    def add_line(self,
                 orientation: str,
                 position: float,
                 line_dash: str,
                 col: str = 'all',
                 color: str = 'black',
                 label: str = ''):
        """
        Add a vertical or horizontal line to the plot.

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
        Add a rectangular zone to the plot.

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
        Get month ticks for daily data, adjusted for start_month.
        
        Returns
        -------
        tuple
            Tuple containing month starts and month labels.
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
        Get month ticks for weekly data, adjusted for start_month.
        
        Returns
        -------
        tuple
            Tuple containing week starts and month labels.
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
        Get month ticks for monthly data, adjusted for start_month.
        
        Returns
        -------
        tuple
            Tuple containing month numbers and month labels.
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
        Create the plot figure based on the configured settings and added data series.

        Returns
        -------
        go.Figure
            Plotly figure object ready for display.
        """
        fig = go.Figure()

        # MODE = CHRONIQUE
        if self.mode == 'chronique':
            for series in self.series_list:
                df = series['df'].copy()
                legend_name = series.get('legend_name', 'var')
                var_col = series['var_col']

                fig.add_trace(
                    go.Scatter(
                        x=df['time'],
                        y=df[var_col],
                        mode='lines',
                        name=legend_name,
                        hovertemplate=(
                            "Date : %{x|%d/%m/%Y}<br>" + f"{var_col} : " + "%{y:.2f}<extra></extra>"
                        )
                    )
                )

            start_year = min(df['time']).year
            end_year   = max(df['time']).year

            fig.update_layout(
                xaxis=dict(
                    type='date',
                    range=[f"{start_year}-01-01", f"{end_year}-12-31"],
                    dtick="M12",
                    tickformat="%Y",
                ),
            )

        # MODE = EVOLUTION
        elif self.mode == 'evolution':
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
        
        # MODE = STATISTIC
        elif self.mode == 'statistic':
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
                name='Focus'
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

        # Add lines and rectangles
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
                title=f"Légende :",
                orientation='v',
                yanchor='bottom',
                y=0.25,
                x=1.1,
                xanchor='right',
                bgcolor='rgba(255, 255, 255, 0.5)',
                bordercolor='black',
                borderwidth=1
            )
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
        Display the resulting figure.

        Parameters
        ----------
        open_browser : bool, optional
            Whether to open the figure in a web browser. Default is False.
        """
        fig = self.create_figure()
        if open_browser:
            pyo.plot(fig, auto_open=True)
        else:
            fig.show()

    def save(self, file_path: str, format: str = 'html', open_browser: bool = False):
        """
        Save the resulting figure to a file.
        
        Parameters
        ----------
        file_path : str
            File path to save the figure.
        format : str, optional
            Format for saving the figure ('html' or 'png'). Default is 'html'.
        open_browser : bool, optional
            Whether to open the figure in a web browser. Default is False.
        """
        fig = self.create_figure()
        if format == 'html':
            pio.write_html(fig, file_path, auto_open=open_browser)
        elif format == 'png':
            fig.write_image(fig, file_path)
        else:
            logging.warning(f"Unsupported format: {format}. Saving as HTML.")
            pio.write_html(fig, file_path, auto_open=open_browser)
            
#%%
if __name__ == "__main__":
    csv_file_path = r"C:\\Users\\basti\\Documents\\Output_HydroModPy\\LakeRes\\Reservoir\\Donnees journalieres EBR\\dam_input_2004_2024.csv"

    df = pd.read_csv(csv_file_path, sep=";")
    df["time"] = pd.to_datetime(df["time"], format="%d/%m/%Y")
    df["ajout"] = df["canut"] + df["meu"]
    df["prelevement"] = df["resti"] + df["usine"]
    df["delta_anthropique"] = df["ajout"] - df["prelevement"]
    df["delta_anthropique_sum"] = df["delta_anthropique"].cumsum()

    Vmin = 1850000
    Vmax = 14500000

    df["natural"] = None

    # Boucle sur toutes les lignes de df
    for i in range(len(df)):
        if i == 0 or (i % 365) == 0:
            # => On démarre une nouvelle année (ou tout début),
            # on réinitialise "natural" au volume réel du lac
            df.at[i, "natural"] = df.at[i, "cheze_vol"]
        else:
            # Jour normal : on calcule la différence journalière
            delta = df.at[i, "cheze_vol"] - df.at[i-1, "cheze_vol"]

            # On retire les apports canut + meu
            delta_nat = delta - (df.at[i, "canut"] + df.at[i, "meu"])
            # Volume naturel avant application des seuils
            nat_before_thresh = df.at[i-1, "natural"] + delta_nat

            # Application des seuils min / max
            if nat_before_thresh < Vmin:
                nat_today = Vmin
            elif nat_before_thresh > Vmax:
                nat_today = Vmax
            else:
                nat_today = nat_before_thresh

            df.at[i, "natural"] = nat_today
        
    plot = TimeSeriesPlot_Plotly(
        title="Volume de la Cheze (2004-2024) - Evolution (Cumul)",
        x_axis_title="Date",
        y_axis_title="Volume (m3)",
        x_range=(2004, 2004),
        log_y=False,
        mode='evolution',
        focus_year=2017,
        start_month=10,
        cumul=True
    )

    plot.add_series(
        df=df,
        time_col="time",
        var_col="cheze_vol",
        legend_name="Volume m3 de la Cheze",
        freq='W',
        year_min=2004,
        year_max=2024,
        rolling_window=5,
    )

    # # (Optional) Add a vertical line example:
    # plot.add_line(orientation="h",
    #               label="Limite du Barrage",
    #               position=14500000,
    #               line_dash="dash",
    #               )

    plot.show(open_browser=True)
    
    # plot.save(f"C:\\Users\\basti\\OneDrive\\PhD\\03_Meeting\\EBR\\2025-02-26\\graph\\{plot.title}.html", format="html", open_browser=False)
# %%