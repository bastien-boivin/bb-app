# BB App

BB App is a Streamlit application designed to visualize and interact with time series data, specifically optimized for hydrological and hydrogeological data. The application allows users to:

- Choose the start of the hydrological year.
- Define the length of moving averages.
- Generate statistical graphs based on quantiles with the option to select the observed year.

This repository is a copy from a GitLab repository.

## Introduction

BB App provides intuitive visualizations and interactive tools for analyzing hydrological and hydrogeological data. Users can customize various parameters to suit their specific needs, such as selecting the start of the hydrological year and adjusting moving average lengths.

## Installation

To install this project, follow the steps below:

1. Clone the repository:
    ```bash
    git clone https://github.com/bastien-boivin/bb-app.git
    ```
2. Navigate to the project directory:
    ```bash
    cd bb-app
    ```
3. Create and activate a conda environment:
    ```bash
    conda create --name bb-app-env python=3.9
    conda activate bb-app-env
    ```
4. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the application, execute the following command:
```bash
streamlit run Home.py
```

## Contact

If you have any questions, feel free to reach out:

- **Name**: Bastien Boivin
- **Email**: [bastien.boivin@univ-rennes.fr]
