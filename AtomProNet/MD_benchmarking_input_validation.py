def validate_repetitions(repetitions):
    """
    Validates the unit cell repetitions input by the user.

    Args:
        repetitions (list): List of repetition values entered by the user.

    Returns:
        list: Validated list of repetition values.
    """
    while True:
        invalid_reps = [rep for rep in repetitions if not rep.isdigit() or int(rep) <= 0]
        if not invalid_reps:
            return repetitions
        print(f"Error: The following repetitions are not valid positive integers: {', '.join(invalid_reps)}")
        repetitions = input("Please re-enter the unit cell repetitions (separated by spaces, e.g., '1 3 5 7 10'): ").split()

def validate_potentials(potentials):
    """
    Validates the interatomic potentials input by the user.

    Args:
        potentials (list): List of potentials entered by the user.

    Returns:
        list: Validated list of potentials.
    """
    from MD_benchmarking_config import VALID_POTENTIALS
    while True:
        invalid_pots = [pot for pot in potentials if pot not in VALID_POTENTIALS]
        if not invalid_pots:
            return potentials
        print(f"Error: The following potentials are not valid: {', '.join(invalid_pots)}")
        print(f"Valid options are: {', '.join(VALID_POTENTIALS)}")
        potentials = input(f"Please re-enter the interatomic potentials ({', '.join(VALID_POTENTIALS)}) separated by spaces: ").lower().split()
