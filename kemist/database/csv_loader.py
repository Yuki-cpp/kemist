import kemist.core as km


def load_molecules(file):
    molecules = []

    for line in file.readlines():
        columns = line.split(";")

        name = columns[0].strip().lower()
        iupac = columns[1].strip().lower() if columns[1] else None
        formula = columns[2].strip().lower() if columns[2] else None
        on_libview = False

        if columns[3] and columns[3].strip().lower() == "yes":
            on_libview = True
        retention_times = [float(s) for s in columns[4:]]

        molecules.append(km.Molecule(iupac=iupac, formula=formula, is_on_libview=on_libview, known_names=[name],
                                     retention_times=retention_times))
    return molecules


def load_storage_areas(file):
    storages = {}

    for line in file.readlines():
        columns = line.split(";")

        storage_name = columns[0].strip().lower()
        molecule_name = columns[1].strip().lower()

        if storage_name in storages:
            storages[storage_name].append(molecule_name)
        else:
            storages[storage_name] = [molecule_name]

    return storages
