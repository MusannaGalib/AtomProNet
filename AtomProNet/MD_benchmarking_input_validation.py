def validate_repetitions(repetitions):
    for rep in repetitions:
        if not rep.isdigit() or int(rep) <= 0:
            print(f"Error: '{rep}' is not a valid positive integer. Please enter only positive integers.")
            exit(1)

def validate_potentials(potentials):
    from config import VALID_POTENTIALS
    for pot in potentials:
        if pot not in VALID_POTENTIALS:
            print(f"Error: '{pot}' is not a valid interatomic potential. Please enter valid options: {', '.join(VALID_POTENTIALS)}.")
            exit(1)
