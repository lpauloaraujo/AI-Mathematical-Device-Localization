from ga.ga_classes import GASample, BSMeasurement


def load_ga_samples(path):
    samples = []

    with open(path, "r") as file:
        for line in file:
            values = line.strip().split(";")

            samples.append(
                GASample(
                    user_x=float(values[0]),
                    user_y=float(values[1]),
                    measurements=[
                        BSMeasurement(
                            x=float(values[2]),
                            y=float(values[3]),
                            distance=float(values[4])
                        ),
                        BSMeasurement(
                            x=float(values[5]),
                            y=float(values[6]),
                            distance=float(values[7])
                        ),
                        BSMeasurement(
                            x=float(values[8]),
                            y=float(values[9]),
                            distance=float(values[10])
                        )
                    ],
                    case=values[11]
                )
            )

    return samples