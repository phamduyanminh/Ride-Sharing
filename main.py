from simulation import (
    RideCompletionSimulation,
    RideCancelationSimulation
)


def main():
    print("\nAvailable Simulations:")
    print("  1. Ride Completion")
    print("  2. Ride Cancelation")

    choice = input("\nSelect simulation (1-2): ").strip()

    simulations = {
        '1': [RideCompletionSimulation],
        '2': [RideCancelationSimulation]
    }

    selected = simulations.get(choice, [])

    for SimClass in selected:
        sim = SimClass()
        sim.execute()


if __name__ == "__main__":
    main()