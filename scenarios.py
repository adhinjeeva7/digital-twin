from twin import DigitalTwin


def run_healthy():
    # no scenario set - baseline run
    twin = DigitalTwin()
    return twin, twin.run()


def run_hypoxia():
    # low FiO2 kicks in after onset_s
    twin = DigitalTwin()
    twin.scenario = "hypoxia"
    return twin, twin.run()


def run_fluid_overload():
    # kidney takes in more fluid than it can clear after onset_s
    twin = DigitalTwin()
    twin.scenario = "fluid_overload"
    return twin, twin.run()


def run_heart_failure():
    # weaker heart (lower sv_baseline, blunted Frank-Starling) after onset_s
    twin = DigitalTwin()
    twin.scenario = "heart_failure"
    return twin, twin.run()


if __name__ == "__main__":
    for name, runner in [
        ("healthy", run_healthy),
        ("hypoxia", run_hypoxia),
        ("fluid_overload", run_fluid_overload),
        ("heart_failure", run_heart_failure),
    ]:
        twin, result = runner()
        print(name, "final state:", result.y[:  , -1])