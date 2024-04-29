from taipy import Config
from taipy.gui import State
import taipy as tp
import pandas as pd
import datetime as dt

data = pd.read_csv(
    "https://raw.githubusercontent.com/Avaiga/taipy-getting-started-core/develop/src/daily-min-temperatures.csv"
)


def predict(
    historical_temperature: pd.DataFrame, date_to_forecast: dt.datetime
) -> float:
    """Execute baseline prediction for predicting temperatures.

    Predicts temperature for a date based on historical data of the same date.

    Args:
        historical_temperature (pd.DataFrame): Temperature history data
        date_to_forecast (dt.datetime): Date to predict

    Returns:
        float: Probability of temperature of date
    """
    print("Running baseline...")
    historical_temperature["Date"] = pd.to_datetime(historical_temperature["Date"])
    historical_same_day = historical_temperature.loc[
        (historical_temperature["Date"].dt.day == date_to_forecast.day)
        & (historical_temperature["Date"].dt.month == date_to_forecast.month)
    ]
    return historical_same_day["Temp"].mean()


# Since we already created it, we can load it immediately.
Config.load("config.toml")

if __name__ == "__main__":
    tp.Core().run()

    scenario_cfg = Config.scenarios["normal_scenario"]

    scenario = tp.create_scenario(scenario_cfg)

    # Write data to data node
    scenario.historical_temperature.write(data)
    scenario.date_to_forecast.write(dt.datetime.now())

    # Execute the scenario
    tp.submit(scenario)

    # Read the value of predictions
    print("Value at the end of task", scenario.predictions.read())

    def save(state: State):
        state.scenario.historical_temperature.write(data)
        state.scenario.date_to_forecast.write(state.date)
        state.refresh("scenario")
        tp.gui.notify(state, "s", "Saved! Ready to submit")

    date = None
    scenario_md = """
<|{scenario}|scenario_selector|>

Select a Date
<|{date}|date|on_change=save|active={scenario}|>

Run the scenario
<|{scenario}|scenario|>
<|{scenario}|scenario_dag|>

View all the information on your prediction here
<|{scenario.predictions}|data_node|>
"""

    tp.Gui(scenario_md).run()
